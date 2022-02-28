from django.urls import path
from django.views.decorators.http import require_POST
from motorpool import views

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
]