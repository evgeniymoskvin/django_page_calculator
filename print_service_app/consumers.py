import json
from random import randint
from asyncio import sleep
from channels.db import database_sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer
from page_calculator_app.models import EmployeeModel, PrintFilesModel

from django.core import serializers


class WsConsumer(AsyncWebsocketConsumer):
    """Обновление контента через websocket
    Не актуально"""
    @database_sync_to_async
    def get_emp(self):
        data = PrintFilesModel.objects.get_queryset().filter(status=1)
        qs_json = serializers.serialize('json', data)
        return {'data': qs_json}

    async def connect(self):
        await self.accept()
        while True:
            self.result = await self.get_emp()
            await self.send(json.dumps({'message': randint(1, 100),
                                        'orm_result': self.result
                                        }))
            await sleep(10)
