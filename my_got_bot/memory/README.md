# 💾 MEMORY (Система памяти)

## Назначение

Модуль `memory` отвечает за **хранение и извлечение контекста** разговоров. Реализует двухуровневую систему памяти: краткосрочную (последние обмены) и долгосрочную (семантический поиск по всей истории).

---

## 📂 Структура

```
memory/
├── __init__.py          # Экспорты: ChatMemory, VectorMemory
├── chat_memory.py       # Краткосрочная память (FIFO queue)
├── vector_store.py      # Долгосрочная память (ChromaDB)
└── README.md            # Эта документация
```

---

## 🔑 Ключевые файлы

### 💬 `chat_memory.py` - Краткосрочная память

**Ответственность:**
- Хранение последних N обменов (по умолчанию 20)
- FIFO очередь (первый вошёл - первый вышел)
- Быстрый доступ к недавней истории
- Форматирование для промптов

**Класс: `ChatMemory`**

```python
class ChatMemory:
    def __init__(self, max_exchanges: int = 20):
        """
        Инициализирует краткосрочную память.
        
        Args:
            max_exchanges: Максимальное количество обменов
        """
    
    def add_exchange(self, user_message: str, bot_response: str):
        """Добавляет обмен в память (автоматически удаляет старые)"""
    
    def get_formatted_history(self) -> str:
        """Возвращает историю в виде строки для промпта"""
    
    def clear(self):
        """Очищает всю историю"""
```

**Пример:**
```python
from memory import ChatMemory

chat_mem = ChatMemory(max_exchanges=20)

# Добавить обмен
chat_mem.add_exchange(
    user_message="Привет!",
    bot_response="Здравствуйте! Чем могу помочь?"
)

# Получить историю
history = chat_mem.get_formatted_history()
# Результат:
# User: Привет!
# Assistant: Здравствуйте! Чем могу помочь?
```

**Технические детали:**
- Хранение: In-memory список кортежей
- Персистентность: Отсутствует (теряется при перезапуске)
- Размер: Настраиваемый (по умолчанию 20)
- Сложность операций: O(1) для добавления, O(n) для форматирования

---

### 🔍 `vector_store.py` - Долгосрочная память

**Ответственность:**
- Постоянное хранение всех разговоров
- Семантический поиск по истории
- Векторные эмбеддинги для контента
- Метаданные обменов (время, длина, теги)

**Класс: `VectorMemory`**

```python
class VectorMemory:
    def __init__(
        self,
        collection_name: str = "conversations",
        persist_dir: str = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Инициализирует долгосрочную векторную память.
        
        Args:
            collection_name: Имя коллекции в ChromaDB
            persist_dir: Путь к директории БД
            embedding_model: SentenceTransformers модель
        """
```

**Основные методы:**

#### `add_exchange(user_message, bot_response, metadata=None)`
Сохраняет обмен в векторную базу.

```python
vector_mem.add_exchange(
    user_message="Что такое Python?",
    bot_response="Python - язык программирования...",
    metadata={"topic": "programming", "rating": 5}
)
```

#### `search_similar(query, n_results=5, min_similarity=0.0)`
Семантический поиск похожих разговоров.

```python
results = vector_mem.search_similar(
    query="Как изучать программирование?",
    n_results=3,
    min_similarity=0.3
)

# Результат:
# [
#     {
#         "text": "User: Что такое Python?...",
#         "similarity": 0.85,
#         "metadata": {...}
#     },
#     ...
# ]
```

#### `get_relevant_context(current_message, n_results=3)`
Форматирует релевантные разговоры для промпта.

```python
context = vector_mem.get_relevant_context(
    current_message="Объясни ООП",
    n_results=3
)

# Результат (строка):
# === RELEVANT PAST CONVERSATIONS ===
# [1] Similarity: 0.85 | 2026-01-04
#     User: Что такое Python?
#     Assistant: Python - язык программирования...
```

**Дополнительные методы:**
- `get_stats()` - Статистика памяти (количество, размерность)
- `export_all()` - Экспорт всей базы в JSON
- `clear_all()` - Удаление всех данных (!)
- `search_by_date_range(start, end)` - Поиск по датам

**Пример:**
```python
from memory import VectorMemory

# Инициализация
vector_mem = VectorMemory(persist_dir="./chroma_db")

# Добавить обмен
vector_mem.add_exchange(
    "Что такое Python?",
    "Python - высокоуровневый язык программирования"
)

# Поиск похожих
similar = vector_mem.search_similar("Расскажи про Python", n_results=5)

# Получить контекст для промпта
context = vector_mem.get_relevant_context("Что учить новичку?", n_results=3)

# Статистика
stats = vector_mem.get_stats()
print(f"Всего обменов: {stats['total_exchanges']}")
```

