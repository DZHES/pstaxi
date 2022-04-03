from django.urls import path
from . import views, test_thread

app_name = 'main'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('test_thread/', test_thread.ThreadView.as_view())
]