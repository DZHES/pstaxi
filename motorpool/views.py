from django.shortcuts import render
from django.http import HttpResponse
from motorpool.models import Brand
from utils.text import plural_form
from django.shortcuts import render, get_object_or_404

def brand_list(request):
    template_name = 'motorpool/brand_list.html'
    brand_number = Brand.objects.all().count()
    brand_objects = Brand.objects.all()
    context = {
        'brand_objects' : brand_objects,
        'brand_number' : brand_number,
    }
    return render(request, template_name, context)

def brand_detail(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    context = {
        'brand' : brand,
        'cars' : brand.cars.all(),
        'brand_number' : Brand.objects.count(),
    }
    return render(request, 'motorpool/brand_detail.html', context)
