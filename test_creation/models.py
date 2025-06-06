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
    #start_time = models.DateTimeField()
    #duration_minutes = models.PositiveIntegerField()
    #total_marks = models.PositiveIntegerField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #allow_navigation = models.BooleanField(default=True)
    #show_question_list = models.BooleanField(default=True)
    #negative_marking = models.BooleanField(default=False)
    #navigation_type = models.CharField(max_length=20, choices=NAVIGATION_TYPE_CHOICES, default='free')

    def __str__(self):
        return self.title

class Section(models.Model):
    section_name = models.CharField(max_length=255)
    section_type = models.CharField(max_length=100, null=True, help_text="e.g., technical, aptitude")
    question_type = models.CharField(max_length=100, help_text="Only one type per section (e.g., text, mcq, fill-in-blanks, passage)", default="text" )
    time_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Time in minutes")
    marks_per_question = models.FloatField(null=True, blank=True)
    max_marks = models.FloatField(null=True, blank=True)
    min_marks = models.FloatField(null=True, blank=True)
    negative_marks = models.FloatField(null=True, blank=True)
    interview_duration = models.PositiveIntegerField(null=True, blank=True)

    tags = models.CharField(max_length=255, blank=True, null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey("Test", on_delete=models.CASCADE, related_name="sections")

    def __str__(self):
        return self.section_name

class Question(models.Model):
    QUESTION_TYPES = [
        ("text", "Text"),
        ("multiple-choice", "Multiple Choice"),
        ("fill-in-blanks", "Fill in the Blanks"),
        ("passage", "Passage"),
        ("video", "Video Response"),
        ("audio", "Audio Response"),
    ]

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="questions")
    parent_question = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name="sub_questions", help_text="Used for passage sub-questions"
    )
    type = models.CharField(max_length=50, choices=QUESTION_TYPES)
    text = models.TextField(help_text="The prompt or question text")
    direction = models.CharField(max_length=100, blank=True)
    correct_answers = models.JSONField(blank=True, null=True, help_text="List of correct answers for single or multi-answer")
    passage_text = models.TextField(blank=True, null=True)
    
    video_time = models.PositiveIntegerField(default=60, help_text="Max seconds allowed for video response")
    audio_time = models.PositiveIntegerField(default=60, help_text="Max seconds allowed for audio response")

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.text[:50]

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.TextField()
    order_index = models.IntegerField(null=True, blank=True)
    is_correct = models.BooleanField(default=False)  # marks if this option is correct

    def __str__(self):
        return f"Option Q{self.question.id}: {self.text[:30]}"

#class SectionTimer(models.Model):
#   session_id = models.IntegerField()
#   section_id = models.IntegerField()
#   remaining_time = models.IntegerField()
#   updated_at = models.DateTimeField(auto_now=True)
