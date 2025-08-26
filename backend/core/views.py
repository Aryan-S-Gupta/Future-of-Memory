# Views for the core application
# This module contains view functions that handle HTTP requests for the core app

from django.http import HttpResponse

def index(request):
    """
    Simple index view that returns a status message.
    
    Args:
        request: The HTTP request object
        
    Returns:
        HttpResponse: A simple text response indicating the backend is running with 200 OK status
    """
    return HttpResponse("MemorySim backend is running.", status=200)
    return HttpResponse("MemorySim backend is running.")


# image generation
import os, shutil, json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from images.generate import run as generate_image_run

def _copy_to_media(src_path: str) -> str:
    dst_dir = settings.MEDIA_ROOT / "generated"
    dst_dir.mkdir(parents=True, exist_ok=True)
    base = os.path.basename(src_path)
    name, ext = os.path.splitext(base)
    dst = dst_dir / base
    i = 1
    while dst.exists():
        dst = dst_dir / f"{name}_{i}{ext}"
        i += 1
    shutil.copy2(src_path, dst)
    rel = dst.relative_to(settings.MEDIA_ROOT).as_posix()
    return settings.MEDIA_URL + rel  # e.g. /media/generated/foo.png

@csrf_exempt
def generate_image_view(request):
    desc = "A small beautiful cat with a small blue hat. --- call a function from llm"
    src_path = generate_image_run(desc)
    public_url = request.build_absolute_uri(_copy_to_media(src_path))  # copy local file into MEDIA_ROOT
    return JsonResponse({"description": desc, "imageUrl": public_url})
