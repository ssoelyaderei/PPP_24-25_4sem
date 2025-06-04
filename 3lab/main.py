import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import base64
from app.celery.tasks import binarize_image_task
from celery.result import AsyncResult

app = FastAPI()

@app.post("/binarize")
async def start_binarization(
    image: UploadFile = File(...),
    algorithm: str = "otsu"
):
    image_data = await image.read()
    encoded_image = base64.b64encode(image_data).decode("utf-8")
    task = binarize_image_task.delay(encoded_image, algorithm)
    return {"task_id": task.id}

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Проверяем статус задачи Celery. Если завершена, возвращаем бинаризованное изображение.
    """
    result = AsyncResult(task_id)
    if result.state == "PENDING":
        return {"status": "PENDING"}
    elif result.state == "STARTED":
        return {"status": "STARTED"}
    elif result.state == "SUCCESS":
        data = result.result or {}
        return {"status": "COMPLETED", **data}
    elif result.state == "FAILURE":
        return {"status": "FAILED", "error": str(result.result)}
    else:
        return {"status": result.state}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
