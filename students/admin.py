from django.contrib import admin
from .models import Student
from courses.models import Enrollment

admin.site.register(Student)
admin.site.register(Enrollment)