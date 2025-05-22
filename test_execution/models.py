from django.db import models
from test_creation.models import Test, Question, Section
from django.contrib.auth import get_user_model

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
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_content = models.JSONField()  # Can be text or structured JSON depending on question_type
    is_correct = models.BooleanField(null=True, blank=True)
    marks_awarded = models.FloatField(null=True, blank=True)

class ProctoringLog(models.Model):
    EVENT_TYPE_CHOICES = [
        ('face_not_detected', 'Face Not Detected'),
        ('noise', 'Noise'),
        ('multiple_people', 'Multiple People'),
        ('tab_switch', 'Tab Switch'),
    ]

    session = models.ForeignKey(TestSession, on_delete=models.CASCADE)
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
    #audio_file = models.FileField(upload_to='audio_responses/')
    #timestamp = models.DateTimeField(auto_now_add=True)

    #def __str__(self):
        #return f"{self.user.username} - {self.timestamp}"
