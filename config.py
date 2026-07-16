import os
from datetime import date

BOT_TOKEN = os.getenv("BOT_TOKEN", "6603511642:AAGO52G65uKqZ08K7SkQONHVlhCiqhtCRQE")

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "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")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "meta/llama-3.1-70b-instruct"

DB_PATH = os.path.join(os.path.dirname(__file__), "bot_data.db")

DEADLINE = date(2025, 8, 21)

DAILY_TASKS = [
    {
        "time": "09:00",
        "task": "Поиск клиентов",
        "description": "Telegram-чаты, LinkedIn, Upwork — найти 30-50 новых контактов",
        "weekend": False,
    },
    {
        "time": "10:00",
        "task": "Подготовка сообщений",
        "description": "Написать 20-30 персональных сообщений потенциальным клиентам",
        "weekend": False,
    },
    {
        "time": "11:00",
        "task": "Отправка откликов",
        "description": "10-20 откликов на Upwork и других биржах",
        "weekend": False,
    },
    {
        "time": "14:00",
        "task": "Работа по проектам",
        "description": "Выполнение заказов или подготовка демо",
        "weekend": True,
    },
    {
        "time": "18:00",
        "task": "Портфолио и кейсы",
        "description": "Улучшить портфолио, добавить кейсы",
        "weekend": True,
    },
    {
        "time": "19:00",
        "task": "Публикации",
        "description": "Опубликовать пост о своих услугах",
        "weekend": False,
    },
    {
        "time": "20:00",
        "task": "Follow-up",
        "description": "Личные сообщения и повторные обращения",
        "weekend": False,
    },
]

WEEKEND_TASKS = [
    {
        "time": "12:00",
        "task": "Портфолио",
        "description": "Улучшить портфолио и кейсы",
        "weekend": True,
    },
    {
        "time": "15:00",
        "task": "Обучение",
        "description": "Изучить что-то полезное для проектов",
        "weekend": True,
    },
]

EVENING_SURVEY_TIME = "21:00"

WEEKDAYS_RU = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье",
}
