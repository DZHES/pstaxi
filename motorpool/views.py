from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseRedirect
from motorpool.models import Brand, Favorite, Auto, AutoReview, AutoRent
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, TemplateView
from motorpool.forms import (SendEmailForm, BrandCreationForm, BrandUpdateForm, AutoFormSet, BrandAddToFavoriteForm,
                             AutoReviewForm, AutoRentForm, AutoFilterForm)
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import ProcessFormView
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, Q, Prefetch, Avg
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

class CacheMixin(object):
    cache_timeout = 60

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(super(CacheMixin, self).dispatch)(*args, **kwargs)

class BrandListView(ListView):
    model = Brand
    template_name = 'motorpool/brand_list.html'

    def get_paginate_by(self, queryset):
        paginate_by = super().get_paginate_by(queryset)
        if 'brand_list_paginate_by' in self.request.session:
            paginate_by = self.request.session['brand_list_paginate_by']
        return paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_number'] = Brand.objects.count()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-pk')

class BrandDetailView(DetailView):
    model = Brand
    template_name = 'motorpool/brand_detail.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        default_object = super().get_object(queryset)
        return default_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cars'] = self.object.cars.all()
        context['favorite_form'] = BrandAddToFavoriteForm(initial={'user': self.request.user, 'brand': self.object})
        return context

    def get_template_names(self):
        default_template_names = super().get_template_names()
        return default_template_names

def send_email_view(request):
    if request.method == 'POST':
        # ???????? ?????????? ???????????? POST (???????????? ???????????? ?????????????????? e-mail),
        # ???? ?????????????? ?????????????????? ?????????? ?? ?????????????? ???? ??????????????
        form = SendEmailForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            email = cd.get('email', '')
            comment = cd.get('comment', '')
            checkbox1 = cd.get('checkbox1', False)
            checkbox2 = cd.get('checkbox2', False)
            variant = int(cd.get('variant', 1))
            variants = cd.get('variants', [])
        else:
            messages.error(request, form.non_field_errors())
    else:
        # ???????? ?????????? ???????????? GET (???????????????? ?????????????? ?? ????????????????),
        # ???? ?????????????? ???????????? ?????????????????? ??????????
        form = SendEmailForm()

    # ???????????????? ?????????? ?? ???????????????? ?? ???????????? form
    return render(request, 'motorpool/send_email.html', {'form': form})

class BrandCreateView(LoginRequiredMixin, CreateView):
    model = Brand
    template_name = 'motorpool/brand_create.html'
    form_class = BrandCreationForm
    success_url = reverse_lazy('motorpool:brand_list')

    def form_valid(self, form):
        messages.success(self.request, '?????????? ?????????? ???????????? ??????????????')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        return super().form_invalid(form)

class BrandUpdateView(UpdateView):
    model = Brand
    template_name = 'motorpool/brand_update.html'
    form_class = BrandUpdateForm

class BrandDeleteView(DeleteView):
    model = Brand
    template_name = 'motorpool/brand_delete.html'
    success_url = reverse_lazy('motorpool:brand_list')

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.success(request, f'?????????? {self.object} ????????????')
        return result

class AutoCreateView(ProcessFormView, TemplateView, LoginRequiredMixin):

    template_name = 'motorpool/auto_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand = get_object_or_404(Brand, pk=self.kwargs.get('brand_pk', ''))
        if self.request.method == 'POST':
            formset = AutoFormSet(self.request.POST, self.request.FILES, instance=brand)
        else:
            formset = AutoFormSet(instance=brand)
        context['formset'] = formset
        return context

    def post(self, request, *args, **kwargs):
        brand = get_object_or_404(Brand, pk=kwargs.get('brand_pk', ''))
        formset = AutoFormSet(request.POST, request.FILES, instance=brand)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(brand.get_absolute_url())
        return super().get(request, *args, **kwargs)

class BrandAddToFavoriteView(LoginRequiredMixin, CreateView):
    model = Favorite
    form_class = BrandAddToFavoriteForm

    def get_success_url(self):
        return self.object.brand.get_absolute_url()

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        brand = form.cleaned_data.get('brand', None)
        if not brand:
            brand = get_object_or_404(Brand, pk=form.data.get('brand'))
        redirect_url = brand.get_absolute_url() if brand else reverse_lazy('motorpool:brand_list')
        return HttpResponseRedirect(redirect_url)

    def form_valid(self, form):
        messages.success(self.request, f'?????????? {form.cleaned_data["brand"]} ???????????????? ?? ??????????????????')
        return super().form_valid(form)

@require_POST
def set_paginate_view(request):
    request.session['brand_list_paginate_by'] = request.POST.get('item_count', 0)
    return HttpResponseRedirect(reverse_lazy('motorpool:brand_list'))

class AutoDetailView(CacheMixin, DetailView):
    model = Auto
    template_name = 'motorpool/auto_detail.html'
    cache_timeout = 1 * 60

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.select_related('user')
        context['review_form'] = AutoReviewForm(initial={'user': self.request.user, 'auto': self.object})
        context['rent_form'] = AutoRentForm(initial={'user': self.request.user, 'auto': self.object})
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('brand').annotate(review_count=Count('reviews'), rate=Avg('reviews__rate'))
        return qs

class AutoSendReview(CreateView):
    model = AutoReview
    form_class = AutoReviewForm

    def get_success_url(self):
        return self.object.auto.get_absolute_url()

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return HttpResponseRedirect(form.get_redirect_url())

class AutoRentView(CreateView):
    model = AutoRent
    form_class = AutoRentForm

    def get_success_url(self):
        return self.object.auto.get_absolute_url()

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return HttpResponseRedirect(form.get_redirect_url())

    def form_valid(self, form):
        messages.success(self.request, f'???? ?????????????? ?????????????????????????? ????????????????????!')
        return super().form_valid(form)

class AutoListView(ListView):
    model = Auto
    template_name = 'motorpool/auto_list.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = self.object_list.count()
        context['filter_form'] = AutoFilterForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        form = AutoFilterForm(self.request.GET)
        if form.is_valid():
            filter_brand = form.cleaned_data['brand']
            filter_class = form.cleaned_data['auto_class']
            filter_options = form.cleaned_data['options']
            if filter_brand:
                queryset = queryset.filter(brand=filter_brand)
            if filter_class:
                queryset = queryset.filter(auto_class__in=filter_class)
            if filter_options:
                for option in filter_options:
                    queryset = queryset.filter(options__in=[option])
        queryset = queryset.select_related('brand').annotate(review_count=Count('reviews'), rate=Avg('reviews__rate'))

        return queryset

@cache_page(20)
def auto_list_cache(request):
    return render(request, 'motorpool/auto_list_cache.html', {'object_list': Auto.objects.all()})