from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Lecturer', 'Lecturer'),
        ('Student', 'Student'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Student')
    matric_no = models.CharField(max_length=20, blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


