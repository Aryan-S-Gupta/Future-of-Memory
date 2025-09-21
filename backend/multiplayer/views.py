import json
import os
import logging
import multiplayer.room_manager as rm
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rag.retrieve import retrieve_chunks

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "../api/data/static_stories.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    story_data = json.load(f)

from .room_manager import create_room, join_room, update_state, get_state, get_room_codes


@csrf_exempt
def create_multiplayer_room(request):
    """
    Creates a new multiplayer room.
    
    Expects JSON POST request with:
      - "host": Name of the player creating the room
      - "room_code" (optional): custom room code (not currently used)
    
    Returns JSON response:
      - "room_code": Generated room identifier
    """
    try:
        # Parse JSON body from request
        data = json.loads(request.body.decode("utf-8"))
        host_name = data.get("host")

        # Validate that host name is provided
        if not host_name:
            return HttpResponseBadRequest("Missing 'host' parameter.")
        
        # Create a new room using room_manager
        room_code = create_room(host_name)
        logger.info(f"Created room: {room_code}")

        # Return room code as JSON
        return JsonResponse({"room_code": room_code})
    
    except json.JSONDecodeError:
        # Return 400 Bad Request if JSON is invalid
        return HttpResponseBadRequest("Invalid JSON")


def list_room_codes(request):
    """
    Returns a list of all active room codes.
    
    Response JSON:
      - "rooms": List of active room codes
    """
    return JsonResponse({"rooms": get_room_codes()})


@csrf_exempt
def join_multiplayer_room(request):
    """
    Adds a player to an existing multiplayer room.
    
    Expects JSON POST request with:
      - "roomCode": Code of the room to join
      - "playerName": Name of the joining player
    
    Returns JSON response:
      - "success": True/False depending on whether join succeeded
    """
    data = json.loads(request.body.decode("utf-8"))
    logger.info("request: "+ str(data))

    room_code = data.get("roomCode")
    player_name = data.get("playerName")

    # Attempt to join the room
    success = join_room(room_code, player_name)
    logger.info("the result of join_room " + str(success))

    return JsonResponse({"success": str(success)})


@csrf_exempt
def sync_state(request):
    """
    Updates the game state for a given room.
    
    Expects JSON POST request with:
      - "room_code": The room to update
      - "state": The new state dictionary
    
    Returns JSON response:
      - "success": True
    """
    data = json.loads(request.body.decode("utf-8"))
    room_code = data.get("room_code")
    state = data.get("state")

    # Update room state using room_manager
    update_state(room_code, state)
    
    return JsonResponse({"success": True})


def get_current_state(request, room_code):
    """
    Retrieves the current state of a specific room.
    
    Args:
        room_code (str): The room identifier
    
    Returns JSON response:
      - "state": Current state of the room
    """
    return JsonResponse({"state": get_state(room_code)})
