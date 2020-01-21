#! -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db.models import (Model, TextField, DateTimeField, ForeignKey,
                              CASCADE, BooleanField, OneToOneField)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import pre_save
from django.dispatch import receiver
import json

class MessageModel(Model):
    """
    This class represents a chat message.
    It has a owner (user), timestamp and
    the message body.
    """
    user = ForeignKey(User,
                      on_delete=CASCADE,
                      verbose_name='user',
                      related_name='from_user',
                      db_index=True)
    recipient = ForeignKey(User,
                           on_delete=CASCADE,
                           verbose_name='recipient',
                           related_name='to_user',
                           db_index=True)
    timestamp = DateTimeField('timestamp',
                              auto_now_add=True,
                              editable=False,
                              db_index=True)
    body = TextField('body')
    viewed = BooleanField(default=False)



    def __str__(self):
        return str(self.id)

    def characters(self):
        """
        Instance Method to count body characters.
        :return: body's char number
        """
        return len(self.body)

    def notify_ws_clients(self):
        """
        Inform client there is a new message
        Using django channles websocket connection.
        """
        event = {
            'type': 'recieve_group_message',
            'message': {"type": "message",
                        "id": "%s" % (self.id)
            }
        }

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)("%s" % (self.user.id), event)
        async_to_sync(channel_layer.group_send)("%s" % (self.recipient.id), event)

    def save(self, *args, **kwargs):
        """
        Trims white spaces, saves the message and notifies the recipient via WS
        if the message is new.
        """
        new = self.id
        self.body = self.body.strip()
        super(MessageModel, self).save(*args, **kwargs)
        if new is None:
            self.notify_ws_clients()


    class Meta:
        verbose_name = 'message'
        verbose_name_plural = 'messages'
        ordering = ('-timestamp',)



class Status(Model):
    """
    Model used to give online offline
    status on the go for the user.
    """
    
    user = OneToOneField(User,
                         on_delete=CASCADE,
                         verbose_name='user',
                         related_name="status")
    last_update = DateTimeField(auto_now=True, null=False, blank=False)
    online = BooleanField(default=False)


    def __str__(self):
        return "%s - %s" % (self.id, self.online)


    def notify_ws_client(self):
        """
        Used to notify other users that this
        user is online now.
        """
        print("notify ws client begins")
        contacted_user_ids = MessageModel.objects.filter(
            user=self.user).order_by('recipient').distinct('recipient').values_list('recipient__id', flat=True)
        print("contacted user are %s" % contacted_user_ids)
        channel_layer = get_channel_layer()
        for user_id in contacted_user_ids:
            if Status.objects.filter(user__id=user_id).exists() and Status.objects.get(user__id=user_id).online:
                event = {
                    'type': 'recieve_group_message',
                    'message': {
                        'type': 'status',
                        'user_id': self.id,
                        'online': self.online
                    }
                }
                async_to_sync(channel_layer.group_send)("%s" % (user_id), event)
                
            
    def save(self, *args, **kwargs):
        new = self.id
        super(Status, self).save(*args, **kwargs)
        if new is None:
            print("notifying inside sa5Ave method")
            self.notify_ws_client()

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Status"

@receiver(pre_save, sender=Status)
def call_ws_client(sender, instance, raw, using, update_fields, **kwargs):
    if instance.id is not None:
        # if this is not the first time
        # this instance is saved in the
        # status model.
        previous_status = Status.objects.get(id=instance.id)
        print("previous status is %s and current_status is %s" % (previous_status.online, instance.online))
        if previous_status.online is instance.online:
            pass
        else:
            print("notifying inside pre_save")
            instance.notify_ws_client()
    else:
        # notfication will be handle
        # in the save method of the model.
        pass
