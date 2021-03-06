#! -*- coding: utf-8 -*-

from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from rest_framework.routers import DefaultRouter
from core.api import MessageModelViewSet, ChatUserModelViewSet

router = DefaultRouter()
router.register(r'message', MessageModelViewSet, base_name='message-api')
router.register(r'user', ChatUserModelViewSet, base_name='chat-user-api')

urlpatterns = [
    path(r'api/v1/', include(router.urls)),
    path('', login_required(
        TemplateView.as_view(template_name='core/chat.html')), name='home'),
]
