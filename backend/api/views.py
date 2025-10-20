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


# new views
from shared.models import Session, Option, Turn, ImageRender

# home page
# need to call this somewhere - as soon as the game is created
def create_session(request):
    """
    Create a new Session and return its ID as JSON.
    Returns:
        JsonResponse: {'session_id': int} 
        Status code: 201 Created
    attributes:
        - session_id (int): The ID of the newly created session. 
    Args:
        request (HttpRequest): The incoming HTTP request.

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
    logger.info("start_turn_pipeline.send() called")
    start_turn_pipeline.send(session_id, year)
    logger.info("start_turn_pipeline.send() called: ")
    return JsonResponse({'status': 'generation_started'})

# question and options display page

# send the existing work
def display_question_and_options(request, session_id, turn_id, year):

    """
    Display the question and options for the latest turn of a given session.
    Args:
        request (HttpRequest): The incoming HTTP request.
        session_id (int): The ID of the session to retrieve the turn for.
    Returns:
        JsonResponse: {
            'message': 'ok',
            'data': {
                'turn_id': int,
                'year': int,
                'question': str,
                'options': [
                    {'option_id': int, 'label': str, 'option_text': str},
                    ...
                ]
            }
        }
        Status code: 200 OK
    attributes:
        - turn_id (int): The ID of the latest turn.
        - year (int): The year of the latest turn.
        - question (str): The question text of the latest turn. 
        - options (list): List of options with their IDs, labels, and texts.
    Raises:
        - 404 Not Found: If the session or turn does not exist.     
    """
    # get session
    logger.debug(f"display_question_and_options called for session_id={session_id}")
    existing_session = get_object_or_404(Session, id=session_id)
    logger.debug(f"Found session: {existing_session}")
    logger.debug(f"turn_id received: {turn_id}")

    logger.info(f'fetching for {year}')
    # find the latest turn for this session
    if int(turn_id) == -1:
        logger.info("year:" + year)
        latest_turn = (
            Turn.objects
            .filter(session_id=existing_session.id)
            .order_by('-year', '-id')
            .first()
        )
        # if the turn is not rrady yet 
        if not latest_turn:
            logger.warning("No turns found for this session")
            return JsonResponse({'error': 'No turn found for this session'}, status=404)
    
    else:
        # get specific turn by ID
        turn_id = int(turn_id) + 1
        latest_turn = get_object_or_404(Turn, year=int(year),  id=int(turn_id))
        
    
    if latest_turn.year != int(year): 
        logger.info("got here")
        return JsonResponse({'error': 'new. year not ready yet'}, status=404)
    
    turn_id = latest_turn.id 
    
    logger.debug(f"Latest turn determined: {latest_turn}")
    logger.debug(f"Latest turn for session: {latest_turn}")

    # fetch options
    options = Option.objects.filter(turn_id=latest_turn.id).order_by('label')
    options_payload = [
        {'option_id': o.id, 'label': o.label, 'option_text': o.option_text or ''}
        for o in options
    ]

    response_payload = {
        'message': 'ok',
        'turn_id': turn_id,
        'year': year,
        'question': latest_turn.question or '',
        'options': options_payload,
    }

    return JsonResponse(response_payload)
 
# scenario and image display page
from shared.services import display_world_view


def display_scenario_and_image(request, session_id, turn_id, year, option_id):
    """
    Display the scenario and image for a given session, turn, year, and option.
    If the world view is ready, it also triggers the generation of the next turn in the background.
    Args:
        request (HttpRequest): The incoming HTTP request.
        session_id (int): The ID of the session.
        turn_id (int): The ID of the turn.
        year (int): The year of the turn.
        option_id (int): The ID of the selected option.
    Returns:
        JsonResponse: {
            'success': bool,
            'status': str,  # "ready", "processing", "error"
            'scenario': str,  # scenario text if ready
            'image_url': str,  # image URL if ready
            'error': str,  # error message if any
        }
        Status code: 200 OK if successful, 500 Internal Server Error if an exception occurs
    attributes:
        - success (bool): True if the operation was successful, False otherwise.
        - status (str): The status of the world view ("ready", "processing", "  
"error").
        - scenario (str): The scenario text if the world view is ready.
        - image_url (str): The image URL if the world view is ready.
        - error (str): An error message if any error occurred.
    Raises:
        - 500 Internal Server Error: If an exception occurs during processing.

    """
    try:
        world_view_data = display_world_view(session_id, turn_id, year, option_id)
        
        # 检查是否是等待状态（数据正在生成中）
        if world_view_data.get("status") == "waiting":
            # 返回等待状态，不是错误
            return JsonResponse({
                "success": False,
                "status": "waiting", 
                "message": "Scenario and image are being generated, please wait...",
                "scenario_ready": world_view_data.get("scenario_ready", False),
                "image_ready": world_view_data.get("image_ready", False)
            }, status=202)  # 202 Accepted - 请求已接收但还在处理中
        
        if world_view_data.get("success"):
            next_year = int(year) + 1
            next_turn = Turn.objects.filter(session_id=session_id, year=next_year).first()
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

            return JsonResponse(world_view_data)
        else:
            # 真正的错误情况
            error_msg = world_view_data.get("error", "No turn found for this session")
            return JsonResponse({'error': error_msg}, status=404)
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

def _to_media_url(rel):
    if not rel:
        return None
    rel = rel.lstrip("/")
    if not rel.startswith("media/"):
        rel = f"media/{rel}"
    return f"/{rel}"

def get_gallery_for_session(request, session_id: int):
    session = get_object_or_404(Session, id=session_id)
    include_pending = request.GET.get("include_pending") in ("1", "true", "True", "yes", "on")

    items = []
    turns = (Turn.objects
             .filter(session=session)
             .order_by('year', 'id')
             .select_related('user_choice'))

    for t in turns:
        if t.user_choice_id:
            # COMPLETED — use displayed image unless it's a fallback; then prefer latest ready render
            chosen = t.user_choice
            img_rel = (t.displayed_image_rel or "").lstrip("/")
            is_fallback = (not img_rel) or img_rel.startswith(("static/fallback_", "media/static/fallback_"))
            if is_fallback:
                r = (ImageRender.objects
                     .filter(option=chosen, status='ready')
                     .order_by('-created_at', '-id')
                     .first())
                if r:
                    img_rel = r.image_rel

            items.append({
                "year": t.year,
                "turn_id": t.id,
                "option_id": chosen.id,
                "option_label": getattr(chosen, "label", None),
                "option_text": chosen.option_text or "",
                "scenario": chosen.scenario or "",
                "image_url": _to_media_url(img_rel),
                "status": "completed",
            })
        elif include_pending:
            # PENDING — pick latest ready render across both options (if any)
            opt_ids = list(Option.objects.filter(turn=t).values_list('id', flat=True))
            r = (ImageRender.objects
                 .filter(option_id__in=opt_ids, status='ready')
                 .order_by('-created_at', '-id')
                 .first())
            image_url = _to_media_url(r.image_rel if r else None)
            items.append({
                "year": t.year,
                "turn_id": t.id,
                "option_id": None,
                "option_label": None,
                "option_text": "",
                "scenario": "",
                "image_url": image_url,
                "status": "pending",
            })

    return JsonResponse({"session_id": session_id, "count": len(items), "items": items}, status=200)