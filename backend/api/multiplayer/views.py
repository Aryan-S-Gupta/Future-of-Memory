from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
import json
import logging
from .room_manager import create_room, join_room, update_state, get_state

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
        host_name = data.get("name")
        if not host_name:
            return HttpResponseBadRequest("Missing 'host' parameter.")
        
        room_code = create_room(host_name)
        logger.info(f"Created room: {room_code}")
        return JsonResponse({"room_code": room_code})
    
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")


@csrf_exempt
def join_multiplayer_room(request):
    data = json.loads(request.body.decode("utf-8"))
    room_code = data.get("room_code")
    player_name = data.get("player")
    success = join_room(room_code, player_name)
    logger.log("the result of join_room " + success)
    return JsonResponse({"success": success})

@csrf_exempt
def sync_state(request):
    data = json.loads(request.body.decode("utf-8"))
    room_code = data.get("room_code")
    state = data.get("state")
    update_state(room_code, state)
    return JsonResponse({"success": True})

def get_current_state(request, room_code):
    return JsonResponse({"state": get_state(room_code)})
