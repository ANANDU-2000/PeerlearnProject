# peerlearn/asgi.py

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "peerlearn.settings")

from django.core.asgi import get_asgi_application

# First create the Django ASGI application, which populates the apps registry.
django_asgi_app = get_asgi_application()

# Now it’s safe to import Channels pieces—including anything that uses get_user_model()
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
