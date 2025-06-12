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

class AnswerSubmissionView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        print("AnswerSubmissionView POST called with data:", request.data)

        session_id = request.data.get('session_id')
        section_id = request.data.get('section_id')
        question_id = request.data.get('question_id')
        answer_text = request.data.get('answer_text')
        marked_for_review = request.data.get('marked_for_review', 'false').lower() == 'true'
        status = request.data.get('status') or 'unanswered'

        

        # Fetch from DB
        try:
            question = Question.objects.get(id=question_id)
            section = Section.objects.get(id=section_id)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=404)
        except Section.DoesNotExist:
            return Response({"error": "Section not found"}, status=404)
        
        question_type = request.data.get('question_type')
        if not question_type or question_type == "undefined":
          question_type = question.type

        # Auto-evaluation logic
        marks_allotted = 0
        evaluated = False

        auto_eval_types = ['multiple-choice', 'fill-in-blanks', 'integer']

        if question_type.lower() in auto_eval_types:
            submitted = str(answer_text).strip().lower() if answer_text else ''
            correct_answers = question.correct_answers or []

            # Normalize correct answers
            correct_answers = [str(ans).strip().lower() for ans in correct_answers]

            if submitted in correct_answers:
                marks_allotted = section.marks_per_question or 0
            evaluated = True

        # Save or update the answer
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
            "evaluated": evaluated,
            "question_type": question.type  #  Include this explicitly for frontend
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
        session_id = request.GET.get('session_id')
        section_id = request.GET.get('section_id')

        if not session_id or not section_id:
            return Response({"error": "session_id and section_id are required."}, status=400)

        answers = Answer.objects.filter(session_id=session_id, section_id=section_id)

        # Fetch related questions once
        questions = Question.objects.filter(section_id=section_id)
        question_lookup = {str(q.id): q for q in questions}

        data = []
        for ans in answers:
            question = question_lookup.get(str(ans.question_id))
            question_text = question.text if question else "Unknown question"
            question_type = question.type if question else ans.question_type or "unknown"

            print(f"[DEBUG] Answer ID: {ans.id}, QID: {ans.question_id}, Type: {question_type}")

            data.append({
                "answer_id": ans.id,
                "question_id": ans.question_id,
                "question": question_text,
                "question_type": question_type,  # ✅ use from Question model
                "section_id": ans.section_id,
                "answer": get_answer_json(ans),
                "marks_allotted": ans.marks_allotted,
                "evaluated": bool(ans.evaluated),
            })

        return Response(data, status=200)


# Utility function
def get_answer_json(ans):
    if ans.question_type == 'audio':
        return {"audioUrl": ans.audio_file.url if ans.audio_file else None}
    elif ans.question_type == 'video':
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
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({"error": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        screenshots = ProctoringScreenshot.objects.filter(session=session_id)
        serializer = ProctoringScreenshotSerializer(screenshots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TestRouteView(APIView):
    def post(self, request):
        return Response({"message": "Test route works!"})