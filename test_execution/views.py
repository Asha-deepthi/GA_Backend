from django.shortcuts import render
from rest_framework import generics
from .models import *
from .serializers import *

class BasicDetailsCreateView(generics.CreateAPIView):
    queryset = BasicDetails.objects.all()
    serializer_class = BasicDetailsSerializer

class DemoQuestionListView(generics.ListAPIView):
    queryset = DemoQuestion.objects.all()
    serializer_class = DemoQuestionSerializer

class TestSessionListCreateView(generics.ListCreateAPIView):
    queryset = TestSession.objects.all()
    serializer_class = TestSessionSerializer

class TestSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestSession.objects.all()
    serializer_class = TestSessionSerializer

class AnswerListCreateView(generics.ListCreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

class AnswerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

class ProctoringLogListCreateView(generics.ListCreateAPIView):
    queryset = ProctoringLog.objects.all()
    serializer_class = ProctoringLogSerializer

class ProctoringLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProctoringLog.objects.all()
    serializer_class = ProctoringLogSerializer

class ProctorCommentListCreateView(generics.ListCreateAPIView):
    queryset = ProctorComment.objects.all()
    serializer_class = ProctorCommentSerializer

class ProctorCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProctorComment.objects.all()
    serializer_class = ProctorCommentSerializer

class PageContentListCreateView(generics.ListCreateAPIView):
    queryset = PageContent.objects.all()
    serializer_class = PageContentSerializer

class PageContentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PageContent.objects.all()
    serializer_class = PageContentSerializer