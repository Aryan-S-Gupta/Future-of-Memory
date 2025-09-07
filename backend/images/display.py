from django.conf import settings
from django.shortcuts import get_object_or_404
from backend.shared.models import Turn, Option
from .render_pipeline import prev_turn_displayed_image_rel
from .status import get_image_status

def display_by_option(session_id: int, turn_id: int, option_id: int, max_wait_s: float = 25.0, poll_every_s: float = 0.5) -> dict:

    turn = get_object_or_404(Turn, id=turn_id, session_id=session_id)
    opt = get_object_or_404(Option, id=option_id, turn=turn)

    status, rel = get_image_status(option_id, max_wait_s, poll_every_s)

    # if ready, display
    if status == "ready" and rel:
        turn.user_choice = opt
        turn.displayed_image_rel = rel
        turn.save(update_fields=['user_choice', 'displayed_image_rel'])
        return {
            "turn_id": turn_id,
            "option_id": opt.id,
            "status": "ready",
            "image_url": f"{settings.MEDIA_URL}{rel}",
        }

    # if failed or timeout, show fallback
    fallback_rel = prev_turn_displayed_image_rel(turn)
    turn.user_choice = opt
    turn.displayed_image_rel = fallback_rel
    turn.save(update_fields=['user_choice', 'displayed_image_rel'])
    return {
        "turn_id": turn_id,
        "option_id": opt.id,
        "status": "failed_fallback",
        "image_url": f"{settings.MEDIA_URL}{fallback_rel}",
    }