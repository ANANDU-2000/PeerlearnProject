from django.db import models
from sessions.models import Session

class PopularityMetric(models.Model):
    """Track session popularity for recommendations"""
    session = models.OneToOneField(Session, on_delete=models.CASCADE, related_name='popularity')
    view_count = models.IntegerField(default=0)
    booking_count = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)  # Percentage of bookings that were completed
    rating_average = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_score(self):
        """Calculate recommendation score based on various factors"""
        # Simple scoring algorithm - can be made more sophisticated
        score = (
            self.view_count * 0.1 +
            self.booking_count * 0.3 +
            self.completion_rate * 0.4 +
            self.rating_average * 0.2
        )
        return score
    
    def __str__(self):
        return f"Popularity for {self.session.title}"
