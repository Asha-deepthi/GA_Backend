from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import *
from .serializers import *
from django.conf import settings
import json

class BasicDetailsCreateView(generics.CreateAPIView):
    queryset = BasicDetails.objects.all()
    serializer_class = BasicDetailsSerializer

class GetUserView(generics.RetrieveAPIView):
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

#class AnswerSubmissionView(APIView):
#    parser_classes = (MultiPartParser, FormParser)
#
#    def post(self, request, *args, **kwargs):
#       session_id = request.data.get('session_id')
#        section_id = request.data.get('section_id')
#        question_id = request.data.get('question_id')
#        question_type = request.data.get('question_type')  # Corrected name
#        answer_text = request.data.get('answer_text')
#        marked_for_review = request.data.get('marked_for_review', 'false').lower() == 'true'
#        status = request.data.get('status') or 'unanswered'
#
#        if not all([session_id, section_id, question_id, question_type]):
#            return Response({"error": "Missing required fields."}, status=400)
#
#        #Auto-evaluate logic
#        marks_allotted = 0
#        evaluated = False
#
#        try:
#            question = Question.objects.get(id=question_id)
#        except Question.DoesNotExist:
#            return Response({"error": "Question not found"}, status=404)
#
#        if question_type.lower() in ['mcq', 'fill_in_the_blank', 'integer']:
#            correct = str(question.correct_answer).strip().lower()
#            submitted = str(answer_text).strip().lower()
#            if correct == submitted:
#                marks_allotted = question.marks
#            evaluated = True
#        else:
#            # Subjective, Audio, Video — manual evaluation later
#            marks_allotted = 0
#            evaluated = False
#
#        #Save answer
#        answer, created = Answer.objects.update_or_create(
#            session_id=session_id,
#            question_id=question_id,
#            defaults={
#                'section_id': section_id,
#                'question_type': question_type,
#                'answer_text': answer_text,
#                'marked_for_review': marked_for_review,
#                'status': status,
#                'audio_file': request.FILES.get('audio_file'),
#                'video_file': request.FILES.get('video_file'),
#                'marks_allotted': marks_allotted,
#                'evaluated': evaluated,
#            }
#        )
#
#        return Response({
#            "message": "Answer saved successfully",
#            "marks_allotted": marks_allotted,
#            "evaluated": evaluated
#        }, status=201)

class AnswerSubmissionView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        session_id = request.data.get('session_id')
        section_id = request.data.get('section_id')
        question_id = request.data.get('question_id')
        question_type = request.data.get('question_type')
        answer_text = request.data.get('answer_text')
        marked_for_review = request.data.get('marked_for_review', 'false').lower() == 'true'
        status = request.data.get('status') or 'unanswered'

        if not all([session_id, section_id, question_id, question_type]):
            return Response({"error": "Missing required fields."}, status=400)

        # Load JSON questions
        try:
            with open(settings.BASE_DIR / 'test_creation' / 'test_questions.json') as f:
                questions_data = json.load(f)
        except Exception:
            return Response({"error": "Failed to load questions JSON."}, status=500)

        # Find question by matching question_id (same key your frontend uses)
        question = next((q for q in questions_data if str(q.get('question_id')) == str(question_id)), None)
        if not question:
            return Response({"error": "Question not found in JSON."}, status=404)

        marks_allotted = 0
        evaluated = False

        # Map frontend sectionType to backend answer types for auto-eval
        auto_eval_types = ['multiple_choice', 'fill_in_the_blank', 'integer']

        if question_type.lower() in auto_eval_types:
            correct = str(question.get('correct_answer', '')).strip().lower()
            submitted = str(answer_text).strip().lower() if answer_text else ''
            if correct == submitted:
                marks_allotted = question.get('marks', 0)
            evaluated = True
        else:
            # subjective, audio, video — manual evaluation later
            marks_allotted = 0
            evaluated = False

        # Save or update answer
        answer, created = Answer.objects.update_or_create(
            session_id=session_id,
            question_id=question_id,
            defaults={
                'section_id': section_id,
                'question_type': question_type,
                'answer_text': answer_text,
                'marked_for_review': marked_for_review,
                'status': status,
                'audio_file': request.FILES.get('audio_file'),
                'video_file': request.FILES.get('video_file'),
                'marks_allotted': marks_allotted,
                'evaluated': evaluated,
            }
        )

        return Response({
            "message": "Answer saved successfully",
            "marks_allotted": marks_allotted,
            "evaluated": evaluated
        }, status=201)

class ManualAnswerEvaluationView(APIView):
    def post(self, request):
        answer_id = request.data.get('answer_id')
        marks = request.data.get('marks')

        if not answer_id or marks is None:
            return Response({'error': 'Missing answer_id or marks'}, status=400)

        try:
            answer = Answer.objects.get(id=answer_id)
            answer.marks_allotted = marks
            answer.evaluated = True
            answer.save()
            return Response({'message': 'Answer manually evaluated'})
        except Answer.DoesNotExist:
            return Response({'error': 'Answer not found'}, status=404)

class AnswerListView(APIView):
    def get(self, request):
        session_id = request.GET.get('session_id')
        section_id = request.GET.get('section_id')

        if not session_id or not section_id:
            return Response({"error": "session_id and section_id are required."}, status=400)

        answers = Answer.objects.filter(session_id=session_id, section_id=section_id)
        data = []
        for ans in answers:
            data.append({
                "question_id": ans.question_id,
                "answer_text": ans.answer_text,
                "marked_for_review": ans.marked_for_review,
                "status": ans.status,
            })
        return Response(data, status=200)


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

class AudioUploadView(generics.CreateAPIView):
    queryset = AudioResponse.objects.all()
    serializer_class = AudioResponseSerializer
    #permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save()

#for canditate who login using token

#class AudioResponseUploadView(generics.CreateAPIView):
    #queryset = AudioResponse.objects.all()
    #serializer_class = AudioResponseSerializer
    #ermission_classes = [IsAuthenticated]

    #def perform_create(self, serializer):
        #user = self.request.user
        #serializer.save(user=user)

class VideoUploadView(generics.CreateAPIView):
    queryset = VideoResponse.objects.all()
    serializer_class = VideoResponseSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def perform_create(self, serializer):
        serializer.save()

class DemoAudioUploadView(generics.CreateAPIView):
    queryset = DemoAudioResponse.objects.all()
    serializer_class = DemoAudioResponseSerializer
    #permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save()

class ProctoringScreenshotUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ProctoringScreenshotSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Screenshot uploaded successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({"error": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        screenshots = ProctoringScreenshot.objects.filter(session_id=session_id)
        serializer = ProctoringScreenshotSerializer(screenshots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TestRouteView(APIView):
    def post(self, request):
        return Response({"message": "Test route works!"})