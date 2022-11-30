from django.test import TestCase

# Create your tests here.
async def hello():
    async with websockets.connect("ws://localhost:8000/ws/pollData", origin="ws://localhost:8000") as websocket:
        await asyncio.gather(
            websocket.send(json.dumps({'value':random.randint(1,100)})),
            websocket.send(json.dumps({'value':random.randint(1,100)})),
            websocket.send(json.dumps({'value':random.randint(1,100)})),
            websocket.send(json.dumps({'value':random.randint(1,100)})),
            websocket.send(json.dumps({'value':random.randint(1,100)})),
            websocket.send(json.dumps({'value':random.randint(1,100)})),
            websocket.send(json.dumps({'value':random.randint(1,100)})),
            websocket.send(json.dumps({'value':random.randint(1,100)})),
            websocket.send(json.dumps({'value':random.randint(1,100)})),
            websocket.send(json.dumps({'value':random.randint(1,100)})),
            websocket.send(json.dumps({'value':random.randint(1,100)})),
            websocket.send(json.dumps({'value':random.randint(1,100)})),
            websocket.send(json.dumps({'value':random.randint(1,100)})),
            websocket.send(json.dumps({'value':random.randint(1,100)})),
            websocket.send(json.dumps({'value':random.randint(1,100)})),
        )


asyncio.run(hello())