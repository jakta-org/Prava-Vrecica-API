
from django.urls import path
from . import views
urlpatterns = [
    path('create-user/',views.UserViews.as_view(), name='create_user'),
    path('get-token/', views.TokenViews.as_view(), name='get_token')
]