#backend/test_creation/urls.py
from django.urls import path
from .views import CreateTestView, ListTestView, TestDetailView, fetch_section_questions

urlpatterns = [
    path('tests/', ListTestView.as_view(), name='test-list'),
    path('tests/create/', CreateTestView.as_view(), name='test-create'),
    path('tests/<int:id>/', TestDetailView.as_view(), name='test-detail'),
    path('fetch-section-questions/<int:section_id>/', fetch_section_questions),
]

