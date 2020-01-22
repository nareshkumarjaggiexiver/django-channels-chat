#! -*- coding: utf-8 -*-

from core import consumers
from django.conf.urls import re_path

websocket_urlpatterns = [
    re_path(r'^ws$', consumers.ChatConsumer),
]
