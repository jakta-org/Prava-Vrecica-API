from django.urls import path
from . import views

urlpatterns = [
    path('user/',views.UserViews.as_view(), name='create_user'),
    path('token/', views.TokenViews.as_view(), name='get_token'),
    path('entrance-key/', views.create_entrance_key, name='create_entrance_key'),
    
    path('user/<int:id>/', views.UserDetailsView.as_view(), name='user_details'),
    path('user/<int:id>/meta-data', views.UserMetaDataViews.as_view(), name='user_meta_data'),

]