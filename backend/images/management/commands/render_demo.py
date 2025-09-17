from django.core.management.base import BaseCommand
from django.db import transaction
from shared.models import Session, Turn, Option, ImageRender

# python manage.py render_demo --year 2035

# assume these are the 4 image_text generated
TEXTS = {
    'A': 'misty forest at dawn, soft volumetric light, filmic color, wide shot',
    'B': 'coastal city skyline in blue hour, subtle haze, architectural emphasis',
    'C': 'desert canyon vista, golden hour long shadows, high contrast',
    'D': 'futuristic harbor, neon reflections, cinematic composition'
}

class Command(BaseCommand):
    help = "Seed four Options with image_text and render 4 images via ComfyUI."

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, default=2035)


    def handle(self, *args, **opts):
        # create session and turn and options
        with transaction.atomic():
            s = Session.objects.create()
            t = Turn.objects.create(session=s, year=opts['year'])

            for lbl, txt in TEXTS.items():
                Option.objects.create(turn=t, label=lbl, image_text=txt)

        # test generation function, should be able to see 4 images generated under backend/media/comfyui/output/
        # and terminal should print out 4 images status and rel_path              
        from images.render_pipeline import generate_four_images_blocking
        out = generate_four_images_blocking(session_id=s.id, turn_id=t.id)
        self.stdout.write(self.style.SUCCESS(f"Turn {t.id} rendered"))
        self.stdout.write(str(out))
