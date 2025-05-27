"""
Advanced Password Reset System with Real Database Changes
Handles forgot password functionality with secure token generation and email notifications
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

User = get_user_model()

class PasswordResetToken:
    """Manage password reset tokens in database"""
    
    @staticmethod
    def generate_token():
        """Generate secure random token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_reset_token(user):
        """Create and store password reset token for user"""
        token = PasswordResetToken.generate_token()
        expires_at = timezone.now() + timedelta(hours=24)  # 24-hour expiry
        
        # Store token in user model (you can also create a separate model)
        user.password_reset_token = token
        user.password_reset_expires = expires_at
        user.save()
        
        return token
    
    @staticmethod
    def verify_token(token):
        """Verify reset token and return user if valid"""
        try:
            user = User.objects.get(
                password_reset_token=token,
                password_reset_expires__gt=timezone.now()
            )
            return user
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def clear_token(user):
        """Clear reset token after successful password change"""
        user.password_reset_token = None
        user.password_reset_expires = None
        user.save()


def send_reset_email(user, token):
    """Send password reset email with real email functionality"""
    reset_url = f"{settings.SITE_URL}/auth/reset-password/?token={token}"
    
    subject = 'Reset Your PeerLearn Password'
    message = f"""
    Hi {user.get_full_name() or user.username},
    
    You requested to reset your password for your PeerLearn account.
    
    Click the link below to set a new password:
    {reset_url}
    
    This link will expire in 24 hours.
    
    If you didn't request this reset, please ignore this email.
    
    Best regards,
    The PeerLearn Team
    """
    
    html_message = f"""
    <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
            <h1 style="color: white; margin: 0;">PeerLearn</h1>
        </div>
        
        <div style="padding: 30px; background: white;">
            <h2 style="color: #333;">Reset Your Password</h2>
            
            <p>Hi {user.get_full_name() or user.username},</p>
            
            <p>You requested to reset your password for your PeerLearn account.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background: #667eea; color: white; padding: 15px 30px; 
                          text-decoration: none; border-radius: 8px; display: inline-block;">
                    Reset Password
                </a>
            </div>
            
            <p><small>This link will expire in 24 hours.</small></p>
            <p><small>If you didn't request this reset, please ignore this email.</small></p>
        </div>
        
        <div style="padding: 20px; background: #f8f9fa; text-align: center; color: #666;">
            <p>Best regards,<br>The PeerLearn Team</p>
        </div>
    </div>
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Failed to send reset email: {e}")
        return False


@require_http_methods(["GET", "POST"])
def forgot_password_view(request):
    """Handle forgot password page and form submission"""
    if request.method == 'GET':
        return render(request, 'auth/forgot_password.html')
    
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({
                'success': False,
                'error': 'Email address is required'
            })
        
        # Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # For security, don't reveal if email exists
            return JsonResponse({
                'success': True,
                'message': 'If an account with this email exists, reset instructions have been sent.'
            })
        
        # Generate reset token
        token = PasswordResetToken.create_reset_token(user)
        
        # Send reset email
        email_sent = send_reset_email(user, token)
        
        if email_sent:
            return JsonResponse({
                'success': True,
                'message': 'Password reset instructions sent to your email.'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to send reset email. Please try again.'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid request format'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Server error. Please try again later.'
        })


@require_http_methods(["GET", "POST"])
def reset_password_view(request):
    """Handle password reset page and form submission"""
    if request.method == 'GET':
        token = request.GET.get('token')
        if not token:
            return redirect('/auth/forgot-password/')
        
        # Verify token
        user = PasswordResetToken.verify_token(token)
        if not user:
            return render(request, 'auth/reset_password_expired.html')
        
        return render(request, 'auth/reset_password.html', {
            'token': token,
            'user': user
        })
    
    try:
        data = json.loads(request.body)
        token = data.get('token')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if not all([token, new_password, confirm_password]):
            return JsonResponse({
                'success': False,
                'error': 'All fields are required'
            })
        
        if new_password != confirm_password:
            return JsonResponse({
                'success': False,
                'error': 'Passwords do not match'
            })
        
        if len(new_password) < 8:
            return JsonResponse({
                'success': False,
                'error': 'Password must be at least 8 characters long'
            })
        
        # Verify token and get user
        user = PasswordResetToken.verify_token(token)
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'Invalid or expired reset token'
            })
        
        # Update password in database
        user.password = make_password(new_password)
        user.save()
        
        # Clear reset token
        PasswordResetToken.clear_token(user)
        
        # Log password change
        print(f"Password successfully reset for user: {user.username} ({user.email})")
        
        return JsonResponse({
            'success': True,
            'message': 'Password successfully updated'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid request format'
        })
    except Exception as e:
        print(f"Password reset error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Server error. Please try again later.'
        })


@require_http_methods(["POST"])
def resend_reset_email(request):
    """Resend password reset email"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        try:
            user = User.objects.get(email=email)
            
            # Generate new token
            token = PasswordResetToken.create_reset_token(user)
            
            # Send email
            email_sent = send_reset_email(user, token)
            
            if email_sent:
                return JsonResponse({
                    'success': True,
                    'message': 'Reset email sent successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to send email'
                })
                
        except User.DoesNotExist:
            # For security, don't reveal if email exists
            return JsonResponse({
                'success': True,
                'message': 'If an account exists, reset email has been sent.'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Server error'
        })