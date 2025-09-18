from django.db import models
from django.conf import settings
from accounts.models import User


class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=200)
    credit_unit = models.IntegerField()
    lecturer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.code} - {self.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "Student"},
        related_name="enrollments"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')  # prevents duplicate enrollments

    def __str__(self):
        return f"{self.student.matric_no} → {self.course.code}"

