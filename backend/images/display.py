from django.conf import settings
from django.shortcuts import get_object_or_404
from shared.models import Turn, Option
from .status import get_image_status

INITIAL_WORLD_IMAGE_REL= "static/fallback_first_turn.png"

def prev_turn_displayed_image_rel(turn: Turn) -> str:
    """
    return previous turn's revealed image if present, else the first-turn fallback.
    """
    prev_turn = (Turn.objects
            .filter(session_id=turn.session_id, id__lt=turn.id)
            .order_by('-id')
            .first())
    
    if (prev_turn and prev_turn.displayed_image_rel):
        return prev_turn.displayed_image_rel
    
    return INITIAL_WORLD_IMAGE_REL

# ideally if frontend gives enough time for generation, no wait needed
def display_by_option(request, session_id: int, turn_id: int, option_id: int, max_wait_s: float = 25.0, poll_every_s: float = 0.5) -> dict:

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
            "image_url": build_image_url(request, rel),
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
        "image_url": build_image_url(request, fallback_rel),
    }


def build_image_url(request, rel_path):
    base = f"{request.scheme}://{request.get_host()}"  # e.g. "http://192.168.0.151:8000"
    full_url = f"{base}{settings.MEDIA_URL}{rel_path}" # e.g. "http://192.168.0.151:8000/media/session_x_turn_y_option_A.png
    return full_url