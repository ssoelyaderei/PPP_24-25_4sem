# app/celery/tasks.py
from app.celery import celery  # Импорт экземпляра Celery
from PIL import Image
import base64
import io
import asyncio
from app.websocket.handlers import notify_task_status

@celery.task(bind=True)
def binarize_image_task(self, image_data: str, algorithm: str):
    task_id = self.request.id
    try:
        # Декодирование изображения
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("L")  # Ч/б

        # Применение алгоритма
        if algorithm == "otsu":
            threshold = 128
            image = image.point(lambda x: 0 if x < threshold else 255, "1")
        elif algorithm == "adaptive":
            image = image.point(lambda x: 0 if x < 128 else 255, "1")
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        # Кодирование результата
        buffered = io.BytesIO()
        image.save(buffered, format=image.format)
        binarized_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Отправка завершения
        notify_task_status(task_id, "COMPLETED", binarized_image=binarized_image)
        return {"binarized_image": binarized_image}
    except Exception as e:
        notify_task_status(task_id, "FAILED", error=str(e))
        return {"error": str(e)}