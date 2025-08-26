"""
API views for handling storyline-related requests.
Provides endpoints to fetch story background, questions, and results based on user choices.
"""
import json
import os
import logging
from django.http import JsonResponse, HttpResponseBadRequest

from rag.retrieve import retrieve_chunks

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'static_stories.json')

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    story_data = json.load(f)

def get_story_background(request):

    """
    Retrieve the background information for a given year from the story data.
    Expects a 'year' parameter in the GET request.
    Returns a JSON response with the background or an error message.
    """
    year = request.GET.get('year')
    if not year:
        return HttpResponseBadRequest("Missing 'year' parameter.")

    entry = next((item for item in story_data if str(item["year"]) == year), None)
    if not entry:
        return JsonResponse({"error": "Year not found."}, status=404)

    return JsonResponse({
        "year": entry["year"],
        "background": entry["background"]
    })


def get_story_question(request):

    """
    Retrieve the question for a given year from the story data.
    Expects a 'year' parameter in the GET request.
    Returns a JSON response with the question or an error message.
    """
    year = request.GET.get('year')
    if not year:
        return HttpResponseBadRequest("Missing 'year' parameter.")

    entry = next((item for item in story_data if str(item["year"]) == year), None)
    if not entry:
        return JsonResponse({"error": "Year not found."}, status=404)

    return JsonResponse({
        "year": entry["year"],
        "question": entry["question"]
    })


def get_story_result_by_choice(request):

    """
    Retrieve the result of a user's choice for a given year from the story data.
    Expects 'year' and 'choice' parameters in the GET request.
    Returns a JSON response with the result, or an error message if not found.
    """
    year = request.GET.get('year')
    choice = request.GET.get('choice')
    if not year or not choice:
        return HttpResponseBadRequest("Missing 'year' or 'choice' parameter.")

    entry = next((item for item in story_data if str(item["year"]) == year), None)
    if not entry:
        return JsonResponse({"error": "Year not found."}, status=404)
    
    result = entry.get("options", {}).get(choice.lower())
    if not result:
        return JsonResponse({"error": f"No result found for choice '{choice}'"}, status=404)

    return JsonResponse({
        "year": entry["year"],
        "choice": choice,
        "result": result,
        "next_year": entry["year"] + 1
    })

def rag_retrieve(request):
    
    default_query = "fatigue"
    query: str
    if request.method != 'POST':
        logger.warning("Non-POST request received. Using default query instead")
        query = default_query
    else:
        query_text = request.POST.get('query_text')
        keywords = request.POST.get('keywords')
        query = query_text or keywords
        if not query:
            logger.warning("No 'query_text' or 'keywords' parameter provided. Using default query instead")
            query = default_query

    items = retrieve_chunks(query)
    return JsonResponse({'items': items})
