from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import logout
from django.shortcuts import redirect
from . import views, api_views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/mentor/', views.mentor_dashboard, name='mentor_dashboard'),
    path('dashboard/learner/', views.learner_dashboard, name='learner_dashboard'),
    
    # API endpoints for live validation
    path('api/check-email/', api_views.check_email_exists, name='check_email_exists'),
]
