import json
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message

# In-memory global active calls dictionary across WebSocket connections
ACTIVE_CALLS = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

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
        data = json.loads(text_data)
        event_type = data.get('event')

        if event_type == 'envoie_message':
            await self.handle_send_message(data)
        elif event_type == 'join_room':
            await self.handle_join_room(data)
        elif event_type == 'create_call':
            await self.handle_create_call(data)
        elif event_type == 'join_call':
            await self.handle_join_call(data)
        elif event_type == 'leave_call':
            await self.handle_leave_call(data)
        elif event_type == 'webrtc_signal':
            await self.handle_webrtc_signal(data)

    async def handle_send_message(self, data):
        new_msg = await self.save_message(
            username=data.get('username'),
            room=str(data.get('room')),
            message=data.get('message', ''),
            file_url=data.get('file_url'),
            file_type=data.get('file_type')
        )
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'msg_dict': new_msg
            }
        )

    async def handle_join_room(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'announcement_join_room',
                'username': data.get('username')
            }
        )
        calls = [c for c in ACTIVE_CALLS.values() if str(c['room']) == str(self.room_id)]
        await self.send(text_data=json.dumps({
            'event': 'active_calls_update',
            'calls': calls
        }))

    async def handle_create_call(self, data):
        room = str(data['room'])
        caller = data['username']
        call_type = data.get('call_type', 'video')
        call_id = f"call_{int(time.time()*1000)}"
        type_label = "Vidéo" if call_type == 'video' else "Audio"

        ACTIVE_CALLS[call_id] = {
            'call_id': call_id,
            'room': room,
            'host': caller,
            'call_type': call_type,
            'title': f"Appel {type_label} de {caller}",
            'participants': [caller]
        }

        await self.broadcast_active_calls(room)
        await self.send(text_data=json.dumps({
            'event': 'call_created',
            'call': ACTIVE_CALLS[call_id]
        }))

    async def handle_join_call(self, data):
        room = str(data['room'])
        call_id = data['call_id']
        username = data['username']

        if call_id in ACTIVE_CALLS:
            if username not in ACTIVE_CALLS[call_id]['participants']:
                ACTIVE_CALLS[call_id]['participants'].append(username)

            await self.broadcast_active_calls(room)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined_call_event',
                    'call_id': call_id,
                    'joined_user': username,
                    'participants': ACTIVE_CALLS[call_id]['participants'],
                    'call_type': ACTIVE_CALLS[call_id]['call_type']
                }
            )

    async def handle_leave_call(self, data):
        room = str(data['room'])
        call_id = data['call_id']
        username = data['username']

        if call_id in ACTIVE_CALLS:
            call = ACTIVE_CALLS[call_id]
            if username == call['host']:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'call_ended_event',
                        'call_id': call_id,
                        'host': username
                    }
                )
                del ACTIVE_CALLS[call_id]
            else:
                if username in call['participants']:
                    call['participants'].remove(username)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_left_call_event',
                        'call_id': call_id,
                        'username': username
                    }
                )
                if len(call['participants']) == 0:
                    del ACTIVE_CALLS[call_id]

            await self.broadcast_active_calls(room)

    async def handle_webrtc_signal(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_signal_event',
                'signal_data': data
            }
        )

    async def broadcast_active_calls(self, room):
        calls = [c for c in ACTIVE_CALLS.values() if str(c['room']) == str(room)]
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'active_calls_update_event',
                'calls': calls
            }
        )

    # Group handlers
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'event': 'recu_msg',
            'data': event['msg_dict']
        }))

    async def announcement_join_room(self, event):
        await self.send(text_data=json.dumps({
            'event': 'announcement_join_room',
            'username': event['username']
        }))

    async def active_calls_update_event(self, event):
        await self.send(text_data=json.dumps({
            'event': 'active_calls_update',
            'calls': event['calls']
        }))

    async def user_joined_call_event(self, event):
        await self.send(text_data=json.dumps({
            'event': 'user_joined_call',
            'call_id': event['call_id'],
            'joined_user': event['joined_user'],
            'participants': event['participants'],
            'call_type': event['call_type']
        }))

    async def user_left_call_event(self, event):
        await self.send(text_data=json.dumps({
            'event': 'user_left_call',
            'call_id': event['call_id'],
            'username': event['username']
        }))

    async def call_ended_event(self, event):
        await self.send(text_data=json.dumps({
            'event': 'call_ended',
            'call_id': event['call_id'],
            'host': event['host']
        }))

    async def webrtc_signal_event(self, event):
        await self.send(text_data=json.dumps({
            'event': 'webrtc_signal',
            'data': event['signal_data']
        }))

    @database_sync_to_async
    def save_message(self, username, room, message, file_url, file_type):
        msg = Message.objects.create(
            username=username,
            room=room,
            message=message,
            file_url=file_url,
            file_type=file_type
        )
        return msg.to_dict()
