"""
ЧТО ДЕЛАЕТ ЭТОТ МОДУЛЬ:
Инициализирует пакет senses (чувства/восприятие), который содержит
модули для обработки входных данных - текста, изображений, документов.

Экспортирует:
- inbox: Валидация и обработка текстового ввода
- eyes: Мультимодальная обработка (изображения, PDF, DOCX)
"""

from .inbox import get_user_message
from .eyes import process_visual_content

__all__ = ["get_user_message", "process_visual_content"]
