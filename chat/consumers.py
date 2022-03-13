from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync

from chat.models import USER_MODEL, Message, Room
from chat.serializers import MessageSerializer, RoomSerializer, UserBasicSerializer


class ChatConsumer(JsonWebsocketConsumer):
    rooms = {}

    def create_chat(self, content):
        user = self.user
        to_user = content.get('to_user')

        if not to_user:
            self.handle_bad_params(content)
        else:
            to_user = self.get_user_model(to_user)
            if not to_user:
                self.handle_bad_params(content)
            else:
                room = self.get_room_model(user, to_user)
                group_name = f'chat_{room.pk}'
                async_to_sync(self.channel_layer.group_add)(
                    group_name,
                    self.channel_name)
                self.rooms[to_user.steamid64] = group_name
                content['status'] = 'success'
                self.send_json(content)

    def delete_chat(self, content):
        pass
#
    def get_chat(self, content):
        user = self.user
        rooms = user.rooms.all()
        rooms = RoomSerializer(rooms, many=True)
        data = rooms.data
        content['data'] = data
        content['status'] = 'success'
        self.send_json(content)
#
    def send_message(self, content):
        user = self.user
        to_user = content.get('to_user')
        message = content.get('message')
        if not to_user or not message or not self.rooms.get(to_user):
            self.handle_bad_params(content)
        else:
            group_name = self.rooms[to_user]
            data = {'content': message, 'steamid64': user.steamid64,
                    'type': 'group_send_message', 'command': 'send_message', 'status': 'success', }
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                data)
            # Save the message into the db
            room = group_name.split('_')[-1]
            self.save_message(int(room), self.user,
                              self.user.username, message)

    def group_send_message(self, data):
        data.pop('type')
        self.send_json(data)

    def delete_message(self, content):
        pass

    def get_messages(self, content):
        to_user = content.get('to_user')
        from_range = content.get('from_range')
        if not to_user or self.rooms.get('to_user'):
            self.handle_bad_params(content)
        else:
            room = self.get_room_model(self.user, self.get_user_model(to_user))
            if from_range:
                try:
                    messages = room.messages.filter(
                        date_sent__lt=from_range).order_by('-date_sent')[0:20]
                except:
                    messages = room.messages.all().order_by('-date_sent')[0:20]
            else:
                messages = room.messages.all().order_by('-date_sent')[0:20]
            data = MessageSerializer(reversed(messages), many=True).data
            content['status'] = 'success'
            content['data'] = data
            if data != []:
                self.send_json(content)

    def get_user(self, content):
        content['data'] = UserBasicSerializer(self.user).data
        content['status'] = 'success'
        self.send_json(content)

    def block_user(self, content):
        pass

    commands = {
        'create_chat': create_chat,
        'delete_chat': delete_chat,
        'get_chat': get_chat,
        'send_message': send_message,
        'delete_message': delete_message,
        'get_messages': get_messages,
        'get_user': get_user,
        'block_user': block_user,
    }

    def connect(self):
        if not self.scope['user'].pk:
            self.close()
        else:
            self.user = self.scope['user']
        self.accept()

    def receive_json(self, content):
        command = content.get('command')
        if not command or not self.commands.get(command):
            self.handle_bad_command(content)
        else:
            # If the given 'command' key is valid in the 'content' dict sent from client,
            # handle it with its respective function
            self.commands[command](self, content)

    def handle_bad_command(self, content):
        data = {'success':False,'data':'Bad command'}
        self.send_json(data)

    def handle_bad_params(self, content):
        data = {'success':False,'data':'Bad parameters'}
        self.send_json(data)

    @staticmethod
    def get_user_model(steamid64):
        user = USER_MODEL.objects.filter(steamid64=steamid64)
        if user.exists():
            return user.first()
        else:
            return None

    @staticmethod
    def get_room_model(user1, user2):
        room = Room.objects.filter(user=user1).filter(user=user2)
        if room.exists():
            room = room.first()
        else:
            room = Room.objects.create()
            room.user.add(user1)
            room.user.add(user2)
        return room

    @staticmethod
    def save_message(room, user, username, content):
        Message.objects.create(
            room_id=room,
            user=user,
            username=username,
            content=content
        )
