from django.urls import path
from . import views

urlpatterns = [
    path('', views.recommendations_page, name='recommendations_page'),
    path('trending/', views.trending_sessions, name='trending_sessions'),
    path('recommended/', views.recommended_sessions, name='recommended_sessions'),
]
