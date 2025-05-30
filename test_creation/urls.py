#backend/test_creation/urls.py
# test_creation/urls.py

from django.urls import path
from .views import (
    CreateTestView, ListTestView, TestDetailView,
    CreateSectionView, ListSectionsByTestView, SectionDetailView,
    CreateQuestionView, ListQuestionsBySectionView, QuestionDetailView,
    CreateOptionView, ListOptionsByQuestionView, OptionDetailView, fetch_section_questions,
)

urlpatterns = [
   
 # Test
    path('tests/create/', CreateTestView.as_view(), name='create-test'),
    path('tests/', ListTestView.as_view(), name='list-tests'),
    path('tests/<uuid:test_id>/', TestDetailView.as_view(), name='test-detail'),

# Section
    path('sections/create/', CreateSectionView.as_view(), name='create-section'),
    path('tests/<uuid:test_id>/sections/', ListSectionsByTestView.as_view(), name='list-sections'),
    path('sections/<uuid:section_id>/', SectionDetailView.as_view(), name='section-detail'),

# Question
    path('questions/create/', CreateQuestionView.as_view(), name='create-question'),
    path('sections/<uuid:section_id>/questions/', ListQuestionsBySectionView.as_view(), name='list-questions'),
    path('questions/<uuid:question_id>/', QuestionDetailView.as_view(), name='question-detail'),

# Option
    path('options/create/', CreateOptionView.as_view(), name='create-option'),
    path('questions/<uuid:question_id>/options/', ListOptionsByQuestionView.as_view(), name='list-options'),
    path('options/<uuid:option_id>/', OptionDetailView.as_view(), name='option-detail'),

    path('fetch-section-questions/<int:section_id>/', fetch_section_questions),
]
