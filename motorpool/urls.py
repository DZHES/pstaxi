from django.urls import path
from django.views.decorators.http import require_POST
from motorpool import views
from django.views.decorators.cache import cache_page

app_name = 'motorpool'

urlpatterns = [
    # model Brand
    path('brand_list/', views.BrandListView.as_view(), name='brand_list'),
    path('brand_detail/<int:pk>/', views.BrandDetailView.as_view(), name='brand_detail'),
    path('brand_create/', views.BrandCreateView.as_view(), name='brand_create'),
    path('brand-update/<int:pk>/', views.BrandUpdateView.as_view(), name='brand_update'),
    path('brand-delete/<int:pk>/', views.BrandDeleteView.as_view(), name='brand_delete'),
    path('send_email/', views.send_email_view, name='send_email'),
    # model Auto
    path('auto-create/<int:brand_pk>/', views.AutoCreateView.as_view(), name='auto_create'),
    path('brand-add-to-favorite/', require_POST(views.BrandAddToFavoriteView.as_view()), name='brand_add_to_favorite'),
    path('brand-set-paginate/', views.set_paginate_view, name='brand_list_set_paginate'),
    path('auto-list/', cache_page(20)(views.AutoListView.as_view()), name='auto_list'),
    path('auto-detail/<int:pk>/', views.AutoDetailView.as_view(), name='auto_detail'),
    path('auto-send-review/', require_POST(views.AutoSendReview.as_view()), name='auto_send_review'),
    path('auto-rent/', require_POST(views.AutoRentView.as_view()), name='auto_rent'),
    path('auto-list-cache/', cache_page(20)(views.auto_list_cache), name='auto_list_cache'),
]