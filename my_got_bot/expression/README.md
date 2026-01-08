# 🗣️ EXPRESSION (Выражение/Вывод)

## Назначение

Модуль `expression` отвечает за **формирование и извлечение финальных ответов** бота. Это последний этап пайплайна - аналог человеческой речи.

---

## 📂 Структура

```
expression/
├── __init__.py          # Экспорты: extract_final_answer, speak
├── mouth.py             # Извлечение и вывод ответов
└── README.md            # Эта документация
```

---

## 🔑 Ключевой файл

### 🗣️ `mouth.py` - Извлечение финального ответа

**Ответственность:**
- Поиск маркера `FINAL_ANSWER:` в ответе модели
- Извлечение чистого ответа без служебной информации
- Fallback логика (если маркер не найден)
- Простой вывод в консоль

**Основные функции:**

#### `extract_final_answer(response_text: str) -> tuple[str, bool]`

Извлекает финальный ответ из текста модели.

**Аргументы:**
- `response_text` - Полный ответ от LLM (может содержать CoT мысли)

**Возвращает:**
```python
(answer: str, is_final: bool)
```
- `answer` - Извлечённый ответ
- `is_final` - True если найден маркер `FINAL_ANSWER:`

**Алгоритм:**
```python
if "FINAL_ANSWER:" in response_text:
    # Извлечь всё после маркера
    answer = response_text.split("FINAL_ANSWER:", 1)[1].strip()
    return (answer, True)
else:
    # Fallback: вернуть последний параграф
    paragraphs = response_text.split("\n\n")
    return (paragraphs[-1], False)
```

**Пример:**
```python
from expression.mouth import extract_final_answer

# С маркером
response = """
🎯 Понять: Пользователь спрашивает про Python
🔍 Анализ: Python - язык программирования

FINAL_ANSWER: Python - это высокоуровневый язык программирования,
известный своей читаемостью и простотой.
"""

answer, is_final = extract_final_answer(response)
# answer = "Python - это высокоуровневый язык..."
# is_final = True

# Без маркера (fallback)
response = """
Это первая мысль.

Это вторая мысль.
"""

answer, is_final = extract_final_answer(response)
# answer = "Это вторая мысль."
# is_final = False
```

---

#### `speak(response_text: str) -> tuple[str, bool]`

Просто вызывает `extract_final_answer` (алиас для читаемости кода).

**Пример:**
```python
from expression.mouth import speak

answer, is_final = speak(model_response)
if is_final:
    print(f"Финальный ответ: {answer}")
```

---

## ⚙️ Как это работает

### Процесс извлечения ответа

```
Ответ модели (response_text)
        ↓
Поиск маркера "FINAL_ANSWER:"
        ↓
    Найден? → YES → Извлечь всё после маркера
        ↓               ↓
        NO          Вернуть (answer, True)
        ↓
    Fallback режим
        ↓
    Разбить на параграфы (\n\n)
        ↓
    Взять последний параграф
        ↓
    Вернуть (answer, False)
```

### Интеграция в пайплайн

```
[ENGINE] - Итерация CoT
    ↓
Получен ответ (response)
    ↓
[EXPRESSION/mouth] extract_final_answer(response)
    ↓
(answer, is_final) ← Проверка маркера
    ↓
is_final == True? → YES → Финальный ответ, стоп
    ↓
    NO
    ↓
Продолжить следующую итерацию (макс 4)
```

---

## 🔌 Интеграция с остальной системой

**Получает данные от:**
- `engine/` - Ответы модели после каждой итерации

**Передаёт данные в:**
- `main.py` / `app_chainlit.py` - Финальный ответ для отображения
- `memory/` - Ответ сохраняется в историю

**Используется в:**
- Каждая итерация CoT (проверка на финальность)
- Финальный вывод пользователю

---

## ✨ Особенности

- ✅ Умное извлечение по маркеру
- ✅ Fallback логика (без маркера)
- ✅ Очистка от служебных символов
- ✅ Поддержка мультиязычности
- ✅ Простой API (одна функция)

---

## 📋 Формат маркера

**Стандартный формат:**
```
FINAL_ANSWER: Текст ответа здесь
```

**Поддерживаются вариации:**
- `FINAL_ANSWER:` (с пробелом после)
- `FINAL_ANSWER:` (без пробела)
- Любой язык после маркера

**Не поддерживается:**
- `Final Answer:` (регистр важен)
- `ОТВЕТ:` (другой маркер)

---

## 🧪 Примеры использования

### Базовое использование

```python
from expression.mouth import extract_final_answer

response = engine_output  # Ответ от engine.think_one_step()

answer, is_final = extract_final_answer(response)

if is_final:
    print(f"✅ Финальный ответ: {answer}")
    # Сохранить в память и остановить итерации
else:
    print(f"⏳ Промежуточная мысль: {answer}")
    # Продолжить следующую итерацию
```

### В основном цикле (main.py)

```python
for iteration in range(1, MAX_COT_ITERATIONS + 1):
    response = think_one_step(...)
    brain.add_step(response)
    
    final_answer, is_final = speak(response)
    
    if is_final:
        print(f"\n{'=' * 60}")
        print(f"💬 Финальный ответ:")
        print(f"{'=' * 60}\n")
        print(final_answer)
        break
```

### С обработкой ошибок

```python
try:
    answer, is_final = extract_final_answer(response)
    
    if not answer or len(answer) < 5:
        # Слишком короткий ответ
        answer = "Извините, не смог сформулировать ответ."
        
except Exception as e:
    print(f"Ошибка извлечения ответа: {e}")
    answer = response  # Вернуть весь ответ как есть
```

---

## 🚀 Будущие улучшения

- [ ] Поддержка множественных маркеров (`ANSWER:`, `ОТВЕТ:`)
- [ ] Автоматическое форматирование ответа (Markdown)
- [ ] Извлечение структурированных ответов (JSON, списки)
- [ ] Валидация качества ответа (длина, полнота)
- [ ] Постобработка (исправление опечаток, форматирование)
- [ ] Эмоциональная окраска (sentiment analysis)
- [ ] Мультимодальный вывод (текст + изображения)
- [ ] Voice output (TTS интеграция)

---

## 🎨 Форматирование вывода

**Текущий формат (простой):**
```
============================================================
💬 Финальный ответ:
============================================================

[Текст ответа]
```

**Возможные улучшения:**
- Markdown рендеринг
- Syntax highlighting для кода
- Bullet points и нумерованные списки
- Цветной вывод в консоли
- Rich text в Chainlit

---

## 🔍 Отладка

**Типичные проблемы:**

1. **Маркер не найден**
   - Проблема: Модель не добавила `FINAL_ANSWER:`
   - Решение: Fallback возвращает последний параграф
   - Проверка: `is_final == False`

2. **Пустой ответ после маркера**
   - Проблема: `FINAL_ANSWER:` в конце без текста
   - Решение: Проверка `if answer.strip()`

3. **Многострочный ответ**
   - Всё после маркера извлекается полностью
   - Включая переносы строк

**Логирование:**
```python
answer, is_final = extract_final_answer(response)
print(f"DEBUG: is_final={is_final}, len={len(answer)}")
```

---

## 🧩 Альтернативные подходы

**Текущий:** Простой поиск строки  
**Альтернативы:**
- Regex с гибкими правилами
- Парсинг JSON-структурированного ответа
- XML/HTML маркеры
- Специальные токены в промпте

---

**Версия:** 2.0  
**Статус:** ✅ Полностью функционален  
**Зависимости:** Нет (только стандартная библиотека)  
**API:** Простой и понятный
