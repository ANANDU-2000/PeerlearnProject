from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import logout
from django.shortcuts import redirect
from . import views, api_views, admin_api, real_admin_api, learner_payment_api, learner_api

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('register/steps/', views.register_steps_view, name='register_steps'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/view/<uuid:user_id>/', views.mentor_profile_view, name='mentor_profile_view'),
    path('profile/upload-image/', views.upload_profile_image, name='upload_profile_image'),
    path('dashboard/mentor/', views.mentor_dashboard, name='mentor_dashboard'),

    path('dashboard/learner/', views.learner_dashboard, name='learner_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/communication-insights/', views.communication_insights_view, name='communication_insights'),
    path('portfolio/anandu/', views.anandu_portfolio, name='anandu_portfolio'),
    
    # API endpoints for live validation
    path('api/check-email/', api_views.check_email_exists, name='check_email_exists'),
    path('api/check-username/', views.check_username_api, name='check_username_api'),
    path('api/check-email-new/', views.check_email_api, name='check_email_api'),
    path('api/users/profile/update/', views.update_profile_api, name='api_update_profile'),
    
    # REAL Working Admin API endpoints
    path('api/admin/toggle-user-status/<uuid:user_id>/', real_admin_api.toggle_user_status, name='admin_toggle_user_status'),
    path('api/admin/real-stats/', real_admin_api.get_real_stats, name='admin_real_stats'),
    path('api/admin/real-users/', real_admin_api.get_real_users, name='admin_real_users'),
    path('api/admin/real-sessions/', real_admin_api.get_real_sessions, name='admin_real_sessions'),
    path('api/admin/real-bookings/', real_admin_api.get_real_bookings, name='admin_real_bookings'),
    path('api/admin/real-activity/', real_admin_api.get_real_activity, name='admin_real_activity'),
    path('api/admin/update-user/<uuid:user_id>/', real_admin_api.update_user, name='admin_update_user'),
    
    # Legacy Admin API endpoints
    path('api/ai-chat/', admin_api.ai_chat_endpoint, name='admin_ai_chat'),
    path('api/admin/bulk-email/', admin_api.bulk_email_endpoint, name='admin_bulk_email'),
    path('api/admin/send-notification/', admin_api.send_notification_endpoint, name='admin_send_notification'),
    path('api/admin/ban-user/<int:user_id>/', admin_api.ban_user_endpoint, name='admin_ban_user'),
    path('api/admin/delete-user/<int:user_id>/', admin_api.delete_user_endpoint, name='admin_delete_user'),
    path('api/admin/users/', admin_api.admin_users_endpoint, name='admin_users'),
    path('api/admin/stats/', admin_api.real_time_stats_endpoint, name='admin_stats'),
    path('api/admin/emergency/', admin_api.emergency_actions_endpoint, name='admin_emergency'),
    path('api/admin/create-admin/', admin_api.create_admin_endpoint, name='admin_create_admin'),
    
    # Learner Payment & Analytics API
    path('api/learner/payment-history/', learner_payment_api.get_learner_payment_history, name='learner_payment_history'),
    path('api/learner/analytics/', learner_payment_api.get_learner_analytics, name='learner_analytics'),
    path('api/learner/create-payment/', learner_payment_api.create_session_payment, name='create_session_payment'),
    path('api/learner/verify-payment/', learner_payment_api.verify_session_payment, name='verify_session_payment'),
    path('api/learner/submit-review/', learner_payment_api.submit_mentor_review, name='submit_mentor_review'),
    path('api/learner/reviews/', learner_payment_api.get_mentor_reviews, name='get_mentor_reviews'),
    
    # New Learner Dashboard API
    path('api/recommendations/ai/', learner_api.ai_recommendations_api, name='ai_recommendations'),
    path('api/session-requests/', learner_api.create_session_request_api, name='create_session_request'),
    path('api/refund-request/', learner_api.request_refund_api, name='request_refund'),
    path('api/notifications/mark-all-read/', learner_api.mark_all_notifications_read_api, name='mark_all_notifications_read'),
]
