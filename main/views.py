from django.views.generic import TemplateView
from motorpool.forms import AutoFilterFormAutoClass
from motorpool.models import Brand
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get(self, request, *args, **kwargs):
        auto_class = request.GET.get('auto_class', '')
        if request.GET.get('search', '') == '1' and auto_class:
            return HttpResponseRedirect(f"{reverse_lazy('motorpool:auto_list')}?auto_class={auto_class}")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_list'] = Brand.objects.annotate(car_count=Count('cars')).all()[:3]
        context['filter_form'] = AutoFilterFormAutoClass()
        return context


