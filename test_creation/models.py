from django.db import models
import uuid
from django.conf import settings

class Test(models.Model):
    NAVIGATION_TYPE_CHOICES = [
        ('free', 'Free'),
        ('linear', 'Linear'),
        ('restricted', 'Restricted'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    total_marks = models.PositiveIntegerField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    allow_navigation = models.BooleanField(default=True)
    show_question_list = models.BooleanField(default=True)
    negative_marking = models.BooleanField(default=False)
    navigation_type = models.CharField(max_length=20, choices=NAVIGATION_TYPE_CHOICES, default='free')

    def __str__(self):
        return self.title


class Section(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order_index = models.PositiveIntegerField()
    time_limit_sec = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.test.title})"


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('MCQ', 'Multiple Choice'),
        ('subjective', 'Subjective'),
        ('code', 'Coding'),
        ('fill_in_the_blank', 'Fill in the Blank'),
        ('audio','Audio'),
        ('video', 'Video'),
        ('integer','Integer'),
    ]

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPE_CHOICES)
    options = models.JSONField(null=True, blank=True)  # Only for MCQ
    correct_answer = models.JSONField()  # JSON to support various types
    marks = models.PositiveIntegerField()
    negative_marks = models.FloatField(default=0.0)
    time_limit_sec = models.PositiveIntegerField(null=True, blank=True)
    referenced_content_id = models.IntegerField(null=True, blank=True)
    blanks = models.JSONField(null=True, blank=True)  # Only for fill in the blanks

class Option(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='option_set')
    text = models.TextField()
    is_correct = models.BooleanField(default=False) # used for auto-grading MCQs
    order_index = models.IntegerField(null=True, blank=True)# For display order, useful in Week 3

    def __str__(self):
        return f"Option for Q-{self.question.id}: {self.option_text[:30]}"

class SectionTimer(models.Model):
    session_id = models.IntegerField()
    section_id = models.IntegerField()
    remaining_time = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
