"""
ЧТО ДЕЛАЕТ ЭТОТ ФАЙЛ / МОДУЛЬ:
Главный движок размышлений чатбота. Содержит функцию think_one_step(), которая
выполняет одну итерацию Chain-of-Thought: загружает промпт из файла, подставляет
контекст (историю, текущие мысли, новое сообщение), отправляет запрос в Together.ai
и возвращает ответ модели. Промпты загружаются из текстовых файлов для удобства редактирования.
"""

import os
import requests
from config import TOGETHER_API_KEY, MODEL_NAME


def load_prompt(filename):
    """
    Загружает промпт из текстового файла в папке prompts/.
    """
    prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
    filepath = os.path.join(prompts_dir, filename)
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Промпт файл не найден: {filepath}")


def think_one_step(user_message, history, current_cot, is_first_step=True):
    """
    Выполняет одну итерацию Chain-of-Thought размышлений.
    
    Параметры:
    - user_message: текущее сообщение пользователя
    - history: отформатированная история диалога
    - current_cot: текущая цепочка мыслей
    - is_first_step: True для первой итерации, False для последующих
    
    Возвращает: текст ответа модели
    """
    print("\n" + "=" * 60)
    print("=== ENGINE ===")
    print("=" * 60)
    
    # Выбираем нужный промпт
    prompt_file = "cot_initial.txt" if is_first_step else "cot_refine.txt"
    prompt_template = load_prompt(prompt_file)
    
    # Подставляем переменные в промпт
    prompt = prompt_template.format(
        history=history,
        user_message=user_message,
        current_cot=current_cot if current_cot else "(empty — starting fresh)"
    )
    
    print(f"🤖 Отправка запроса к {MODEL_NAME}...")
    print(f"📝 Используется промпт: {prompt_file}")
    
    # Формируем запрос к Together.ai API
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        assistant_message = result["choices"][0]["message"]["content"]
        
        print("✅ Ответ получен")
        return assistant_message
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при запросе к API: {e}")
        return f"ERROR: Could not reach Together.ai API - {e}"
