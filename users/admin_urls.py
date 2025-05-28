from django.urls import path
from . import admin_views

app_name = 'admin_dashboard'

urlpatterns = [
    # Main admin dashboard
    path('dashboard/', admin_views.admin_dashboard, name='dashboard'),
    
    # API endpoints for real-time data
    path('api/users/', admin_views.admin_users_api, name='users_api'),
    path('api/live-sessions/', admin_views.admin_live_sessions_api, name='live_sessions_api'),
    path('api/analytics/', admin_views.admin_analytics_api, name='analytics_api'),
    path('api/live-activity/', admin_views.admin_live_activity_api, name='live_activity_api'),
    path('api/system-stats/', admin_views.admin_system_stats, name='system_stats_api'),
    
    # Action endpoints
    path('api/user-action/', admin_views.admin_user_action, name='user_action'),
    path('api/session-action/', admin_views.admin_session_action, name='session_action'),
    
    # Enhanced Mobile Admin Features
    path('direct-login/', admin_views.direct_admin_login, name='direct_admin_login'),
    path('api/create-user/', admin_views.admin_create_user_manual, name='create_user_manual'),
    path('api/create-session/', admin_views.admin_create_session_manual, name='create_session_manual'),
    path('api/model-data/<str:model_name>/', admin_views.admin_model_data, name='model_data'),
    path('api/export-data/', admin_views.admin_export_data, name='export_data'),
    path('api/system-logs/', admin_views.admin_system_logs, name='system_logs'),
    
    # Email Support
    path('api/send-email/', admin_views.admin_send_email, name='send_email'),
    path('api/email-templates/', admin_views.admin_email_templates, name='email_templates'),
    
    # Notifications System
    path('api/notifications/', admin_views.admin_notifications, name='notifications'),
    path('api/mark-notification-read/', admin_views.mark_notification_read, name='mark_notification_read'),
]