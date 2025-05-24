import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import sessions.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peerlearn.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            sessions.routing.websocket_urlpatterns
        )
    ),
})
