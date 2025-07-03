# In your main project urls.py - Remove duplicates
# In your main project urls.py - Remove duplicates

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from sessions import api_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-dashboard/', include('users.admin_urls')),
    path('', include('users.urls')),
    path('sessions/', include('sessions.urls')),  # This includes all session URLs
    
    # Add the start session URL directly here
    path('api/sessions/<uuid:session_id>/start/', api_views.start_session_api, name='api_start_session'),
    
    # Add the end session URL directly here to fix 404 issue
    path('api/sessions/<uuid:session_id>/end/', api_views.end_session, name='api_end_session_direct'),
    
    # Add the mark-ready URL directly here temporarily
    path('api/sessions/<uuid:session_id>/mark-ready/', api_views.mark_ready_unified, name='api_mark_ready'),
    
    # API Routes for Mentor Dashboard
    path('api/sessions/mentor-data/', api_views.mentor_dashboard_data, name='mentor_dashboard_data'),
    path('api/sessions/learner-data/', api_views.learner_dashboard_data, name='learner_dashboard_data'),
    path('api/requests/', api_views.get_requests_api, name='api_get_requests'),
    path('api/notifications/', api_views.get_notifications_api, name='get_notifications_api'),
    path('api/notifications/<int:notification_id>/read/', api_views.mark_notification_read_api, name='mark_notification_read_api'),
    path('api/notifications/read/', api_views.mark_notifications_read, name='mark_notifications_read'),
    path('api/analytics/', api_views.mentor_analytics_api, name='mentor_analytics_api'),
    
    # Other API routes
    path('api/follow-mentor/', api_views.follow_mentor_api, name='follow_mentor_api'),
    path('api/request-mentor-session/', api_views.request_mentor_session_api, name='request_mentor_session_api'),
    path('recommendations/', include('recommendations.urls')),
    
    # Password Reset System
    path('auth/', include('users.password_urls')),
    
    # User Feedback System
    path('', include('users.feedback_urls')),
    
    # LIVE VIDEO DEMO
    path('demo/video/', TemplateView.as_view(template_name='demo_video_room.html'), name='demo_video_room'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from django.views.generic import TemplateView
# from sessions import api_views

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('admin-dashboard/', include('users.admin_urls')),
#     path('', include('users.urls')),
#     path('sessions/', include('sessions.urls')),  # This includes all session URLs
    
#     # Only keep URLs that are NOT already in sessions/urls.py
#     path('api/sessions/mentor-data/', api_views.mentor_dashboard_data, name='mentor_dashboard_data'),
#     path('api/follow-mentor/', api_views.follow_mentor_api, name='follow_mentor_api'),
#     path('api/request-mentor-session/', api_views.request_mentor_session_api, name='request_mentor_session_api'),
#     path('recommendations/', include('recommendations.urls')),
    
#     # Password Reset System
#     path('auth/', include('users.password_urls')),
    
#     # User Feedback System
#     path('', include('users.feedback_urls')),
    
#     # LIVE VIDEO DEMO
#     path('demo/video/', TemplateView.as_view(template_name='demo_video_room.html'), name='demo_video_room'),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)