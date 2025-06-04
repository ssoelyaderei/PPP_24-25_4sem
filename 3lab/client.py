import argparse
import asyncio
import base64
import json
from pathlib import Path

import websockets


async def main(image_path: Path, algorithm: str):
    uri = "ws://localhost:8000/ws"
    task_id = f"task_{image_path.stem}"

    async with websockets.connect(uri) as ws:
        # отправляем картинку
        with open(image_path, "rb") as f:
            payload = {
                "task_id": task_id,
                "algorithm": algorithm,
                "image_data": base64.b64encode(f.read()).decode(),
            }
        await ws.send(json.dumps(payload))

        # слушаем статусы
        while True:
            msg = json.loads(await ws.recv())
            status = msg["status"]
            print(f"[{task_id}] {status}")
            if status == "COMPLETED":
                out = Path(f"binarized_{image_path.name}")
                out.write_bytes(base64.b64decode(msg["binarized_image"]))
                print(f"✔ результат сохранён в {out}")
                break
            if status == "FAILED":
                print("✖ ошибка:", msg.get("error"))
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Путь к файлу")
    parser.add_argument(
        "--algorithm", default="otsu", choices=["otsu", "adaptive"]
    )
    args = parser.parse_args()

    asyncio.run(main(Path(args.image), args.algorithm))
