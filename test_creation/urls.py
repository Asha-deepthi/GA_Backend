#backend/test_creation/urls.py
# test_creation/urls.py

from django.urls import path
from .views import (
    CreateTestView, ListTestView, TestDetailView,
    CreateSectionView, ListSectionsByTestView, SectionDetailView, ImportCandidatesFromTestView,
    CreateQuestionView, ListQuestionsBySectionView, QuestionDetailView, FullTestDetailView,
    CreateOptionView, ListOptionsByQuestionView, OptionDetailView,AssignTestToCandidateView,  ValidateTestAttemptView,
    FullTestCreateView,CreateCandidateUserView,fetch_section_questions,SendInvitationsView,ListAssignedCandidatesView,
    CreateOptionView, ListOptionsByQuestionView, OptionDetailView, GetTimerView, SaveTimerView, AllSectionsListView, get_candidate_test_id,  SubmitTestView
)

urlpatterns = [
    # Test URLs
    path('tests/create/', CreateTestView.as_view(), name='create-test'),
    path('tests/', ListTestView.as_view(), name='list-tests'),
    path('tests/<int:test_id>/', TestDetailView.as_view(), name='test-detail'),
    path('tests/full-create/', FullTestCreateView.as_view(), name='full-test-create'),

    # Section URLs (Grouped with Tests for clarity)
    # THIS FIXES: GET .../tests/5/sections/
    path('tests/<int:test_id>/sections/', ListSectionsByTestView.as_view(), name='list-sections-by-test'),
    path('sections/<int:section_id>/', SectionDetailView.as_view(), name='section-detail'),
    
    # Question URLs (The main fix from our previous discussion)
    # THIS FIXES: GET .../tests/5/sections/1/questions/
    path('tests/<int:test_id>/sections/<int:section_id>/questions/', ListQuestionsBySectionView.as_view(), name='list-questions-by-section'),
    path('questions/<int:question_id>/', QuestionDetailView.as_view(), name='question-detail'),
    
    # Option URLs
    path('options/create/', CreateOptionView.as_view(), name='create-option'),
    path('questions/<int:question_id>/options/', ListOptionsByQuestionView.as_view(), name='list-options'),
    path('options/<int:option_id>/', OptionDetailView.as_view(), name='option-detail'),

    # Timer URLs
    # THIS FIXES: GET .../get-timer/?...
    path('get-timer/', GetTimerView.as_view(), name='get_timer'),
    path('save-timer/', SaveTimerView.as_view(), name='save_timer'),

    # Candidate and Invitation URLs
    path('create-candidate/', CreateCandidateUserView.as_view(), name='create-candidate'),
    path('assign-test/', AssignTestToCandidateView.as_view(), name='assign-test'),
    path('tests/<int:test_id>/assigned-candidates/', ListAssignedCandidatesView.as_view(), name='list-assigned-candidates'),
    path('send-invitations/', SendInvitationsView.as_view(), name='send-invitations'),
    path('validate-attempt/', ValidateTestAttemptView.as_view(), name='validate-test-attempt'),
    path('tests/full-detail/<int:test_id>/', FullTestDetailView.as_view(), name='full-test-detail'),
    path("candidate-test-id/", get_candidate_test_id),
    path('submit-test/', SubmitTestView.as_view(), name='submit-test'),
     path('tests/<int:test_id>/import-candidates/', ImportCandidatesFromTestView.as_view(), name='import-candidates-from-test'),
]
   
