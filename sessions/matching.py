"""
Intelligent Learner-Mentor Matching System
Matches learners with mentors based on skills, interests, availability, and preferences
"""

import json
from typing import List, Dict, Tuple
from django.db.models import Q, Count, Avg
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Session, Booking, Feedback

User = get_user_model()

class MentorMatchingEngine:
    """Advanced matching engine for learner-mentor connections"""
    
    def __init__(self):
        self.skill_weights = {
            'exact_match': 10,
            'related_match': 7,
            'domain_match': 5,
            'experience_match': 3
        }
        
        self.availability_weights = {
            'immediate': 10,
            'same_day': 8,
            'within_week': 6,
            'flexible': 4
        }
        
        self.rating_weights = {
            'rating_boost': 5,
            'session_count_boost': 3,
            'response_time_boost': 2
        }

    def find_best_mentors(self, learner_profile: Dict, max_results: int = 10) -> List[Dict]:
        """
        Find the best mentors for a learner based on comprehensive matching
        
        Args:
            learner_profile: Dict containing learner's requirements
            max_results: Maximum number of mentors to return
            
        Returns:
            List of matched mentors with scores
        """
        
        # Get all available mentors
        mentors = User.objects.filter(
            role='mentor',
            is_active=True,
            is_verified=True
        ).select_related().prefetch_related('mentor_sessions', 'received_feedback')
        
        matched_mentors = []
        
        for mentor in mentors:
            score = self._calculate_mentor_score(mentor, learner_profile)
            if score > 20:  # Minimum threshold
                matched_mentors.append({
                    'mentor': mentor,
                    'score': score,
                    'match_reasons': self._get_match_reasons(mentor, learner_profile),
                    'availability': self._get_mentor_availability(mentor),
                    'stats': self._get_mentor_stats(mentor)
                })
        
        # Sort by score and return top results
        matched_mentors.sort(key=lambda x: x['score'], reverse=True)
        return matched_mentors[:max_results]

    def _calculate_mentor_score(self, mentor: User, learner_profile: Dict) -> float:
        """Calculate comprehensive matching score for a mentor"""
        
        total_score = 0
        
        # 1. Skills matching
        skills_score = self._calculate_skills_score(mentor, learner_profile)
        total_score += skills_score
        
        # 2. Domain matching
        domain_score = self._calculate_domain_score(mentor, learner_profile)
        total_score += domain_score
        
        # 3. Availability matching
        availability_score = self._calculate_availability_score(mentor, learner_profile)
        total_score += availability_score
        
        # 4. Rating and experience boost
        rating_score = self._calculate_rating_score(mentor)
        total_score += rating_score
        
        # 5. Price compatibility
        price_score = self._calculate_price_score(mentor, learner_profile)
        total_score += price_score
        
        # 6. Recent activity boost
        activity_score = self._calculate_activity_score(mentor)
        total_score += activity_score
        
        return round(total_score, 2)

    def _calculate_skills_score(self, mentor: User, learner_profile: Dict) -> float:
        """Calculate skill matching score"""
        
        mentor_skills = set(skill.strip().lower() for skill in (mentor.skills or '').split(',') if skill.strip())
        required_skills = set(skill.strip().lower() for skill in learner_profile.get('skills', []))
        
        if not required_skills:
            return 0
        
        exact_matches = len(mentor_skills.intersection(required_skills))
        related_matches = self._find_related_skills(mentor_skills, required_skills)
        
        score = (exact_matches * self.skill_weights['exact_match'] + 
                related_matches * self.skill_weights['related_match'])
        
        # Normalize by number of required skills
        return min(score / len(required_skills) * 2, 25)

    def _calculate_domain_score(self, mentor: User, learner_profile: Dict) -> float:
        """Calculate domain expertise matching"""
        
        learner_domain = learner_profile.get('domain', '').lower()
        mentor_domain = getattr(mentor, 'domain', '').lower() if hasattr(mentor, 'domain') else ''
        
        if learner_domain and mentor_domain:
            if learner_domain == mentor_domain:
                return self.skill_weights['domain_match']
            elif learner_domain in mentor_domain or mentor_domain in learner_domain:
                return self.skill_weights['domain_match'] * 0.7
        
        return 0

    def _calculate_availability_score(self, mentor: User, learner_profile: Dict) -> float:
        """Calculate availability matching score"""
        
        urgency = learner_profile.get('urgency', 'flexible')
        preferred_times = learner_profile.get('preferred_times', [])
        
        # Check mentor's upcoming availability
        upcoming_sessions = Session.objects.filter(
            mentor=mentor,
            schedule__gte=timezone.now(),
            schedule__lte=timezone.now() + timedelta(days=7),
            status__in=['scheduled', 'live']
        ).count()
        
        # Lower session count = better availability
        availability_factor = max(0, 10 - upcoming_sessions)
        
        # Urgency matching
        urgency_score = self.availability_weights.get(urgency, 4)
        
        return (availability_factor + urgency_score) / 2

    def _calculate_rating_score(self, mentor: User) -> float:
        """Calculate rating and reputation score"""
        
        # Get mentor's average rating
        avg_rating = Feedback.objects.filter(
            session__mentor=mentor
        ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        # Get total sessions completed
        completed_sessions = Session.objects.filter(
            mentor=mentor,
            status='completed'
        ).count()
        
        # Calculate score
        rating_boost = (avg_rating / 5) * self.rating_weights['rating_boost']
        session_boost = min(completed_sessions / 10, 1) * self.rating_weights['session_count_boost']
        
        return rating_boost + session_boost

    def _calculate_price_score(self, mentor: User, learner_profile: Dict) -> float:
        """Calculate price compatibility score"""
        
        learner_budget = learner_profile.get('budget')
        mentor_rate = getattr(mentor, 'hourly_rate', 0)
        
        if not learner_budget or not mentor_rate:
            return 5  # Neutral score
        
        try:
            # Extract numeric budget (assuming format like "₹500-1000" or "500")
            if '-' in str(learner_budget):
                budget_range = [int(x.strip('₹').strip()) for x in str(learner_budget).split('-')]
                max_budget = max(budget_range)
            else:
                max_budget = int(str(learner_budget).strip('₹').strip())
            
            if mentor_rate <= max_budget:
                return 10  # Perfect price match
            elif mentor_rate <= max_budget * 1.2:
                return 7   # Slightly over budget
            elif mentor_rate <= max_budget * 1.5:
                return 4   # Moderately over budget
            else:
                return 1   # Significantly over budget
                
        except (ValueError, TypeError):
            return 5  # Neutral if can't parse

    def _calculate_activity_score(self, mentor: User) -> float:
        """Calculate recent activity boost"""
        
        # Check last activity
        if hasattr(mentor, 'last_active') and mentor.last_active:
            hours_since_active = (timezone.now() - mentor.last_active).total_seconds() / 3600
            
            if hours_since_active < 1:
                return 5  # Very recently active
            elif hours_since_active < 24:
                return 3  # Active today
            elif hours_since_active < 168:  # 1 week
                return 1  # Active this week
        
        return 0

    def _find_related_skills(self, mentor_skills: set, required_skills: set) -> int:
        """Find related skills using simple keyword matching"""
        
        skill_relations = {
            'python': ['django', 'flask', 'fastapi', 'programming'],
            'javascript': ['react', 'vue', 'angular', 'node.js', 'web development'],
            'web development': ['html', 'css', 'javascript', 'frontend', 'backend'],
            'data science': ['python', 'r', 'statistics', 'machine learning', 'analytics'],
            'machine learning': ['python', 'tensorflow', 'pytorch', 'data science', 'ai'],
            'mobile development': ['android', 'ios', 'react native', 'flutter', 'swift', 'kotlin'],
        }
        
        related_count = 0
        for required_skill in required_skills:
            if required_skill in skill_relations:
                related_skills = set(skill_relations[required_skill])
                if mentor_skills.intersection(related_skills):
                    related_count += 1
        
        return related_count

    def _get_match_reasons(self, mentor: User, learner_profile: Dict) -> List[str]:
        """Get human-readable reasons for the match"""
        
        reasons = []
        
        # Skill matches
        mentor_skills = set(skill.strip().lower() for skill in (mentor.skills or '').split(',') if skill.strip())
        required_skills = set(skill.strip().lower() for skill in learner_profile.get('skills', []))
        
        skill_matches = mentor_skills.intersection(required_skills)
        if skill_matches:
            reasons.append(f"Expert in {', '.join(list(skill_matches)[:3])}")
        
        # Rating
        avg_rating = Feedback.objects.filter(
            session__mentor=mentor
        ).aggregate(avg_rating=Avg('rating'))['avg_rating']
        
        if avg_rating and avg_rating >= 4.5:
            reasons.append(f"Highly rated ({avg_rating:.1f}/5 stars)")
        
        # Experience
        completed_sessions = Session.objects.filter(
            mentor=mentor,
            status='completed'
        ).count()
        
        if completed_sessions > 10:
            reasons.append(f"Experienced ({completed_sessions} sessions completed)")
        
        # Recent activity
        if hasattr(mentor, 'last_active') and mentor.last_active:
            hours_since_active = (timezone.now() - mentor.last_active).total_seconds() / 3600
            if hours_since_active < 24:
                reasons.append("Recently active")
        
        return reasons[:4]  # Limit to top 4 reasons

    def _get_mentor_availability(self, mentor: User) -> Dict:
        """Get mentor's availability information"""
        
        # Get upcoming sessions
        upcoming_sessions = Session.objects.filter(
            mentor=mentor,
            schedule__gte=timezone.now(),
            schedule__lte=timezone.now() + timedelta(days=7),
            status__in=['scheduled']
        ).count()
        
        # Determine availability status
        if upcoming_sessions == 0:
            availability_status = "Fully Available"
        elif upcoming_sessions <= 3:
            availability_status = "Mostly Available"
        elif upcoming_sessions <= 6:
            availability_status = "Limited Availability"
        else:
            availability_status = "Busy"
        
        return {
            'status': availability_status,
            'upcoming_sessions': upcoming_sessions,
            'can_schedule_today': upcoming_sessions < 2
        }

    def _get_mentor_stats(self, mentor: User) -> Dict:
        """Get mentor's statistics"""
        
        total_sessions = Session.objects.filter(mentor=mentor, status='completed').count()
        avg_rating = Feedback.objects.filter(
            session__mentor=mentor
        ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        response_time = "< 1 hour"  # This would be calculated from actual data
        
        return {
            'total_sessions': total_sessions,
            'average_rating': round(avg_rating, 1),
            'response_time': response_time,
            'hourly_rate': getattr(mentor, 'hourly_rate', 0),
            'experience_years': getattr(mentor, 'experience_years', 0)
        }

    def find_session_recommendations(self, learner: User, limit: int = 5) -> List[Session]:
        """Find recommended sessions for a learner"""
        
        learner_interests = set(interest.strip().lower() 
                             for interest in (learner.interests or '').split(',') 
                             if interest.strip())
        
        # Get upcoming sessions
        upcoming_sessions = Session.objects.filter(
            status='scheduled',
            schedule__gte=timezone.now(),
            max_participants__gt=Count('bookings')
        ).select_related('mentor').prefetch_related('bookings')
        
        scored_sessions = []
        
        for session in upcoming_sessions:
            score = 0
            
            # Interest matching
            session_skills = set(skill.strip().lower() 
                               for skill in (session.skills or '').split(',') 
                               if skill.strip())
            
            interest_matches = len(learner_interests.intersection(session_skills))
            score += interest_matches * 5
            
            # Mentor rating
            mentor_rating = Feedback.objects.filter(
                session__mentor=session.mentor
            ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
            
            score += mentor_rating
            
            # Availability (sooner is better, but not too soon)
            hours_until_session = (session.schedule - timezone.now()).total_seconds() / 3600
            if 24 <= hours_until_session <= 168:  # 1-7 days
                score += 3
            elif 2 <= hours_until_session < 24:  # 2-24 hours
                score += 5
            
            # Session popularity (not too full, not empty)
            fill_rate = session.current_participants / session.max_participants
            if 0.3 <= fill_rate <= 0.8:
                score += 2
            
            if score > 5:  # Minimum threshold
                scored_sessions.append((session, score))
        
        # Sort by score and return top sessions
        scored_sessions.sort(key=lambda x: x[1], reverse=True)
        return [session for session, score in scored_sessions[:limit]]


# Utility functions for easy access
def get_mentor_recommendations(learner_profile: Dict, max_results: int = 10) -> List[Dict]:
    """Get mentor recommendations for a learner profile"""
    engine = MentorMatchingEngine()
    return engine.find_best_mentors(learner_profile, max_results)

def get_session_recommendations(learner: User, limit: int = 5) -> List[Session]:
    """Get session recommendations for a learner"""
    engine = MentorMatchingEngine()
    return engine.find_session_recommendations(learner, limit) 