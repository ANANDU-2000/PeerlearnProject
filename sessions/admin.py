from django.contrib import admin
from .models import Session, Booking, Feedback

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'mentor', 'schedule', 'status', 'current_participants', 'max_participants')
    list_filter = ('status', 'schedule', 'created_at')
    search_fields = ('title', 'mentor__username', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('learner', 'session', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('learner__username', 'session__title')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('session', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('session__title', 'user__username', 'comment')
