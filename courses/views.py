from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment, Grade, Attendance
from .forms import CourseForm
from django.contrib import messages
from accounts.utils import create_notification


# ✅ Notify all admins (or specific users)
from django.contrib.auth import get_user_model
User = get_user_model()
admins = User.objects.filter(role="Admin")


@login_required
def course_list(request):
    if request.method == "POST":
        course_id = request.POST.get("course_id")
        course = get_object_or_404(Course, id=course_id)

        if request.user.role == "Student":
            # Enroll the student
            Enrollment.objects.get_or_create(student=request.user, course=course)
            msg = f"You have successfully enrolled in {course.code}"
            messages.success(request, msg)

            create_notification(request.user, msg)
            for admin in admins:
                create_notification(admin, f"{request.user.matric_no} enrolled in '{course.code}'.")
            if course.lecturer:
                msg = f"{request.user.matric_no} enrolled in '{course.code}'."
                create_notification(course.lecturer, msg)


        elif request.user.role == "Lecturer":
            # Assign lecturer to the course
            if course.lecturer is None:  # only if not already assigned
                course.lecturer = request.user
                course.save()
                msg = f"You have successfully registered for {course.code}"
                messages.success(request, msg)
                create_notification(request.user, msg)
                for admin in admins:
                    create_notification(admin, f"{request.user.first_name} registered for '{course.code}'.")

            else:
                messages.error(request, f"{course.title} already has a lecturer assigned.")

        return redirect("course_list")

    # Filtering logic
    if request.user.role == "Student":
        enrolled_courses = Enrollment.objects.filter(student=request.user).values_list("course_id", flat=True)
        courses = Course.objects.exclude(id__in=enrolled_courses)
    elif request.user.role == "Lecturer":
        courses = Course.objects.filter(lecturer__isnull=True)
    else:  # Admin
        courses = Course.objects.all()

    return render(request, "courses/course_list.html", {"courses": courses})



@login_required
def my_courses(request):
    if request.method == "POST":
        course_id = request.POST.get("course_id")
        course = get_object_or_404(Course, id=course_id)

        if request.user.role == "Student":
            # Delete enrollment
            Enrollment.objects.filter(student=request.user, course=course).delete()
            msg = f"You have dropped {course.code}."
            messages.success(request, msg)

            create_notification(request.user, msg)
            if course.lecturer:
                msg = f"{request.user.matric_no} have dropped '{course.code}'."
                create_notification(course.lecturer, msg)
            for admin in admins:
                create_notification(admin, msg)

        elif request.user.role == "Lecturer":
            # Unassign lecturer
            if course.lecturer == request.user:
                course.lecturer = None
                course.save()
                msg = f"You have unregistered {course.code}."
                messages.success(request, msg)

                create_notification(request.user, msg)
                for admin in admins:
                    create_notification(admin, f"{request.user.first_name} have unregistered {course.code}.")

            else:
                messages.error(request, "You are not assigned to this course.")

        return redirect("my_courses")

    # GET request → show courses
    if request.user.role == "Student":
        enrollments = Enrollment.objects.filter(student=request.user).select_related("course")
        lecturer_courses = []
    elif request.user.role == "Lecturer":
        enrollments = []
        lecturer_courses = Course.objects.filter(lecturer=request.user)
    else:
        enrollments = []
        lecturer_courses = Course.objects.all()

    return render(
        request,
        "courses/my_courses.html",
        {"enrollments": enrollments, "lecturer_courses": lecturer_courses},
    )



@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, "courses/course_detail.html", {"course": course})



@login_required
def add_course(request):
    if request.method == "POST":
        name = request.POST.get("name")
        lecturer = request.POST.get("lecturer")  # example
        
        course = Course.objects.create(name=name, lecturer_id=lecturer)
        messages.success(request, f"Course '{name}' created successfully.")

        # ✅ Notify all admins
        for admin in admins:
            create_notification(admin, f"New course '{name}' was added.")

        # ✅ Notify the lecturer
        if course.lecturer:
            create_notification(course.lecturer, f"You have been assigned to '{name}'.")

        return redirect("course_list")

    return render(request, "courses/add_course.html")



@login_required
def delete_course(request, course_id):
    if request.user.role != "Admin":
        messages.error(request, "You don’t have permission to delete courses.")
        return redirect("course_list")

    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        course.delete()
        msg = messages.success(request, f"Course '{course.title}' has been deleted successfully.")
        create_notification(request.user, msg)
        
        students = User.objects.filter(role="Student")
        lecturers = User.objects.filter(role="Lecturer")
        for student in students:
            create_notification(student, f"Course '{course.code} {course.title}' was deleted.")
        for lecturer in lecturers:
            create_notification(lecturer, f"Course '{course.code} {course.title}' was deleted.")
  
        return redirect("course_list")

    return redirect("course_list")

def mark_attendance(request, course_id):
    course = get_object_or_404(Course, id=course_id, lecturer=request.user)
    students = Enrollment.objects.filter(course=course).select_related("student")

    if request.method == "POST":
        for enrollment in students:
            present = request.POST.get(f"student_{enrollment.student.id}", "off") == "on"
            Attendance.objects.update_or_create(
                student=enrollment.student,
                course=course,
                date=timezone.now().date(),
                defaults={'present': present}
            )
        return redirect("dashboard")

    return render(request, "courses/mark_attendance.html", {"course": course, "students": students})


def upload_grades(request, course_id):
    course = get_object_or_404(Course, id=course_id, lecturer=request.user)
    students = Enrollment.objects.filter(course=course).select_related("student")

    if request.method == "POST":
        grade_type = request.POST.get("grade_type")  # assignment/test/exam/final

        for enrollment in students:
            score = request.POST.get(f"grade_{enrollment.student.id}")
            if score:
                Grade.objects.update_or_create(
                    student=enrollment.student,
                    course=course,
                    grade_type=grade_type,
                    defaults={'score': score}
                )
        return redirect("dashboard")

    return render(request, "courses/upload_grades.html", {"course": course, "students": students})

