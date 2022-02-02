from django.contrib import admin

import motorpool.models
from .models  import Brand, Auto, Option, VehiclePassport

class EnginePowerFilter(admin.SimpleListFilter):
    title = 'Мощность двигателя'
    parameter_name = 'engine_power_filter'

    def lookups(self, request, model_admin):
        filter_list = (
            ('0', '0-100'),
            ('1', '101-200'),
            ('2', '201-300')
        )
        return filter_list

    def queryset(self, request, queryset):
        filter_value = self.value()
        if filter_value == '0':
            return queryset.filter(pts__engine_power__gte=0, pts__engine_power__lte=100)
        elif filter_value == '1':
            return queryset.filter(pts__engine_power__gte=101, pts__engine_power__lte=200)
        elif filter_value == '2':
            return queryset.filter(pts__engine_power__gte=201, pts__engine_power__lte=300)
        return queryset

class AutoInstanceInline(admin.TabularInline):
    model = motorpool.models.Auto
    extra = 0

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    inlines = [AutoInstanceInline]

@admin.register(Auto)
class AutoAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'brand', 'year', 'auto_class', 'display_engine_power']
    list_select_related = ['brand', 'pts']
    list_display_links = ['id', 'number', 'brand', ]
    list_filter = [EnginePowerFilter, 'auto_class', 'options', 'brand', ]
    search_fields = ['brand__title', 'number', ]

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    pass

@admin.register(VehiclePassport)
class VehiclePassportAdmin(admin.ModelAdmin):
    list_display = ['id', 'auto', 'vin', 'engine_volume', 'engine_power']
    list_filter = ['auto__brand', ]
    list_filter = ['auto__brand', ]
