from datetime import datetime

from wewager.models import Game
from wewager.views.web.htmx_view import HtmxTemplateView


class GamesView(HtmxTemplateView):

    template_name = "games.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = Game.objects.filter(date_eastern__date=datetime.today().date())
        league = self.request.GET.get("league", None)
        if league:
            qs = qs.filter(league=league)
        context["games"] = qs.order_by("league").order_by("date_eastern")
        return context
