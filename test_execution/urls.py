from django.urls import path
from .views import BasicDetailsCreateView

urlpatterns = [
    path('submit-details/', BasicDetailsCreateView.as_view(), name='submit-details'),
]
