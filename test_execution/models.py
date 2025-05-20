from django.db import models

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

