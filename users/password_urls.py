"""
URL patterns for password reset functionality
"""

from django.urls import path
from users.password_reset import (
    forgot_password_view,
    reset_password_view,
    resend_reset_email
)

urlpatterns = [
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('reset-password/', reset_password_view, name='reset_password'),
    path('resend-email/', resend_reset_email, name='resend_reset_email'),
]