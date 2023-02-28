from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_update, name='get_update'),
    path('ai_model', views.get_latest_ai_model, name='get_latest_ai_model'),
    path('thresh_map', views.get_latest_thresh_map, name='get_latest_thresh_map'),
]