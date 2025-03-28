import os
import json
import socket
import struct
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HOST = '127.0.0.1'
PORT = 65432
DATA_FILE = 'env_info.json'
HISTORY_FILE = 'env_history.json'


# Функция получения исполняемых файлов из PATH
def get_executables():
    paths = os.environ.get("PATH", "").split(os.pathsep)
    executables = {}

    for path in paths:
        if os.path.isdir(path):
            try:
                files = [f for f in os.listdir(path) if os.access(os.path.join(path, f), os.X_OK)]
                executables[path] = files
            except Exception as e:
                logging.warning(f"Не удалось получить файлы из {path}: {e}")

    return executables


# Функция сохранения данных в файл
def save_data():
    data = {
        "env": dict(os.environ),
        "executables": get_executables()
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    logging.info("Данные сохранены в файл.")


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_history(var_name, new_value):
    history = load_history()
    history[var_name] = history.get(var_name, []) + [(datetime.now().isoformat(), new_value)]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)
    logging.info("История обновлена.")


# Запуск сервера
def start_server():
    save_data()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        logging.info("Сервер запущен и ожидает подключения...")

        while True:
            conn, addr = server.accept()
            with conn:
                logging.info(f"Подключение от {addr}")
                data = conn.recv(1024).decode()
                if data == "UPDATE":
                    save_data()
                    with open(DATA_FILE, "rb") as f:
                        content = f.read()
                    conn.sendall(struct.pack("I", len(content)) + content)
                elif data.startswith("SETENV"):
                    _, var, value = data.split(" ", 2)
                    os.environ[var] = value
                    save_history(var, value)
                    conn.sendall(b"OK")


if __name__ == "__main__":
    start_server()
