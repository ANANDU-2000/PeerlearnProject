from django.urls import path
from . import views, api_views
from .create_session_api import create_session_api

urlpatterns = [
    # Web views
    path('', views.session_list, name='session_list'),
    path('<uuid:session_id>/', views.session_detail_new, name='session_detail'),
    path('<uuid:session_id>/book/', views.book_session, name='book_session'),
    path('<uuid:session_id>/room/', views.session_room, name='session_room'),
    path('room/<uuid:session_id>/', views.session_room, name='session_room_alt'),
    path('<uuid:session_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('create/', views.create_session, name='create_session'),
    path('<uuid:session_id>/edit/', views.edit_session, name='edit_session'),
    
    # API endpoints
    path('api/sessions/', api_views.get_sessions_api, name='get_sessions_api'),
    path('api/sessions/create/', create_session_api, name='api_create_session'),
    path('api/sessions/<uuid:session_id>/book/', api_views.book_session, name='api_book_session'),
    path('api/sessions/<uuid:session_id>/start/', api_views.start_session, name='api_start_session'),
    path('api/sessions/<uuid:session_id>/end/', api_views.end_session, name='api_end_session'),
    path('api/sessions/<uuid:session_id>/publish/', api_views.publish_session, name='api_publish_session'),
    path('api/sessions/<uuid:session_id>/feedback/', api_views.submit_feedback, name='api_submit_feedback'),
    path('api/sessions/<uuid:session_id>/submit-rating/', api_views.submit_rating_simple, name='submit_rating_simple'),
    
    # Request endpoints
    path('api/requests/create/', api_views.create_session_request, name='api_create_request'),
    path('api/requests/<int:request_id>/accept/', api_views.accept_request, name='api_accept_request'),
    path('api/requests/<int:request_id>/decline/', api_views.decline_request, name='api_decline_request'),
    
    # Notification endpoints
    path('api/notifications/', api_views.get_notifications_api, name='get_notifications_api'),
    path('api/notifications/read/', api_views.mark_notifications_read, name='mark_notifications_read'),
    
    # Earnings endpoints
    path('api/earnings/payout/', api_views.request_payout, name='api_request_payout'),
    
    # Dashboard data endpoints
    path('api/mentor-dashboard/', api_views.mentor_dashboard_data, name='mentor_dashboard_data'),
    
    # Session management endpoints
    path('api/sessions/<uuid:session_id>/mark-ready/', api_views.mark_ready, name='api_mark_ready'),
    path('api/sessions/<uuid:session_id>/start/', api_views.start_session_api, name='api_start_session_new'),
    path('api/sessions/<uuid:session_id>/bookings/', api_views.session_bookings, name='api_session_bookings'),
    path('api/sessions/<uuid:session_id>/send-reminders/', api_views.send_session_reminders, name='api_send_reminders'),
    
    # Advanced WebRTC Features (using existing functions)
    path('api/sessions/<uuid:session_id>/end-advanced/', api_views.end_session, name='end_session_advanced'),
    
    # Gift Payment System with Razorpay
    path('api/gift/create/', views.create_gift_payment, name='create_gift_payment'),
    path('api/gift/verify/', views.verify_gift_payment, name='verify_gift_payment'),
    
    # WebRTC Room access endpoints
    path('<uuid:session_id>/room/', views.session_room, name='session_room'),
    path('<uuid:session_id>/waiting-room/', views.waiting_room, name='waiting_room'),
    
    # Advanced Feedback System endpoints
    path('api/sessions/<uuid:session_id>/live-feedback/', api_views.live_feedback, name='api_live_feedback'),
    path('api/sessions/<uuid:session_id>/feedback-messages/', api_views.feedback_messages, name='api_feedback_messages'),
    path('api/messages/<int:message_id>/mark-read/', api_views.mark_message_read, name='api_mark_message_read'),
    path('api/mentor-feedback/', api_views.mentor_feedback, name='api_mentor_feedback'),
]
