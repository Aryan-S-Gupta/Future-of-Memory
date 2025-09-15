from django.db import transaction
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
        with transaction.atomic():
            # lock the option so only one thread claims it at a time
            opt_locked = Option.objects.select_for_update().get(pk=opt.pk)

            ir = (ImageRender.objects
                  .filter(option=opt_locked)
                  .order_by('-created_at')
                  .first())

            if ir and ir.status in ('pending', 'ready', 'failed'):
                # already generating or finished -> no rendering needed for this thread
                results[opt.id] = {'status': ir.status, 'image_rel': ir.image_rel or None}
                continue

            # no ir yet
            ir = ImageRender.objects.create(option=opt_locked, status='pending', image_rel='')
            ir_pk = ir.pk

        try:
            rel_path = build_image_relpath(session_id, turn_id, opt.label)
            final_rel = render_option_to_media(opt.image_text, rel_path)

            ImageRender.objects.filter(pk=ir_pk).update(status='ready', image_rel=final_rel)
            results[opt.id] = {'status': 'ready', 'image_rel': final_rel}

        except Exception:
            ImageRender.objects.filter(pk=ir_pk).update(status='failed')
            results[opt.id] = {'status': 'failed', 'image_rel': None}

    return {'turnId': turn_id, 'image_rels': results}

