from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .logic import ChatUserHandler

class ChatConsumer(AsyncJsonWebsocketConsumer):
    rooms = {}

    async def create_chat(self, content):
        try:
            user_steamid64 = content['user_steamid64']
        except KeyError:
            self.handle_bad_params(content)

        user = self.handler.get_user_by_steamid64(user_steamid64)
        if not user:
            self.handle_bad_params(content)
        
        room = await self.handler.get_or_create_room_with_user(user) 
        group_name = f'{room.pk}'
        self.channel_layer.group_add(group_name,self.channel_name)

        self.rooms[group_name] = room

        content['success'] = True
        content['room'] = room.pk
        self.send_json(content)

    async def delete_chat(self, content):
        pass

    async def get_chat(self, content): 
        content['data'] = await self.handler.get_rooms()
        content['success'] = True
        await self.send_json(content)

    async def send_message(self, content):
        try:
            room = content['room']
            message = content['message']
        except KeyError:
            self.handle_bad_params(content)
        
        room = self.rooms[room]
        message = self.handler.sanitize_message(message)

        group_name = f"{room.pk}"
        data = {'content': message, 'steamid64': self.user.steamid64,
                'type': 'group_send_message', 'command': 'send_message', 'status': 'success', }
        self.channel_layer.group_send(group_name,data)

        await self.save_message(room, self.user, message)

    async def group_send_message(self, data):
        await self.send_json(data)

    async def delete_message(self, content):
        pass

    async def get_messages(self, content):
        try:
            room = content['room']
            from_range = content.get('from_range',None)
        except KeyError:
            self.handle_bad_params(content)

        room = self.rooms[room]
        content['data'] = await self.handler.get_messages(room, from_range)
        content['success'] = True
        await self.send_json(content)

    async def get_user(self, content):
        content['data'] = await self.handler.get_user()
        content['success'] = True
        await self.send_json(content)

    async def block_user(self, content):
        pass

    async def pong(self,content):
        content['data'] = 'pong'
        content['success'] = True
        await self.send_json(content)

    commands = {
        'ping':pong,
        'create_chat': create_chat,
        'delete_chat': delete_chat,
        'get_rooms': get_chat,
        'send_message': send_message,
        'delete_message': delete_message,
        'get_messages': get_messages,
        'get_user': get_user,
        'block_user': block_user,
    }

    async def connect(self):
        if not self.scope['user'].pk:
            self.close()
        else:
            self.user = self.scope['user']
            self.handler = ChatUserHandler(self.user)
        self.accept()
    
    async def disconnect(self, code):
        return super().disconnect(code)

    async def receive_json(self, content):
        try:
            self.commands[content['command']](self, content)
        except KeyError:
            self.handle_bad_command(content)

    async def handle_bad_command(self, content):
        content['success'] = False
        content['data'] = 'Bad command'
        await self.send_json(content)
        return None

    async def handle_bad_params(self, content):
        content['success'] = False
        content['data'] = 'Bad parameters'
        await self.send_json(content)
        return None