**Технические детали:**
- База данных: ChromaDB (embedded, persistent)
- Модель эмбеддингов: `all-MiniLM-L6-v2` (384 dim)
- Метрика схожести: Косинусная близость (через L2 distance)
- Индексация: Автоматическая (HNSW)
- Размер модели: ~120MB
- Скорость: ~1000 запросов/сек (зависит от размера БД)

---

## ⚙️ Как это работает

### Двухуровневая архитектура памяти

```
Новый обмен (user_msg, bot_response)
            ↓
    ┌───────┴───────┐
    ↓               ↓
ChatMemory      VectorMemory
(In-memory)     (Persistent)
    ↓               ↓
Последние      Все разговоры
20 обменов     + эмбеддинги
    ↓               ↓
FIFO queue    ChromaDB + vectors
    ↓               ↓
История       Семантический поиск
для промпта   релевантного контекста
```

### Интеграция в пайплайн бота

```
User Message → [SENSES] → [MEMORY]
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
              ChatMemory          VectorMemory
                    ↓                   ↓
            get_formatted_      get_relevant_
               history()          context()
                    ↓                   ↓
                    └─────────┬─────────┘
                              ↓
                         [ENGINE]
                    (Рассуждения с контекстом)
                              ↓
                        [EXPRESSION]
                              ↓
                         Ответ
                              ↓
                         [MEMORY]
                    add_exchange() → Обе памяти
```

---

## 🔌 Интеграция с остальной системой

**Получает данные от:**
- `main.py` / `app_chainlit.py` - Новые обмены для сохранения

**Передаёт данные в:**
- `engine/` - История и релевантный контекст для промптов

**Используется в:**
- Каждый запрос (чтение контекста)
- После каждого ответа (сохранение обмена)

---

## ✨ Особенности

- ✅ Двухуровневая система (fast + smart)
- ✅ Персистентная долгосрочная память
- ✅ Семантический поиск (не по ключевым словам!)
- ✅ Метаданные для обменов
- ✅ Настраиваемые размеры и модели
- ✅ Экспорт/импорт данных
- ✅ Статистика и аналитика

---

## 📊 Сравнение двух типов памяти

| Характеристика | ChatMemory | VectorMemory |
|---------------|------------|--------------|
| **Хранение** | In-memory | Disk (ChromaDB) |
| **Персистентность** | ❌ Нет | ✅ Да |
| **Размер** | 20 обменов | Неограниченно |
| **Поиск** | Хронологический | Семантический |
| **Скорость** | Мгновенно | ~50-100ms |
| **Назначение** | Недавний контекст | Релевантный опыт |
| **Когда использовать** | Каждый запрос | Когда нужна история |

---

## 🧪 Примеры использования

### Базовое использование

```python
from memory import ChatMemory, VectorMemory

# Инициализация
chat_mem = ChatMemory()
vector_mem = VectorMemory()

# Сохранить обмен
user_msg = "Привет!"
bot_response = "Здравствуйте!"

chat_mem.add_exchange(user_msg, bot_response)
vector_mem.add_exchange(user_msg, bot_response)

# Получить контекст для следующего запроса
history = chat_mem.get_formatted_history()
relevant = vector_mem.get_relevant_context("Как дела?", n_results=3)
```

### Поиск по темам

```python
# Поиск разговоров про Python
results = vector_mem.search_similar(
    query="Python программирование",
    n_results=10,
    min_similarity=0.5
)

for r in results:
    print(f"Similarity: {r['similarity']:.2f}")
    print(f"Text: {r['text'][:100]}...")
```

### Экспорт данных

```python
# Экспорт всей истории
all_data = vector_mem.export_all()

import json
with open("conversation_history.json", "w") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)
```

---

## 🚀 Будущие улучшения

- [ ] Сжатие старых обменов (summarization)
- [ ] Автоматическая категоризация (topic modeling)
- [ ] Персональный граф знаний (knowledge graph)
- [ ] Забывание неважной информации (forgetting mechanism)
- [ ] Multi-user поддержка (изоляция пользователей)
- [ ] Репликация и бэкапы
- [ ] Аналитика разговоров (sentiment, topics)

---

## 🔐 Безопасность и приватность

**Текущая реализация:**
- Локальное хранение (не отправляется на сервер)
- Без шифрования (plaintext в ChromaDB)
- Одноп пользовательская

**Рекомендации для продакшн:**
- Шифрование БД at rest
- Аутентификация пользователей
- Изоляция данных между пользователями
- Политика retention (автоудаление старого)
- GDPR compliance (право на забвение)

---

**Версия:** 2.0  
**Статус:** ✅ Полностью функционален  
**Зависимости:** `chromadb`, `sentence-transformers`  
**База данных:** ChromaDB (embedded)
