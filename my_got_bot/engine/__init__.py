"""
ЧТО ДЕЛАЕТ ЭТОТ МОДУЛЬ:
Инициализирует пакет engine, который содержит основной движок рассуждений.
Экспортирует главную функцию think_one_step() для выполнения одной итерации
Chain-of-Thought размышлений.
"""

from .engine import think_one_step

__all__ = ["think_one_step"]
