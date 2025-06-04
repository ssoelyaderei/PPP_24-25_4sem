from __future__ import annotations

from app.celery.celery_app import celery
from app.websocket.handlers import notify_task_status

from PIL import Image
import base64
import io
import asyncio


@celery.task(bind=True)
def binarize_image_task(self, image_data: str, algorithm: str = "otsu") -> dict:
    """Бинаризация изображения в Celery-воркере."""
    task_id = self.request.id
    # сообщаем клиенту, что задача стартовала
    notify_task_status(task_id, "STARTED", algorithm=algorithm)

    try:
        # ----- чтение исходника -----
        img_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(img_bytes)).convert("L")  # grayscale

        # ----- сама бинаризация -----
        if algorithm == "otsu":
            threshold = 128
            image = image.point(lambda px: 0 if px < threshold else 255, "1")
        elif algorithm == "adaptive":
            image = image.point(lambda px: 0 if px < 128 else 255, "1")
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        # ----- кодируем ответ -----
        out = io.BytesIO()
        image.save(out, format="PNG")
        result_b64 = base64.b64encode(out.getvalue()).decode()

        notify_task_status(task_id, "COMPLETED", binarized_image=result_b64)
        return {"binarized_image": result_b64}

    except Exception as exc:
        notify_task_status(task_id, "FAILED", error=str(exc))
        raise
