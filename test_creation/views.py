# test_creation/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions
from rest_framework.views import APIView , View
from rest_framework.response import Response
from .models import Test, Section, Question, Option
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
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ListQuestionsBySectionView(generics.ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        section_id = self.kwargs['section_id']
        return Question.objects.filter(section__id=section_id)


class QuestionDetailView(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    #lookup_field = 'question_id'
    lookup_field = 'id'
    lookup_url_kwarg = 'question_id'


# Option Views
class CreateOptionView(generics.CreateAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [permissions.IsAuthenticated]


class ListOptionsByQuestionView(generics.ListAPIView):
    serializer_class = OptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        question_id = self.kwargs['question_id']
        return Option.objects.filter(question__id=question_id)


class OptionDetailView(generics.RetrieveAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    #lookup_field = 'option_id'
    lookup_field = 'id'
    lookup_url_kwarg = 'option_id'


def fetch_section_questions(request, section_id):
    print("Request GET params:", request.GET)
    session_id = request.GET.get('session_id')
    if not session_id:
        return JsonResponse({'error': 'Session ID is required as a query parameter'}, status=400)

    cache_key = f"json_qns_s{section_id}_sess{session_id}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse(cached_data, safe=False)

    try:
        with open(settings.BASE_DIR / 'test_creation' / 'test_questions.json') as f:
            data = json.load(f)
    except FileNotFoundError:
        return JsonResponse({'error': 'Question file not found'}, status=500)

    section_data = next((sec for sec in data if sec.get("section_id") == section_id), None)
    if not section_data:
        return JsonResponse({'error': 'Section not found'}, status=404)

    questions = section_data.get("questions", [])

    # Shuffle questions and options
    random.shuffle(questions)
    for question in questions:
        if "options" in question:
            random.shuffle(question["options"])

    # Fetch existing answers for this session and section from DB
    answers = Answer.objects.filter(session_id=session_id, section_id=section_id)
    answer_map = {str(ans.question_id): ans for ans in answers}

    # Attach answer details to each question if present
    for question in questions:
        qid = str(question.get('question_id'))
        ans = answer_map.get(qid)
        if ans:
            question['answer_id'] = ans.id
            question['marks_allotted'] = ans.marks_allotted
            question['answer_text'] = ans.answer_text
            question['evaluated'] = ans.evaluated
            question['marked_for_review'] = ans.marked_for_review
            # Attach any other answer fields you want frontend to have

    response_data = {
        "section_type": section_data.get("section_type", "unknown"),
        "questions": questions,
    }

    cache.set(cache_key, response_data, timeout=60 * 60)

    return JsonResponse(response_data, safe=False)

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