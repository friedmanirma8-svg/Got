"""
ЧТО ДЕЛАЕТ ЭТОТ МОДУЛЬ:
Инициализирует пакет engine, который содержит основной движок рассуждений
и структуры для хранения цепочки мыслей.

Экспортирует:
- think_one_step: Функция для выполнения одной итерации Chain-of-Thought
- BrainText: Класс для хранения цепочки мыслей
"""

from .engine import think_one_step
from .brain import BrainText

__all__ = ["think_one_step", "BrainText"]
