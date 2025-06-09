#backend/test_creation/urls.py
# test_creation/urls.py

from django.urls import path
from .views import (
    CreateTestView, ListTestView, TestDetailView,
    CreateSectionView, ListSectionsByTestView, SectionDetailView,
    CreateQuestionView, ListQuestionsBySectionView, QuestionDetailView,
    CreateOptionView, ListOptionsByQuestionView, OptionDetailView, GetTimerView, SaveTimerView,
)

urlpatterns = [
   
 # Test
    path('tests/create/', CreateTestView.as_view(), name='create-test'),
    path('tests/', ListTestView.as_view(), name='list-tests'),
    path('tests/<int:test_id>/', TestDetailView.as_view(), name='test-detail'),

# Section
    path('sections/create/', CreateSectionView.as_view(), name='create-section'),
    path('tests/<int:test_id>/sections/', ListSectionsByTestView.as_view(), name='list-sections'),
    path('sections/<int:section_id>/', SectionDetailView.as_view(), name='section-detail'),

# Question
    path('questions/create/', CreateQuestionView.as_view(), name='create-question'),
    path('sections/<int:section_id>/questions/', ListQuestionsBySectionView.as_view(), name='list-questions'),
    path('questions/<int:question_id>/', QuestionDetailView.as_view(), name='question-detail'),

# Option
    path('options/create/', CreateOptionView.as_view(), name='create-option'),
    path('questions/<int:question_id>/options/', ListOptionsByQuestionView.as_view(), name='list-options'),
    path('options/<int:option_id>/', OptionDetailView.as_view(), name='option-detail'),

    #path('fetch-section-questions/<int:section_id>/', fetch_section_questions),

    path('get-timer/', GetTimerView.as_view(), name='get_timer'),

    path('save-timer/', SaveTimerView.as_view(), name='save_timer'),
]
