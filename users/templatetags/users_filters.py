from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter and return a list"""
    if not value:
        return []
    return [item.strip() for item in str(value).split(delimiter) if item.strip()]

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary using key"""
    return dictionary.get(key, '')

@register.filter
def multiply(value, multiplier):
    """Multiply a value by multiplier"""
    try:
        return float(value) * float(multiplier)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """Calculate percentage of value from total"""
    try:
        if float(total) == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError):
        return 0

@register.filter
def duration_format(minutes):
    """Format duration in minutes to hours and minutes"""
    try:
        minutes = int(minutes)
        hours = minutes // 60
        mins = minutes % 60
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"
    except (ValueError, TypeError):
        return "0m"

@register.filter
def currency_format(amount):
    """Format currency amount"""
    try:
        amount = float(amount)
        if amount >= 1000:
            return f"₹{amount/1000:.1f}K"
        return f"₹{amount:.0f}"
    except (ValueError, TypeError):
        return "₹0"

@register.filter
def status_badge_class(status):
    """Return CSS class for status badge"""
    status_classes = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'confirmed': 'bg-green-100 text-green-800',
        'completed': 'bg-blue-100 text-blue-800',
        'cancelled': 'bg-red-100 text-red-800',
        'scheduled': 'bg-purple-100 text-purple-800',
        'live': 'bg-red-100 text-red-800 animate-pulse',
        'draft': 'bg-gray-100 text-gray-800',
    }
    return status_classes.get(status.lower(), 'bg-gray-100 text-gray-800')

@register.filter
def rating_stars(rating):
    """Generate star rating HTML"""
    try:
        rating = float(rating)
        full_stars = int(rating)
        half_star = 1 if (rating - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        html = ""
        for i in range(full_stars):
            html += '<i class="fas fa-star text-yellow-400"></i>'
        if half_star:
            html += '<i class="fas fa-star-half-alt text-yellow-400"></i>'
        for i in range(empty_stars):
            html += '<i class="far fa-star text-gray-300"></i>'
        
        return mark_safe(html)
    except (ValueError, TypeError):
        return mark_safe('<i class="far fa-star text-gray-300"></i>' * 5)

@register.filter
def format_duration(seconds):
    """Format duration in seconds to readable format"""
    try:
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {remaining_seconds}s"
        elif minutes > 0:
            return f"{minutes}m {remaining_seconds}s"
        else:
            return f"{remaining_seconds}s"
    except (ValueError, TypeError):
        return "0s"
