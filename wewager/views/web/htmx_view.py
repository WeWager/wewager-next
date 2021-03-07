from django.views.generic import TemplateView


class HtmxTemplateView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["base_template"] = "ajax.html" if self.request.htmx else "index.html"
        return context