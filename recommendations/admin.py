from django.contrib import admin
from .models import PopularityMetric

@admin.register(PopularityMetric)
class PopularityMetricAdmin(admin.ModelAdmin):
    list_display = ('session', 'view_count', 'booking_count', 'completion_rate', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('session__title', 'session__mentor__username')
    readonly_fields = ('updated_at',)
