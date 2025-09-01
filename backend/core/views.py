# Views for the core application
# This module contains view functions that handle HTTP requests for the core app

from django.http import HttpResponse

def index(request):
    """
    Simple index view that returns a status message.
    
    Args:{'display_text': str, 'image_text': str, 'world_id': int}
        request: The HTTP request object
        
    Returns:
        HttpResponse: A simple text response indicating the backend is running with 200 OK status
    """
    return HttpResponse("MemorySim backend is running.", status=200)
    return HttpResponse("MemorySim backend is running.")

# ---------------------------- now in api.views -----------------------------
# image
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET

from backend.images.generate import (
    clean_llm_description,
    build_prompt_payload,
    enqueue_render,
    map_world_to_prompt,
    get_prompt_id_for_world,
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

    # map world -> prompt_id for later lookup
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
        return JsonResponse({'status': 'ready', 'image_url': f'/render/{world_id}'}, status=200)
    except TimeoutError:
        return JsonResponse({'status': 'pending'}, status=202)
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)