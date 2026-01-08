"""
ЧТО ДЕЛАЕТ ЭТОТ МОДУЛЬ:
Инициализирует пакет memory, который содержит систему памяти чатбота.
Экспортирует классы для работы с краткосрочной памятью (последние сообщения)
и векторной долгосрочной памятью (ChromaDB с семантическим поиском).
"""

from .chat_memory import ChatMemory
from .vector_store import VectorMemory

__all__ = ["ChatMemory", "VectorMemory"]
