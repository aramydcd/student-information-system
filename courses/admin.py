from django.contrib import admin
from .models import Course, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "credit_unit", "lecturer")
    search_fields = ("code", "title")
    list_filter = ("credit_unit", "lecturer")

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "date_enrolled")
    search_fields = ("student__username", "course__code")
    list_filter = ("course", "date_enrolled")

