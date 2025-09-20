from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"), 
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("about/", views.about, name="about"),
    path("help/", views.help_support, name="help"),
    path('profile/', views.profile, name='profile'),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("notifications/", views.notifications_list, name="notifications_list"),
    path("notifications/read/<int:pk>/", views.mark_as_read, name="mark_as_read"),
    path("notifications/read-all/", views.mark_all_as_read, name="mark_all_as_read"),
]


