# In your sessions/urls.py - Replace the conflicting URL patterns

from django.urls import path
from . import views, api_views
from .create_session_api import create_session_api
from django.views.generic import TemplateView

urlpatterns = [
    # Web views
    path('', views.session_list, name='session_list'),
    path('webrtc-test/', TemplateView.as_view(template_name='sessions/webrtc_test.html'), name='webrtc_test'),
    path('<uuid:session_id>/', views.session_detail_new, name='session_detail'),
    path('<uuid:session_id>/book/', views.book_session, name='book_session'),
    path('<uuid:session_id>/room/', views.session_room, name='session_room'),
    path('room/<uuid:session_id>/', views.session_room, name='session_room_alt'),
    path('<uuid:session_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('create/', views.create_session, name='create_session'),
    path('<uuid:session_id>/edit/', views.edit_session, name='edit_session'),
    path('<uuid:session_id>/publish/', views.publish_session, name='publish_session'),
    path('<uuid:session_id>/unpublish/', views.unpublish_session, name='unpublish_session'),
    path('<uuid:session_id>/payment/', views.razorpay_checkout, name='razorpay_checkout'),
    path('<uuid:session_id>/verify-payment/', views.verify_payment, name='verify_payment'),
    path('<uuid:session_id>/payment-success/', views.payment_success, name='payment_success'),
    path('<uuid:session_id>/payment-failure/', views.payment_failure, name='payment_failure'),
    
    # API endpoints
    path('api/sessions/', api_views.get_sessions_api, name='get_sessions_api'),
    path('api/sessions/create/', create_session_api, name='api_create_session'),
    path('api/sessions/<uuid:session_id>/book/', api_views.book_session, name='api_book_session'),
    path('api/sessions/<uuid:session_id>/end/', api_views.end_session, name='api_end_session'),
    path('api/sessions/<uuid:session_id>/publish/', api_views.publish_session, name='api_publish_session'),
    path('api/sessions/<uuid:session_id>/feedback/', api_views.submit_feedback, name='api_submit_feedback'),
    path('api/sessions/<uuid:session_id>/status/', api_views.get_session_status, name='api_get_session_status'),
    
    # Use the unified approach - handles both learner and mentor
    path('api/sessions/<uuid:session_id>/mark-ready/', api_views.mark_ready_unified, name='api_mark_ready_sessions'),
    
    # Request Management APIs - Enhanced
    path('api/requests/create/', api_views.create_request_api, name='create_request_api'),
    path('api/requests/mentors/', api_views.get_available_mentors, name='get_available_mentors'),
    path('api/requests/learner/', api_views.get_learner_requests, name='get_learner_requests'),
    path('api/requests/mentor/', api_views.get_mentor_requests, name='get_mentor_requests'),
    path('api/requests/respond/', api_views.respond_to_request, name='respond_to_request'),
    path('api/requests/acknowledge/', api_views.acknowledge_request_response, name='acknowledge_request_response'),
    
    # FIXED: Add missing direct accept/reject endpoints
    path('api/requests/<uuid:request_id>/accept/', api_views.accept_request, name='api_accept_request'),
    path('api/requests/<uuid:request_id>/decline/', api_views.decline_request, name='api_decline_request'),
    
    # Follow System APIs
    path('api/mentors/follow/', api_views.follow_mentor, name='follow_mentor'),
    
    # Notification endpoints
    path('api/notifications/', api_views.get_notifications_api, name='get_notifications_api'),
    path('api/notifications/recent/', api_views.get_recent_notifications_api, name='get_recent_notifications_api'),
    path('api/notifications/<int:notification_id>/read/', api_views.mark_notification_read_api, name='mark_notification_read_api'),
    path('api/notifications/read/', api_views.mark_notifications_read, name='mark_notifications_read'),
    
    # Earnings endpoints
    path('api/earnings/payout/', api_views.request_payout, name='api_request_payout'),
    
    # Dashboard data endpoints
    path('api/sessions/mentor-data/', api_views.mentor_dashboard_data, name='mentor_dashboard_data'),
    
    # Session management endpoints
    path('api/sessions/<uuid:session_id>/bookings/', api_views.session_bookings, name='api_session_bookings'),
    path('api/sessions/<uuid:session_id>/send-reminders/', api_views.send_session_reminders, name='api_send_reminders'),
    path('api/sessions/send-reminder/', api_views.send_session_reminders, name='api_send_reminder_alt'),
    path('api/sessions/<uuid:session_id>/join/', api_views.join_session_api, name='api_join_session'),
    
    # Advanced WebRTC Features
    path('api/sessions/<uuid:session_id>/end-advanced/', api_views.end_session, name='end_session_advanced'),
    
    # Gift Payment System
    path('api/gift/create/', views.create_gift_payment, name='create_gift_payment'),
    path('api/gift/verify/', views.verify_gift_payment, name='verify_gift_payment'),
    
    # WebRTC Room access endpoints
    path('<uuid:session_id>/room/', views.session_room, name='session_room'),
    path('<uuid:session_id>/waiting-room/', views.waiting_room, name='waiting_room'),
    path('api/sessions/<uuid:session_id>/join-waiting-room/', views.join_waiting_room_api, name='join_waiting_room_api'),
    
    # Session Request API endpoints
    path('api/sessions/request/', api_views.create_session_request, name='create_session_request'),
    path('api/sessions/request/<uuid:request_id>/handle/', api_views.handle_session_request, name='handle_session_request'),
    
    # Session status endpoints
    path('api/sessions/<uuid:session_id>/status/', api_views.get_session_status_real_time, name='api_session_status'),
    path('api/sessions/<uuid:session_id>/start/', api_views.start_session_api, name='api_start_session'),
    
    # Live sessions endpoints
    path('api/live-sessions/', api_views.get_live_sessions, name='api_get_live_sessions'),
    path('api/mark-ready/<uuid:session_id>/', api_views.mark_ready_api, name='api_mark_ready'),

    # New matching and connection APIs
    path('api/find-mentors/', api_views.find_mentors_api, name='find_mentors_api'),
    path('api/recommended-sessions/', api_views.get_recommended_sessions_api, name='get_recommended_sessions_api'),
    path('api/request-mentor-match/', api_views.request_mentor_match_api, name='request_mentor_match_api'),
    path('api/ai-matching/', api_views.ai_matching_api, name='api_ai_matching'),
    path('api/connection-status/<uuid:session_id>/', api_views.get_connection_status_api, name='get_connection_status_api'),
    path('api/update-connection/<uuid:session_id>/', api_views.update_connection_status_api, name='update_connection_status_api'),
    path('api/live-sessions/', api_views.get_live_sessions_advanced, name='api_live_sessions_advanced'),

    # Feedback APIs
    path('api/session/<uuid:session_id>/feedback/', api_views.get_session_feedback_api, name='get_session_feedback_api'),
    path('api/session/<uuid:session_id>/feedback/submit/', api_views.submit_enhanced_feedback, name='submit_enhanced_feedback'),
    path('api/feedback/mentor/stats/', api_views.get_mentor_feedback_stats, name='get_mentor_feedback_stats'),
    path('api/feedback/learner/history/', api_views.get_learner_feedback_history, name='get_learner_feedback_history'),
    path('api/feedback/realtime/', api_views.get_real_time_feedback_updates, name='get_real_time_feedback_updates'),
    path('api/admin/feedback/', api_views.get_admin_session_feedback, name='get_admin_session_feedback'),
]