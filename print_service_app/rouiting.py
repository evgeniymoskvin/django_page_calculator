from django.urls import path
from .consumers import WsConsumer

# Ссылки для websocket

ws_urlpatterns = [
    path('ws/some_url/', WsConsumer.as_asgi())
]
