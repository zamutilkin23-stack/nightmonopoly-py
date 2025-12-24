# sync_to_server.py
import subprocess
import os

# 🔧 Настройки
VPS_HOST = "123.45.67.89"         # IP сервера
VPS_USER = "root"                 # Пользователь
VPS_PORT = "22"                   # Порт SSH
REMOTE_PATH = "/var/www/nightmonopoly"  # Путь на сервере

def sync():
    print("🔁 Синхронизация с VPS...")
    try:
        # Команда rsync
        cmd = [
            "rsync", "-avz", "-e", f"ssh -p {VPS_PORT}",
            "./",  # текущая папка
            f"{VPS_USER}@{VPS_HOST}:{REMOTE_PATH}"
        ]
        subprocess.run(cmd, check=True)
        print("✅ Файлы синхронизированы")

        # Перезапуск на сервере (если через PM2)
        ssh_cmd = f"ssh -p {VPS_PORT} {VPS_USER}@{VPS_HOST} 'cd {REMOTE_PATH} && python3 wsgi.py &'"
        subprocess.run(ssh_cmd, shell=True)
        print("✅ Сервер перезапущен")
    except subprocess.CalledProcessError as e:
        print("❌ Ошибка синхронизации:", str(e))

if __name__ == '__main__':
    sync()