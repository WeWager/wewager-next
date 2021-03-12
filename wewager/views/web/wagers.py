from wewager.models import Wager, WagerState
from wewager.views.web.htmx_view import HtmxTemplateView

class WagerView(HtmxTemplateView):

    template_name = "wagers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sent_wagers"] = Wager.objects.filter(sender=self.request.user).exclude(status=WagerState.EXPIRED)
        context["recieved_wagers"] = Wager.objects.filter(recipient=self.request.user).exclude(status=WagerState.EXPIRED)
        return context