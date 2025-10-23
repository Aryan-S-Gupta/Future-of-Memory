import json
import os
import logging

from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .mini_game import get_scores, submit_score_single
from .game_logic import VotingSession, VotingSessions
from api.views import rag_retrieve as rag_retrieve_api
import multiplayer.room_manager as rm
from shared.models import Session, Option, Turn
from shared.services import display_world_view
from shared.tasks import start_turn_pipeline

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "../api/data/static_stories.json")


with open(DATA_FILE, "r", encoding="utf-8") as f:
    story_data = json.load(f)


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
        mode = data.get("mode")

        # Validate that host name is provided
        if not host_name:
            return HttpResponseBadRequest("Missing 'host' parameter.")
        
        if mode == "host": 
            room_code, session = rm.create_host_room(host_name, mode)
        else: 
            room_code, session = rm.create_room(host_name, mode)

        turn_id = rm.get_state(room_code).get("turn_id", -1)
        VotingSessions[(room_code, turn_id)] = VotingSession(room_code, turn_id)
        logger.info(f"Initialized VotingSession for room {room_code}")
        logger.info(f"Created room: {room_code}")

        # Return room code as JSON
        return JsonResponse({"room_code": room_code, "session_id": session, "mode": mode})
    
    except json.JSONDecodeError:
        # Return 400 Bad Request if JSON is invalid
        return HttpResponseBadRequest("Invalid JSON")

def get_host(request, room_code): 
    host = rm.get_host(room_code)
    return JsonResponse({'host': host})

def check_game_started(request, room_code):
    if rm.get_mode(room_code) != "host":
        return JsonResponse({"unable to perform this action"})
    return JsonResponse({"game_started": rm.is_game_started(room_code)})


def start_game(request, room_code):
    if not rm.room_exists(room_code):
        logger.info("rooom does not exist")
        return JsonResponse({'error': 'Room not found'}, status=404)
    
    elif rm.get_players(room_code) == []:
        logger.info("room is empty")
        return JsonResponse({'empty': True})
    else: 
        if rm.get_mode(room_code) != "host":
            return JsonResponse({"unable to perform this action"})
        
    rm.set_game_started(room_code)
    return JsonResponse({'state': rm.is_game_started(room_code)})

def list_room_codes(request):
    """
    Returns a list of all active room codes.

    Response JSON:
      - "rooms": List of active room codes
    """
    return JsonResponse({"rooms": rm.get_room_codes()})


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
    logger.info("request: " + str(data))

    room_code = data.get("roomCode")
    player_name = data.get("playerName")
    session = None

    if not rm.room_exists:
        JsonResponse({"Success": False, "room_exists": False})
    
    if rm.is_game_started(room_code):
        logger.info(f"Game already started in room {room_code}")
        return JsonResponse({
            "success": False,
            "room_exists": True,
            "mode": rm.get_state(room_code),
            "game_started": str(rm.is_game_started(room_code))
        })
    
     # Check if player name is already taken in the room

    if rm.player_in_room_exists(room_code, player_name):
        logger.info(f"Player {player_name} already in room {room_code}")
        return JsonResponse({
            "success": False,
            "room_exists": True,
            "message": f"Player {player_name} already in room {room_code}"
        })
    # Attempt to join the room
    success = rm.join_room(room_code, player_name)
    if success:
        room_host = rm.get_host(room_code)
        mode = rm.get_mode(room_code)
        turn = rm.get_state(room_code)
        VotingSessions[(room_code, turn.get("turn_id"))].update_players()
        logger.info(
            f"Current turn for room {room_code} is {turn.get('turn_id')} and year is {turn.get('year')}"
        )
        logger.info(f"Player {player_name} joined room {room_code}")
        session = rm.get_session_id(room_code)
        logger.info(f"Session id for room {room_code} is {session}")
    else:
        logger.warning(f"Failed to join room {room_code}: Room does not exist")
    logger.info("the result of join_room " + str(success))

    return JsonResponse({
        "success": str(success),
        "session_id": session, 
        "turn_id" : str(turn), 
        "host": room_host,
        "mode": mode,
        "game_started": str(rm.is_game_started(room_code))
    })


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
        return JsonResponse({"success": False, "room_exists": False})

    # Update room state using room_manager
    rm.update_state(room_code, state)
    
    return JsonResponse({"success": True})


