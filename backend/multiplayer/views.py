import json
import os
import logging

from django.shortcuts import get_object_or_404
import multiplayer.room_manager as rm
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rag.retrieve import retrieve_chunks
from .game_logic import VotingSession

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "../api/data/static_stories.json")
VOTING_SESSION = None # Global variable to hold the current voting session
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
        room_code, session = create_room(host_name)
        global VOTING_SESSION
        VOTING_SESSION = VotingSession(room_code)
        logger.info(f"Initialized VotingSession for room {room_code}")
        logger.info(f"Created room: {room_code}")

        # Return room code as JSON
        return JsonResponse({"room_code": room_code, "session_id": session})
    
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
@require_POST
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

    if not rm.room_exists: 
        JsonResponse({"Success": False, "room_exists": False})
    # Attempt to join the room
    success = join_room(room_code, player_name)
    session = None
    if success:
        global VOTING_SESSION
        VOTING_SESSION.update_players()
        turn = rm.get_state(room_code)
        logger.info(f"Current turn for room {room_code} is {turn}")
        logger.info(f"Player {player_name} joined room {room_code}")
        session = rm.get_session_id(room_code)
        logger.info(f"Session id for room {room_code} is {session}")
    else:
        logger.warning(f"Failed to join room {room_code}: Room does not exist")
    logger.info("the result of join_room " + str(success))

    return JsonResponse({"success": str(success), "session_id": session, "turn_id" : str(turn)})


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
    
    if not rm.room_exists(room_code):
        return JsonResponse({'success': False, 'room_exists': False})

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


@csrf_exempt
def leave_multiplayer_room(request):
    room_code = request.GET.get("roomCode")
    player_name = request.GET.get("playerName")

    if not rm.room_exists(room_code):
        logging.info(f'the room code {room_code} does not exist')
        return JsonResponse({'success': False, 'room_exists': False})
    
    success = rm.leave_room(room_code, player_name)
    logging.info(f'the output of leave is {success}')
    data_payload = {}
    if success:
        # delete all voting sessions
        logging.info("Emptied out all voting sessions and left the room")
        if rm.room_exists(room_code):
            rem_players = rm.get_players(room_code)
            logging.info(f'One player removed but the room exists. ' +
                         f'The remaining players are {rem_players}')
            data_payload = {
                'success': success,
                'room_code': room_code,
                'player_name': player_name,
                'destroy': False,
                'message': f'player removed but {room_code} still exists'
            }
        else:
            data_payload = {
                'success': success,
                'room_code': room_code,
                'player_name': player_name,
                'destroy': True,
                'message': f'Host removed and {room_code} does not exists'
            }

    else: 
        data_payload = {
            'success': success,
            'room_code': room_code,
            'player_name': player_name,
            'message': f'Failed to leave room {room_code}'
        }
        logger.warning(f'Failed to leave room {room_code}')
    return JsonResponse(data_payload)



@csrf_exempt
def submit_choice(request):
    data = json.loads(request.body.decode("utf-8"))
    mode = data.get("mode")
    get_multiplayer_result(request)


def get_multiplayer_result(data):
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



# new views
from shared.models import Session, Option, Turn


# need to call this somewhere - as soon as the game is created
def create_session(request):
    """
    Create a new Session and return its ID as JSON.
    """
    session = Session.objects.create()
    logger.debug(f'session id created: {session.id}')
    return JsonResponse({'session_id': session.id}, status=201)

# intro page

# need a call in background page - it starts gebnerating question and options and images and scenario
from shared.tasks import start_turn_pipeline
def start_prerendering(request):
    year = int(request.GET.get("year"))
    session_id = request.GET.get("session_id")
    logger.debug("start_turn_pipeline.send() called with session id " + str(session_id) + " and year " + year)
    response = start_turn_pipeline.send(session_id, year)
    logger.debug("start_turn_pipeline.send() called: " + response)
    return JsonResponse({'status': 'generation_started'})


# send the existing work
# everytime this is called update turn id 
def display_question_and_options(request, session_id, room_code, turn_id):

    logger.debug(f"display_question_and_options called for session_id={session_id}")
    existing_session = get_object_or_404(Session, id=session_id)
    logger.debug(f"Found session: {existing_session}")
    logger.debug(f"turn_id received: {turn_id}")

    if not rm.room_exists(room_code):
        return JsonResponse({'success': False, 'room_exists': False})

    if int(turn_id) == -1:
        # first turn, get the latest turn (or none)
        latest_turn = (
            Turn.objects
            .filter(session_id=existing_session.id)
            .order_by('-year', '-id')
            .first()
        )
        if not latest_turn:
            logger.warning("No turns found for this session")
            return JsonResponse({'error': 'No turn found for this session'}, status=404)
    else:
        # get specific turn by ID
        latest_turn = get_object_or_404(Turn, id=int(turn_id))

    logger.debug(f"Latest turn for session: {latest_turn}")

    # fetch options
    options = Option.objects.filter(turn_id=latest_turn.id).order_by('label')
    options_payload = [
        {'option_id': o.id, 'label': o.label, 'option_text': o.option_text or ''}
        for o in options
    ]

    response_payload = {
        'message': 'ok',
        'room_code': room_code,
        'turn_id': latest_turn.id,
        'year': latest_turn.year,
        'question': latest_turn.question or '',
        'options': options_payload,
    }

    return JsonResponse(response_payload)


