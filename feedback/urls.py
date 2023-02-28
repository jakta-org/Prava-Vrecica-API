from django.conf.urls import url
from . import views

urlpatterns = [
    url('', views.get_update, name='get_update'),
]