def get_current_state(request, room_code):
    """
    Retrieves the current state of a specific room.

    Args:
        room_code (str): The room identifier

    Returns JSON response:
      - "state": Current state of the room
    """
    return JsonResponse({"state": rm.get_state(room_code)})

 
@csrf_exempt
def leave_multiplayer_room(request):
    room_code = request.GET.get("roomCode")
    player_name = request.GET.get("playerName")

    if not rm.room_exists(room_code):
        logging.info(f"the room code {room_code} does not exist")
        return JsonResponse({"success": False, "room_exists": False})

    success = rm.leave_room(room_code, player_name)
    logging.info(f"the output of leave is {success}")
    data_payload = {}
    if success:
        # delete all voting sessions
        logging.info("Emptied out all voting sessions and left the room")
        if rm.room_exists(room_code):
            rem_players = rm.get_players(room_code)
            logging.info(
                f"One player removed but the room exists. "
                + f"The remaining players are {rem_players}"
            )
            data_payload = {
                "success": success,
                "room_code": room_code,
                "player_name": player_name,
                'destroy': rm.room_exists(room_code),
                "message": f"player removed but {room_code} still exists",
            }
        else:
            data_payload = {
                "success": success,
                "room_code": room_code,
                "player_name": player_name,
                "destroy": True,
                "message": f"Host removed and {room_code} does not exists",
            }

    else:
        data_payload = {
            "success": success,
            "room_code": room_code,
            "player_name": player_name,
            'destroy': rm.room_exists(room_code),
            "message": f"Failed to leave room {room_code}",
        }
        logger.warning(f"Failed to leave room {room_code}")
    return JsonResponse(data_payload)


@csrf_exempt
@require_POST
def rag_retrieve(request):
    """
    See rag_retrieve in backend/api/views
    """
    return rag_retrieve_api(request)


@csrf_exempt
def get_voting_status_with_options(request, room_code, turn_id):
    """
    Returns the current voting status for a room including player choices.
    """
    session_key = (room_code, int(turn_id))
    voting_session = VotingSessions.get(session_key)

    if not voting_session:
        return JsonResponse({"error": "No voting session found"}, status=404)

    votes = voting_session.get_current_votes()  # dict: {player: option_id or 'Pending'}
    payload = {
        "success": True,
        "votes": votes,
        "turn_id": turn_id,
        "num_responses": voting_session.num_responses,
        "total_players": voting_session.total_players,
        "final_option": voting_session.final_option,
        "player_votes": voting_session.get_p_votes()
    }
    logger.info(payload)
    return JsonResponse(payload)


def create_session(request):
    """
    Create a new Session and return its ID as JSON.
    Returns:
        JsonResponse with session_id.
    attributes of response payload:
        - session_id: The ID of the newly created session.
    args:
        request: HTTP request object.
    """
    session = Session.objects.create()
    logger.debug(f"session id created: {session.id}")
    return JsonResponse({"session_id": session.id}, status=201)


def start_prerendering(request):
    year = int(request.GET.get("year"))
    session_id = request.GET.get("session_id")
    logger.debug(
        "start_turn_pipeline.send() called with session id "
        + str(session_id)
        + " and year "
        + year
    )
    response = start_turn_pipeline.send(session_id, year)
    logger.debug("start_turn_pipeline.send() called: " + response)
    return JsonResponse({"status": "generation_started"})

