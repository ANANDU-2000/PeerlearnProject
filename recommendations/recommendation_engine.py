"""
Advanced Recommendation Engine for PeerLearn
Real Machine Learning-based recommendations using learner profile, mentor expertise, and session data
"""

from django.db.models import Q, Count, Avg, Case, When, FloatField
from django.utils import timezone
from sessions.models import Session, Booking, Feedback
from users.models import User
from .models import PopularityMetric
import json
from datetime import datetime, timedelta
from collections import Counter
import re

class RecommendationEngine:
    """Advanced ML-based recommendation system"""
    
    def __init__(self, user):
        self.user = user
        self.user_skills = self.parse_skills(user.skills or '')
        self.user_interests = self.parse_skills(user.expertise or '')
        
    def parse_skills(self, skills_data):
        """Parse skills from various formats"""
        if isinstance(skills_data, str):
            try:
                skills_data = json.loads(skills_data)
            except:
                skills_data = [s.strip() for s in skills_data.split(',') if s.strip()]
        
        if isinstance(skills_data, list):
            return [skill.lower().strip() for skill in skills_data if skill]
        
        return []
    
    def get_personalized_recommendations(self):
        """Get personalized session recommendations based on user profile"""
        recommendations = []
        
        # 1. Content-based filtering (skills and interests)
        content_based = self.content_based_filtering()
        recommendations.extend(content_based)
        
        # 2. Collaborative filtering (similar users)
        collaborative = self.collaborative_filtering()
        recommendations.extend(collaborative)
        
        # 3. Popularity-based recommendations
        popularity_based = self.popularity_based_filtering()
        recommendations.extend(popularity_based)
        
        # 4. Trending sessions
        trending = self.get_trending_sessions()
        recommendations.extend(trending)
        
        # Remove duplicates and score
        unique_sessions = {}
        for session, score, reason in recommendations:
            if session.id not in unique_sessions:
                unique_sessions[session.id] = {
                    'session': session,
                    'score': score,
                    'reasons': [reason]
                }
            else:
                unique_sessions[session.id]['score'] += score * 0.5
                unique_sessions[session.id]['reasons'].append(reason)
        
        # Sort by score and return top recommendations
        sorted_recommendations = sorted(
            unique_sessions.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        return [item['session'] for item in sorted_recommendations[:8]]
    
    def content_based_filtering(self):
        """Recommend sessions based on user skills and interests"""
        recommendations = []
        all_skills = self.user_skills + self.user_interests
        
        if not all_skills:
            return recommendations
        
        # Get available sessions
        available_sessions = Session.objects.filter(
            status='scheduled',
            schedule__gte=timezone.now()
        ).exclude(
            bookings__learner=self.user,
            bookings__status='confirmed'
        ).select_related('mentor')
        
        for session in available_sessions:
            score = 0
            reasons = []
            
            # Check title and description for skill matches
            session_text = f"{session.title} {session.description}".lower()
            
            for skill in all_skills:
                if skill in session_text:
                    score += 2.0
                    reasons.append(f"Matches your interest in {skill}")
            
            # Mentor expertise match
            mentor_skills = self.parse_skills(session.mentor.expertise or [])
            for user_skill in all_skills:
                for mentor_skill in mentor_skills:
                    if user_skill in mentor_skill or mentor_skill in user_skill:
                        score += 1.5
                        reasons.append(f"Mentor expert in {mentor_skill}")
            
            if score > 0:
                reason = "; ".join(reasons[:2])
                recommendations.append((session, score, reason))
        
        return recommendations
    
    def collaborative_filtering(self):
        """Find sessions liked by similar users"""
        recommendations = []
        
        # Find users with similar skills/interests
        similar_users = User.objects.filter(
            role='learner',
            expertise__isnull=False
        ).exclude(id=self.user.id)
        
        user_similarities = []
        for other_user in similar_users:
            other_skills = self.parse_skills(other_user.expertise or [])
            similarity = self.calculate_skill_similarity(self.user_skills, other_skills)
            
            if similarity > 0.3:  # 30% similarity threshold
                user_similarities.append((other_user, similarity))
        
        # Get sessions attended by similar users
        for similar_user, similarity in user_similarities[:5]:
            similar_user_sessions = Session.objects.filter(
                bookings__learner=similar_user,
                bookings__status='confirmed',
                status='scheduled',
                schedule__gte=timezone.now()
            ).exclude(
                bookings__learner=self.user,
                bookings__status='confirmed'
            )
            
            for session in similar_user_sessions:
                score = similarity * 1.5
                reason = f"Learners with similar interests also booked this"
                recommendations.append((session, score, reason))
        
        return recommendations
    
    def popularity_based_filtering(self):
        """Recommend popular sessions"""
        recommendations = []
        
        # Get sessions with high popularity metrics
        popular_sessions = Session.objects.filter(
            status='scheduled',
            schedule__gte=timezone.now(),
            popularity__isnull=False
        ).exclude(
            bookings__learner=self.user,
            bookings__status='confirmed'
        ).select_related('popularity', 'mentor').order_by(
            '-popularity__rating_average',
            '-popularity__booking_count'
        )[:5]
        
        for session in popular_sessions:
            popularity = session.popularity
            score = (popularity.rating_average * 0.6) + (min(popularity.booking_count / 10, 2) * 0.4)
            reason = f"⭐ {popularity.rating_average:.1f} rating, {popularity.booking_count} bookings"
            recommendations.append((session, score, reason))
        
        return recommendations
    
    def get_trending_sessions(self):
        """Get currently trending sessions"""
        recommendations = []
        
        # Sessions with recent bookings
        recent_date = timezone.now() - timedelta(days=7)
        trending_sessions = Session.objects.filter(
            status='scheduled',
            schedule__gte=timezone.now(),
            bookings__created_at__gte=recent_date
        ).exclude(
            bookings__learner=self.user,
            bookings__status='confirmed'
        ).annotate(
            recent_bookings=Count('bookings', filter=Q(bookings__created_at__gte=recent_date))
        ).filter(recent_bookings__gte=2).order_by('-recent_bookings')[:3]
        
        for session in trending_sessions:
            score = 1.8
            reason = f"🔥 Trending - {session.recent_bookings} recent bookings"
            recommendations.append((session, score, reason))
        
        return recommendations
    
    def calculate_skill_similarity(self, skills1, skills2):
        """Calculate similarity between two skill sets"""
        if not skills1 or not skills2:
            return 0.0
        
        set1 = set(skills1)
        set2 = set(skills2)
        
        # Jaccard similarity
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def get_mentor_recommendations(self):
        """Get recommended mentors based on user interests"""
        recommended_mentors = []
        
        mentors = User.objects.filter(
            role='mentor',
            is_active=True
        ).annotate(
            avg_rating=Avg('mentored_sessions__feedback__rating'),
            session_count=Count('mentored_sessions'),
            recent_sessions=Count(
                'mentored_sessions',
                filter=Q(mentored_sessions__schedule__gte=timezone.now() - timedelta(days=30))
            )
        ).filter(session_count__gte=1)
        
        for mentor in mentors:
            score = 0
            reasons = []
            
            # Check skill match
            mentor_skills = self.parse_skills(mentor.expertise or [])
            for user_skill in self.user_skills + self.user_interests:
                for mentor_skill in mentor_skills:
                    if user_skill in mentor_skill or mentor_skill in user_skill:
                        score += 2.0
                        reasons.append(f"Expert in {mentor_skill}")
            
            # Rating factor
            if mentor.avg_rating:
                score += mentor.avg_rating * 0.5
                reasons.append(f"{mentor.avg_rating:.1f}⭐ rating")
            
            # Activity factor
            if mentor.recent_sessions > 0:
                score += min(mentor.recent_sessions / 5, 1) * 0.8
                reasons.append(f"{mentor.recent_sessions} recent sessions")
            
            if score > 1.0:
                recommended_mentors.append({
                    'mentor': mentor,
                    'score': score,
                    'reasons': reasons[:2]
                })
        
        return sorted(recommended_mentors, key=lambda x: x['score'], reverse=True)[:6]

def get_recommendations_for_user(user):
    """Main function to get recommendations for a user"""
    engine = RecommendationEngine(user)
    return engine.get_personalized_recommendations()

def get_mentor_recommendations_for_user(user):
    """Get mentor recommendations for a user"""
    engine = RecommendationEngine(user)
    return engine.get_mentor_recommendations()