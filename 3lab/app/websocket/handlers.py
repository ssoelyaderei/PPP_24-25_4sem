import asyncio
import json
from typing import Dict

from fastapi import WebSocket

# храним «клиент <-> task_id»
_clients: Dict[str, WebSocket] = {}


async def handle_incoming(ws: WebSocket) -> None:
    """
    Получаем первое сообщение от клиента:
    {
        "task_id": "...",
        "image_data": "...base64...",
        "algorithm": "otsu" | "adaptive"
    }
    Ставим задачу в Celery и ждём, пока воркер пошлёт статусы.
    """
    data = await ws.receive_json()
    task_id = data["task_id"]
    image_data = data["image_data"]
    algorithm = data.get("algorithm", "otsu")

    # регистрируем сокет
    _clients[task_id] = ws

    # импорт тут, чтобы избежать циклического импорта при старте
    from app.celery.tasks import binarize_image_task

    # кладём задачу
    binarize_image_task.delay(image_data, algorithm)

    # ждём, пока вебсокет не закроется (чтобы не вышли из функции раньше времени)
    try:
        while True:
            await ws.receive_text()
    except Exception:
        pass
    finally:
        _clients.pop(task_id, None)


def notify_task_status(task_id: str, status: str, **payload) -> None:
    """
    Вызывается из Celery-таски. Планирует отправку
    статуса в текущем event-loop FastAPI/Uvicorn.
    """
    message = json.dumps({"task_id": task_id, "status": status, **payload})

    loop = asyncio.get_event_loop()
    if ws := _clients.get(task_id):
        loop.create_task(ws.send_text(message))
