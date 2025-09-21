from pathlib import Path, PurePosixPath
from django.conf import settings

def build_image_relpath(session_id: int, turn_id: int, label: str) -> str:
    """
    Input: ids + label
    Output: 'comfyui/output/session{sid}_turn{tid}_option_{label}_world.png'
    """
    filename = f"session{session_id}_turn{turn_id}_option_{label}_world.png"
    # filename = f"option_{label}_world.png"
    rel = PurePosixPath("comfyui") / "output" / filename # image will be stored under comfyui/output/
    return rel.as_posix()

def save_png_to_media(rel_path: str, png_bytes: bytes) -> str:
    """
    Input:
        rel_path (str): path to store the image
        png_bytes (bytes): png bytes retrieved from comfyui view?...
    Output: rel_path
    """
    if not png_bytes:
        raise ValueError("png_bytes is empty.")
    
    target = Path(settings.MEDIA_ROOT) / rel_path
    target.parent.mkdir(parents=True, exist_ok=True) 
    target.write_bytes(png_bytes)
    return rel_path
