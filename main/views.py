import logging
import q
from django.views.generic import TemplateView
from motorpool.forms import AutoFilterFormAutoClass
from motorpool.models import Brand
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)

class IndexView(TemplateView):
    template_name = 'main/index.html'

    @q
    def get(self, request, *args, **kwargs):
        auto_class = request.GET.get('auto_class', '')
        if request.GET.get('search', '') == '1' and auto_class:
            return HttpResponseRedirect(f"{reverse_lazy('motorpool:auto_list')}?auto_class={auto_class}")
        return super().get(request, *args, **kwargs)
    @q
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_list'] = Brand.objects.annotate(car_count=Count('cars')).all()[:3]
        context['filter_form'] = AutoFilterFormAutoClass()
        logger.info(f'brand_list = {context["brand_list"]}')
        q(context['brand_list'])
        return context


