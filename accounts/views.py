from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, CustomLoginForm
from django.contrib.auth import  logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from courses.models import Course, Enrollment
from accounts.models import User




def home(request):
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
            # if user.role == 'admin':
            #     user.role = 'student'

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
        enrollments = Enrollment.objects.filter(student=user)
        context["enrollments"] = enrollments

    elif user.role == "Lecturer":
        # Courses assigned to this lecturer
        courses = Course.objects.filter(lecturer=user)
        context["courses"] = courses

    elif user.role == "Admin":
        # Some system stats
        context["students_count"] = User.objects.filter(role="Student").count()
        context["courses_count"] = Course.objects.count()
        context["enrollments_count"] = Enrollment.objects.count()

    return render(request, "accounts/dashboard.html")
