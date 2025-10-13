import pytest
from unittest.mock import patch, MagicMock

import multiplayer.room_manager as rm

@pytest.fixture(autouse=True)
def clean_rooms():
    """Ensure rooms and sessions are clean before each test."""
    rm.rooms.clear()
    rm.room_sessions.clear()
    yield
    rm.rooms.clear()
    rm.room_sessions.clear()



def test_create_room(mock_session):
    room_code, session_id = rm.create_room("Manya")
    assert room_code in rm.rooms
    assert rm.rooms[room_code]["host"] == "Manya"
    assert "Manya" in rm.rooms[room_code]["players"]


def test_join_and_leave_room(mock_session):
    code, _ = rm.create_room("Host")

    assert rm.join_room(code, "Alice")
    assert "Alice" in rm.get_players(code)

    assert rm.leave_room(code, "Alice")
    assert "Alice" not in rm.get_players(code)



def test_destroy_room(mock_session):
    code, _ = rm.reate_room("Host")
    assert rm.room_exists(code)

    assert rm.destroy_room(code)
    assert not rm.room_exists(code)


def test_destroy_all_rooms():
    rm.rooms["0001"] = {"host": "Manya", "players": ["Manya"], "state": {}}
    rm.room_sessions["0001"] = 10
    rm.destroy_all_rooms()
    assert rm.rooms == {}
    assert rm.room_sessions == {}



def test_host_and_player_management(mock_session):
    code, _ = rm.create_room("Manya")

    rm.add_player(code, "Alice")
    assert rm.get_player_count(code) == 2
    assert rm.is_host(code, "Manya")

    rm.set_host(code, "Alice")
    assert rm.get_host(code) == "Alice"
    assert rm.is_host(code, "Alice")

    assert rm.player_in_room_exists(code, "Alice")
    assert rm.remove_player(code, "Alice")
    assert not rm.player_in_room_exists(code, "Alice")


def test_transfer_host():
    code, _ = rm.create_room("Host")
    rm.add_player(code, "NewHost")
    assert rm.transfer_host(code, "NewHost")
    assert rm.get_host(code) == "NewHost"

def test_state_management():
    code, _ = rm.create_room("Host")

    state = {"turn_id": 5, "year": 2050}
    assert rm.update_state(code, state)
    assert rm.get_state(code) == state

    assert rm.reset_state(code)
    assert grm.et_state(code) == {"turn_id": -1, "year": 2035}


def test_room_summary_and_logging(mock_session, caplog):
    mock_session.objects.create.return_value = MagicMock(id=7)
    code, session_id = rm.create_room("Host")

    summary = rm.room_summary(code)
    assert summary is not None
    assert summary["session_id"] == session_id

    rm.log_all_rooms()
    assert f"Room {code}" in caplog.text


def test_get_room_codes_and_rooms():
    rm.rooms["0001"] = {"host": "H", "players": ["H"], "state": {}}
    assert rm.get_room_codes() == ["0001"]
    assert rm.get_rooms()["0001"]["host"] == "H"


def test_get_room_and_session_id():
    rm.rooms["0001"] = {"host": "H", "players": ["H"], "state": {}}
    rm.room_sessions["0001"] = 42
    assert rm.get_room("0001") == rooms["0001"]
    assert rm.get_session_id("0001") == 42
