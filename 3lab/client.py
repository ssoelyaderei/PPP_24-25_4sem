import asyncio
import websockets
import json
import base64
from pathlib import Path

async def connect_to_server(image_path: Path, algorithm: str):
    async with websockets.connect("ws://localhost:8765") as websocket:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        task_id = f"task_{Path(image_path).stem}"
        await websocket.send(json.dumps({
            "command": "start_task",
            "task_id": task_id,
            "image_data": image_data,
            "algorithm": algorithm
        }))
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            if data["status"] == "STARTED":
                print(f"[{data['task_id']}] Задача запущена. Алгоритм: {data.get('algorithm', '')}")
            elif data["status"] == "PROGRESS":
                print(f"[{data['task_id']}] Прогресс: {data.get('progress', 0)}%")
            elif data["status"] == "COMPLETED":
                result_image = base64.b64decode(data["binarized_image"])
                output_path = f"result_{task_id}.png"
                with open(output_path, "wb") as f:
                    f.write(result_image)
                print(f"[{data['task_id']}] Завершено! Результат: {output_path}")
                break
            elif data["status"] == "FAILED":
                print(f"[{data['task_id']}] Ошибка: {data.get('error', '')}")
                break

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Путь к изображению")
    parser.add_argument("--algorithm", default="otsu", choices=["otsu", "adaptive"], help="Алгоритм")
    args = parser.parse_args()
    asyncio.run(connect_to_server(args.image, args.algorithm))