# backend/images/render_pipeline.py
from django.shortcuts import get_object_or_404
from backend.shared.models import Session, Turn, Option, ImageRender
from .comfyui_client import (
    clean_llm_description, build_prompt_payload, enqueue_render, get_image_location, fetch_png_bytes,
)
from .save import build_image_relpath, save_png_to_media

INITAL_WORLD_IMAGE_REL= "static/fallback_first_turn.png"

def render_option_to_media(image_text: str, rel_path: str) -> str:
    """
    image_text -> clean -> /prompt -> /history -> /view?... -> save under rel_path
    """
    clean = clean_llm_description(image_text)
    payload = build_prompt_payload(clean)
    prompt_id = enqueue_render(payload)
    loc = get_image_location(prompt_id)
    png = fetch_png_bytes(loc)
    return save_png_to_media(rel_path, png)

def generate_four_images_blocking(session_id: int, turn_id: int) -> dict:
    """
    For each of the 4 options of this turn:
      - build rel_path
      - render and save into MEDIA_ROOT
      - create ImageRender
    """
    turn = get_object_or_404(Turn, id=turn_id)
    if turn.session_id != session_id:
        raise ValueError('Session/turn mismatch.')

    options = list(Option.objects.filter(turn=turn).order_by('label'))
    if len(options) != 4:
        raise ValueError('Expected 4 options for this turn.')

    fallback_rel = prev_revealed_rel(turn)
    results = {}

    for opt in options:
        rel_path = build_image_relpath(session_id, turn_id, opt.label)
        try:
            final_rel = render_option_to_media(opt.image_text, rel_path)
            ImageRender.objects.create(
                option=opt, status='ready', file_rel=final_rel, last_render_file_rel=''
            )
            results[opt.id] = {
                'status': 'ready',
                'filename': final_rel,
                'fallback': None,
                'shown': final_rel,
            }
        except Exception:
            ImageRender.objects.create(
                option=opt, status='failed', filename='', last_render_file_rel=fallback_rel
            )
            results[opt.id] = {
                'status': 'failed',
                'filename': None,
                'fallback': fallback_rel,
                'shown': fallback_rel,
            }

    return {'turnId': turn_id, 'files': results}

def prev_revealed_rel(turn: Turn) -> str:
    """
    return previous turn's revealed image if present, else the first-turn fallback.
    """
    prev_turn = (Turn.objects
            .filter(session_id=turn.session_id, id__lt=turn.id)
            .order_by('-id')
            .first())
    
    if (prev_turn and prev_turn.revealed_image_file_rel):
        return prev_turn.revealed_image_file_rel
    
    return INITAL_WORLD_IMAGE_REL

