"""
ЧТО ДЕЛАЕТ ЭТОТ ФАЙЛ / МОДУЛЬ:
Управляет краткосрочной памятью чатбота — хранит последние 20 обменов сообщениями
между пользователем и ботом. Это нужно, чтобы модель помнила контекст недавнего
разговора и могла давать релевантные ответы с учётом предыдущих реплик.
Автоматически обрезает старые сообщения, когда достигнут лимит.
"""


class ChatMemory:
    """
    Хранит последние N обменов сообщениями (по умолчанию 20).
    Каждый обмен = пара (user_message, bot_response).
    """
    
    def __init__(self, max_exchanges=20):
        """
        Инициализирует память с заданным лимитом обменов.
        """
        self.max_exchanges = max_exchanges
        self.history = []  # Список кортежей (user_msg, bot_response)
    
    def add_exchange(self, user_message, bot_response):
        """
        Добавляет новый обмен в историю.
        Если превышен лимит — удаляет самый старый обмен.
        """
        self.history.append((user_message, bot_response))
        
        # Обрезаем историю, если превышен лимит
        if len(self.history) > self.max_exchanges:
            self.history.pop(0)  # Удаляем самый старый обмен
    
    def get_formatted_history(self):
        """
        Возвращает историю в виде отформатированной строки для промпта.
        """
        if not self.history:
            return "No previous messages."
        
        formatted = []
        for user_msg, bot_response in self.history:
            formatted.append(f"User: {user_msg}")
            formatted.append(f"Assistant: {bot_response}")
        
        return "\n".join(formatted)
    
    def clear(self):
        """
        Очищает всю историю.
        """
        self.history = []
    
    def __len__(self):
        """
        Возвращает количество обменов в памяти.
        """
        return len(self.history)
