from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .room_manager import create_room, join_room, update_state, get_state

@csrf_exempt
def create_multiplayer_room(request):
    data = json.loads(request.body.decode("utf-8"))
    host_name = data.get("host")
    room_code = create_room(host_name)
    return JsonResponse({"room_code": room_code})

@csrf_exempt
def join_multiplayer_room(request):
    data = json.loads(request.body.decode("utf-8"))
    room_code = data.get("room_code")
    player_name = data.get("player")
    success = join_room(room_code, player_name)
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
