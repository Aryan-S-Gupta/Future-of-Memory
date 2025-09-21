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

def get_entry_by_year(year):
    return next((item for item in story_data if str(item["year"]) == str(year)), None)


def get_story_scenario(request, roomCode):
    logger.info(request)
    year = request.GET.get("year")
    if not year:
        return HttpResponseBadRequest("Missing 'year' parameter.")

    entry = get_entry_by_year(year)
    if not entry:
        return JsonResponse({"error": "Year not found."}, status=404)

    room = rm.get_rooms().get(room_code)
    if not room:
        return JsonResponse({"error": "Room not found"}, status=404)

    return JsonResponse({
        "year": entry["year"],
        "scenario": entry["background"]
    })


def get_multiplayer_question(request, room_code):
    year = request.GET.get("year")
    if not year:
        return HttpResponseBadRequest("Missing year")

    entry = get_entry_by_year(year)
    if not entry:
        return JsonResponse({"error": "Year not found"}, status=404)

    room = rooms.get(room_code)
    if not room:
        return JsonResponse({"error": "Room not found"}, status=404)


def get_story_question(request, room_code):
    """
    Retrieve the question for a given year from the story data.
    Expects a 'year' parameter in the GET request.
    Returns a JSON response with the question or an error message.
    """
    year = request.GET.get("year")
    room_code = request.get("roomCode")
    if not year or not room_code:
        return HttpResponseBadRequest("Missing 'year' parameter.")

    entry = get_entry_by_year(year)
    if not entry:
        return JsonResponse({"error": "Year not found."}, status=404)

    room = rooms.get(room_code)
    if not room:
        return JsonResponse({"error": "Room not found"}, status=404)
    return JsonResponse(
        {
            "year": entry["year"],
            "question": entry["question"],
            "options": entry["options"],
        }
    )


def get_story_result_by_choice(request, room_code):
    """
    Retrieve the result of a user's choice for a given year from the story data.
    Expects 'year' and 'choice' parameters in the GET request.
    Returns a JSON response with the result, or an error message if not found.
    """
    year = request.GET.get("year")
    choice = request.GET.get("choice")
    if not year or not choice:
        return HttpResponseBadRequest("Missing 'year' or 'choice' parameter.")

    entry = next((item for item in story_data if str(item["year"]) == year), None)
    if not entry:
        return JsonResponse({"error": "Year not found."}, status=404)

    result = entry.get("options", {}).get(choice.lower())
    if not result:
        return JsonResponse(
            {"error": f"No result found for choice '{choice}'"}, status=404
        )
    room = rooms.get(room_code)
    if not room:
        return JsonResponse({"error": "Room not found"}, status=404)
    return JsonResponse(
        {
            "year": entry["year"],
            "choice": choice,
            "result": result,
            "next_year": entry["year"] + 1,
        }
    )


def submit_choice(request):
    data = json.loads(request.body.decode("utf-8"))
    mode = data.get("mode")

    if mode == "single":
        get_singleplayer_result(request)

    elif mode == "multi":
        get_multiplayer_result(request)


def get_multiplayer_result(data, room_code):
        room_code = data.get("room_code")
        player_name = data.get("player_name")
        choice = data.get("choice")

        room = rm.get_rooms[room_code]
        player = room["players"].get[player_name]
        player.last_choice = choice
        player.save()

        # check if all players have submitted
        all_answered = all(p.last_choice for p in room.players.all())
        outcome = None
        if all_answered:
            from collections import Counter
            votes = [p.last_choice for p in room.players.all()]
            outcome = Counter(votes).most_common(1)[0][0]
            room.current_year += 1
            room.save()
        return JsonResponse({"all_answered": all_answered, "outcome": outcome})

@csrf_exempt
@require_POST
def get_story_result(request):
    """
    Retrieves the user's selected choice for a given question. This is a post method
    which means this is directly retrived from the user input
    """
    try:
        body = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    year = body.get("year")
    choice = body.get("choice")

    if not year or not choice:
        return HttpResponseBadRequest("Missing 'year' or 'choice' parameter.")

    return JsonResponse(
        {
            "year": year,
            "choice": choice,
        }
    )


@csrf_exempt
@require_POST
def rag_retrieve(request):

    default_query = "fatigue"
    query: str
    if request.method != "POST":
        logger.warning("Non-POST request received. Using default query instead")
        query = default_query
    else:
        data = json.loads(request.body.decode("utf-8"))
        query_text = data.get("query_text")
        keywords = data.get("keywords")
        logger.debug(
            f"Incoming RAG retrieval API request, {query_text = }, {keywords = }"
        )
        query = query_text or keywords
        if not query:
            logger.warning(
                "No 'query_text' or 'keywords' parameter provided. Using default query instead"
            )
            query = default_query

    items = retrieve_chunks(query)
    return JsonResponse({"items": items})
