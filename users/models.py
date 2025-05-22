from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('candidate', 'Candidate'),
        ('proctor', 'Proctor'),
        ('admin', 'Admin'),
        ('creator','Creator')
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate')

    def __str__(self):
        return f"{self.username} ({self.role})"


