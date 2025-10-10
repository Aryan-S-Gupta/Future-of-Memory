"""
API views for handling storyline-related requests.
Provides endpoints to fetch story background, questions, and results based on user choices.
"""

import json
import os
import logging
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from rag.retrieve import retrieve_chunks
from rag.fun_facts.retrieve_fun_facts import retrieve_fun_facts

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from rag.retrieve import retrieve_chunks


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "static_stories.json")

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
    """
    session = Session.objects.create()
    logger.debug(f"session id created: {session.id}")
    return JsonResponse({"session_id": session.id}, status=201)


# intro page

# need a call in background page - it starts generating question and options and images and scenario
from shared.tasks import start_turn_pipeline


def start_prerendering(request):
    year = request.GET.get("year")
    session_id = request.GET.get("session_id")
    logger.debug("start_turn_pipeline.send() called")
    start_turn_pipeline.send(session_id, year)
    logger.debug("start_turn_pipeline.send() called")
    return JsonResponse({"status": "generation_started"})


# question and options display page


# send the existing work
def display_question_and_options(request, session_id):
    # get session
    logger.debug(f"display_question_and_options called for session_id={session_id}")
    existing_session = get_object_or_404(Session, id=session_id)
    logger.debug(f"Found session: {existing_session}")

    # find the latest turn for this session
    latest_turn = (
        Turn.objects.filter(session_id=existing_session.id)
        .order_by("-year", "-id")
        .first()
    )
    if latest_turn is None:
        logger.warning("No turn found for this session")
        return JsonResponse({"error": "No turn found for this session"}, status=404)
    logger.debug(f"Latest turn for session: {latest_turn}")
    # use the latest turn's id to fetch its question and related options
    question_text = latest_turn.question or ""  # ensure a string
    options = Option.objects.filter(turn_id=latest_turn.id).order_by("label")
    logger.debug(f"Options for turn {latest_turn.id}: {list(options)}")

    # serialize the options as exactly: option_id, label, option_text
    options_payload = [
        {
            "option_id": option.id,
            "label": option.label,
            "option_text": option.option_text or "",
        }
        for option in options
    ]

    # build the final JSON payload that the frontend can render directly
    response_payload = {
        "turn_id": latest_turn.id,
        "year": latest_turn.year,
        "question": question_text,
        "options": options_payload,
    }
    logger.debug(f"Payload to return: {response_payload}")
    return JsonResponse({"message": "ok", "data": response_payload}, status=200)


# scenario and image display page
from shared.services import display_world_view


def display_scenario_and_image(request, session_id, turn_id, year, option_id):
    """
    Display the world view after user makes a choice.
    """
    try:
        world_view_data = display_world_view(session_id, turn_id, year, option_id)

        if world_view_data.get("success"):
            next_year = int(year) + 1
            try:
                # start generating next turn in background
                start_turn_pipeline.send(session_id, next_year)
                logger.info(
                    f"Started generating next turn (year {next_year}) in background"
                )
            except Exception as e:
                logger.warning(f"Failed to start next turn generation: {e}")
        return JsonResponse(world_view_data)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Failed to display world view: {str(e)}'
        }, status=500)

@csrf_exempt
@require_POST
def retrieve_fun_facts_api(request) -> JsonResponse:
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
    number of fun facts retrieved on eac call.
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