# scenario and image display page
from shared.services import display_world_view




def display_scenario_and_image(request, session_id, turn_id, year, option_id, room_code):
    """
    Display the world view after user makes a choice.
    """
    player_name = request.GET.get("playerName")
    logger.debug(f"playername is {player_name}")
    if not rm.room_exists(room_code):
        return JsonResponse({'success': False, 'room_exists': False})
    final_option = VOTING_SESSION.process_player_response(room_code, player_name, option_id)
    if final_option is None:
        logger.debug("Not all players have voted yet.")
        print("Not all players have voted yet.")
        return JsonResponse({
            'success': False,
            'image': {"status": "waiting"},
            'message': 'Waiting for other players to vote.' 
            }, status=404)
    logger.debug(f"Voting result is {final_option}")
    logger.debug(f"votes so far {VOTING_SESSION.votes}")
    logger.debug(f"num responses so far {VOTING_SESSION.num_responses}")
    logger.debug(f"votes for option {option_id} is {VOTING_SESSION.votes.get(option_id)}")
    

    # when you receive request check no of players, check number of responses, create a map of option id, and num votes, then get the votes from the reqwuest 
    # the max voted option id, and use that to generate the world view
    try:
        world_view_data = display_world_view(session_id, turn_id, int(year), final_option)

        if world_view_data.get("success"):
            next_year = int(year) + 1
            next_turn = Turn.objects.filter(session_id=session_id, year=next_year).first()
            if next_turn:
                world_view_data["next_turn_id"] = next_turn.id 
            try:
                # start generating next turn in background
                start_turn_pipeline.send(session_id, next_year)
                logger.info(f"Started generating next turn (year {next_year}) in background")
            except Exception as e:
                logger.warning(f"Failed to start next turn generation: {e}")
        print("world view data: " + str(world_view_data))
        return JsonResponse(world_view_data)
        
    except Exception as e:
        print(f"Error displaying world view: {e}")
        return JsonResponse({
            'success': False,
            'status': 'error',
            'error': f'Failed to display world view: {str(e)}'
        }, status=500)

from shared.services import display_world_view
from django.http import JsonResponse

def display_scenario_and_image(request, session_id, turn_id, year, option_id, room_code):
    """
    Display the world view after user makes a choice.
    Returns current votes and scenario if all players have voted.
    """
    player_name = request.GET.get("playerName")
    logger.info(f"playername is {player_name}")
    if not rm.room_exists(room_code):
        return JsonResponse({'success': False, 'room_exists': False})

    # Process player response and determine the winning option if all voted
    final_option = VOTING_SESSION.process_player_response(room_code, player_name, option_id)

    # Prepare vote tracking info
    votes_info = {
        "num_responses": VOTING_SESSION.num_responses,
        "players_voted": list(VOTING_SESSION.votes.keys()),  # player names who voted
        "total_players": VOTING_SESSION.total_players,
    }

    # If not all players have voted, return votes info only
    if final_option is None:
        logger.info("Not all players have voted yet.")
        return JsonResponse({
            "success": False,
            "scenario": "",
            "votes_info": votes_info,
            "message": "Waiting for other players to vote."
        }, status=404)

    # All players have voted → generate world view
    try:
        world_view_data = display_world_view(session_id, turn_id, year, final_option)

        if world_view_data.get("success") and world_view_data.get("scenario").get("text") != "":
            next_year = int(year) + 1
            next_turn = Turn.objects.filter(session_id=session_id, year=next_year).first()
            if next_turn:
                world_view_data["next_turn_id"] = next_turn.id
            # start generating next turn in background
            try:
                start_turn_pipeline.send(session_id, next_year)
                logger.info(f"Started generating next turn (year {next_year}) in background")
            except Exception as e:
                logger.warning(f"Failed to start next turn generation: {e}")

            # Include votes info always
            world_view_data["votes_info"] = votes_info

            return JsonResponse(world_view_data)
        else:
            return JsonResponse({'error': 'No turn found for this session'}, status=404)

    except Exception as e:
        logger.error(f"Error displaying world view: {e}")
        return JsonResponse({
            'success': False,
            'status': 'error',
            'votes_info': votes_info,
            'error': f'Failed to display world view: {str(e)}'
        }, status=500)
