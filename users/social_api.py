"""
Social Features API for PeerLearn
Advanced Instagram/Facebook-like social interactions
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
import json

from .follow_models import Follow, PersonalMessage, ProfileView, UserActivity, UserBadge, UserSocialStats
from sessions.models import Session, Booking, Feedback

User = get_user_model()

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def follow_user(request):
    """Follow or unfollow a user"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        action = data.get('action')  # 'follow' or 'unfollow'
        
        target_user = get_object_or_404(User, id=user_id)
        
        if request.user == target_user:
            return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
        
        if action == 'follow':
            follow, created = Follow.objects.get_or_create(
                follower=request.user,
                following=target_user
            )
            
            if created:
                # Create activity for the followed user
                UserActivity.objects.create(
                    user=target_user,
                    activity_type='new_follower',
                    description=f'{request.user.username} started following you',
                    related_user=request.user
                )
                
                # Update social stats
                stats, _ = UserSocialStats.objects.get_or_create(user=target_user)
                stats.update_stats()
                
                return JsonResponse({
                    'success': True,
                    'action': 'followed',
                    'followers_count': target_user.followers.count()
                })
            else:
                return JsonResponse({'error': 'Already following'}, status=400)
                
        elif action == 'unfollow':
            try:
                follow = Follow.objects.get(follower=request.user, following=target_user)
                follow.delete()
                
                # Update social stats
                stats, _ = UserSocialStats.objects.get_or_create(user=target_user)
                stats.update_stats()
                
                return JsonResponse({
                    'success': True,
                    'action': 'unfollowed',
                    'followers_count': target_user.followers.count()
                })
            except Follow.DoesNotExist:
                return JsonResponse({'error': 'Not following'}, status=400)
                
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def send_message(request):
    """Send a personal message to another user"""
    try:
        data = json.loads(request.body)
        recipient_id = data.get('recipient_id')
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        recipient = get_object_or_404(User, id=recipient_id)
        
        if request.user == recipient:
            return JsonResponse({'error': 'Cannot message yourself'}, status=400)
        
        # Create the message
        personal_message = PersonalMessage.objects.create(
            sender=request.user,
            recipient=recipient,
            message=message
        )
        
        return JsonResponse({
            'success': True,
            'message_id': personal_message.id,
            'sent_at': personal_message.created_at.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_messages(request, user_id):
    """Get message history with a specific user"""
    try:
        other_user = get_object_or_404(User, id=user_id)
        
        messages = PersonalMessage.objects.filter(
            Q(sender=request.user, recipient=other_user) |
            Q(sender=other_user, recipient=request.user)
        ).order_by('created_at')
        
        # Mark messages as read
        PersonalMessage.objects.filter(
            sender=other_user,
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'sender_id': str(msg.sender.id),
                'sender_name': msg.sender.username,
                'message': msg.message,
                'created_at': msg.created_at.isoformat(),
                'is_read': msg.is_read
            })
        
        return JsonResponse({
            'success': True,
            'messages': messages_data,
            'other_user': {
                'id': str(other_user.id),
                'username': other_user.username,
                'profile_image': other_user.profile_image.url if other_user.profile_image else None
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_conversations(request):
    """Get list of all conversations for the user"""
    try:
        # Get all users the current user has messaged with
        sent_to = PersonalMessage.objects.filter(sender=request.user).values_list('recipient', flat=True)
        received_from = PersonalMessage.objects.filter(recipient=request.user).values_list('sender', flat=True)
        
        conversation_users = set(list(sent_to) + list(received_from))
        
        conversations = []
        for user_id in conversation_users:
            user = User.objects.get(id=user_id)
            
            # Get latest message
            latest_message = PersonalMessage.objects.filter(
                Q(sender=request.user, recipient=user) |
                Q(sender=user, recipient=request.user)
            ).order_by('-created_at').first()
            
            # Count unread messages
            unread_count = PersonalMessage.objects.filter(
                sender=user,
                recipient=request.user,
                is_read=False
            ).count()
            
            conversations.append({
                'user_id': str(user.id),
                'username': user.username,
                'profile_image': user.profile_image.url if user.profile_image else None,
                'latest_message': latest_message.message if latest_message else '',
                'latest_message_time': latest_message.created_at.isoformat() if latest_message else '',
                'unread_count': unread_count
            })
        
        # Sort by latest message time
        conversations.sort(key=lambda x: x['latest_message_time'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'conversations': conversations
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_user_profile(request, user_id):
    """Get detailed user profile with social stats"""
    try:
        user = get_object_or_404(User, id=user_id)
        
        # Record profile view if not viewing own profile
        if request.user != user:
            ProfileView.objects.get_or_create(
                viewer=request.user,
                viewed_profile=user
            )
        
        # Get or create social stats
        social_stats, _ = UserSocialStats.objects.get_or_create(user=user)
        social_stats.update_stats()
        
        # Check if current user follows this user
        is_following = Follow.objects.filter(
            follower=request.user,
            following=user
        ).exists() if request.user != user else False
        
        # Get recent activities
        activities = UserActivity.objects.filter(user=user)[:10]
        activities_data = []
        for activity in activities:
            activities_data.append({
                'type': activity.activity_type,
                'description': activity.description,
                'created_at': activity.created_at.isoformat(),
                'related_user': activity.related_user.username if activity.related_user else None
            })
        
        # Get user badges
        badges = UserBadge.objects.filter(user=user)
        badges_data = [{'type': badge.badge_type, 'earned_at': badge.earned_at.isoformat()} for badge in badges]
        
        # Get recent sessions (for mentors)
        recent_sessions = []
        if user.role == 'mentor':
            sessions = Session.objects.filter(mentor=user).order_by('-created_at')[:5]
            for session in sessions:
                recent_sessions.append({
                    'title': session.title,
                    'created_at': session.created_at.isoformat(),
                    'status': session.status
                })
        
        profile_data = {
            'id': str(user.id),
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': user.bio,
            'role': user.role,
            'skills': user.skills,
            'interests': user.interests,
            'domain': user.domain,
            'expertise': user.expertise,
            'location': user.location,
            'website': user.website,
            'profile_image': user.profile_image.url if user.profile_image else None,
            'is_verified': user.is_verified,
            'created_at': user.created_at.isoformat(),
            'is_following': is_following,
            'social_stats': {
                'followers_count': social_stats.followers_count,
                'following_count': social_stats.following_count,
                'profile_views_count': social_stats.profile_views_count,
                'total_sessions': social_stats.total_sessions,
                'average_rating': social_stats.average_rating,
                'response_time_hours': social_stats.response_time_hours
            },
            'recent_activities': activities_data,
            'badges': badges_data,
            'recent_sessions': recent_sessions
        }
        
        return JsonResponse({
            'success': True,
            'profile': profile_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def submit_real_time_feedback(request):
    """Submit real-time feedback during or after a session"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        session = get_object_or_404(Session, id=session_id)
        
        # Create or update feedback
        feedback, created = Feedback.objects.update_or_create(
            session=session,
            user=request.user,
            defaults={
                'rating': rating,
                'comment': comment
            }
        )
        
        # Create activity for mentor
        UserActivity.objects.create(
            user=session.mentor,
            activity_type='feedback_received',
            description=f'Received {rating}-star feedback from {request.user.username}',
            related_user=request.user,
            metadata={'session_id': str(session.id), 'rating': rating}
        )
        
        # Update mentor's social stats
        stats, _ = UserSocialStats.objects.get_or_create(user=session.mentor)
        stats.update_stats()
        
        return JsonResponse({
            'success': True,
            'feedback_id': feedback.id,
            'created': created
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)