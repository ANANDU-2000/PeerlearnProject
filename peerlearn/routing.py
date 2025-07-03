from django.urls import re_path
from sessions.consumers import SessionConsumer, DashboardConsumer

websocket_urlpatterns = [
    re_path(r'ws/session/(?P<session_id>[0-9a-f-]+)/$', SessionConsumer.as_asgi()),
    re_path(r'ws/sessions/(?P<session_id>[0-9a-f-]+)/$', SessionConsumer.as_asgi()),  # Alternative route
    re_path(r'ws/dashboard/$', DashboardConsumer.as_asgi()),
] 