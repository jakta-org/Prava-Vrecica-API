from django.urls import path
from . import views
from .views import Updates
from .views import AImodelView
from .views import MappingRegionsView

urlpatterns = [
    # path('ai_model/', AImodelView.as_view(), name='ai_model'),
    # path('mapping_regions/', MappingRegionsView.as_view(), name='latest_mapping_regions'),
]