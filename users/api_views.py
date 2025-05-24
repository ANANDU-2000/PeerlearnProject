from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
import json

User = get_user_model()

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