from django.urls import path
from . import admin_views, admin_api

app_name = 'admin_dashboard'

urlpatterns = [
    path('', admin_views.admin_complete_dashboard, name='dashboard'),
    path('dashboard/', admin_views.admin_complete_dashboard, name='complete_dashboard'),
    path('direct-login/', admin_views.direct_admin_login, name='direct_login'),
    path('create-user/', admin_views.admin_create_user_manual, name='create_user'),
    path('create-session/', admin_views.admin_create_session_manual, name='create_session'),
    path('system-logs/', admin_views.admin_system_logs, name='system_logs'),
    path('send-email/', admin_views.admin_send_email, name='send_email'),
    path('email-templates/', admin_views.admin_email_templates, name='email_templates'),
    path('export-data/', admin_views.admin_export_data, name='export_data'),
    path('model-data/<str:model_name>/', admin_views.admin_model_data, name='model_data'),
    
    # API endpoints that actually exist
    path('api/analytics/', admin_views.admin_analytics_api, name='analytics_api'),
    path('api/notifications/', admin_views.admin_notifications, name='notifications'),
    path('api/mark-notification-read/', admin_views.mark_notification_read, name='mark_notification_read'),
    
    # FIXED: Complete Admin API endpoints
    path('api/admin/users/', admin_api.get_real_users, name='admin_get_real_users'),
    path('api/admin/users/online/', admin_api.get_online_users, name='admin_get_online_users'),
    path('api/admin/users/banned/', admin_api.get_banned_users, name='admin_get_banned_users'),
    path('api/admin/users/create/', admin_api.create_admin_user, name='admin_create_user'),
    path('api/admin/user/<uuid:user_id>/status/', admin_api.update_user_status, name='admin_update_user_status'),
    path('api/admin/user/<uuid:user_id>/activities/', admin_api.get_user_activities, name='admin_get_user_activities'),
    path('api/admin/stats/', admin_api.get_admin_stats, name='admin_get_stats'),
    
    # Enhanced Real-time Admin APIs
    path('api/real-stats/', admin_api.get_real_admin_stats, name='admin_real_stats'),
    path('api/real-users/', admin_api.get_real_users, name='admin_real_users'),
    path('api/live-sessions/', admin_api.get_real_admin_stats, name='admin_live_sessions'),
    path('api/notifications/', admin_api.get_notifications, name='admin_notifications'),
    path('api/recent-activity/', admin_api.get_recent_activity, name='admin_recent_activity'),
    path('api/toggle-user-status/<uuid:user_id>/', admin_api.update_user_status, name='toggle_user_status'),
    
    # Real-time Admin APIs
    path('api/real-data/', admin_api.admin_real_data_api, name='admin_real_data_api'),
    path('api/user-action/', admin_api.admin_user_action_api, name='admin_user_action_api'),
]