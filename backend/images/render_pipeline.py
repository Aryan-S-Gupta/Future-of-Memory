from django.shortcuts import get_object_or_404
from backend.shared.models import Session, Turn, Option, ImageRender
from .comfyui_client import (
    clean_llm_description, build_prompt_payload, enqueue_render, get_image_location, fetch_png_bytes,
)
from .save import build_image_relpath, save_png_to_media

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

# this needs to be run in the background
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

    results = {}

    for opt in options:
        rel_path = build_image_relpath(session_id, turn_id, opt.label)
        try:
            final_rel = render_option_to_media(opt.image_text, rel_path)
            # no need for last_turn_image_rel now? now tracked in turn displayed_image_rel
            ImageRender.objects.create(
                option=opt, status='ready', image_rel=final_rel
            )
            results[opt.id] = {
                'status': 'ready',
                'image_rel': final_rel
            }
        except Exception:
            ImageRender.objects.create(
                option=opt, status='failed', image_rel=''
            )
            results[opt.id] = {
                'status': 'failed',
                'image_rel': None
            }

    return {'turnId': turn_id, 'image_rels': results}

