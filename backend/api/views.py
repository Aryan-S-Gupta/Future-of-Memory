"""
API views for handling storyline-related requests.
Provides endpoints to fetch story background, questions, and results based on user choices.
"""

import json
import os
import logging
import multiplayer.room_manager as rm
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rag.retrieve import retrieve_chunks
from rag.fun_facts.retrieve_fun_facts import retrieve_fun_facts

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "static_stories.json")
VOTING_SESSIONS = {}


with open(DATA_FILE, "r", encoding="utf-8") as f:
    story_data = json.load(f)


# --- helper method ---
def get_entry_by_year(year):
    return next((item for item in story_data if str(item["year"]) == str(year)), None)


def get_story_scenario(request):
    """
    Retrieve the background information for a given year from the story data.
    Expects a 'year' parameter in the GET request.
    Returns a JSON response with the background or an error message.
    """
    year = request.GET.get("year")
    if not year:
        return HttpResponseBadRequest("Missing 'year' parameter.")

    entry = get_entry_by_year(year)
    if not entry:
        return JsonResponse({"error": "Year not found."}, status=404)

    return JsonResponse({"year": entry["year"], "scenario": entry["background"]})


def get_story_question(request):
    """
    Retrieve the question for a given year from the story data.
    Expects a 'year' parameter in the GET request.
    Returns a JSON response with the question or an error message.
    """
    year = request.GET.get("year")
    if not year:
        return HttpResponseBadRequest("Missing 'year' parameter.")

    entry = get_entry_by_year(year)
    if not entry:
        return JsonResponse({"error": "Year not found."}, status=404)

    return JsonResponse(
        {
            "year": entry["year"],
            "question": entry["question"],
            "options": entry["options"],
        }
    )

def get_story_result_by_choice(request):
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

    return JsonResponse(
        {
            "year": entry["year"],
            "choice": choice,
            "result": result,
            "next_year": entry["year"] + 1,
        }
    )

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

@csrf_exempt
@require_GET
def get_voting_status(request, room_code):
    """
       Returns current voting progress: who has voted, who is pending.
    """
    session = voting_sessions.get(room_code)
    if not session:
        return JsonResponse({"success": False, "error": "No active voting session"}, status=404)
    votes = session.get_current_votes()

    # Check if voting has finished
    all_voted = all(v != "Pending" for v in votes.values())
    still_active = session.vote_timer is not None

    return JsonResponse({
        "success": True,
        "votes": votes,  # { "Alice": "A", "Bob": "Pending" ... }
        "all_voted": all_voted,
        "still_active": still_active
    })




# new views
from shared.models import Session, Option, Turn

# home page

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
    year = request.GET.get("year")
    session_id = request.GET.get("session_id")
    logger.debug("start_turn_pipeline.send() called")
    start_turn_pipeline.send(session_id, year)
    logger.debug("start_turn_pipeline.send() called: ")
    return JsonResponse({'status': 'generation_started'})

# question and options display page

# send the existing work
def display_question_and_options(request, session_id):
    # get session
    logger.debug(f"display_question_and_options called for session_id={session_id}")
    existing_session = get_object_or_404(Session, id=session_id)
    logger.debug(f"Found session: {existing_session}")

    # find the latest turn for this session
    latest_turn = (
        Turn.objects
        .filter(session_id=existing_session.id)
        .order_by('-year', '-id')
        .first()
    )
    if latest_turn is None:
        logger.warning("No turn found for this session")
        return JsonResponse({'error': 'No turn found for this session'}, status=404)
    logger.debug(f"Latest turn for session: {latest_turn}")
    # use the latest turn's id to fetch its question and related options
    question_text = latest_turn.question or ''  # ensure a string
    options = Option.objects.filter(turn_id=latest_turn.id).order_by('label')
    logger.debug(f"Options for turn {latest_turn.id}: {list(options)}")

    # serialize the options as exactly: option_id, label, option_text
    options_payload = [
        {
            'option_id': option.id,
            'label': option.label,
            'option_text': option.option_text or ''
        }
        for option in options
    ]

    # build the final JSON payload that the frontend can render directly
    response_payload = {
        'turn_id': latest_turn.id,
        'year': latest_turn.year,
        'question': question_text,
        'options': options_payload,
    }
    logger.debug(f"Payload to return: {response_payload}")
    return JsonResponse({'message': 'ok', 'data': response_payload}, status=200)

# scenario and image display page
from shared.services import display_world_view


def display_scenario_and_image(request, session_id, turn_id, year, option_id):
    """
    Display the world view after user makes a choice.
    """
    try:
        world_view_data = display_world_view(session_id, turn_id, year, option_id)

        if world_view_data.get("success") and world_view_data.get("status") == "ready":
            next_year = int(year) + 1
            try:
                start_turn_pipeline.send(session_id, next_year)
                logger.info(f"Started generating next turn (year {next_year}) in background")
            except Exception as e:
                logger.warning(f"Failed to start next turn generation: {e}")

        # return the raw payload from services.py (status-aware)
        return JsonResponse(world_view_data)

    except Exception as e:
        logger.exception("Error in display_scenario_and_image")
        return JsonResponse({
            "success": False,
            "status": "error",
            "error": f"Failed to display world view: {str(e)}"
        }, status=500)
    


@csrf_exempt
def retrieve_fun_facts_api(request) -> JsonResponse:
    logger.debug("retrieve_fun_facts_api called")
    """Retrieve fun facts based on the most recent retrieved chunks.
    
    Input format: no data given
    
    Return format: {
        "data": [
            {
                "fact": "the fact text, probably single sentence",
                "link": "link to the original document",
                "link_text": "text to display for the link e.g. 'Cambridge Core article'"
            },
            ...
            (one item for each fact)
        ]
    }
    
    The constant NUM_FUN_FACTS in backend/rag/fun_facts/retrieve_fun_facts.py will determine the 
    number of fun facts retrieved on each call.
    """
    return JsonResponse({"data": retrieve_fun_facts()})
