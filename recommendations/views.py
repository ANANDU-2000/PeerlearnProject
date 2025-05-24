from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from sessions.models import Session
from .models import PopularityMetric

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trending_sessions(request):
    """Get trending sessions based on popularity metrics"""
    limit = int(request.GET.get('limit', 5))
    
    # Get sessions with popularity metrics, ordered by score
    popular_sessions = []
    metrics = PopularityMetric.objects.select_related('session').all()
    
    # Calculate scores and sort
    session_scores = []
    for metric in metrics:
        if metric.session.status == 'scheduled':
            score = metric.calculate_score()
            session_scores.append((metric.session, score))
    
    # Sort by score and take top N
    session_scores.sort(key=lambda x: x[1], reverse=True)
    top_sessions = session_scores[:limit]
    
    data = []
    for session, score in top_sessions:
        data.append({
            'id': str(session.id),
            'title': session.title,
            'description': session.description,
            'schedule': session.schedule.isoformat(),
            'mentor': session.mentor.username,
            'current_participants': session.current_participants,
            'max_participants': session.max_participants,
            'score': score,
        })
    
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommended_sessions(request):
    """Get personalized recommendations for the user"""
    # Simple recommendation: trending sessions that user hasn't booked
    user = request.user
    limit = int(request.GET.get('limit', 5))
    
    if user.is_learner:
        # Get sessions user hasn't booked
        booked_session_ids = user.bookings.values_list('session_id', flat=True)
        available_sessions = Session.objects.exclude(
            id__in=booked_session_ids
        ).filter(status='scheduled')
        
        # Get top trending from available sessions
        recommendations = []
        for session in available_sessions[:limit]:
            try:
                metric = session.popularity
                score = metric.calculate_score()
            except PopularityMetric.DoesNotExist:
                score = 0
            
            recommendations.append({
                'id': str(session.id),
                'title': session.title,
                'description': session.description,
                'schedule': session.schedule.isoformat(),
                'mentor': session.mentor.username,
                'current_participants': session.current_participants,
                'max_participants': session.max_participants,
                'score': score,
            })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return Response(recommendations[:limit])
    
    else:
        # For mentors, show trending sessions in their domain
        return Response([])

def update_session_popularity(session_id, action):
    """Helper function to update popularity metrics"""
    try:
        session = Session.objects.get(id=session_id)
        metric, created = PopularityMetric.objects.get_or_create(
            session=session,
            defaults={
                'view_count': 0,
                'booking_count': 0,
                'completion_rate': 0.0,
                'rating_average': 0.0,
            }
        )
        
        if action == 'view':
            metric.view_count += 1
        elif action == 'book':
            metric.booking_count += 1
        elif action == 'complete':
            # Update completion rate
            total_bookings = session.bookings.filter(status='confirmed').count()
            completed_bookings = session.bookings.filter(
                status='confirmed',
                session__status='completed'
            ).count()
            
            if total_bookings > 0:
                metric.completion_rate = (completed_bookings / total_bookings) * 100
        
        # Update rating average
        feedbacks = session.feedback.all()
        if feedbacks:
            total_rating = sum(f.rating for f in feedbacks)
            metric.rating_average = total_rating / len(feedbacks)
        
        metric.save()
        
    except Session.DoesNotExist:
        pass
