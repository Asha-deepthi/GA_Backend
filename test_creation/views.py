# test_creation/views.py
from rest_framework.permissions import AllowAny
from rest_framework import generics, permissions
from rest_framework.views import APIView , View
from rest_framework.response import Response
from .models import Test, Section, Question, Option
from users.models import Candidate
from .models import Test, Section, Question, Option, SectionTimer
from .serializers import TestSerializer, SectionSerializer, QuestionSerializer, OptionSerializer, FullTestDetailSerializer
import json
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from django.conf import settings
from django.core.cache import cache
import random
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.utils import timezone
from dateutil.parser import isoparse
#from .models import SectionTimer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Candidate_Test
from .serializers import TestAssignmentSerializer
from users.models import Candidate
from django.db import transaction
import secrets
import string
from django.contrib.auth import get_user_model

User = get_user_model()

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
    permission_classes = [AllowAny]

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

class AllSectionsListView(generics.ListAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [AllowAny]

# Question Views
class CreateQuestionView(generics.CreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# Replace it with this (CORRECTED)
class ListQuestionsBySectionView(generics.ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [AllowAny] # You might want to change this to IsAuthenticated later

    def get_queryset(self):
        # Get both IDs from the URL
        test_id = self.kwargs['test_id']
        section_id = self.kwargs['section_id']
        
        # Filter by both to ensure we only get questions from the correct section of the correct test
        return Question.objects.filter(section__test__id=test_id, section__id=section_id)

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

def fetch_section_questions(request, section_id):
    print("Request GET params:", request.GET)  # add this line to console log
    # Get session_id from query parameters
    session_id = request.GET.get('session_id')
    if not session_id:
        return JsonResponse({'error': 'Session ID is required as a query parameter'}, status=400)

    # Create a cache key using section_id and session_id
    cache_key = f"json_qns_s{section_id}_sess{session_id}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return JsonResponse(cached_data, safe=False)

    # Load JSON data
    try:
        with open(settings.BASE_DIR / 'test_creation' / 'test_questions.json') as f:
            data = json.load(f)
    except FileNotFoundError:
        return JsonResponse({'error': 'Question file not found'}, status=500)

    # Find the section with the matching ID
    section_data = next((sec for sec in data if sec.get("section_id") == section_id), None)

    if not section_data:
        return JsonResponse({'error': 'Section not found'}, status=404)

    questions = section_data.get("questions", [])

    # Shuffle questions and their options
    random.shuffle(questions)
    for question in questions:
        if "options" in question:
            random.shuffle(question["options"])

    # Prepare response data
    response_data = {
        "section_type": section_data.get("section_type", "unknown"),
        "questions": questions
    }

    # Cache the result for 1 hour
    cache.set(cache_key, response_data, timeout=60 * 60)

    return JsonResponse(response_data, safe=False)

# -# --- IN test_creation/views.py ---
# --- REPLACE your existing AssignTestToCandidateView with this ---

class AssignTestToCandidateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        candidate_email = request.data.get('candidate_email')
        test_id = request.data.get('test_id')

        if not candidate_email or not test_id:
            return Response({"error": "candidate_email and test_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=candidate_email, role='CANDIDATE')
            test = Test.objects.get(id=test_id)

            if test.created_by != request.user:
                return Response({"error": "You can only assign tests that you have created."}, status=status.HTTP_403_FORBIDDEN)

            # --- THIS IS THE FINAL FIX ---
            # Instead of guessing the reverse relationship name, we will query for the
            # Candidate profile directly. This is the most robust way.
            candidate_profile = Candidate.objects.get(user=user)
            
            assignment, created = Candidate_Test.objects.get_or_create(
                candidate=candidate_profile,
                test=test
            )

            if not created:
                return Response(
                    {"error": f"Candidate {candidate_email} is already assigned to this test."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            response_serializer = TestAssignmentSerializer(assignment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        # This will now correctly catch if the Candidate profile is missing
        except Candidate.DoesNotExist:
            return Response({
                "error": f"Data Integrity Error: User '{candidate_email}' exists but has no Candidate Profile. Please re-create this candidate."
            }, status=status.HTTP_409_CONFLICT)

        except User.DoesNotExist:
             return Response({"error": f"No candidate user found with email {candidate_email}."}, status=status.HTTP_404_NOT_FOUND)
        
        except Test.DoesNotExist:
            return Response({"error": f"No test found with id {test_id}."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": f"An unexpected server error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetTimerView(View):
    def get(self, request, *args, **kwargs):
        try:
            candidate_test_id = request.GET.get('candidate_test_id')
            section_id = int(request.GET.get('section_id'))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'candidate_test_id and section_id must be valid.'}, status=400)

        try:
            # Try fetching existing timer
            timer = SectionTimer.objects.filter(
                candidate_test_id=candidate_test_id,
                section_id=section_id
            ).first()

            if timer:
                return JsonResponse({'remaining_time': timer.remaining_time})

            # If timer doesn't exist, fetch section's default time
            section = Section.objects.get(id=section_id)

            if section.time_limit:
                if isinstance(section.time_limit, str) and ':' in section.time_limit:
                    try:
                        mins, secs = map(int, section.time_limit.split(":"))
                        default_seconds = mins * 60 + secs
                    except Exception:
                        default_seconds = 30 * 60  # fallback to 30 min
                else:
                    try:
                        default_seconds = int(section.time_limit) * 60
                    except Exception:
                        default_seconds = 30 * 60
            else:
                default_seconds = 30 * 60

            return JsonResponse({'remaining_time': default_seconds})

        except Section.DoesNotExist:
            return JsonResponse({'error': 'Section not found'}, status=404)
        except Exception as e:
            print("❌ Unexpected error in GetTimerView:", e)
            return JsonResponse({'error': 'Internal server error'}, status=500)

# --- Your SaveTimerView was mostly correct, but needs to be a separate class ---
@method_decorator(csrf_exempt, name='dispatch')
class SaveTimerView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            candidate_test_id = data.get('candidate_test_id')
            section_id = data.get('section_id')
            remaining_time = data.get('remaining_time')

            if candidate_test_id is None or section_id is None or remaining_time is None:
                return JsonResponse({'error': 'candidate_test_id, section_id, and remaining_time are required.'}, status=400)

            SectionTimer.objects.update_or_create(
                candidate_test_id=candidate_test_id,
                section_id=section_id,
                defaults={'remaining_time': remaining_time}
            )
            return JsonResponse({'status': 'success'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print("❌ Error in SaveTimerView:", e)
            return JsonResponse({'error': 'Internal server error'}, status=500)

# In test_creation/views.py

class FullTestCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        details_data = data.get('details', {})
        settings_data = data.get('settings', {})
        sections_data = data.get('sections', [])

        try:
            test = Test.objects.create(
                created_by=user,
                title=details_data.get('title'),
                level=details_data.get('level'),
                description=details_data.get('description'),
                duration=details_data.get('duration'),
                tags=details_data.get('tags'),
                passing_percentage=settings_data.get('passingPercentage'),
                scoring_type=settings_data.get('scoring'),
                negative_marking_type=settings_data.get('negativeMarking'),
                allow_back_navigation=settings_data.get('backNavigation', False),
                results_display_type=settings_data.get('results'),
                attempts_type=settings_data.get('attempts'),
                number_of_attempts=settings_data.get('numberOfAttempts') if settings_data.get('attempts') == 'limited' else None,
            )
        except Exception as e:
            return Response({"error": f"Failed to create test: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        for section_data in sections_data:
            is_negative_marking_enabled = test.negative_marking_type == 'negative_marking'
            cleaned_negative_marks = None
            if is_negative_marking_enabled:
                nm_value = section_data.get('negativeMarks')
                cleaned_negative_marks = 0 if nm_value in (None, '') else nm_value
            
            section = Section.objects.create(
                test=test, 
                created_by=user,
                name=section_data.get('name'),
                type=section_data.get('type'),
                time_limit=section_data.get('timeLimit'),
                num_questions=section_data.get('numQuestions'),
                marks_per_question=section_data.get('marksPerQuestion'),
                max_marks=section_data.get('maxMarks'),
                min_marks=section_data.get('minMarks'),
                negative_marks=cleaned_negative_marks,
                shuffle_questions=section_data.get('shuffleQuestions', False),
                shuffle_answers=section_data.get('shuffleAnswers', False),
                instructions=section_data.get('instructions'),
            )

            for q_data in section_data.get('questions', []):
                question_type = q_data.get('type')

                if question_type == 'Paragraph':
                    parent_question = Question.objects.create(
                        section=section,
                        created_by=user,
                        type='Paragraph',
                        text='Read the following passage and answer the questions.',
                        paragraph_content=q_data.get('paragraph')
                    )
                    
                    for sub_q_data in q_data.get('subQuestions', []):
                        sub_question_type = sub_q_data.get('type')
                        sub_correct_answer = None
                        sub_audio_time = None
                        sub_video_time = None

                        # This `if/elif` block now handles all sub-question types
                        if sub_question_type == 'Multiple Choice':
                            correct_options = [opt.get('text') for opt in sub_q_data.get('options', []) if opt.get('isCorrect')]
                            if correct_options:
                                sub_correct_answer = ','.join(correct_options)
                        elif sub_question_type in ['Fill in the blank', 'Subjective']:
                            sub_correct_answer = sub_q_data.get('correctAnswer')
                        elif sub_question_type == 'Audio based':
                            sub_audio_time = sub_q_data.get('mediaTime', 60)
                        elif sub_question_type == 'Video based':
                            sub_video_time = sub_q_data.get('mediaTime', 60)

                        sub_question = Question.objects.create(
                            section=section,
                            parent_question=parent_question,
                            created_by=user,
                            type=sub_question_type,
                            text=sub_q_data.get('text'),
                            correct_answer=sub_correct_answer,
                            allow_multiple=sub_q_data.get('allowMultiple', False),
                           # This is the new, correct block for sub-questions

                            audio_time=sub_audio_time if sub_audio_time is not None else 60,
                            video_time=sub_video_time if sub_video_time is not None else 60
)

                        if sub_question_type == 'Multiple Choice':
                            for opt_data in sub_q_data.get('options', []):
                                Option.objects.create(
                                    question=sub_question,
                                    text=opt_data.get('text'),
                                    is_correct=opt_data.get('isCorrect', False)
                                )
                
                else: # Handles all non-paragraph questions
                    question = Question.objects.create(
                        section=section,
                        created_by=user,
                        type=q_data.get('type'),
                        text=q_data.get('text'),
                        allow_multiple=q_data.get('allowMultiple', False),
                        video_time=q_data.get('mediaTime', 60),
                         audio_time=q_data.get('mediaTime', 60),
                        correct_answer=q_data.get('correctAnswer')
                    )

                    if question_type == 'Multiple Choice':
                        for opt_data in q_data.get('answers', []):
                            Option.objects.create(
                                question=question,
                                text=opt_data.get('text'),
                                weightage=opt_data.get('weightage', ''),
                                is_correct=opt_data.get('isCorrect', False)
                            )
        
        return Response({"message": "Test created successfully!", "test_id": test.id}, status=status.HTTP_201_CREATED)

class CreateCandidateUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        name = request.data.get('name')
        phone = request.data.get('phone')

        if not email or not name:
            return Response({"error": "Email and Name are required."}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"error": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create a user with no password yet.
            user = User.objects.create_user(
                email=email, 
                phone=phone,
                role='CANDIDATE',
                is_active=False # User is inactive until invitation is sent
            )
            Candidate.objects.create(user=user, name=name)
            return Response({"message": f"Candidate '{name}' created and ready for invitation."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            User.objects.filter(email=email).delete()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# This view gets the list of candidates for the SendInvitations page.
class ListAssignedCandidatesView(generics.ListAPIView):
    serializer_class = TestAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        test_id = self.kwargs['test_id']
        # Prefetch related data to optimize database queries
        return Candidate_Test.objects.filter(test_id=test_id).select_related('candidate__user', 'test')
      
class SendInvitationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        test_id = request.data.get('test_id')
        message_body = request.data.get('message', 'You have been invited to take an online assessment.')
        expiry_date_str = request.data.get('expiry_date')

        if not test_id or not expiry_date_str:
            return Response({"error": "Test ID and expiry_date are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            expiry_date_obj = isoparse(expiry_date_str)
        except ValueError:
            return Response({"error": "Invalid expiry_date format. Please use ISO 8601 format."}, status=status.HTTP_400_BAD_REQUEST)

        assignments = Candidate_Test.objects.filter(test_id=test_id, status='PENDING')
        if not assignments:
            return Response({"message": "All assigned candidates have already been invited."}, status=status.HTTP_200_OK)

        sent_count = 0
        for assignment in assignments:
            user = assignment.candidate.user
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(10))
            user.set_password(password)
            user.is_active = True
            user.save()

            print(f"--- SENDING INVITE TO: {user.email}, PASSWORD: {password} ---")
            
            login_link = f"{settings.FRONTEND_URL}/login?testId={assignment.test.id}"
            
            try:
                send_mail(
                    subject=f"Invitation to take the {assignment.test.title} Assessment",
                    message=(
                        f"Hello {assignment.candidate.name},\n\n"
                        f"{message_body}\n\n"
                        f"Please use the following credentials to log in to our platform.\n\n"
                        f"Username: {user.email}\n"
                        f"Password: {password}\n\n"
                        f"Click here to proceed:\n{login_link}\n"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )
                
                assignment.status = 'SENT'
                assignment.date_invited = timezone.now()
                assignment.expiry_date = expiry_date_obj
                assignment.save()
                sent_count += 1
            except Exception as e:
                print(f"Failed to send email to {user.email}: {e}")
                # Don't update status if email fails, so admin can try again
                continue

        return Response({"message": f"{sent_count} invitation(s) sent successfully."}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_candidate_test_id(request):
    candidate_id = request.GET.get("candidate_id")
    test_id = request.GET.get("test_id")

    try:
        ct = Candidate_Test.objects.get(candidate_id=candidate_id, test_id=test_id)
        test = ct.test
        return Response({
            "id": ct.id,
            "sections": [
                {
                    "id": s.id,
                    "name": s.name,
                    "time_limit": s.time_limit,
                }
                for s in test.sections.all()
            ],
        })
    except Candidate_Test.DoesNotExist:
        return Response({"detail": "Candidate_Test not found"}, status=404)
    
class ValidateTestAttemptView(APIView):
    """
    Checks if the currently logged-in candidate's attempt for a specific
    test is still valid (i.e., not expired or completed).
    This is called by the "Accept" button on the Welcome Page.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        test_id = request.data.get('test_id')

        if not test_id:
            return Response({"error": "A test_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.role != 'CANDIDATE':
            return Response({"error": "This action is only for candidates."}, status=status.HTTP_403_FORBIDDEN)

        try:
            # Find the specific assignment for THIS user and THIS test
            assignment = Candidate_Test.objects.get(candidate__user=user, test_id=test_id)
        except Candidate_Test.DoesNotExist:
            return Response({"error": "You are not assigned to this test."}, status=status.HTTP_404_NOT_FOUND)

        # The Expiry Check
        if assignment.status == 'COMPLETED':
            return Response({"error": "You have already completed this test."}, status=status.HTTP_403_FORBIDDEN)

        if assignment.expiry_date and timezone.now() > assignment.expiry_date:
            assignment.status = 'EXPIRED'
            assignment.save()
            return Response({
                "error": f"Your access to this test expired on {assignment.expiry_date.strftime('%B %d, %Y')}"
            }, status=status.HTTP_403_FORBIDDEN)

        # If all checks pass, the candidate can proceed.
        return Response({"message": "Validation successful. You may proceed."}, status=status.HTTP_200_OK)
    
class FullTestDetailView(generics.RetrieveAPIView):
    """
    Provides a complete, nested representation of a test,
    including all sections, questions, and options, formatted
    for direct use by the frontend for importing.
    """
    # Use prefetch_related to efficiently get all related data in fewer database queries.
    queryset = Test.objects.prefetch_related(
        'sections__questions__options'
    ).all()
    serializer_class = FullTestDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'test_id'


# --- IN test_creation/views.py ---
# --- REPLACE your existing ImportCandidatesFromTestView with this ---

class ImportCandidatesFromTestView(APIView):
    """
    Imports all assigned candidates from a source test to a destination test.
    """
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        destination_test_id = kwargs.get('test_id')
        source_test_id = request.data.get('source_test_id')
        
        if not destination_test_id:
            return Response({"error": "Destination test ID not found in URL."}, status=status.HTTP_400_BAD_REQUEST)

        if not source_test_id:
            return Response({"error": "A 'source_test_id' is required in the request body."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            destination_test = Test.objects.get(id=destination_test_id, created_by=request.user)
            source_assignments = Candidate_Test.objects.filter(test_id=source_test_id)

            if not source_assignments.exists():
                return Response({"message": "The selected source test has no candidates to import."}, status=status.HTTP_200_OK)

            newly_added_count = 0
            already_assigned_count = 0

            for assignment in source_assignments:
                candidate = assignment.candidate
                _, created = Candidate_Test.objects.get_or_create(
                    candidate=candidate,
                    test=destination_test
                )
                if created:
                    newly_added_count += 1
                else:
                    already_assigned_count += 1
            
            return Response({
                "message": f"Import complete. Added {newly_added_count} new candidates. {already_assigned_count} candidates were already assigned."
            }, status=status.HTTP_200_OK)

        except Test.DoesNotExist:
            return Response({"error": "Destination test not found or you do not have permission to modify it."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": "An unexpected server error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)