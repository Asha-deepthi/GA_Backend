from django.urls import path
from .views import (
    BasicDetailsCreateView, DemoQuestionListView, TestSessionListCreateView, TestSessionDetailView, AnswerListCreateView,
    AnswerDetailView, ProctoringLogListCreateView, ProctoringLogDetailView, ProctorCommentListCreateView, ProctorCommentDetailView,
    PageContentListCreateView, PageContentDetailView, AudioUploadView,
)
 
urlpatterns = [
    path('submit-details/', BasicDetailsCreateView.as_view(), name='submit-details'),
    path('demo-questions/', DemoQuestionListView.as_view(), name='demo-questions'),

    # TestSession
    path('test-sessions/', TestSessionListCreateView.as_view(), name='testsession-list-create'),
    path('test-sessions/<int:pk>/', TestSessionDetailView.as_view(), name='testsession-detail'),

    # Answer
    path('answers/', AnswerListCreateView.as_view(), name='answer-list-create'),
    path('answers/<int:pk>/', AnswerDetailView.as_view(), name='answer-detail'),

    # ProctoringLog
    path('proctoring-logs/', ProctoringLogListCreateView.as_view(), name='proctoringlog-list-create'),
    path('proctoring-logs/<int:pk>/', ProctoringLogDetailView.as_view(), name='proctoringlog-detail'),

    # ProctorComment
    path('proctor-comments/', ProctorCommentListCreateView.as_view(), name='proctorcomment-list-create'),
    path('proctor-comments/<int:pk>/', ProctorCommentDetailView.as_view(), name='proctorcomment-detail'),

    # PageContent
    path('page-contents/', PageContentListCreateView.as_view(), name='pagecontent-list-create'),
    path('page-contents/<int:pk>/', PageContentDetailView.as_view(), name='pagecontent-detail'),

    path('upload-audio/', AudioUploadView.as_view(), name='upload-audio'),
]
