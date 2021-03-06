from datetime import datetime

import pytz
from rest_framework import viewsets

from wewager.models import Game
from wewager.serializers import GameSerializer


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /game
    /game/:id
    Returns games currently in progress or in the future
    """

    queryset = Game.objects.filter(date__gte=datetime.utcnow().replace(tzinfo=pytz.utc))
    serializer_class = GameSerializer