def display_question_and_options(request, session_id, room_code, turn_id, year):
    """
    Display the question and options for the current turn.
    Args:
        request: HTTP request object.
        session_id (int): ID of the game session.
        room_code (str): Code of the multiplayer room.
        turn_id (int): ID of the current turn. If -1, fetch the latest turn.
    Returns:
        JsonResponse with question, options, and turn details.

    attributes of response payload:
        - room_code: The code of the multiplayer room.
        - turn_id: The ID of the current turn.
        - year: The year associated with the current turn.
        - question: The question text for the current turn.
        - options: A list of options, each with:
    """
    logger.info(f"display_question_and_options called for session_id={session_id}")
    session_id = int(session_id)
    existing_session = get_object_or_404(Session, id=session_id)
    logger.info(f"Found session: {existing_session}")
    logger.info(f"turn_id received: {turn_id}")

    latest_turn = get_object_or_404(Turn, year=int(year),  session_id=session_id)
    logger.info(f'latest turn is; {latest_turn}')
        
    
    if latest_turn.year != int(year): 
        logger.info("got here")
        return JsonResponse({"error": "new. year not ready yet"}, status=404)

    turn_id = latest_turn.id

    if (room_code, int(turn_id)) not in VotingSessions.keys():
        VotingSessions[(room_code, int(turn_id))] = VotingSession(
            room_code, int(turn_id)
        )

    if VotingSessions[(room_code, int(turn_id))].is_timer_on() == False:
        VotingSessions[(room_code, int(turn_id))].start_voting()
    logger.debug(f"Latest turn determined: {latest_turn}")

    rm.update_state(room_code, {"turn_id": turn_id, "year": latest_turn.year})
    logger.debug(f"Latest turn for session: {latest_turn}")

    # fetch options
    options = Option.objects.filter(turn_id=latest_turn.id).order_by("label")
    options_payload = [
        {"option_id": o.id, "label": o.label, "option_text": o.option_text or ""}
        for o in options
    ]

    response_payload = {
        'message': 'ok',
        'room_code': room_code,
        'room_exists': rm.room_exists(room_code),
        'turn_id': turn_id,
        'year': year,
        'question': latest_turn.question or '',
        'options': options_payload,
    }

    return JsonResponse(response_payload)


def display_scenario_and_image(
    request, session_id, turn_id, year, option_id, room_code
):
    """
    Display the world view after user makes a choice.
    Returns current votes and scenario if all players have voted.
    Args:
        request: HTTP request object containing playerName as GET parameter.
        session_id (int): ID of the game session.
        turn_id (int): ID of the current turn.
        year (int): Current year in the game.
        option_id (int): ID of the option chosen by the player.
        room_code (str): Code of the multiplayer room.
    Returns:
        JsonResponse with voting status and scenario details.
    """
    player_name = request.GET.get("playerName")
    logger.info(f"playername is {player_name}")
    if not rm.room_exists(room_code):
        return JsonResponse({"success": False, "room_exists": False})

    logger.info(f"Voting session state before processing response: {VotingSessions}")
    # Process player response and determine the winning option if all voted
    current = rm.get_state(room_code).get("turn_id", -1)
    logger.info(f"turn_id received: {turn_id}")
    
    # Get the current turn to ensure we have the correct year
    try:
        current_turn = Turn.objects.get(id=current)
        current_year = current_turn.year
    except Turn.DoesNotExist:
        logger.error(f"Current turn {current} does not exist")
        return JsonResponse({"error": "Current turn not found"}, status=404)
    
    final_option = VotingSessions[(room_code, int(current))].process_player_response(room_code, player_name, option_id)

    logger.info(f"[Vote Submitted] {player_name} voted for {option_id} in room {room_code}")
    logger.info(f"[Current Votes] {VotingSessions[(room_code, int(current))].get_p_votes()}")
    if final_option is None: 
        final_option = VotingSessions[(room_code, int(current))].get_final_option()
        logger.info(f"Voting result is {final_option}")


    # Prepare vote tracking info
    votes_info = {
        "num_responses": VotingSessions[(room_code, current)].num_responses,
        "players_voted": list(
            VotingSessions[(room_code, current)].voted_players
        ),  # player names who voted
        "total_players": VotingSessions[(room_code, current)].total_players,
        "final_option": final_option
    }
    if final_option == "TIE":
        logger.info("sending tie")
        return JsonResponse({
            'success': False,
            'room_exists': True,
            "tie": True,
            "votes_info": votes_info,
            "message": "Votes tied, switching to minigame."
        })

    # If not all players have voted, return votes info only
    if final_option is None:
        logger.info("Not all players have voted yet.")
        return JsonResponse({
            "success": False,
            "scenario": "",
            "room_exists": rm.room_exists(room_code),
            "tie": False,
            "votes_info": votes_info,
            "message": "Waiting for other players to vote."
        }, status=404)

    # All players have voted → generate world view
    try:
        world_view_data = display_world_view(request, session_id, current, current_year, final_option)

        if world_view_data.get("success"):
            next_year = current_year + 1
            next_turn = Turn.objects.filter(
                session_id=session_id, year=next_year
            ).first()
            if next_turn:
                world_view_data["next_turn_id"] = next_turn.id
            
            if not next_turn:
                # start generating next turn in background only if it doesn't exist yet
                try:
                    start_turn_pipeline.send(session_id, next_year)
                    logger.info(f"Started generating next turn (year {next_year}) in background")
                except Exception as e:
                    logger.warning(f"Failed to start next turn generation: {e}")
            else:
                logger.debug(f"Next turn (year {next_year}) already exists, skipping generation")

            # Include votes info always
            world_view_data["votes_info"] = votes_info

            return JsonResponse(world_view_data)
        else:
            return JsonResponse({"error": "No turn found for this session"}, status=404)

    except Exception as e:
        logger.error(f"Error displaying world view: {e}")
        return JsonResponse({
            'success': False,
            'status': 'error',
            'room_exists': rm.room_exists(room_code),
            'votes_info': votes_info,
            'error': f'Failed to display world view: {str(e)}'
        }, status=500)


