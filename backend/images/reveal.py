from django.conf import settings
from django.shortcuts import get_object_or_404
from backend.shared.models import Session, Turn, Option, ImageRender
from .render_pipeline import prev_turn_displayed_image_rel

def reveal_by_option(session_id: int, turn_id: int, option_id: int) -> dict:
    """
    use option_id to get image, if ready, show, if no image ready yet, show a fallback
    Input: session_id, turn_id, option_id chosen by users
    Output: JSON with the image URL to show
    """
    turn = get_object_or_404(Turn, id=turn_id, session_id=session_id)
    opt = get_object_or_404(Option, id=option_id, turn=turn)

    image_ready = (ImageRender.objects
             .filter(option_id=opt.id, status='ready')
             .order_by('-id')
             .first())

    shown_rel = image_ready.image_rel if (image_ready and image_ready.image_rel) else prev_turn_displayed_image_rel(turn)

    turn.user_choice = opt
    turn.displayed_image_rel = shown_rel
    turn.save(update_fields=['user_choice', 'displayed_image_rel'])

    return {
        'turn_id': turn_id,
        'option_id': opt.id,
        'image_url': f"{settings.MEDIA_URL}{shown_rel}"
        }
