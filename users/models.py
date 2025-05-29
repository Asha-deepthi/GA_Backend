#backend/users/models.py
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
from django.db import models
from django.utils import timezone

#class CustomUser(AbstractUser):
 #   ROLE_CHOICES = [
 #      ('candidate', 'Candidate'),
 #      ('proctor', 'Proctor'),
 #      ('admin', 'Admin'),
 #      ('creator','Creator')
 #   ]
 #  role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate')

 #  def __str__(self):
 #      return f"{self.username} ({self.role})"

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, phone=None, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)  # hashes the password
        user.is_active = False  # inactive until email activation
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        user = self.create_user(email, password, **extra_fields)
        user.is_active = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    email_verification_uuid = models.UUIDField( unique=True, default=uuid.uuid4)
    is_email_verified = models.BooleanField(default=False)



    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email