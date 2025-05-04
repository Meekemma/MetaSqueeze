import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

# Optional: import your websocket routing if you have any
# from yourapp.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MetaSqueeze.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Add WebSocket handling if needed
    # "websocket": AuthMiddlewareStack(
    #     URLRouter(
    #         websocket_urlpatterns
    #     )
    # ),
})
