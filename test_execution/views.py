from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import *
from test_creation.models import Test, Section, Candidate_Test
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

class AnswerSubmissionView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        print("AnswerSubmissionView POST called with data:", request.data)

        candidate_test_id = request.data.get('candidate_test_id')
        section_id = request.data.get('section_id')
        question_id = request.data.get('question_id')
        answer_text = request.data.get('answer_text')
        marked_for_review = request.data.get('marked_for_review', 'false').lower() == 'true'
        status = request.data.get('status') or 'unanswered'

        # Validate candidate_test
        try:
            candidate_test = Candidate_Test.objects.get(id=candidate_test_id)
        except Candidate_Test.DoesNotExist:
            return Response({"error": "Candidate_Test not found"}, status=404)

        # Fetch question and section
        try:
            question = Question.objects.get(id=question_id)
            section = Section.objects.get(id=section_id)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=404)
        except Section.DoesNotExist:
            return Response({"error": "Section not found"}, status=404)

        # Use section.type as section_type
        section_type = section.type

        # Auto-evaluation logic
        marks_allotted = 0
        evaluated = False
        auto_eval_types = ['mcq', 'fib', 'integer']

        if section_type.lower() in auto_eval_types:
            submitted = str(answer_text).strip().lower() if answer_text else ''
            correct_answers = getattr(question, 'correct_answers', []) or []
            correct_answers = [str(ans).strip().lower() for ans in correct_answers]

            if submitted in correct_answers:
                marks_allotted = section.marks_per_question or 0
            evaluated = True

        # Save or update the answer
        answer, created = Answer.objects.update_or_create(
            candidate_test=candidate_test,
            question_id=question_id,
            defaults={
                'section_id': section_id,
                'section_type': section_type,
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
            "evaluated": evaluated,
            "section_type": section_type,  # For frontend use
        }, status=201)


class ManualAnswerEvaluationView(APIView):
    def post(self, request):
        print("ManualAnswerEvaluationView called with:", request.data)
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
        candidate_test_id = request.GET.get('candidate_test_id')
        section_id = request.GET.get('section_id')

        if not candidate_test_id or not section_id:
            return Response({"error": "candidate_test_id and section_id are required."}, status=400)

        answers = Answer.objects.filter(candidate_test_id=candidate_test_id, section_id=section_id)

        # Fetch related questions once
        questions = Question.objects.filter(section_id=section_id)
        question_lookup = {str(q.id): q for q in questions}

        data = []
        for ans in answers:
            question = question_lookup.get(str(ans.question_id))
            question_text = question.text if question else "Unknown question"
            question_type = question.type if question else ans.section_type or "unknown"

            print(f"[DEBUG] Answer ID: {ans.id}, QID: {ans.question_id}, Type: {question_type}")

            data.append({
                "answer_id": ans.id,
                "question_id": ans.question_id,
                "question": question_text,
                "question_type": question_type,  # From Question model or fallback
                "section_id": ans.section_id,
                "answer": get_answer_json(ans),
                "marks_allotted": ans.marks_allotted,
                "evaluated": bool(ans.evaluated),
            })

        return Response(data, status=200)


# Utility function
def get_answer_json(ans):
    if ans.section_type == 'audio':
        return {"audioUrl": ans.audio_file.url if ans.audio_file else None}
    elif ans.section_type == 'video':
        return {"videoUrl": ans.video_file.url if ans.video_file else None}
    else:
        return {"text": ans.answer_text}

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
        candidate_test_id = request.query_params.get('candidate_test_id')
        if not candidate_test_id:
            return Response({"error": "candidate_test_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        screenshots = ProctoringScreenshot.objects.filter(candidate_test_id=candidate_test_id)
        serializer = ProctoringScreenshotSerializer(screenshots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TestRouteView(APIView):
    def post(self, request):
        return Response({"message": "Test route works!"})

class ListSectionsWithProgressView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        test_id = request.query_params.get("test_id")
        candidate_test_id = request.query_params.get("candidate_test_id")

        if not test_id or not candidate_test_id:
            return Response({"error": "Both test_id and candidate_test_id are required."}, status=400)

        try:
            candidate_test = Candidate_Test.objects.get(id=candidate_test_id)
        except Candidate_Test.DoesNotExist:
            return Response({"error": "Invalid candidate_test_id"}, status=404)

        sections = Section.objects.filter(test__id=test_id)
        result = []

        for section in sections:
            total_questions = section.questions.count()
            attempted_answers = Answer.objects.filter(
                candidate_test_id=candidate_test_id,
                section_id=section.id
            ).exclude(answer_text__isnull=True).exclude(answer_text="").count()

            result.append({
                "section_id": section.id,
                "section_name": section.name,
                "section_type": section.type,
                "total_questions": total_questions,
                "attempted_questions": attempted_answers
            })

        return Response(result, status=200)
