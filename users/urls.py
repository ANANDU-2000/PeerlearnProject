from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import logout
from django.shortcuts import redirect
from . import views, api_views, admin_api, learner_payment_api, skill_suggestion_api
from . import admin_views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('register/steps/', views.register_steps_view, name='register_steps'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/advanced/', views.advanced_profile_view, name='advanced_profile'),
    path('dashboard/mentor/', views.mentor_dashboard, name='mentor_dashboard'),
    path('dashboard/learner/', views.learner_dashboard, name='learner_dashboard'),
    path('dashboard/admin/', views.admin_dashboard_redirect, name='admin_dashboard'),
    path('portfolio/anandu/', views.anandu_portfolio, name='anandu_portfolio'),
    path('mentors/<uuid:mentor_id>/profile/', views.mentor_profile_view, name='mentor_profile'),
    
    # API endpoints for live validation
    path('api/check-email/', api_views.check_email_exists, name='check_email_exists'),
    path('api/check-username/', views.check_username_api, name='check_username_api'),
    path('api/check-email-new/', views.check_email_api, name='check_email_api'),
    path('api/users/profile/update/', views.update_profile_api, name='api_update_profile'),
    
    # Enhanced Profile & Social API
    path('api/user/profile-image/', api_views.upload_profile_image, name='api_upload_profile_image'),
    path('api/user/profile/', api_views.update_profile, name='api_update_profile_new'),
    path('api/user/sessions/', api_views.get_user_sessions, name='api_user_sessions'),
    path('api/user/payments/', api_views.get_payment_history, name='api_payment_history'),
    path('api/user/activity/', api_views.get_user_activity, name='api_user_activity'),
    path('api/user/followers/', api_views.get_followers, name='api_get_followers'),
    path('api/user/following/', api_views.get_following, name='api_get_following'),
    # FIXED: Follow system with complete API
    path('api/user/follow/<uuid:user_id>/', api_views.follow_user, name='api_follow_user'),
    path('api/user/unfollow/<uuid:user_id>/', api_views.unfollow_user, name='api_unfollow_user'),
    path('api/user/follow-status/<uuid:user_id>/', api_views.follow_status, name='api_follow_status'),
    path('api/user/followers/<uuid:user_id>/', api_views.get_followers, name='api_get_followers'),
    path('api/user/following/<uuid:user_id>/', api_views.get_following, name='api_get_following'),
    path('api/user/search/', api_views.search_users, name='api_search_users'),
    path('api/user/mentor-followers-sessions/', api_views.get_mentor_followers_sessions, name='api_mentor_followers_sessions'),
    # path('api/feedback/<uuid:feedback_id>/reply/', api_views.reply_to_feedback, name='api_reply_feedback'),  # Temporarily disabled
    
    # Advanced ML-powered skill suggestions
    path('api/skill-suggestions/', skill_suggestion_api.get_skill_suggestions, name='skill_suggestions'),
    
    # Admin API endpoints - Real Data
    path('api/admin/real-stats/', admin_api.get_real_admin_stats, name='admin_real_stats'),
    path('api/admin/real-users/', admin_api.get_real_users, name='admin_real_users'),
    # Removed get_live_sessions as it's not in admin_api
    path('api/admin/toggle-user-status/<uuid:user_id>/', admin_api.update_user_status, name='admin_toggle_user_status'),
    path('api/admin/recent-activity/', admin_api.get_recent_activity, name='admin_recent_activity'),
    path('api/admin/notifications/', admin_api.get_notifications, name='admin_notifications'),
    path('api/admin/mark-read/<uuid:notification_id>/', admin_api.mark_notification_read, name='admin_mark_notification_read'),
    path('api/admin/send-notification/', admin_api.send_user_notification, name='admin_send_notification'),
    
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
]
