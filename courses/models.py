from django.db import models
from django.conf import settings


class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=200)
    credit_unit = models.PositiveIntegerField(default=3)
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'Lecturer'},
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="assigned_courses"
    )

    def __str__(self):
        return f"{self.code} - {self.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'Student'},
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')  # Prevent duplicate enrollment

    def __str__(self):
        return f"{self.student.matric_no} enrolled in → {self.course.code}"
    
 

class Attendance(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'Student'},
        on_delete=models.CASCADE,
        null=True,
        related_name="attendance_records"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE,null=True, related_name="attendance_records")
    date = models.DateField(auto_now_add=True)   # Defaults to the date it’s marked
    present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'course', 'date')  # One record per student per day

    def __str__(self):
        return f"{self.student.username} - {self.course.code} ({self.date}) → {'Present' if self.present else 'Absent'}"



GRADE_TYPE_CHOICES = [
    ('assignment', 'Assignment'),
    ('test', 'Test'),
    ('exam', 'Exam'),
    ('final', 'Final'),
]

class Grade(models.Model):
    GRADE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,limit_choices_to={'role': 'Student'},null=True,
                                related_name="grades")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, related_name="grades")
    grade_type = models.CharField(max_length=20, choices=GRADE_TYPE_CHOICES,null=True)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    letter_grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True, null=True)
    date_recorded = models.DateTimeField(auto_now_add=True,null=True)

    def grade_point(self):
        """Convert letter grade to numeric grade point"""
        mapping = {
            'A': 5,  # or 4 depending on your GPA scale
            'B': 4,
            'C': 3,
            'D': 2,
            'F': 0,
        }
        return mapping.get(self.letter_grade, 0)

    def save(self, *args, **kwargs):
        """Auto-calculate letter grade from score if not provided"""
        if not self.letter_grade:
            if self.score >= 70:
                self.letter_grade = 'A'
            elif self.score >= 60:
                self.letter_grade = 'B'
            elif self.score >= 50:
                self.letter_grade = 'C'
            elif self.score >= 45:
                self.letter_grade = 'D'
            else:
                self.letter_grade = 'F'
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('student', 'course', 'grade_type')

    def __str__(self):
        return f"{self.student} - {self.course.code} [{self.grade_type}] → ({self.letter_grade})"    



def calculate_gpa(student):
    enrollments = Enrollment.objects.filter(student=student).select_related("course")
    total_points, total_units = 0, 0

    for e in enrollments:
        # fetch grades for this student in this course
        grades = Grade.objects.filter(student=student, course=e.course).order_by("-date_recorded")
        if grades.exists():
            grade = grades.first()  # latest grade
            total_points += grade.grade_point() * e.course.credit_unit
            total_units += e.course.credit_unit

    return round(total_points / total_units, 2) if total_units > 0 else 0.0


def calculate_exam_eligibility(student):
    enrollments = Enrollment.objects.filter(student=student).select_related("course")
    total_classes, total_present = 0, 0

    for e in enrollments:
        # All attendance records for this student's course
        records = Attendance.objects.filter(student=student, course=e.course)
        total_classes += records.count()
        total_present += records.filter(present=True).count()

    percentage = (total_present / total_classes) * 100 if total_classes > 0 else 0
    return round(percentage, 1)
