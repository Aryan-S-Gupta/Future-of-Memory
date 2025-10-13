import pytest
import threading
from unittest.mock import patch, MagicMock
from multiplayer.voting_session import VotingSession  # adjust import path as needed

# --- FIXTURES AND HELPERS ---

@pytest.fixture
def mock_rm():
    """Mock the room_manager module to isolate VotingSession from external dependencies."""
    with patch("multiplayer.voting_session.rm") as mock_rm:
        mock_rm.get_players.return_value = ["Alice", "Bob", "Charlie"]
        yield mock_rm


@pytest.fixture
def session(mock_rm):
    """Create a fresh VotingSession instance for testing."""
    return VotingSession(room_code="ROOM123", turn_id=1, vote_timeout=5)


# --- BASIC INITIALIZATION TESTS ---

def test_session_initialization(session):
    """Verify initialization sets all attributes correctly."""
    assert session.room_code == "ROOM123"
    assert session.turn_id == 1
    assert isinstance(session.lock, threading.Lock)
    assert session.final_option is None
    assert isinstance(session.vote_timer, threading.Timer)
    assert session.total_players == 3


# --- START VOTING ---

def test_start_voting_resets_state(session, mock_rm):
    """Ensure start_voting() resets relevant attributes and starts the timer."""
    session.votes = {"opt1": 2}
    session.voted_players = ["Alice"]
    session.num_responses = 1

    session.start_voting()

    assert session.votes == {}
    assert session.voted_players == []
    assert session.num_responses == 0
    mock_rm.get_players.assert_called_with("ROOM123")


# --- PROCESS PLAYER RESPONSE ---

def test_process_player_response_records_vote(session):
    """Ensure process_player_response() records a vote and updates tallies."""
    session.total_players = 3

    result = session.process_player_response("ROOM123", "Alice", "opt1")

    assert "Alice" in session.voted_players
    assert session.p_votes["Alice"] == "opt1"
    assert session.votes["opt1"] == 1
    assert result is None  # Not finished yet


def test_process_player_response_all_voted(session):
    """Test early vote completion when all players vote."""
    session.total_players = 2
    session.voted_players = []
    session.votes = {}

    session.process_player_response("ROOM123", "Alice", "opt1")
    result = session.process_player_response("ROOM123", "Bob", "opt1")

    assert result == "opt1"  # Voting should complete
    assert session.final_option == "opt1"


def test_process_player_response_invalid_room(session):
    """Should raise ValueError if player votes in wrong room."""
    with pytest.raises(ValueError):
        session.process_player_response("WRONGROOM", "Alice", "opt1")


def test_process_player_response_duplicate_vote(session):
    """Ensure duplicate votes from the same player are ignored."""
    session.voted_players = ["Alice"]
    result = session.process_player_response("ROOM123", "Alice", "opt2")
    assert result is None


# --- FINAL VOTE COMPUTATION ---

def test_compute_final_vote_normal(session):
    """Test normal winner selection when no tie."""
    session.votes = {"opt1": 3, "opt2": 1}
    result = session.compute_final_vote()
    assert result == "opt1"
    assert session.final_option == "opt1"


def test_compute_final_vote_tie(session):
    """Test tie detection logic."""
    session.votes = {"opt1": 2, "opt2": 2}
    result = session.compute_final_vote()
    assert result == "TIE"
    assert session.tie_mode
    assert set(session.tie_options) == {"opt1", "opt2"}


# --- TIEBREAKERS ---

def test_submit_tiebreak_score_and_resolve(session):
    """Test tie-breaker flow from score submission to resolution."""
    session.tie_mode = True
    session.tie_players = ["Alice", "Bob"]
    session.p_votes = {"Alice": "opt1", "Bob": "opt2"}

    # Alice submits first — not resolved yet
    result = session.submit_tiebreak_score("Alice", 90)
    assert result is None
    assert session.tie_scores["Alice"] == 90

    # Bob submits — should trigger resolution
    result = session.submit_tiebreak_score("Bob", 95)
    assert result is not None
    assert result["winner"] == "Bob"
    assert result["winning_option"] == "opt2"
    assert not session.tie_mode  # tie-break should be turned off


