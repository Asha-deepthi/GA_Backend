# test_creation/views.py
from rest_framework.permissions import AllowAny
from rest_framework import generics, permissions
from rest_framework.views import APIView , View
from rest_framework.response import Response
from .models import Test, Section, Question, Option, SectionTimer
from .serializers import TestSerializer, SectionSerializer, QuestionSerializer, OptionSerializer
import json
from django.http import JsonResponse
from django.conf import settings
from django.core.cache import cache
import random
from .models import SectionTimer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from test_execution.models import Answer

# Test Views (already created)
class CreateTestView(generics.CreateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ListTestView(generics.ListAPIView):
    serializer_class = TestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Test.objects.filter(created_by=self.request.user)


class TestDetailView(generics.RetrieveAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [permissions.IsAuthenticated]
    #lookup_field = 'test_id'
    lookup_field = 'id'            # model field used to get instance
    lookup_url_kwarg = 'test_id'   # URL kwarg to match


# Section Views
class CreateSectionView(generics.CreateAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ListSectionsByTestView(generics.ListAPIView):
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        test_id = self.kwargs['test_id']
        return Section.objects.filter(test__id=test_id)


class SectionDetailView(generics.RetrieveAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    #lookup_field = 'section_id'
    lookup_field = 'id'
    lookup_url_kwarg = 'section_id'


# Question Views
class CreateQuestionView(generics.CreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ListQuestionsBySectionView(generics.ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        section_id = self.kwargs['section_id']
        return Question.objects.filter(section__id=section_id)


class QuestionDetailView(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [AllowAny]
    #lookup_field = 'question_id'
    lookup_field = 'id'
    lookup_url_kwarg = 'question_id'


# Option Views
class CreateOptionView(generics.CreateAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [AllowAny]


class ListOptionsByQuestionView(generics.ListAPIView):
    serializer_class = OptionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        question_id = self.kwargs['question_id']
        return Option.objects.filter(question__id=question_id)


class OptionDetailView(generics.RetrieveAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [AllowAny]
    #lookup_field = 'option_id'
    lookup_field = 'id'
    lookup_url_kwarg = 'option_id'

class GetTimerView(View):
    def get(self, request):
        session_id = request.GET.get('session_id')
        section_id = request.GET.get('section_id')

        if not all([session_id, section_id]):
            return JsonResponse({'error': 'Missing parameters'}, status=400)

        try:
            timer = SectionTimer.objects.get(session_id=session_id, section_id=section_id)
            return JsonResponse({'remaining_time': timer.remaining_time})
        except SectionTimer.DoesNotExist:
            return JsonResponse({'remaining_time': None})

@method_decorator(csrf_exempt, name='dispatch')
class SaveTimerView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            print("Received data in save-timer:", data) 
            session_id = data.get('session_id')
            section_id = data.get('section_id')
            remaining_time = data.get('remaining_time')
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        print(f"Parsed -> session_id: {session_id}, section_id: {section_id}, remaining_time: {remaining_time}")  
        if session_id is None or section_id is None or remaining_time is None:
            print("Missing one or more required fields")  
            return JsonResponse({'error': 'Missing parameters'}, status=400)

        timer, created = SectionTimer.objects.update_or_create(
            session_id=session_id,
            section_id=section_id,
            defaults={'remaining_time': remaining_time}
        )
        print("Timer saved or updated")  
        return JsonResponse({'message': 'Timer saved successfully'})