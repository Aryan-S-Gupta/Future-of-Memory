"""
API views for handling storyline-related requests.
Provides endpoints to fetch story background, questions, and results based on user choices.
"""

import json
import os
import logging
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from rag.retrieve import retrieve_chunks

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

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


"""
What is this function supposed to do??? 
currently it is sending the same question back so not using it 
"""


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




from shared.models import Session

# home page
@require_POST
def create_session(request):
    """
    Create a new Session and return its ID as JSON.
    """
    session = Session.objects.create()
    return JsonResponse({'session_id': session.id}, status=201)

# intro page
from shared.services import generate_complete_turn
def start_prerendering(request, session_id, year):
    return generate_complete_turn(session_id, year) # replace by start_turn_pipeline.send()


def display_question_and_options(request, session_id, turn_id):
    # llm funtion?
    return

# display page
from shared.services import display_world_view
@require_POST
def display_scenario_and_image(request, session_id, turn_id, year, option_id):
    """
    Display the world view after user makes a choice.
    """
    try:
        world_view_data = display_world_view(session_id, turn_id, year, option_id)

        if world_view_data.get('success'):
            next_year = int(year) + 1
            try:
                # start generating next turn in background
                generate_complete_turn(session_id, next_year) # start_turn_pipeline.send()
                logger.info(f"Started generating next turn (year {next_year}) in background")
            except Exception as e:
                logger.warning(f"Failed to start next turn generation: {e}")
        
        return JsonResponse(world_view_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Failed to display world view: {str(e)}'
        }, status=500)



# bg manager
from shared.services import start_turn_pipeline

def start_prerendering(request, session_id, year):
    start_turn_pipeline.send(session_id, year)
    return JsonResponse({'status': 'generation_started'})
