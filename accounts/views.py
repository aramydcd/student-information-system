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

    if user.role == "Student":
        # Enrollments for the student
        student_enrollments = Enrollment.objects.filter(student=user).select_related("course__lecturer")
        student_courses = [en.course for en in student_enrollments]
        total_courses = len(student_courses)


        # Dummy GPA prediction (later we connect to Grades)
        predicted_gpa = 3.5  

        gpa = calculate_gpa(user)
        exam_eligibility = calculate_exam_eligibility(user)

        # Example GPA trend (latest 5 semesters or random for now)
        gpa_trend = [3.26, 3.36, 0.0, gpa]


        context = {
            "courses": student_courses,
            "total_courses": total_courses,
            "gpa": predicted_gpa,
            "eligibility": exam_eligibility,
            "gpa_trend": gpa_trend,
        }

    elif user.role == "Lecturer":
        # Courses assigned to this lecturer
        lecturer_courses = Course.objects.filter(lecturer=user).prefetch_related("enrollments")

        # Stats
        total_courses = lecturer_courses.count()
        total_students = Enrollment.objects.filter(course__lecturer=user).count()

        # Example: Course progress (attendance % or grade submission %)
        course_progress = []
        for course in lecturer_courses:
            total_enrolled = course.enrollments.count()
            if total_enrolled > 0:
                # Example progress: % of students graded
                graded = Grade.objects.filter(course=course).values("student").distinct().count()
                progress = round((graded / total_enrolled) * 100, 1)
            else:
                progress = 0
            course_progress.append({"course": course, "progress": progress})

        context = {
            "lecturer_courses": lecturer_courses,
            "total_courses": total_courses,
            "total_students": total_students,
            "course_progress": course_progress,
        }

    elif user.role == "Admin":
        # Some system stats
        context["students_count"] = User.objects.filter(role="Student").count()
        context["courses_count"] = Course.objects.count()
        context["enrollments_count"] = Enrollment.objects.count()

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