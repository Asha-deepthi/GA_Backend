from django.urls import path
from .views import BasicDetailsCreateView
from .views import DemoQuestionListView

urlpatterns = [
    path('submit-details/', BasicDetailsCreateView.as_view(), name='submit-details'),
    path('demo-questions/', DemoQuestionListView.as_view(), name='demo-questions'),
]
