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


def get_story_result(request):
    """
    Retrieves the user's selected choice for a given question. This is a post method 
    which means this is directly retrived from the user input
    """
    if request.method == "POST":
        year = request.get("year")
        choice = request.get("choice")

    if not year or not choice:
        return HttpResponseBadRequest("Missing 'year' or 'choice' parameter.")

    return JsonResponse({
        "year": year,
        "choice": choice,
    })


# image
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET

from backend.images.generate import (
    clean_llm_description,
    build_prompt_payload,
    enqueue_render,
    get_image_location,
    fetch_png_bytes,
)
from backend.images.cache import (
    cache_world_image_text,
    get_cached_image_text,
    get_prompt_id_for_world,
    map_world_to_prompt,
)

# sudo
def call_llm_update_world(choice: str) -> dict:
    return {'display_text': str, 'image_text': str, 'world_id': str}

# sudo function, modify world based on user choice, link llm with image generation, the get_story_result_by_choice() I guess?
@require_POST
def apply_choice(request):
    """
    Input JSON:  {'choice': '...'}
    Output JSON: {'display_text': '...', 'world_id': '...', 'image_url': '/render/<world_id>'}
    Flow:
      choice -> LLM -> cache image_text -> enqueue -> map world->prompt -> return
    """
    data = json.loads(request.body.decode('utf-8'))
    choice = data['choice']

    # expected output: {'display_text': str, 'image_text': str, 'world_id': str}
    llm_result = call_llm_update_world(choice) # llm function
    display_text = llm_result['display_text']
    image_text = llm_result['image_text']
    world_id = llm_result['world_id']

    # cache (for regeneration if failure, not implemented yet)
    cache_world_image_text(world_id, image_text)

    # enqueue ComfyUI render, starts image generation
    cleaned = clean_llm_description(image_text)
    payload = build_prompt_payload(cleaned)
    prompt_id = enqueue_render(payload)

    # cache world -> prompt_id for later lookup
    map_world_to_prompt(world_id, prompt_id)

    # return to frontend
    return JsonResponse({
        'display_text': display_text,
        'world_id': world_id,
        'image_url': f'/render/{world_id}', # image src is set as the url, triggers a GET
    }, status=200)


# GET /render/world_id
@require_GET
def render_image(request, world_id: str):

    try:
        prompt_id = get_prompt_id_for_world(world_id) # world_id -> prompt_id
    except KeyError:
        return JsonResponse({'error': 'unknown world id'}, status=404)

    try:
        location = get_image_location(prompt_id)
        png_bytes = fetch_png_bytes(location)
        return HttpResponse(png_bytes, content_type='image/png')
    
    except TimeoutError:
        return JsonResponse({'status': 'pending'}, status=202)
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)


# render/status/world_id, frontend continuously pools from the url, if status is ready, set the image src to image_url
# avoid the case when timeout, the image is broken
@require_GET
def render_status(request, world_id: str):
    """
    no broken image when pending
    Returns:
      200 {'status':'ready','image_url':'/render/<world_id>'}
      202 {'status':'pending'}
      404 {'error':'unknown world id'}
      500 {'status':'error', 'error': '...'}
    """
    try:
        prompt_id = get_prompt_id_for_world(world_id)
    except KeyError:
        return JsonResponse({'error': 'unknown world id'}, status=404)

    try:
        location = get_image_location(prompt_id, timeout_seconds=1, interval_seconds=0.2)
        return JsonResponse({'status': 'ready', 'image_url': f'/render/{world_id}'}, status=200) # if view gives the url, then no need there
    except TimeoutError:
        return JsonResponse({'status': 'pending'}, status=202)
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)
