from rest_framework import serializers
from .models import USER_MODEL, Message, Room

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = USER_MODEL
        fields = ['username','steamid64','avatar']


class RoomSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(many=True)
    class Meta:
        model = Room
        fields = ['user','id']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['username','content','date_sent','status','steamid64',]