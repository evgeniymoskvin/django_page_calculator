from django.urls import path
from .consumers import WsConsumer

ws_urlpatterns = [
    path('ws/some_url/', WsConsumer.as_asgi())
]
