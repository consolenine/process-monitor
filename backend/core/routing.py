from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/snapshot/$', consumers.SnapshotConsumer.as_asgi()),
]
