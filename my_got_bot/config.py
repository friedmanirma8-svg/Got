"""
ЧТО ДЕЛАЕТ ЭТОТ ФАЙЛ / МОДУЛЬ:
Загружает конфигурацию приложения: API-ключ Together.ai из переменных окружения
и определяет название модели для генерации ответов. Это центральное место
для всех настроек, которые могут меняться в зависимости от окружения.
"""

import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# API ключ для Together.ai
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# Модель для генерации
MODEL_NAME = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"

# Максимальное количество итераций CoT
MAX_COT_ITERATIONS = 4

if not TOGETHER_API_KEY:
    raise ValueError("TOGETHER_API_KEY не найден в .env файле!")
