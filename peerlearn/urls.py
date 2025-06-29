from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from sessions import api_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-dashboard/', include('users.admin_urls')),  # Modern admin dashboard
    path('', include('users.urls')),
    path('sessions/', include('sessions.urls')),
    path('api/sessions/<uuid:session_id>/bookings/', api_views.session_bookings, name='api_session_bookings'),
    path('api/sessions/<uuid:session_id>/send-reminders/', api_views.send_session_reminders, name='api_send_reminders'),
    path('api/sessions/<uuid:session_id>/ready/', api_views.mark_ready, name='api_mark_ready'),
    path('api/sessions/<uuid:session_id>/start/', api_views.start_session_api, name='api_start_session'),
    
    # Direct API endpoints
    path('api/sessions/mentor-data/', api_views.mentor_dashboard_data, name='mentor_dashboard_data'),
    path('api/follow-mentor/', api_views.follow_mentor_api, name='follow_mentor_api'),
    path('api/request-mentor-session/', api_views.request_mentor_session_api, name='request_mentor_session_api'),
    path('recommendations/', include('recommendations.urls')),
    
    # Password Reset System
    path('auth/', include('users.password_urls')),
    
    # User Feedback System
    path('', include('users.feedback_urls')),
    
    # LIVE VIDEO DEMO - DIRECT ACCESS (NO LOGIN NEEDED)
    path('demo/video/', TemplateView.as_view(template_name='demo_video_room.html'), name='demo_video_room'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
