from rest_framework import viewsets
import django_filters.rest_framework as filters

from wewager.models import Game
from wewager.serializers import GameSerializer
from common.mixins import SearchActionMixin


class GameFilter(filters.FilterSet):
    since = filters.DateTimeFilter(field_name="date", lookup_expr="gte")
    on = filters.DateTimeFilter(
        field_name="date", method="get_games_on_date", label="On date"
    )

    ordering = filters.OrderingFilter(fields=(("date", "date"), ("league", "league")))

    def get_games_on_date(self, queryset, field_name, value):
        return queryset.filter(date__date=value.date())

    class Meta:
        model = Game
        fields = ("description", "date", "league", "ended", "since", "ordering")


class GameViewSet(viewsets.ReadOnlyModelViewSet, SearchActionMixin):
    """
    View current and past games
    """

    queryset = Game.objects.all()
    serializer_class = GameSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = GameFilter
    search_fields = ("description", "date", "league", "outcomes__description")
