from django.urls import path
from . import views

urlpatterns = [
    path('', views.session_list, name='session_list'),
    path('<uuid:session_id>/', views.session_detail, name='session_detail'),
    path('<uuid:session_id>/book/', views.book_session, name='book_session'),
    path('<uuid:session_id>/room/', views.session_room, name='session_room'),
    path('<uuid:session_id>/start/', views.start_session, name='start_session'),
    path('<uuid:session_id>/end/', views.end_session, name='end_session'),
    path('<uuid:session_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('create/', views.create_session, name='create_session'),
    path('api/list/', views.session_api_list, name='session_api_list'),
]
