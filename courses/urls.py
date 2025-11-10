from django.urls import path
from . import views

urlpatterns = [
    path("", views.course_list, name="course_list"),
    path("my-courses/", views.my_courses, name="my_courses"),
    path("<int:pk>/", views.course_detail, name="course_detail"),
    path("<int:course_id>/delete/", views.delete_course, name="delete_course"),
    path("add_course/", views.add_course, name= "add_course"),
    path("<int:course_id>/attendance/", views.mark_attendance, name="mark_attendance"),
    path("<int:course_id>/grades/", views.upload_grades, name="upload_grades"),
    path("attendance_details/", views.attendance_details, name="attendance_details"),
]
