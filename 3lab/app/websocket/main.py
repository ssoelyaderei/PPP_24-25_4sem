from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.websocket.handlers import handle_incoming

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        await handle_incoming(ws)
    except WebSocketDisconnect:
        pass
