import json
import re
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import Room, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = self.get_valid_group_name(self.room_name)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '')
            username = data.get('username', '')

            if not message or not username:
                raise ValueError("Message or username missing")

            await self.save_message(username, self.room_name, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username
                }
            )
        except json.JSONDecodeError:
            print("Invalid JSON format")
        except ValueError as e:
            print(f"Error: {e}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))

    @sync_to_async
    def save_message(self, username, room_name, message):
        try:
            user = User.objects.get(username=username)
            room = Room.objects.get(name=room_name)
            Message.objects.create(user=user, room=room, content=message)
        except User.DoesNotExist:
            print(f"User {username} does not exist")
        except Room.DoesNotExist:
            print(f"Room {room_name} does not exist")
        except Exception as e:
            print(f"Error saving message: {e}")

    def get_valid_group_name(self, name):
        # Заменяем все недопустимые символы на подчеркивания
        return re.sub(r'[^a-zA-Z0-9\-_\.]', '_', name)





