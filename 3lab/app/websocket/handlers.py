import asyncio
import json

connected_clients = set()

async def register_client(websocket):
    connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)

async def broadcast(message):
    for client in connected_clients:
        try:
            await client.send(message)
        except Exception as e:
            print(f"Error sending message to client: {e}")

def notify_task_status(task_id, status, **kwargs):
    message = {
        "status": status,
        "task_id": task_id,
        **kwargs
    }
    asyncio.run(broadcast(json.dumps(message)))