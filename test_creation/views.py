# test_creation/views.py
from rest_framework.permissions import AllowAny
from rest_framework import generics, permissions
from rest_framework.views import APIView , View
from rest_framework.response import Response
from .models import Test, Section, Question, Option
from users.models import Candidate
from .models import Test, Section, Question, Option, SectionTimer
from .serializers import TestSerializer, SectionSerializer, QuestionSerializer, OptionSerializer
import json
from rest_framework import status
from django.http import JsonResponse
from django.conf import settings
from django.core.cache import cache
import random
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.utils import timezone
from dateutil.parser import isoparse
#from .models import SectionTimer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Test,Candidate_Test
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

# test_creation/views.py

# --- FIX 1: AssignTestToCandidateView is now a clean, separate class. ---
# Its only job is to assign a test. All timer logic has been removed.
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
            # Step 1: Fetch the user and test objects.
            user = User.objects.get(email=candidate_email, role='CANDIDATE')
            test = Test.objects.get(id=test_id)

            # --- FIX 2: All logic using 'user' and 'test' is now INSIDE the 'try' block. ---
            # This guarantees they exist and prevents the NameError.
            
            # Optional: Check if the admin owns the test they are assigning
            if test.created_by != request.user:
                return Response({"error": "You can only assign tests that you have created."}, status=status.HTTP_403_FORBIDDEN)

            # Get the candidate profile associated with the user
            candidate_profile = user.candidate_profile
            
            # Create the assignment using get_or_create
            assignment, created = Candidate_Test.objects.get_or_create(
                candidate=candidate_profile,
                test=test
            )

            if not created:
                return Response(
                    {"error": f"Candidate {candidate_email} is already assigned to this test."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Serialize the new assignment for a clean response
            response_serializer = TestAssignmentSerializer(assignment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        # Step 2: Handle specific "not found" errors.
        except User.DoesNotExist:
            return Response({"error": f"No candidate user found with email {candidate_email}."}, status=status.HTTP_404_NOT_FOUND)
        except Test.DoesNotExist:
            return Response({"error": f"No test found with id {test_id}."}, status=status.HTTP_404_NOT_FOUND)
        except Candidate.DoesNotExist:
            return Response({"error": f"A profile for the user {candidate_email} does not exist."}, status=404)
        except Exception as e:
            # Catch any other unexpected database errors.
            return Response({"error": f"An unexpected error occurred during assignment: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- FIX 3: GetTimerView is now its own class with the correct logic. ---
class GetTimerView(View):
    def get(self, request, *args, **kwargs):
        try:
            # These were undefined in your original code, causing a NameError
            session_id = int(request.GET.get('session_id'))
            section_id = int(request.GET.get('section_id'))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'session_id and section_id are required and must be numbers.'}, status=400)

        try:
            timer = SectionTimer.objects.get(session_id=session_id, section_id=section_id)
            return JsonResponse({'remaining_time': timer.remaining_time})
        except SectionTimer.DoesNotExist:
            try:
                # Fetch default from Section model if no timer exists
                section = Section.objects.get(id=section_id)
                # default to 60 mins (3600s) if time_limit is not set
                default_time = (section.time_limit or 60) * 60  
                return JsonResponse({'remaining_time': default_time})
            except Section.DoesNotExist:
                return JsonResponse({'error': 'Section not found'}, status=404)


# --- Your SaveTimerView was mostly correct, but needs to be a separate class ---
@method_decorator(csrf_exempt, name='dispatch')
class SaveTimerView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            section_id = data.get('section_id')
            remaining_time = data.get('remaining_time')
            
            if session_id is None or section_id is None or remaining_time is None:
                return JsonResponse({'error': 'session_id, section_id, and remaining_time are required.'}, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Your logic for saving the timer would go here. For example:
        SectionTimer.objects.update_or_create(
            session_id=session_id,
            section_id=section_id,
            defaults={'remaining_time': remaining_time}
        )
        return JsonResponse({'status': 'success'}, status=200)

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
            # 1. Create the Test with details and settings (This part is unchanged)
            test = Test.objects.create(
                created_by=user,
                title=details_data.get('title'),
                level=details_data.get('level'),
                description=details_data.get('description'),
                duration=details_data.get('duration'),
                tags=details_data.get('tags'),
                start_date=details_data.get('startDate'),
                end_date=details_data.get('endDate'),
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

        # 2. Create Sections, Questions, and Options
        for section_data in sections_data:
            
            # --- START OF THE FIX ---
            # Get the global setting from the Test object we just created.
            is_negative_marking_enabled = test.negative_marking_type == 'negative_marking'
            
            cleaned_negative_marks = None # Default to None (null in the database)

            if is_negative_marking_enabled:
                # If enabled, get the value. Default to 0 if it's missing or an empty string.
                nm_value = section_data.get('negativeMarks')
                if nm_value in (None, ''):
                    cleaned_negative_marks = 0
                else:
                    cleaned_negative_marks = nm_value
            # If negative marking is NOT enabled, `cleaned_negative_marks` will remain None.
            # This correctly ignores any value sent from the frontend when the setting is off.
            
            # --- END OF THE FIX ---

            section = Section.objects.create(
                test=test, created_by=user,
                name=section_data.get('name'),
                type=section_data.get('type'),
                time_limit=section_data.get('timeLimit'),
                num_questions=section_data.get('numQuestions'),
                marks_per_question=section_data.get('marksPerQuestion'),
                max_marks=section_data.get('maxMarks'),
                min_marks=section_data.get('minMarks'),
                # Use our new, cleaned variable here.
                negative_marks=cleaned_negative_marks,
                shuffle_questions=section_data.get('shuffleQuestions', False),
                shuffle_answers=section_data.get('shuffleAnswers', False),
                instructions=section_data.get('instructions'),
            )
            # =================== START: PASTE THE NEW, CORRECTED CODE HERE ===================
            # This loop now correctly handles all question types and their specific issues.
            for q_data in section_data.get('questions', []):
                question_type = q_data.get('type')

                # --- Section for PARAGRAPH questions ---
                if question_type == 'paragraph':
                    # FIX #1: Correctly save BOTH the default text and the paragraph content.
                    parent_question = Question.objects.create(
                        section=section,
                        created_by=user,
                        type='paragraph',
                        text='Read the following passage and answer the questions that follow.',
                        paragraph_content=q_data.get('paragraph') # This was the missing line.
                    )
                    
                    # Loop through the sub-questions.
                    for sub_q_data in q_data.get('subQuestions', []):
                        sub_question_type = sub_q_data.get('type')
                        sub_fib_answer = None

                        # FIX #2 (for sub-questions): Handle multiple correct answers.
                        if sub_question_type == 'mcq':
                            correct_options = [opt.get('text') for opt in sub_q_data.get('options', []) if opt.get('isCorrect')]
                            if correct_options:
                                sub_fib_answer = '|'.join(correct_options) # Join multiple answers with '|||'
                        elif sub_question_type == 'fib':
                            sub_fib_answer = sub_q_data.get('correctAnswer')

                        # Create the sub-question object.
                        sub_question = Question.objects.create(
                            section=section,
                            parent_question=parent_question,
                            created_by=user,
                            type=sub_question_type,
                            text=sub_q_data.get('text'),
                            fib_answer=sub_fib_answer,
                            allow_multiple=sub_q_data.get('allowMultiple', False)
                        )

                        # This part to save options for sub-questions is correct.
                        if sub_question_type == 'mcq':
                            for opt_data in sub_q_data.get('options', []):
                                Option.objects.create(
                                    question=sub_question,
                                    text=opt_data.get('text'),
                                    is_correct=opt_data.get('isCorrect', False)
                                )
                
                # --- Section for ALL OTHER question types (MCQ, FIB, etc.) ---
                else:
                    fib_answer_value = None
                    # FIX #2 (for main questions): Handle multiple correct answers.
                    if question_type == 'mcq':
                        correct_answers = [opt.get('text') for opt in q_data.get('answers', []) if opt.get('isCorrect')]
                        if correct_answers:
                            fib_answer_value = '|'.join(correct_answers) # Join multiple answers with '|||'
                    elif question_type == 'fib':
                        fib_answer_value = q_data.get('fib_answer')

                    # Create the main question object with all fixes.
                    question = Question.objects.create(
                        section=section,
                        created_by=user,
                        type=question_type,
                        text=q_data.get('text'),
                        video_time=q_data.get('videoTime'),
                        audio_time=q_data.get('audioTime'),
                        fib_answer=fib_answer_value,
                        # FIX #3: Correctly save the 'allow_multiple' boolean value.
                        allow_multiple=q_data.get('allowMultiple', False)
                    )

                    # This part for creating options for main MCQs is correct.
                    if question_type == 'mcq':
                        for opt_data in q_data.get('answers', []):
                            Option.objects.create(
                                question=question,
                                text=opt_data.get('text'),
                                weightage=opt_data.get('weightage', ''),
                                is_correct=opt_data.get('isCorrect', False)
                            )
            # =================== END: OF THE PASTED CODE ===================
        return Response({"message": "Test created successfully!", "test_id": test.id}, status=status.HTTP_201_CREATED)
    
# --- ADD THIS ENTIRE NEW VIEW CLASS AT THE END OF THE FILE ---
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
    
class CandidateTestStartView(APIView):
    """
    View for a logged-in candidate to start their assigned test.
    This view performs critical checks before returning test data.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, assignment_id, *args, **kwargs):
        # The user must be a candidate to take a test
        if request.user.role != 'CANDIDATE':
            return Response({"error": "Only candidates can take tests."}, status=status.HTTP_403_FORBIDDEN)

        try:
            # Step 1: Get the specific test assignment for this candidate
            # This ensures a candidate can only access their own assigned test.
            assignment = Candidate_Test.objects.get(id=assignment_id, candidate__user=request.user)

        except Candidate_Test.DoesNotExist:
            return Response({"error": "Test assignment not found or you are not authorized."}, status=status.HTTP_404_NOT_FOUND)

        # Step 2: Check the assignment status first
        if assignment.status == 'COMPLETED':
            return Response({"error": "You have already completed this test."}, status=status.HTTP_403_FORBIDDEN)
        
        if assignment.status == 'EXPIRED':
            return Response({"error": "This test link has expired."}, status=status.HTTP_403_FORBIDDEN)

        # Step 3: *** THE CRUCIAL EXPIRY CHECK ***
        # Check if an expiry date is set AND if the current time is past it.
        if assignment.expiry_date and timezone.now() > assignment.expiry_date:
            # The link has expired. Update the status and block access.
            assignment.status = 'EXPIRED'
            assignment.save()
            return Response({
                "error": f"This test link expired on {assignment.expiry_date.strftime('%B %d, %Y at %I:%M %p')}."
            }, status=status.HTTP_403_FORBIDDEN)

        # Step 4: If all checks pass, mark the test as 'STARTED'
        # This is a good practice to prevent re-entry and track progress.
        if assignment.status not in ['STARTED', 'COMPLETED']:
            assignment.status = 'STARTED'
            assignment.save()

        # Step 5: Success! Return the full test data.
        # The frontend will now receive this data and render the test page.
        test_data = TestSerializer(assignment.test).data
        return Response(test_data, status=status.HTTP_200_OK)