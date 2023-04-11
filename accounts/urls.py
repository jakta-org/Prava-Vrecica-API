
from django.urls import path
from . import views
urlpatterns = [
    path('user/',views.UserViews.as_view(), name='create_user'),
    path('token/', views.TokenViews.as_view(), name='get_token'),
    path('entrance-key/', views.create_entrance_key, name='create_entrance_key'),
]

'''
root = https://karlo13.pythonanywhere.com/

/accounts/entrance-key/
	POST:
        int group_id        - opcinalno
		datetime expires_at - opcinalno
		int uses_left       - opcinalno
		-> returns entrance_code

/accounts/user/
	POST:
		string email
		string password
		string username     - opcinalno
		string entrance_code - opcinalno
		-> returns token

/accounts/token/
	POST:
		string username / email
		string password
		-> returns token
'''