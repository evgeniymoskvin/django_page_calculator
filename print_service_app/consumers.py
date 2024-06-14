import json
from random import randint
from asyncio import sleep
from channels.db import database_sync_to_async

from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from page_calculator_app.models import EmployeeModel, PrintFilesModel

from django.http import JsonResponse
from django.core import serializers





class WsConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_emp(self):
        data = PrintFilesModel.objects.get_queryset().filter(status=1)
        qs_json = serializers.serialize('json', data)
        return {'data': qs_json}

    async def connect(self):
        await self.accept()
        while True:
            self.result = await self.get_emp()
            # print(self.result)
            # await self.send(json.dumps({'message': randint(1, 100)}))
            await self.send(json.dumps({'message': randint(1, 100),
                                        'orm_result': self.result
                                        }))
            await sleep(10)


# class WsConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         print(self.scope)
#         self.room_name = self.scope['root_path']
#         self.room_group_name = 'chat_%s' % self.room_name
#
#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#
#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )
#
#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event['message']
#
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))
