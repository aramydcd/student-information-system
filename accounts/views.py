from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, CustomLoginForm
from django.contrib.auth import  logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from courses.models import Course, Enrollment,Grade, calculate_exam_eligibility, calculate_gpa
from accounts.models import User
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Notification
from django.db.models import Count
import json
from django.utils.safestring import mark_safe




def home(request):
    # unread_count = 0
    # if request.user.is_authenticated:
    #     unread = Notification.objects.filter(user=request.user, is_read=False)
    #     unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    # return render(request, "home.html", {"unread_count": unread_count,"unread": unread})
    return render(request, "home.html")




class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomLoginForm

    def get_success_url(self):
        # Redirect all users to the same dashboard
        return reverse_lazy("dashboard")
    
    

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # 🔒 prevent normal signup as admin
            # if user.role == 'Admin':
            #     user.role = 'Student'

            user.save()
            login(request, user)  # auto-login after signup
            return redirect('dashboard')

    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})



# Logout View
def logout_view(request):
    logout(request)
    return redirect("login")



@login_required
def dashboard_view(request):
    user = request.user
    context = {}

    # ===================== STUDENT DASHBOARD =====================
    if user.role == "Student":
        student_enrollments = Enrollment.objects.filter(student=user).select_related("course__lecturer")
        student_courses = [en.course for en in student_enrollments]
        total_courses = len(student_courses)

        gpa = calculate_gpa(user)
        exam_eligibility = calculate_exam_eligibility(user)
        gpa_trend = [3.26, 3.36, 0.0, gpa]  # Dummy trend for now

        context.update({
            "courses": student_courses,
            "total_courses": total_courses,
            "gpa": gpa,
            "eligibility": exam_eligibility,
            "gpa_trend": gpa_trend,
        })

    # ===================== LECTURER DASHBOARD =====================
    elif user.role == "Lecturer":
        lecturer_courses = Course.objects.filter(lecturer=user).prefetch_related("enrollments")
        total_courses = lecturer_courses.count()
        total_students = Enrollment.objects.filter(course__lecturer=user).count()

        course_progress = []
        for course in lecturer_courses:
            total_enrolled = course.enrollments.count()
            if total_enrolled > 0:
                graded = Grade.objects.filter(course=course).values("student").distinct().count()
                progress = round((graded / total_enrolled) * 100, 1)
            else:
                progress = 0
            course_progress.append({"course": course, "progress": progress})

        context.update({
            "lecturer_courses": lecturer_courses,
            "total_courses": total_courses,
            "total_students": total_students,
            "course_progress": course_progress,
        })

    # ===================== ADMIN DASHBOARD =====================
    elif user.role == "Admin":
        students_count = User.objects.filter(role="Student").count()
        lecturers_count = User.objects.filter(role="Lecturer").count()
        courses_count = Course.objects.count()
        enrollments_count = Enrollment.objects.count()

        # distribution of courses among lecturers
        lecturer_allocations = (
            Course.objects.values("lecturer__username")
            .annotate(course_count=Count("id"))
            .order_by("-course_count")
        )

        lecturer_names = [item["lecturer__username"] or "Unassigned" for item in lecturer_allocations]
        course_counts = [item["course_count"] for item in lecturer_allocations]

        context = {
            "students_count": students_count,
            "lecturers_count": lecturers_count,
            "courses_count": courses_count,
            "enrollments_count": enrollments_count,
            # Pass as proper JS arrays
            "lecturer_names_json": mark_safe(json.dumps(lecturer_names)),
            "course_counts_json": mark_safe(json.dumps(course_counts)),
        }


    return render(request, "accounts/dashboard.html", context)




def about(request):
    return render(request, "accounts/about.html")

def help_support(request):
    return render(request, "accounts/help.html")



@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile')  # refresh page
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })



@login_required
def notifications_list(request):
    notifications = request.user.notifications.all()
    return render(request, 'accounts/notifications_list.html', {'notifications': notifications})


@login_required
def mark_as_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect(request.META.get("HTTP_REFERER", "home"))

@login_required
def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get("HTTP_REFERER", "home"))