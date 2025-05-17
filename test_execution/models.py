from django.db import models

class BasicDetails(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)

    submitted_at = models.DateTimeField(auto_now_add=True)  # Optional: timestamp

    def __str__(self):
        return f"{self.name} - {self.email}"
