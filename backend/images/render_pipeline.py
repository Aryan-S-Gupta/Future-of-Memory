import json
import logging

from django.db import transaction
from django.shortcuts import get_object_or_404
from shared.models import Session, Turn, Option, ImageRender
from .comfyui_client import (
    clean_llm_description,
    build_prompt_payload,
    enqueue_render,
    get_image_location,
    fetch_png_bytes,
)
from .save import build_image_relpath, save_png_to_media

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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


def generate_two_images_blocking(session_id: int, turn_id: int) -> dict:
    """
    For each of the 2 options of this turn:
      - build rel_path
      - render and save into MEDIA_ROOT
      - create ImageRender
    """
    turn = get_object_or_404(Turn, id=turn_id)
    print(f"Session: {session_id} vs {turn.session_id} vs {turn.id} vs {turn}")
    if int(turn.session_id) != int(session_id):
        print(f"Session/turn mismatch: {session_id} vs {turn.session_id}")
        return {}
        # raise ValueError('Session/turn mismatch.')

    options = list(Option.objects.filter(turn=turn).order_by("label"))
    if len(options) != 2:
        raise ValueError("Expected 2 options for this turn.")

    results = {}

    for opt in options:
        with transaction.atomic():
            # lock the option so only one thread claims it at a time
            opt_locked = Option.objects.select_for_update().get(pk=opt.pk)
            print("line 46")
            ir = (
                ImageRender.objects.filter(option=opt_locked)
                .order_by("-created_at")
                .first()
            )

            if ir and ir.status in ("pending", "ready", "failed"):
                # already generating or finished -> no rendering needed for this thread
                results[opt.id] = {
                    "status": ir.status,
                    "image_rel": ir.image_rel or None,
                }
                continue

            # no ir yet
            ir = ImageRender.objects.create(
                option=opt_locked, status="pending", image_rel=""
            )
            ir_pk = ir.pk

        try:
            print("line 64")
            rel_path = build_image_relpath(
                session_id, turn_id, opt.label
            )  # comfyui/output/xxx.png
            final_rel = render_option_to_media(opt.image_text, rel_path)
            print("line 68")
            ImageRender.objects.filter(pk=ir_pk).update(
                status="ready", image_rel=final_rel
            )
            results[opt.id] = {"status": "ready", "image_rel": final_rel}
            print("line 70")
        except Exception:
            logger.exception("Got exception during image demo:")
            ImageRender.objects.filter(pk=ir_pk).update(status="failed")
            results[opt.id] = {"status": "failed", "image_rel": None}
    print("line 71")
    print(f"image results: {results}")
    return {"turnId": turn_id, "image_rels": results}
