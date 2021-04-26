from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError

from wewager.models import Game
from wewager.bet_closer import BetCloser


class Command(BaseCommand):
    help = "Closes all active games"

    def handle(self, *args, **kwargs):
        yesterday = datetime.now() - timedelta(days=1)
        games = Game.objects.filter(date__gte=yesterday, ended=True)
        for game in games:
            BetCloser.resolve_game(game)
