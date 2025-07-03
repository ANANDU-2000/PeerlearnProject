from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q, Count
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import base64
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User, Follow, PaymentHistory, UserActivity  # , FeedbackReply
from sessions.models import Session, Booking, Feedback, Notification

@csrf_exempt
@require_http_methods(["POST"])
def check_email_exists(request):
    """Check if email already exists in database - live validation"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({'exists': False})
        
        # Check if email exists in database
        exists = User.objects.filter(email__iexact=email).exists()
        
        return JsonResponse({'exists': exists})
        
    except (json.JSONDecodeError, Exception):
        return JsonResponse({'exists': False})

@login_required
@require_http_methods(["POST"])
def upload_profile_image(request):
    """Upload and resize profile image"""
    try:
        if 'profile_image' not in request.FILES:
            return JsonResponse({'error': 'No image file provided'}, status=400)
        
        image_file = request.FILES['profile_image']
        
        # Validate file size (5MB max)
        if image_file.size > 5 * 1024 * 1024:
            return JsonResponse({'error': 'Image file too large (max 5MB)'}, status=400)
        
        # Validate file type
        if not image_file.content_type.startswith('image/'):
            return JsonResponse({'error': 'Invalid file type. Please upload an image.'}, status=400)
        
        # Delete old profile image if exists
        if request.user.profile_image:
            try:
                default_storage.delete(request.user.profile_image.path)
            except:
                pass
        
        # Save new image
        request.user.profile_image = image_file
        request.user.save()
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='profile_updated',
            description='Updated profile image'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Profile image updated successfully',
            'image_url': request.user.profile_image.url
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["PUT"])
def update_profile(request):
    """Update user profile information"""
    try:
        data = json.loads(request.body)
        
        # Update basic fields
        if 'first_name' in data:
            request.user.first_name = data['first_name']
        if 'last_name' in data:
            request.user.last_name = data['last_name']
        if 'bio' in data:
            request.user.bio = data['bio']
        if 'location' in data:
            request.user.location = data['location']
        if 'website' in data:
            request.user.website = data['website']
        
        # Role-specific fields
        if request.user.is_mentor and 'skills' in data:
            request.user.skills = data['skills']
        elif request.user.is_learner and 'interests' in data:
            request.user.interests = data['interests']
        
        request.user.save()
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='profile_updated',
            description='Updated profile information'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_user_sessions(request):
    """Get user's session history"""
    try:
        if request.user.is_mentor:
            sessions = Session.objects.filter(mentor=request.user).order_by('-created_at')
        else:
            bookings = Booking.objects.filter(learner=request.user).select_related('session')
            sessions = [booking.session for booking in bookings]
        
        sessions_data = []
        for session in sessions[:20]:  # Limit to 20 recent sessions
            sessions_data.append({
                'id': str(session.id),
                'title': session.title,
                'date': session.schedule.strftime('%Y-%m-%d %H:%M'),
                'status': session.status,
                'duration': session.duration,
                'participants': session.current_participants,
            })
        
        return JsonResponse({
            'success': True,
            'sessions': sessions_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_payment_history(request):
    """Get user's payment history"""
    try:
        payments = PaymentHistory.objects.filter(user=request.user).order_by('-created_at')[:20]
        
        payments_data = []
        for payment in payments:
            payments_data.append({
                'id': str(payment.id),
                'amount': float(payment.amount),
                'description': payment.description or f"{payment.payment_type.replace('_', ' ').title()}",
                'status': payment.status,
                'date': payment.created_at.strftime('%Y-%m-%d %H:%M'),
                'payment_type': payment.payment_type,
                'gateway': payment.gateway,
            })
        
        return JsonResponse({
            'success': True,
            'payments': payments_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_user_activity(request):
    """Get user's recent activity"""
    try:
        activities = UserActivity.objects.filter(user=request.user).order_by('-created_at')[:20]
        
        activities_data = []
        for activity in activities:
            time_diff = timezone.now() - activity.created_at
            if time_diff.days > 0:
                time_ago = f"{time_diff.days} days ago"
            elif time_diff.seconds > 3600:
                time_ago = f"{time_diff.seconds // 3600} hours ago"
            elif time_diff.seconds > 60:
                time_ago = f"{time_diff.seconds // 60} minutes ago"
            else:
                time_ago = "Just now"
            
            activities_data.append({
                'id': str(activity.id),
                'description': activity.description,
                'activity_type': activity.activity_type,
                'time_ago': time_ago,
                'created_at': activity.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'activities': activities_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_followers(request):
    """Get user's followers"""
    try:
        follows = Follow.objects.filter(following=request.user).select_related('follower')[:50]
        
        users_data = []
        for follow in follows:
            user = follow.follower
            users_data.append({
                'id': str(user.id),
                'name': user.get_full_name() or user.username,
                'username': user.username,
                'role': user.role,
                'avatar_letter': user.avatar_letter,
                'is_online': user.is_online,
                'followed_at': follow.created_at.strftime('%Y-%m-%d'),
            })
        
        return JsonResponse({
            'success': True,
            'users': users_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_following(request):
    """Get users this user is following"""
    try:
        follows = Follow.objects.filter(follower=request.user).select_related('following')[:50]
        
        users_data = []
        for follow in follows:
            user = follow.following
            users_data.append({
                'id': str(user.id),
                'name': user.get_full_name() or user.username,
                'username': user.username,
                'role': user.role,
                'avatar_letter': user.avatar_letter,
                'is_online': user.is_online,
                'followed_at': follow.created_at.strftime('%Y-%m-%d'),
            })
        
        return JsonResponse({
            'success': True,
            'users': users_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, user_id):
    """Follow or unfollow a user (mentor)"""
    try:
        user_to_follow = User.objects.get(id=user_id)
        
        if user_to_follow == request.user:
            return Response({'error': 'Cannot follow yourself'}, status=400)
        
        follow_obj, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        
        if created:
            # Increment follower counts
            user_to_follow.followers_count += 1
            request.user.following_count += 1
            user_to_follow.save()
            request.user.save()
            
            # Create activity record
            UserActivity.objects.create(
                user=request.user,
                activity_type='followed_user',
                description=f'Followed {user_to_follow.username}',
                related_user_id=user_to_follow.id
            )
            
            return Response({
                'status': 'followed',
                'message': f'You are now following {user_to_follow.username}',
                'followers_count': user_to_follow.followers_count
            })
        else:
            return Response({
                'status': 'already_following',
                'message': f'You are already following {user_to_follow.username}'
            })
            
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, user_id):
    """Unfollow a user"""
    try:
        user_to_unfollow = User.objects.get(id=user_id)
        
        follow_obj = Follow.objects.filter(
            follower=request.user,
            following=user_to_unfollow
        ).first()
        
        if follow_obj:
            follow_obj.delete()
            
            # Decrement follower counts
            user_to_unfollow.followers_count = max(0, user_to_unfollow.followers_count - 1)
            request.user.following_count = max(0, request.user.following_count - 1)
            user_to_unfollow.save()
            request.user.save()
            
            # Create activity record
            UserActivity.objects.create(
                user=request.user,
                activity_type='unfollowed_user',
                description=f'Unfollowed {user_to_unfollow.username}',
                related_user_id=user_to_unfollow.id
            )
            
            return Response({
                'status': 'unfollowed',
                'message': f'You have unfollowed {user_to_unfollow.username}',
                'followers_count': user_to_unfollow.followers_count
            })
        else:
            return Response({
                'status': 'not_following',
                'message': f'You are not following {user_to_unfollow.username}'
            })
            
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def follow_status(request, user_id):
    """Check if user is following another user"""
    try:
        user_to_check = User.objects.get(id=user_id)
        is_following = Follow.objects.filter(
            follower=request.user,
            following=user_to_check
        ).exists()
        
        return Response({
            'is_following': is_following,
            'followers_count': user_to_check.followers_count,
            'following_count': user_to_check.following_count
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_followers(request, user_id):
    """Get followers list for a user"""
    try:
        user = User.objects.get(id=user_id)
        followers = Follow.objects.filter(following=user).select_related('follower')
        
        followers_data = []
        for follow in followers:
            followers_data.append({
                'id': str(follow.follower.id),
                'username': follow.follower.username,
                'full_name': follow.follower.full_name,
                'profile_image': follow.follower.profile_image_url,
                'role': follow.follower.role,
                'followed_at': follow.created_at.isoformat()
            })
        
        return Response({
            'followers': followers_data,
            'count': len(followers_data)
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_following(request, user_id):
    """Get following list for a user"""
    try:
        user = User.objects.get(id=user_id)
        following = Follow.objects.filter(follower=user).select_related('following')
        
        following_data = []
        for follow in following:
            following_data.append({
                'id': str(follow.following.id),
                'username': follow.following.username,
                'full_name': follow.following.full_name,
                'profile_image': follow.following.profile_image_url,
                'role': follow.following.role,
                'followed_at': follow.created_at.isoformat()
            })
        
        return Response({
            'following': following_data,
            'count': len(following_data)
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

@login_required
@require_http_methods(["GET"])
def get_mentor_followers_sessions(request):
    """Get sessions from followed mentors for learners"""
    try:
        if not request.user.is_learner:
            return JsonResponse({'error': 'Only learners can access this'}, status=403)
        
        # Get mentors this user follows
        following = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
        
        # Get upcoming sessions from followed mentors
        sessions = Session.objects.filter(
            mentor_id__in=following,
            status='scheduled',
            schedule__gt=timezone.now()
        ).select_related('mentor').order_by('schedule')[:20]
        
        sessions_data = []
        for session in sessions:
            # Check if user has already booked
            is_booked = Booking.objects.filter(
                learner=request.user,
                session=session,
                status='confirmed'
            ).exists()
            
            sessions_data.append({
                'id': str(session.id),
                'title': session.title,
                'description': session.description[:200] + '...' if len(session.description) > 200 else session.description,
                'mentor_name': session.mentor.get_full_name() or session.mentor.username,
                'mentor_id': str(session.mentor.id),
                'schedule': session.schedule.strftime('%Y-%m-%d %H:%M'),
                'duration': session.duration,
                'price': float(session.price) if session.price else 0,
                'current_participants': session.current_participants,
                'max_participants': session.max_participants,
                'is_booked': is_booked,
                'is_full': session.is_full,
                'category': session.category,
            })
        
        return JsonResponse({
            'success': True,
            'sessions': sessions_data,
            'following_count': len(following)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def search_users(request):
    """Search for users to follow"""
    try:
        query = request.GET.get('q', '').strip()
        role_filter = request.GET.get('role', '')
        
        if not query:
            return JsonResponse({'error': 'Search query required'}, status=400)
        
        # Search users
        users_query = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query),
            is_active=True
        ).exclude(id=request.user.id)
        
        if role_filter in ['mentor', 'learner']:
            users_query = users_query.filter(role=role_filter)
        
        users = users_query[:20]
        
        users_data = []
        for user in users:
            # Check if already following
            is_following = Follow.objects.filter(
                follower=request.user,
                following=user
            ).exists()
            
            users_data.append({
                'id': str(user.id),
                'name': user.get_full_name() or user.username,
                'username': user.username,
                'role': user.role,
                'bio': user.bio[:100] + '...' if user.bio and len(user.bio) > 100 else user.bio,
                'avatar_letter': user.avatar_letter,
                'profile_image_url': user.profile_image_url,
                'is_following': is_following,
                'is_verified': user.is_verified,
                'followers_count': user.followers_count,
                'total_sessions': user.total_sessions,
            })
        
        return JsonResponse({
            'success': True,
            'users': users_data,
            'query': query
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def log_user_activity(user, activity_type, description, **kwargs):
    """Helper function to log user activities"""
    UserActivity.objects.create(
        user=user,
        activity_type=activity_type,
        description=description,
        related_user_id=kwargs.get('related_user_id'),
        related_session_id=kwargs.get('related_session_id'),
        ip_address=kwargs.get('ip_address'),
        user_agent=kwargs.get('user_agent'),
        metadata=kwargs.get('metadata', {})
    )