"""
URL patterns for social features
Instagram/Facebook-like social interactions
"""

from django.urls import path
from . import social_api

urlpatterns = [
    path('follow/', social_api.follow_user, name='follow_user'),
    path('send-message/', social_api.send_message, name='send_message'),
    path('messages/<uuid:user_id>/', social_api.get_messages, name='get_messages'),
    path('conversations/', social_api.get_conversations, name='get_conversations'),
    path('profile/<uuid:user_id>/', social_api.get_user_profile, name='get_user_profile'),
    path('feedback/', social_api.submit_real_time_feedback, name='submit_feedback'),
]