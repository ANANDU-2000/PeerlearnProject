from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from sessions import api_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('sessions/', include('sessions.urls')),
    path('api/sessions/', include('sessions.urls')),
    
    # Direct API endpoints
    path('api/sessions/mentor-data/', api_views.mentor_dashboard_data, name='mentor_dashboard_data'),
    path('api/follow-mentor/', api_views.follow_mentor_api, name='follow_mentor_api'),
    path('api/request-mentor-session/', api_views.request_mentor_session_api, name='request_mentor_session_api'),
    path('recommendations/', include('recommendations.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
