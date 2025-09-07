from django.conf import settings
from django.shortcuts import get_object_or_404
from backend.shared.models import Session, Turn, Option, ImageRender
from .render_pipeline import prev_revealed_rel

def reveal_by_option(session_id: int, turn_id: int, option_id: int) -> dict:
    """
    Input: session_id, turn_id, option_id chosen by users
    Output: JSON with the image URL to show
    Side effects: sets Turn.user_choice and Turn.revealed_image_file_rel
    """
    turn = get_object_or_404(Turn, id=turn_id, session_id=session_id)
    opt = get_object_or_404(Option, id=option_id, turn=turn)

    image_ready = (ImageRender.objects
             .filter(option_id=opt.id, status='ready')
             .order_by('-id')
             .first())

    shown_rel = image_ready.file_rel if (image_ready and image_ready.file_rel) else prev_revealed_rel(turn)

    turn.user_choice = opt
    turn.revealed_image_file_rel = shown_rel
    turn.save(update_fields=['user_choice', 'revealed_image_file_rel'])

    return {
        'turn_id': turn_id,
        'option_id': opt.id,
        'image_url': f"{settings.MEDIA_URL}{shown_rel}"
        }
