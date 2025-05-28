"""
URL patterns for the feedback system
"""

from django.urls import path
from . import feedback_views

urlpatterns = [
    # Feedback pages
    path('feedback/', feedback_views.app_feedback_page, name='app_feedback'),
    path('feedback/submit/', feedback_views.submit_feedback, name='submit_feedback'),
    
    # Admin feedback management APIs
    path('admin-dashboard/api/feedback/', feedback_views.admin_feedback_api, name='admin_feedback_api'),
    path('admin-dashboard/api/feedback/reply/', feedback_views.admin_reply_feedback, name='admin_reply_feedback'),
    path('admin-dashboard/api/notifications/', feedback_views.admin_notifications_api, name='admin_notifications_api'),
]