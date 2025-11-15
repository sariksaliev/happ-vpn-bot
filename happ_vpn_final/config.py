import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "-5096915630"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "happ_vpn.db")
MEDIA_DIR = os.path.join(BASE_DIR, "media")

MEDIA = {
    "main_image": os.path.join(MEDIA_DIR, "главное меню.jpg"),  # ← исправлено
    "tariffs_image": os.path.join(MEDIA_DIR, "наши тарифы.jpg"),
    "keys_image": os.path.join(MEDIA_DIR, "мои ключи.jpg"),
    "instruction_image": os.path.join(MEDIA_DIR, "инструкция установки.jpg"),
    "success_image": os.path.join(MEDIA_DIR, "успешная покупка.jpg"),
    "instruction_iphone": os.path.join(MEDIA_DIR, "инструкция на айфон.mp4"),
    "instruction_android": os.path.join(MEDIA_DIR, "инструкция на андроид.MP4"),
    "instruction_pc": os.path.join(MEDIA_DIR, "инструкция на компьютер.mp4"),
    "instruction_tv": os.path.join(MEDIA_DIR, "инструкция на телевизор.mp4"),
}


INSTALLATION_TEXTS = {
    "iphone": "📱 Инструкция для iPhone:\n1. Скачайте Happ VPN в App Store.\n2. Введите выданный вам ключ.\n3. Включите VPN.",
    "android": "🤖 Инструкция для Android:\n1. Установите Happ VPN из Google Play.\n2. Введите ключ активации.\n3. Нажмите 'Подключить'.",
    "pc": "💻 Инструкция для компьютера:\n1. Скачайте Happ VPN для Windows.\n2. Установите и введите ключ.\n3. Активируйте соединение.",
    "tv": "📺 Инструкция для телевизора:\n1. Откройте настройки сети Smart TV.\n2. Добавьте VPN Happ.\n3. Введите ключ.",
}

SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "slvsrdr")
SUPPORT_URL = f"https://t.me/{SUPPORT_USERNAME}"

__all__ = [
    "BOT_TOKEN",
    "ADMIN_CHAT_ID",
    "DB_PATH",
    "MEDIA_DIR",
    "MEDIA",
    "INSTALLATION_TEXTS",
    "SUPPORT_USERNAME",
    "SUPPORT_URL",
]
