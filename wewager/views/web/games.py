from wewager.models import Game
from wewager.views.web.htmx_view import HtmxTemplateView

class GamesView(HtmxTemplateView):

    template_name = "games.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["games"] = Game.objects.all()
        return context