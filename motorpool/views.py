from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseRedirect
from motorpool.models import Brand, Favorite, Auto, AutoReview, AutoRent
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, TemplateView
from motorpool.forms import (SendEmailForm, BrandCreationForm, BrandUpdateForm, AutoFormSet, BrandAddToFavoriteForm,
                             AutoReviewForm, AutoRentForm)
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import ProcessFormView
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, Q, Prefetch, Avg



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
        # Если метод запрос POST (нажата кнопка Отправить e-mail),
        # то создаем экземпляр формы с данными из запроса
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
        # Если метод запрос GET (страница открыта в браузере),
        # то создаем пустой экземпляр формы
        form = SendEmailForm()

    # Передаем форму в контекст с именем form
    return render(request, 'motorpool/send_email.html', {'form': form})

class BrandCreateView(LoginRequiredMixin, CreateView):
    model = Brand
    template_name = 'motorpool/brand_create.html'
    form_class = BrandCreationForm
    success_url = reverse_lazy('motorpool:brand_list')

    def form_valid(self, form):
        messages.success(self.request, 'Новый бренд создан успешно')
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
        messages.success(request, f'Бренд {self.object} удален')
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
        messages.success(self.request, f'Бренд {form.cleaned_data["brand"]} добавлен в избранное')
        return super().form_valid(form)

@require_POST
def set_paginate_view(request):
    request.session['brand_list_paginate_by'] = request.POST.get('item_count', 0)
    return HttpResponseRedirect(reverse_lazy('motorpool:brand_list'))

def auto_list(request):
    cars_qs = Auto.objects.select_related('pts')
    prefetch_all_cars = Prefetch('cars', queryset=cars_qs.all(), to_attr='all_cars_list')
    prefetch_new_cars = Prefetch('cars', queryset=cars_qs.filter(year__gt=2010), to_attr='new_cars_list')
    prefetch_old_cars = Prefetch('cars', queryset=cars_qs.filter(year__lt=2010), to_attr='old_cars_list')
    qs = Brand.objects.prefetch_related(prefetch_all_cars, prefetch_new_cars, prefetch_old_cars).annotate(
        car_count=Count('cars'),
        total_engine_power=Sum('cars__pts__engine_power'),
        new_cars=Count('cars', Q(cars__year__gt=2010)),
        old_cars=Count('cars', Q(cars__year__lt=2010))
    )

    return render(request, 'motorpool/auto_list.html', {'object_list': qs})

class AutoDetailView(DetailView):
    model = Auto
    template_name = 'motorpool/auto_detail.html'

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
        messages.success(self.request, f'Вы успешно забронировали автомобиль!')
        return super().form_valid(form)