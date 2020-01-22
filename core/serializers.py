from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from core.models import MessageModel
from rest_framework.serializers import ModelSerializer, CharField, SerializerMethodField


class MessageModelSerializer(ModelSerializer):
    user = CharField(source='user.username', read_only=True)
    recipient = CharField(source='recipient.username')

    def create(self, validated_data):
        user = self.context['request'].user
        recipient = get_object_or_404(
            User, username=validated_data['recipient']['username'])
        msg = MessageModel(recipient=recipient,
                           body=validated_data['body'],
                           user=user)
        msg.save()
        return msg

    class Meta:
        model = MessageModel
        fields = ('id', 'user', 'recipient', 'timestamp', 'body', 'viewed')


class ChatUserModelSerializer(ModelSerializer):
    has_conversation = SerializerMethodField()
    online = SerializerMethodField()

    def get_has_conversation(self, instance):
        user = self.context.get('request').user
        return MessageModel.objects.filter(user=user, recipient=instance).exists()

    def get_online(self, instance):
        if(instance.status):
            return instance.status.online
        else:
            return False

    class Meta:
        model = User
        fields = ('id', 'username', 'has_conversation', 'online')
