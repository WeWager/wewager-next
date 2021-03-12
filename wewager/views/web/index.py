from django.http import HttpResponse
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "index.html"


def balance_view(request):
    return HttpResponse(request.user.wallet.balance)
