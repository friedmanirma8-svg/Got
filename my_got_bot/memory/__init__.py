"""
ЧТО ДЕЛАЕТ ЭТОТ МОДУЛЬ:
Инициализирует пакет memory, который содержит систему памяти чатбота.
Экспортирует классы для работы с краткосрочной памятью (последние сообщения),
долгосрочной памятью (заглушка) и векторной памятью (ChromaDB с семантическим поиском).
"""

from .chat_memory import ChatMemory
from .big_memory import BigMemory
from .vector_store import VectorMemory

__all__ = ["ChatMemory", "BigMemory", "VectorMemory"]
