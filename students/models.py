from django.db import models
from django.conf import settings
from courses.models import Course

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    matric_no = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    level = models.CharField(max_length=10)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.matric_no}"

