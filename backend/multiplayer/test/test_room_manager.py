import pytest
from unittest.mock import MagicMock, patch
import multiplayer.room_manager as rm

# -----------------------------------------------------------------------------
# Global Test Setup
# -----------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_rooms():
    """
    Automatically runs before and after each test.

    Ensures a clean state by clearing the global room and session dictionaries.
    Prevents one test's data from affecting another.
    """
    rm.rooms.clear()
    rm.room_sessions.clear()
    yield
    rm.rooms.clear()
    rm.room_sessions.clear()

# -----------------------------------------------------------------------------
# Room Creation & Basic Lifecycle Tests
# -----------------------------------------------------------------------------

@patch("multiplayer.room_manager.Session")
def test_create_room(mock_session):
    """
    Test that a new room is correctly created with a unique room code,
    host name, and player list.
    """
    mock_session.objects.create.return_value = MagicMock(id=1)
    room_code, session_id = rm.create_room("Manya")

    # Verify the room exists and has expected data
    assert room_code in rm.rooms
    assert rm.rooms[room_code]["host"] == "Manya"
    assert "Manya" in rm.rooms[room_code]["players"]
    assert rm.room_sessions[room_code] == 1


@patch("multiplayer.room_manager.Session")
def test_join_and_leave_room():
    """
    Test that a player can join and leave a room successfully.
    """
    code, _ = rm.create_room("Host")

    # Player joins
    assert rm.join_room(code, "Alice")
    assert "Alice" in rm.get_players(code)

    # Player leaves
    assert rm.leave_room(code, "Alice")
    assert "Alice" not in rm.get_players(code)


@patch("multiplayer.room_manager.Session")
def test_destroy_room():
    """
    Test that a room can be destroyed and properly removed from global storage.
    """
    code, _ = rm.create_room("Host")
    assert rm.room_exists(code)

    # Destroy and verify deletion
    assert rm.destroy_room(code)
    assert not rm.room_exists(code)


def test_destroy_all_rooms():
    """
    Test that all rooms and sessions are cleared at once.
    """
    rm.rooms["0001"] = {"host": "Manya", "players": ["Manya"], "state": {}}
    rm.room_sessions["0001"] = 10
    rm.destroy_all_rooms()
    assert rm.rooms == {}
    assert rm.room_sessions == {}

# -----------------------------------------------------------------------------
# Host & Player Management Tests
# -----------------------------------------------------------------------------
def test_host_and_player_management():
    """
    Test player addition/removal and host changes.
    """
    code, _ = rm.create_room("Manya")

    # Add player
    rm.add_player(code, "Alice")
    assert rm.get_player_count(code) == 2
    assert rm.is_host(code, "Manya")

    # Change host
    rm.set_host(code, "Alice")
    assert rm.get_host(code) == "Alice"
    assert rm.is_host(code, "Alice")

    # Remove player
    assert rm.player_in_room_exists(code, "Alice")
    assert rm.remove_player(code, "Alice")
    assert not rm.player_in_room_exists(code, "Alice")

def test_transfer_host():
    """
    Test that host transfer correctly assigns a new host from existing players.
    """
    code, _ = rm.create_room("Host")
    rm.add_player(code, "NewHost")

    assert rm.transfer_host(code, "NewHost")
    assert rm.get_host(code) == "NewHost"

# -----------------------------------------------------------------------------
# Room State Management Tests
# -----------------------------------------------------------------------------
def test_state_management():
    """
    Test updating, retrieving, and resetting a room's state.
    """
    code, _ = rm.create_room("Host")

    # Update state
    state = {"turn_id": 5, "year": 2050}
    assert rm.update_state(code, state)
    assert rm.get_state(code) == state

    # Reset state to default
    assert rm.reset_state(code)
    assert rm.get_state(code) == {"turn_id": -1, "year": 2035}

# -----------------------------------------------------------------------------
# Summary & Logging Tests
# -----------------------------------------------------------------------------

@patch("multiplayer.room_manager.Session")
def test_room_summary_and_logging(mock_session, caplog):
    """
    Test that room summary and logging outputs work as expected.
    """
    mock_session.objects.create.return_value = MagicMock(id=7)
    code, session_id = rm.create_room("Host")

    summary = rm.room_summary(code)
    assert summary is not None
    assert summary["session_id"] == session_id

    # Verify room info logged
    rm.log_all_rooms()
    assert f"Room {code}" in caplog.text

# -----------------------------------------------------------------------------
# Utility & Accessor Tests
# -----------------------------------------------------------------------------

def test_get_room_codes_and_rooms():
    """
    Test that room accessors return the correct data.
    """
    rm.rooms["0001"] = {"host": "H", "players": ["H"], "state": {}}
    assert rm.get_room_codes() == ["0001"]
    assert rm.get_rooms()["0001"]["host"] == "H"


def test_get_room_and_session_id():
    """
    Test fetching individual room and session ID mappings.
    """
    rm.rooms["0001"] = {"host": "H", "players": ["H"], "state": {}}
    rm.room_sessions["0001"] = 42
    assert rm.get_room("0001") == rm.rooms["0001"]
    assert rm.get_session_id("0001") == 42
