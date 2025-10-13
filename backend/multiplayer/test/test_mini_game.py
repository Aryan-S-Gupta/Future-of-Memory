import pytest
import logging
from multiplayer import mini_game

@pytest.fixture(autouse=True)
def clear_scores():
    """Ensure SINGLE_PLAYER_SCORES is reset before each test."""
    mini_game.SINGLE_PLAYER_SCORES.clear()
    yield
    mini_game.SINGLE_PLAYER_SCORES.clear()


def test_submit_score_success(caplog):
    """Test submitting a valid score."""
    caplog.set_level(logging.INFO)
    result = mini_game.submit_score_single("Alice", 85)

    assert result == {
        "status": "success",
        "player_name": "Alice",
        "score": 85,
    }
    assert "Alice" in mini_game.SINGLE_PLAYER_SCORES
    assert mini_game.SINGLE_PLAYER_SCORES["Alice"] == 85
    assert "Score submitted: Alice -> 85" in caplog.text


def test_submit_score_missing_name(caplog):
    """Test submitting a score with missing player name."""
    caplog.set_level(logging.WARNING)
    result = mini_game.submit_score_single("", 90)

    assert "error" in result
    assert result["error"] == "Missing player_name or score"
    assert mini_game.SINGLE_PLAYER_SCORES == {}
    assert "missing parameters" in caplog.text


def test_submit_score_missing_score(caplog):
    """Test submitting a score with missing score value."""
    caplog.set_level(logging.WARNING)
    result = mini_game.submit_score_single("Bob", None)

    assert result == {"error": "Missing player_name or score"}
    assert "Bob" not in mini_game.SINGLE_PLAYER_SCORES
    assert "missing parameters" in caplog.text


def test_get_scores_returns_all():
    """Test retrieving all stored scores."""
    mini_game.SINGLE_PLAYER_SCORES["Alice"] = 85
    mini_game.SINGLE_PLAYER_SCORES["Bob"] = 72

    result = mini_game.get_scores()
    assert result == {"Alice": 85, "Bob": 72}


def test_submit_and_get_scores_combined():
    """Test that submitting a score is reflected in get_scores()."""
    mini_game.submit_score_single("Charlie", 99)
    scores = mini_game.get_scores()

    assert "Charlie" in scores
    assert scores["Charlie"] == 99


def test_multiple_submissions_same_player():
    """Test that submitting multiple times updates existing score."""
    mini_game.submit_score_single("Dana", 50)
    mini_game.submit_score_single("Dana", 75)

    scores = mini_game.get_scores()
    assert scores["Dana"] == 75  # latest score should overwrite old one
