from django.db import models
from test_creation.models import Test, Question, Section
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class BasicDetails(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)

    submitted_at = models.DateTimeField(auto_now_add=True)  # Optional: timestamp

    def __str__(self):
        return f"{self.name} - {self.email}"

class DemoQuestion(models.Model):
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('audio', 'Audio Response'),
        ('video', 'Video Response'),
        ('coding', 'Coding Question'),
    ]

    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    options = models.JSONField(blank=True, null=True)  # Only used for MCQ
    is_demo = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question_type.upper()} - {self.question_text[:50]}"

class TestSession(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('submitted', 'Submitted'),
        ('flagged', 'Flagged'),
    ]

    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'candidate'})
    join_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ongoing')
    score = models.FloatField(null=True, blank=True)

class Answer(models.Model):
    # Temporarily using IntegerFields instead of ForeignKeys
    session_id = models.IntegerField(null=True, blank=True)  # Temporary substitute for ForeignKey to TestSession
    section_id = models.IntegerField(null=True, blank=True)
    question_id = models.IntegerField(null=True, blank=True)  # Temporary substitute for ForeignKey to Question
    question_type=models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)

    # Supports all types
    answer_text = models.TextField(null=True, blank=True)
    audio_file = models.FileField(upload_to='audio_answers/', null=True, blank=True)
    video_file = models.FileField(upload_to='video_answers/', null=True, blank=True)

    # New field
    marked_for_review = models.BooleanField(default=False)

    submitted_at = models.DateTimeField(auto_now_add=True)

    def is_answered(self):
        return bool(self.answer_text or self.audio_file or self.video_file)

    def is_valid_for_evaluation(self):
        return self.is_answered()

    def __str__(self):
        return f"Answer to Q{self.question_id} by Session {self.session_id}"

class ProctoringLog(models.Model):
    EVENT_TYPE_CHOICES = [
        ('face_not_detected', 'Face Not Detected'),
        ('noise', 'Noise'),
        ('multiple_people', 'Multiple People'),
        ('tab_switch', 'Tab Switch'),
        ('fullscreen_exit', 'Fullscreen Exit'),
        ('WindowBlur', 'Window Blur'),
    ]

    session_id = models.IntegerField(null=True, blank=True)  # Temporary substitute for ForeignKey to TestSession
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    confidence = models.FloatField()
    remarks = models.TextField(null=True, blank=True)

class ProctorComment(models.Model):
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE)
    proctor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'proctor'})
    timestamp = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()

class PageContent(models.Model):
    title = models.CharField(max_length=255)
    content_body = models.TextField()  # HTML/Markdown
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'admin'})
    created_at = models.DateTimeField(auto_now_add=True)

class AudioResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    audio_file = models.FileField(upload_to='audio_responses/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AudioResponse by {self.user.username} at {self.uploaded_at}"

#for candidates who login using token

#class AudioResponse(models.Model):
    #user = models.ForeignKey(User, on_delete=models.CASCADE)
    #question = models.ForeignKey(Question, on_delete=models.CASCADE)
    #audio_file = models.FileField(upload_to='audio_responses/')
    #timestamp = models.DateTimeField(auto_now_add=True)

    #def __str__(self):
        #return f"{self.user.username} - {self.timestamp}"

class VideoResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    #question = models.ForeignKey(Question, on_delete=models.CASCADE)
    video = models.FileField(upload_to='video_responses/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"VideoResponse by {self.user.username} at {self.created_at}"

class DemoAudioResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    demo_audio_file = models.FileField(upload_to='demo_audio_responses/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DemoAudioResponse by {self.user.username} at {self.uploaded_at}"
