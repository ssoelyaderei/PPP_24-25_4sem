import asyncio
import websockets
import json
from app.celery.tasks import binarize_image_task
from app.websocket.handlers import register_client, broadcast

async def handler(websocket, path):
    await register_client(websocket)
    async for message in websocket:
        data = json.loads(message)
        if data.get("command") == "start_task":
            task_id = data.get("task_id")
            image_data = data.get("image_data")
            algorithm = data.get("algorithm")
            binarize_image_task.delay(image_data, algorithm)

start_server = websockets.serve(handler, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()