def test_submit_tiebreak_score_invalid_player(session):
    """Ignore tiebreak submissions from non-tie players."""
    session.tie_mode = True
    session.tie_players = ["Alice"]
    result = session.submit_tiebreak_score("Bob", 50)
    assert result is None


# --- RESET AND STATE CHECKS ---

def test_reset_votes_clears_state(session):
    """Ensure reset_votes() clears all vote-related data."""
    session.votes = {"opt1": 2}
    session.voted_players = ["Alice"]
    session.final_option = "opt1"
    session.vote_timer = threading.Timer(10, lambda: None)

    session.reset_votes()
    assert session.votes == {}
    assert session.voted_players == []
    assert session.final_option is None
    assert session.vote_timer is None


def test_has_finished(session):
    """Test has_finished() correctly identifies completion."""
    assert not session.has_finished()
    session.final_option = "opt1"
    assert session.has_finished()


def test_get_current_votes(session, mock_rm):
    """Verify get_current_votes() returns correct pending/voted mapping."""
    session.p_votes = {"Alice": "opt1"}
    session.voted_players = ["Alice"]

    votes = session.get_current_votes()
    assert votes["Alice"] == "opt1"
    assert votes["Bob"] == "Pending"



# --- ADDITIONAL TESTS FOR FULL COVERAGE ---

def test_end_voting_marks_inactive_players(session, mock_rm):
    """Ensure end_voting() marks inactive players and computes final result."""
    session.voted_players = ["Alice"]
    session.votes = {"opt1": 1}
    session.compute_final_vote = MagicMock(return_value="opt1")

    session.end_voting()

    assert session.inactive_players == {"Bob", "Charlie"}
    assert session.num_responses == len(mock_rm.get_players.return_value)
    session.compute_final_vote.assert_called_once()


def test_resolve_tiebreak_winner_handles_secondary_tie(session):
    """Test resolve_tiebreak_winner() handles secondary tie with random.choice."""
    session.p_votes = {"Alice": "opt1", "Bob": "opt2"}
    session.tie_scores = {"Alice": 90, "Bob": 90}

    with patch("multiplayer.voting_session.random.choice", return_value="Alice"):
        result = session.resolve_tiebreak_winner()

    assert result["winner"] == "Alice"
    assert result["winning_option"] == "opt1"
    assert session.final_option == "opt1"


def test_add_and_remove_player(session):
    """Verify player count increases and decreases correctly."""
    original = session.total_players
    session.add_player()
    assert session.total_players == original + 1

    session.remove_player()
    assert session.total_players == original

    # Test boundary case: removing when 0 players
    session.total_players = 0
    session.remove_player()
    assert session.total_players == 0


def test_update_players_reflects_room_manager(session, mock_rm):
    """Ensure update_players() fetches player count from room_manager."""
    mock_rm.get_players.return_value = ["A", "B"]
    session.update_players()
    assert session.total_players == 2


def test_get_vote_status(session):
    """Verify get_vote_status() returns correct structure."""
    session.num_responses = 2
    session.voted_players = ["Alice", "Bob"]
    session.total_players = 3
    session.final_option = "opt1"
    status = session.get_vote_status()

    assert status == {
        "num_responses": 2,
        "players_voted": ["Alice", "Bob"],
        "total_players": 3,
        "final_option": "opt1",
        "turn_id": 1,
    }


def test_getters_and_setters(session):
    """Test all getter/setter methods behave correctly."""
    session.set_room_code("NEWCODE")
    assert session.get_room_code() == "NEWCODE"

    session.set_turn_id(99)
    assert session.get_turn_id() == 99

    session.set_vote_timeout(123)
    assert session.get_vote_timeout() == 123

    dummy_timer = threading.Timer(1, lambda: None)
    session.set_vote_timer(dummy_timer)
    assert session.get_vote_timer() == dummy_timer


def test_compute_final_vote_empty(session):
    """Should return None if no votes exist."""
    session.votes = {}
    assert session.compute_final_vote() is None


def test_is_timer_on_returns_timer(session):
    """Ensure is_timer_on() returns a Timer instance."""
    assert isinstance(session.is_timer_on(), threading.Timer)


