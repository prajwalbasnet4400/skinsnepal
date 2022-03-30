from django.contrib.auth import get_user_model
from bleach.linkifier import LinkifyFilter
from bleach.sanitizer import Cleaner
from channels.db import database_sync_to_async

from .models import Room, Message, RoomUser, BlockedUser
from .serializers import MessageSerializer, RoomSerializer, UserBasicSerializer

USER_MODEL = get_user_model()
sanitizer = Cleaner(filters=[LinkifyFilter])


class ChatUserHandler:
    def __init__(self, user):
        """
            Class to handle Room model's permission, methods 
        """
        self.user = user

    @database_sync_to_async
    def get_user(self):
        user = UserBasicSerializer(self.user)
        return user.data

    @database_sync_to_async
    def in_room(self, room_pk):
        return self.user.rooms.filter(pk=room_pk).exists()

    @database_sync_to_async
    def get_rooms(self):
        rooms = Room.objects.filter(user=self.user)
        data = RoomSerializer(rooms, many=True)
        return data.data

    @database_sync_to_async
    def get_or_create_room_with_user(self, user):
        room = Room.objects.filter(user=user).filter(user=self.user)
        if room.exists():
            room = room.first()
        else:
            room = Room.objects.create()
            room.user.add(self.user)
            room.user.add(user)
        data = RoomSerializer(room, many=False)
        return data.data

    @database_sync_to_async
    def get_messages(self, room, from_date_range=None):
        if from_date_range:
            pass
        else:
            messages = room.messages.all()
        data = MessageSerializer(messages, many=True)
        return data.data

    def block_user(self, user):
        pass

    @database_sync_to_async
    def save_message(self, room, content):
        Message.objects.create(
            room=room,
            user=self.user,
            content=content
        )

    @staticmethod
    def sanitize_message(message):
        return sanitizer.clean(message)

    @database_sync_to_async
    @staticmethod
    def get_user_by_steamid64(steamid64):
        try:
            return USER_MODEL.objects.get(steamid64=steamid64)
        except USER_MODEL.DoesNotExist:
            return None
