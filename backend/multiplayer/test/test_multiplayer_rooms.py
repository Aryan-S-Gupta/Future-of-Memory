import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.http import JsonResponse

import multiplayer.room_manager as rm
from multiplayer import views


class BaseMultiplayerTest(TestCase):
    """Base test class setting up the Django test client and mocks."""
    def setUp(self):
        self.client = Client()
        rm.rooms.clear()
        rm.room_sessions.clear()
        views.VotingSessions.clear()


# ------------------ ROOM CREATION & JOINING ------------------

class TestRoomCreationAndJoining(BaseMultiplayerTest):
    """Tests for room creation, listing, and joining views."""

    @patch("multiplayer.views.create_room", return_value=("1234", 99))
    @patch("multiplayer.views.rm.get_state", return_value={"turn_id": -1})
    def test_create_multiplayer_room(self):
        """Should create a room and initialize VotingSession."""
        response = self.client.post(
            "/multiplayer/create-room/",
            json.dumps({"host": "Manya"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["room_code"], "1234")
        self.assertEqual(data["session_id"], 99)
        self.assertIn(("1234", -1), views.VotingSessions.keys())

    def test_create_room_missing_host(self):
        """Should return 400 if host name is missing."""
        response = self.client.post(
            "/multiplayer/create-room/",
            json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    @patch("multiplayer.views.get_room_codes", return_value=["1234", "5678"])
    def test_list_room_codes(self):
        """Should return all active room codes."""
        response = self.client.get("/multiplayer/rooms/")
        self.assertJSONEqual(response.content, {"rooms": ["1234", "5678"]})

    @patch("multiplayer.views.join_room", return_value=True)
    @patch("multiplayer.views.rm.get_state", return_value={"turn_id": 0, "year": 2035})
    @patch("multiplayer.views.rm.get_session_id", return_value=55)
    @patch("multiplayer.views.rm.room_exists", return_value=True)
    def test_join_multiplayer_room_success(self, *mocks):
        """Should add player to room and update voting session."""
        rm.rooms["ABCD"] = {"players": ["Host"], "host": "Host", "state": {"turn_id": 0}}
        views.VotingSessions[("ABCD", 0)] = MagicMock()
        response = self.client.post(
            "/multiplayer/join-room/",
            json.dumps({"roomCode": "ABCD", "playerName": "Alice"}),
            content_type="application/json"
        )
        data = response.json()
        self.assertEqual(data["success"], "True")
        self.assertIn("session_id", data)


# ------------------ STATE SYNCHRONIZATION ------------------

class TestStateSync(BaseMultiplayerTest):
    """Tests for syncing and retrieving game state."""

    @patch("multiplayer.views.update_state")
    @patch("multiplayer.views.rm.room_exists", return_value=True)
    def test_sync_state_updates_room(self, mock_exists, mock_update):
        """Should update room state when valid room is provided."""
        payload = {"room_code": "1234", "state": {"year": 2036}}
        response = self.client.post(
            "/multiplayer/sync/",
            json.dumps(payload),
            content_type="application/json"
        )
        self.assertJSONEqual(response.content, {"success": True})
        mock_update.assert_called_once()

    @patch("multiplayer.views.rm.room_exists", return_value=False)
    def test_sync_state_invalid_room(self, mock_exists):
        """Should return room_exists False if room does not exist."""
        payload = {"room_code": "9999", "state": {}}
        response = self.client.post(
            "/multiplayer/sync/",
            json.dumps(payload),
            content_type="application/json"
        )
        self.assertJSONEqual(response.content, {"success": False, "room_exists": False})

    @patch("multiplayer.views.get_state", return_value={"turn_id": 1, "year": 2036})
    def test_get_current_state(self, mock_state):
        """Should return the current room state."""
        response = self.client.get("/multiplayer/state/1234/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], {"turn_id": 1, "year": 2036})


# ------------------ LEAVE ROOM ------------------

class TestLeaveRoom(BaseMultiplayerTest):
    """Tests for leaving a multiplayer room."""

    @patch("multiplayer.views.rm.room_exists", return_value=True)
    @patch("multiplayer.views.rm.leave_room", return_value=True)
    @patch("multiplayer.views.rm.get_players", return_value=["Bob"])
    def test_leave_room_success(self, *mocks):
        """Should allow player to leave and return JSON response."""
        rm.rooms["A1"] = {"players": ["Host", "Bob"], "host": "Host", "state": {}}
        response = self.client.get("/multiplayer/leave-room/?roomCode=A1&playerName=Host")
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json())

    @patch("multiplayer.views.rm.room_exists", return_value=False)
    def test_leave_room_invalid(self, mock_exists):
        """Should return error if room does not exist."""
        response = self.client.get("/multiplayer/leave-room/?roomCode=BAD&playerName=Host")
        data = response.json()
        self.assertFalse(data["room_exists"])
