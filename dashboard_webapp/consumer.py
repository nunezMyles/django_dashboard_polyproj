import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class DashConsumer(AsyncJsonWebsocketConsumer):
    print('==================')
    async def connect(self):
        self.groupname='dashboard'
        await self.channel_layer.group_add(
            self.groupname,
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self,close_code):
        await self.channel_layer.group_discard(
            self.groupname,
            self.channel_name
        )   

    async def receive(self, text_data):
        datapoint = json.loads(text_data)
        val =datapoint['value']

        await self.channel_layer.group_send(
            self.groupname,
            {
                'type':'deprocessing', #function name to run
                'value':val #value to send function
            }
        )
        print ('>>>>',text_data)

    async def deprocessing(self,event):
        valOther=event['value']
        valOther = f'IP VALUE: {valOther}'
        await self.send(text_data=json.dumps({'value2':valOther}))# send for frontend