@csrf_exempt
@require_POST
def submit_score_single_view(request):
    """
    Handle POST request to submit a score for the single-player memory mini-game.

    Expects JSON request body with:
      - player_name (str): The name of the player.
      - score (int): The player's score.

    Returns:
        JsonResponse: A JSON object with either a success message or error details.
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
        player_name = data.get("player_name")
        score = data.get("score")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    if player_name is None or score is None:
        return HttpResponseBadRequest("Missing 'player_name' or 'score'")

    result = submit_score_single(player_name, score)
    return JsonResponse(result)


@csrf_exempt
def get_scores_view(request):
    """
    Retrieve all submitted single-player scores.
    """
    scores = get_scores()
    return JsonResponse({"scores": scores})


@csrf_exempt
@require_POST
def submit_tiebreak_score_view(request):
    """
    POST /mini-game/submit_tiebreak_score
    Used by both players and host.

    Body:
      {
          "room_code": "ABC123",
          "turn_id": 5,
          "player_name": "Alice" or "HOST",
          "score": 92  # or -1 if host
      }

    Returns:
      {"status": "pending"}                     -> if unresolved
      {"status": "resolved", "winner": "..."}   -> once resolved
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
        room_code = data["room_code"]
        turn_id = int(data["turn_id"])
        player_name = data["player_name"]
        score = int(data["score"])
    except (KeyError, ValueError, json.JSONDecodeError):
        return HttpResponseBadRequest("Invalid or missing parameters")

    voting_sesh = VotingSessions.get((room_code, turn_id))
    if not voting_sesh:
        return JsonResponse({"error": "No active voting session found"}, status=404)

    if player_name.upper() == "HOST" or score == -1:
        winner_info = voting_sesh.get_tiebreak_winner()
        if winner_info:
            return JsonResponse({
                "status": "resolved",
                "winner": winner_info["winner"],
                "winning_option": winner_info["winning_option"]
            })
        return JsonResponse({"status": "pending"})

    result = voting_sesh.submit_tiebreak_score(player_name, score)
    if result:
        return JsonResponse({
            "status": "resolved",
            "winner": result["winner"],
            "winning_option": result["winning_option"]
        })
    else:
        return JsonResponse({"status": "pending"})
