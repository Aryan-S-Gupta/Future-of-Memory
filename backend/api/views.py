"""
API views for handling storyline-related requests.
Provides endpoints to fetch story background, questions, and results based on user choices.
"""
import json
import os
from django.http import JsonResponse, HttpResponseBadRequest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'static_stories.json')

with open(DATA_FILE, 'r', encoding='utf-8') as f:
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
    year = request.GET.get('year')
    if not year:
        return HttpResponseBadRequest("Missing 'year' parameter.")

    entry = get_entry_by_year(year)
    if not entry:
        return JsonResponse({"error": "Year not found."}, status=404)

    return JsonResponse({
        "year": entry["year"],
        "scenario": entry["background"]
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

    entry = get_entry_by_year(year)
    if not entry:
        return JsonResponse({"error": "Year not found."}, status=404)

    return JsonResponse({
        "year": entry["year"],
        "question": entry["question"],
        "options": entry["options"]
    })


def get_story_result_by_choice(request):

    """
    Retrieve the result of a user's choice for a given year from the story data.
    Expects 'year' and 'choice' parameters in the GET request.
    Returns a JSON response with the result, or an error message if not found.
    """
    year = request.GET.get('year')
    choice = request.GET.get('choice').get(choice.lower())
    if not year or not choice:
        return HttpResponseBadRequest("Missing 'year' or 'choice' parameter.")

    entry = get_entry_by_year(year)
    if not entry:
        return JsonResponse({"error": "Year not found."}, status=404)
    
    if not result:
        return JsonResponse({"error": f"No result found for choice '{choice}'"}, status=404)

    next_scenario = get_story_scenario(year + 1)
    next_question = get_story_question(year + 1)


def get_story_result(request):
    """
    Retrieves the user's selected choice for a given question. This is a post method 
    which means this is directly retrived from the user input
    """
    if request.method == "POST":
        data = json.loads(request.body)
        year = data.get("year")
        choice = data.get("choice")

        return JsonResponse({
            "year": year,
            "choice": choice,
        })

    return JsonResponse({"error": "Invalid request"}, status=400)
