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
DATA_FILE = os.path.join(BASE_DIR, "data", "static_stories.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    story_data = json.load(f)

from .room_manager import create_room, join_room, update_state, get_state, get_room_codes

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@csrf_exempt
def create_multiplayer_room(request):
    """
    Creates a multiplayer room.
    Accepts:
      - host: the name of the player creating the room
      - room_code (optional): custom room code
    Returns:
      - room_code: the room identifier
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
        host_name = data.get("host")
        if not host_name:
            return HttpResponseBadRequest("Missing 'host' parameter.")
        
        room_code = create_room(host_name)
        logger.info(f"Created room: {room_code}")
        return JsonResponse({"room_code": room_code})
    
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

def list_room_codes(request):
    """
    Returns list of active room codes.
    """
    return JsonResponse({"rooms": get_room_codes()})


@csrf_exempt
def join_multiplayer_room(request):
    data = json.loads(request.body.decode("utf-8"))
    logger.info("request: "+ str(data))
    room_code = data.get("roomCode")
    player_name = data.get("playerName")
    success = join_room(room_code, player_name)
    logger.info("the result of join_room " + str(success))
    return JsonResponse({"success": str(success)})

@csrf_exempt
def sync_state(request):
    data = json.loads(request.body.decode("utf-8"))
    room_code = data.get("room_code")
    state = data.get("state")
    update_state(room_code, state)
    return JsonResponse({"success": True})

def get_current_state(request, room_code):
    return JsonResponse({"state": get_state(room_code)})
