import os
import json
import socket
import struct
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HOST = '127.0.0.1'
PORT = 65432


# Функция для получения данных от сервера
def request_update():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        client.sendall(b"UPDATE")

        data_size = struct.unpack("I", client.recv(4))[0]
        data = client.recv(data_size)

        with open("received_env_info.json", "wb") as f:
            f.write(data)
        logging.info("Данные получены и сохранены.")


# Функция для установки переменной окружения
def set_env_var(var, value):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        client.sendall(f"SETENV {var} {value}".encode())
        response = client.recv(1024).decode()
        if response == "OK":
            logging.info(f"Переменная {var} установлена в значение {value}.")
        else:
            logging.error("Ошибка установки переменной окружения.")


# Функция пользовательского интерфейса
def main():
    while True:
        print("Выберите действие:")
        print("1. Обновить и получить данные")
        print("2. Установить переменную окружения")
        print("3. Выйти")

        choice = input("Введите номер действия: ")
        if choice == "1":
            request_update()
        elif choice == "2":
            var = input("Введите имя переменной: ")
            value = input("Введите значение: ")
            set_env_var(var, value)
        elif choice == "3":
            break
        else:
            print("Неверный ввод, попробуйте снова.")


if __name__ == "__main__":
    main()
