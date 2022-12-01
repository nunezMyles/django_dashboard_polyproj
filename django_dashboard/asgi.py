"""
ASGI config for django_dashboard project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from django.urls import path
from dashboard_webapp import consumer


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_dashboard.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.

django_asgi_app = get_asgi_application()

"""
websocket_urlpatterns = [
    #re_path(r"ws/chat/(?P<room_name>\w+)/$", consumer.DashConsumer.as_asgi()),
    path('ws/pollData', consumer.DashConsumer.as_asgi()),
]

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
        #"websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
"""
