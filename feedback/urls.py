from django.urls import path
from . import views

urlpatterns = [
    path('feedback/', views.FeedbackView.as_view(), name='feedback'),
    path('feedback/<int:feedback_id>/', views.FeedbackDetailsView.as_view(), name='feedback_details'),
]