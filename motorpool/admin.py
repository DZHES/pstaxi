from django.contrib import admin

from .models  import Brand, Auto, Option, VehiclePassport


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    pass

@admin.register(Auto)
class AutoAdmin(admin.ModelAdmin):
    pass

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    pass

@admin.register(VehiclePassport)
class VehiclePassportAdmin(admin.ModelAdmin):
    pass
