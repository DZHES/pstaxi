from django.urls import path
from motorpool import views

app_name = 'motorpool'

urlpatterns = [
    path('brand_list/', views.brand_list, name='brand_list'),
    path('brand_detail/<int:pk>/', views.brand_detail, name='brand_detail')
]