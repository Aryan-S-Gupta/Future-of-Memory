from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
from shared.models import Session, Turn, Option
from images.display import display_by_option

# python manage.py display_demo --session 1 --turn 1 --option C

class Command(BaseCommand):
    help = "Test display_by_option() for a given session/turn/option."

    def add_arguments(self, parser):
        parser.add_argument('--session', type=int, help='Session ID (default: latest session)')
        parser.add_argument('--turn', type=int, help='Turn ID (default: latest turn in the chosen session)')
        parser.add_argument('--option', type=str, default='A', help='Option label A|B|C|D')
        parser.add_argument('--wait', type=float, default=25.0, help='Max wait seconds for image readiness')
        parser.add_argument('--poll', type=float, default=0.5, help='Poll interval seconds')

    def handle(self, *args, **opts):
        # pick session
        if opts['session']:
            session = get_object_or_404(Session, pk=opts['session'])
        else:
            session = Session.objects.order_by('-id').first()
            if not session:
                self.stderr.write(self.style.ERROR('No sessions found. Run the generate command first.'))
                return

        # pick turn
        if opts['turn']:
            turn = get_object_or_404(Turn, pk=opts['turn'], session=session)
        else:
            turn = Turn.objects.filter(session=session).order_by('-id').first()
            if not turn:
                self.stderr.write(self.style.ERROR('No turns found for this session.'))
                return

        # pick option
        option = Option.objects.filter(turn=turn, label=opts['option'].upper()).first()
        if not option:
            self.stderr.write(self.style.ERROR(f'Option {opts["option"]} not found for Turn {turn.id}.'))
            return

        # call display
        out = display_by_option(
            session_id=session.id,
            turn_id=turn.id,
            option_id=option.id,
            max_wait_s=opts['wait'],
            poll_every_s=opts['poll'],
        )

        self.stdout.write(self.style.SUCCESS('display_by_option result:'))
        self.stdout.write(str(out))
