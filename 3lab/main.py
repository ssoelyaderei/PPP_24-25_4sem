import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from app.celery.tasks import binarize_image_task
import base64

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)