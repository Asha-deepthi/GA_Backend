# test_creation/models.py (UPDATED)
from django.db import models
import uuid
from django.conf import settings
from users.models import Candidate
# Note: Your Candidate_Test and other models are fine and remain unchanged.

class Test(models.Model):
    # --- Fields from QuizDetailsForm.jsx ---
    title = models.CharField(max_length=255)
    level = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True, help_text="Total duration in minutes")
    tags = models.CharField(max_length=255, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # --- Fields from QuizSettings.jsx ---
    passing_percentage = models.PositiveIntegerField(null=True, blank=True)
    scoring_type = models.CharField(max_length=50, default='per_question') # 'per_question' or 'per_section'
    negative_marking_type = models.CharField(max_length=50, default='no_negative_marking') # 'no_negative_marking' or 'negative_marking'
    allow_back_navigation = models.BooleanField(default=False)
    results_display_type = models.CharField(max_length=50, default='immediately') # 'immediately' or 'later'
    attempts_type = models.CharField(max_length=50, default='unlimited') # 'unlimited' or 'limited'
    number_of_attempts = models.PositiveIntegerField(null=True, blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title

class Section(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="sections")
    
    # --- Fields from SectionSetupPage.jsx ---
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100, help_text="e.g., mcq, fib, audio, video, paragraph")
    time_limit = models.CharField(max_length=20, blank=True, help_text="e.g., 00:00:00",default=30)
    num_questions = models.PositiveIntegerField(null=True, blank=True)
    marks_per_question = models.FloatField(null=True, blank=True)
    max_marks = models.FloatField(null=True, blank=True)
    min_marks = models.FloatField(null=True, blank=True)
    negative_marks = models.FloatField(null=True, blank=True)
    shuffle_questions = models.BooleanField(default=False)
    shuffle_answers = models.BooleanField(default=False)
    instructions = models.TextField(blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="questions")
    parent_question = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="sub_questions")

    # --- Fields from CreateQuestionsPage.jsx ---
    type = models.CharField(max_length=50)
    text = models.TextField(help_text="The prompt or question text")
    allow_multiple = models.BooleanField(default=False, help_text="For MCQ, allow multiple correct answers")
    paragraph_content = models.TextField(blank=True, null=True)
    fib_answer = models.CharField(max_length=255, blank=True, null=True) # For fill-in-the-blank
    video_time = models.PositiveIntegerField(default=60, help_text="Max seconds for video")
    audio_time = models.PositiveIntegerField(default=60, help_text="Max seconds for audio")
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.text[:50]

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    
    # --- Fields from AnswerOption component ---
    text = models.TextField()
    weightage = models.CharField(max_length=50, blank=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Option for Q{self.question.id}: {self.text[:30]}"
    
class Candidate_Test(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="Unique ID for the test invitation link.")
    
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="test_assignments")
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="assignments")
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'), # <-- NEW DEFAULT
        ('SENT', 'Sent'),
        ('STARTED', 'Started'),
        ('COMPLETED', 'Completed'),
    ]
    # Set the default status to 'PENDING'
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    # --- END OF CHANGE ---
    score = models.FloatField(null=True, blank=True)
    date_invited = models.DateTimeField(null=True, blank=True) # Changed to allow null initially
    is_submitted = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('candidate', 'test')

    def __str__(self):
        return f"{self.candidate.name} assigned to {self.test.title}"

class SectionTimer(models.Model):
    candidate_test = models.ForeignKey(
        Candidate_Test, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name="timers"
    )
    section = models.ForeignKey(
        Section, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    remaining_time = models.IntegerField()

    def __str__(self):
        return f"Timer - CandidateTest {self.candidate_test_id}, Section {self.section_id}"
