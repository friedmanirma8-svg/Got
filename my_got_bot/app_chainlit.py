"""
ЧТО ДЕЛАЕТ ЭТОТ ФАЙЛ:
Окончательный веб-интерфейс через Chainlit.
Бот однопользовательский — только я.
Все улучшения (глаза, память, GoT) будут работать автоматически через этот файл.
Больше его никогда не трогаем.
"""

import chainlit as cl
from eyes import process_visual_content
from memory import ChatMemory
from brain import BrainText
from engine import think_one_step
from mouth import extract_final_answer
from config import MAX_COT_ITERATIONS
import sys
import io


# Глобальная память для пользователя
chat_memory = ChatMemory(max_exchanges=20)
brain = BrainText()


class SuppressOutput:
    """Контекстный менеджер для подавления вывода в консоль"""
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr


@cl.on_chat_start
async def start():
    """Инициализация при запуске чата"""
    await cl.Message(
        content="👋 Привет! Я Chain-of-Thought бот. Задавай любые вопросы или загружай файлы (картинки, PDF, txt, docx)."
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Обработка входящих сообщений"""
    
    # Определяем входной контент
    if message.elements:
        # Если есть прикрепленные файлы — берем первый
        file_path = message.elements[0].path
        user_input = process_visual_content(file_path)
    else:
        # Иначе просто текст
        user_input = message.content
    
    # Очищаем brain для нового запроса
    brain.clear()
    
    # Получаем историю
    history = chat_memory.get_formatted_history()
    
    # Выполняем CoT итерации (с подавлением вывода в UI)
    final_answer = None
    
    with SuppressOutput():
        for iteration in range(1, MAX_COT_ITERATIONS + 1):
            print(f"\n🔄 Итерация {iteration}/{MAX_COT_ITERATIONS}")
            print("=" * 60)
            print("=== ENGINE ===")
            print("=" * 60)
            
            is_first = (iteration == 1)
            response = think_one_step(
                user_message=user_input,
                history=history,
                current_cot=brain.get_chain(),
                is_first_step=is_first
            )
            
            brain.add_step(response)
            
            # Проверяем наличие финального ответа
            answer, is_final = extract_final_answer(response)
            
            if is_final:
                final_answer = answer
                break
    
    # Если не нашли FINAL_ANSWER за MAX_COT_ITERATIONS
    if final_answer is None:
        final_answer = brain.get_chain().split("\n\n")[-1]
    
    # Сохраняем в память
    chat_memory.add_exchange(user_input, final_answer)
    
    # Отправляем ТОЛЬКО финальный ответ в UI
    await cl.Message(content=final_answer).send()
