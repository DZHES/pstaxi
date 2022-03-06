from django.views.generic import TemplateView

from motorpool.models import Brand

class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_list'] = Brand.objects.all()[:3]
        return context
