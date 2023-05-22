from django.urls import path
from . import views

urlpatterns = [
    path('user/',views.UserViews.as_view(), name='create_user'),
    path('user/',views.UserViews.as_view(), name='get_user_list'),
    path('token/', views.TokenViews.as_view(), name='get_token'),
    path('entrance_key/', views.create_entrance_key, name='create_entrance_key'),
    
    path('user/<int:user_id>/', views.UserDetailsView.as_view(), name='user_details'),
    path('user/<int:user_id>/meta_data/', views.UserMetaDataViews.as_view(), name='user_meta_data'),
    path('user/<int:user_id>/score/', views.UserScoreViews.as_view(), name='user_score'),

    path('group/', views.create_group, name='create_group'),
    path('group/<int:group_id>/', views.GroupViews.as_view(), name='group'),
    path('group/<int:group_id>/user/<int:user_id>/', views.UserGroupViews.as_view(), name='group_user'),

    path('group/<int:group_id>/user/', views.get_group_members, name='group_members'),

    path('user/<int:user_id>/group/', views.get_user_groups, name='user_groups'),
]