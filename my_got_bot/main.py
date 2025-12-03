"""
ЧТО ДЕЛАЕТ ЭТОТ ФАЙЛ / МОДУЛЬ:
Главная точка входа в приложение. Содержит бесконечный цикл взаимодействия с пользователем:
принимает сообщения через inbox, обрабатывает их через весь пайплайн (eyes -> memory -> brain -> engine),
выполняет до 4 итераций Chain-of-Thought размышлений, извлекает финальный ответ через mouth
и сохраняет обмен в краткосрочную память. Запускается командой `python main.py`.
"""

from inbox import get_user_message
from eyes import process_visual_content
from memory import ChatMemory, BigMemory
from brain import BrainText
from engine import think_one_step
from mouth import speak
from config import MAX_COT_ITERATIONS


def main():
    """
    Главная функция — бесконечный цикл общения с пользователем.
    """
    print("\n" + "=" * 60)
    print("🤖 Chain-of-Thought Chatbot (Together.ai)")
    print("=" * 60)
    print("Введите 'exit' или 'quit' для выхода\n")
    
    # Инициализируем компоненты
    chat_memory = ChatMemory(max_exchanges=20)
    big_memory = BigMemory()  # Пока не используется
    brain = BrainText()
    
    # Основной цикл
    while True:
        # 1. Получаем сообщение от пользователя
        user_message = get_user_message()
        
        if user_message is None:
            print("\n👋 До свидания!")
            break
        
        if not user_message:
            continue
        
        # 2. Обрабатываем визуальный контент (пока заглушка)
        processed_message = process_visual_content(user_message)
        
        # 3. Получаем историю диалога из памяти
        history = chat_memory.get_formatted_history()
        
        # 4. Очищаем brain для нового запроса
        brain.clear()
        
        # 5. Выполняем итерации Chain-of-Thought
        final_answer = None
        
        for iteration in range(1, MAX_COT_ITERATIONS + 1):
            print(f"\n🔄 Итерация {iteration}/{MAX_COT_ITERATIONS}")
            
            # Выполняем один шаг размышлений
            is_first = (iteration == 1)
            response = think_one_step(
                user_message=processed_message,
                history=history,
                current_cot=brain.get_chain(),
                is_first_step=is_first
            )
            
            # Добавляем результат в brain
            brain.add_step(response)
            
            # Показываем текущее состояние brain (для отладки)
            # brain.display()
            
            # 6. Пытаемся извлечь финальный ответ
            answer, is_final = speak(response)
            
            if is_final:
                final_answer = answer
                break
        
        # Если за MAX_COT_ITERATIONS не получили финальный ответ — берём последний
        if final_answer is None:
            print("⚠️  Достигнут лимит итераций, беру последний ответ")
            final_answer = brain.get_chain().split("\n\n")[-1]  # Последний абзац
            print("\n" + "=" * 60)
            print("=== MOUTH (принудительно) ===")
            print("=" * 60)
            print(f"🗣️  {final_answer}\n")
        
        # 7. Сохраняем обмен в память
        chat_memory.add_exchange(user_message, final_answer)
        print(f"💾 Сохранено в память ({len(chat_memory)} обменов)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Прервано пользователем. До свидания!")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        raise
