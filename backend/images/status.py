import time
from typing import Literal, Tuple, Optional
from backend.shared.models import ImageRender

def get_image_status(option_id: int, max_wait_s: float = 25.0, 
                     poll_every_s: float = 0.5,) -> Tuple[Literal["ready","failed","timeout"], Optional[str]]:
    """
    if ready -> ready + rel path
    if failed -> failed + None
    if pending -> keep fetching till timeout
        if timeout -> timeout + None
    """
    deadline = time.time() + max_wait_s
    while time.time() < deadline:
        latest = (ImageRender.objects
                  .filter(option_id=option_id)
                  .order_by('-id')
                  .first())

        if latest:
            if latest.status == 'ready' and latest.image_rel:
                return ("ready", latest.image_rel)

            if latest.status == 'failed':
                return ("failed", None)

        time.sleep(poll_every_s)
        
    return ("timeout", None)

