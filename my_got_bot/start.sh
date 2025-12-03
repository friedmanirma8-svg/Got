#!/bin/bash

# Скрипт быстрого старта для Chain-of-Thought Chatbot

echo "🚀 Установка Chain-of-Thought Chatbot"
echo "======================================"
echo ""

# Проверяем Python
if ! command -v python &> /dev/null; then
    echo "❌ Python не найден. Установите Python 3.7+"
    exit 1
fi

echo "✅ Python найден: $(python --version)"
echo ""

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip install -q requests python-dotenv

if [ $? -eq 0 ]; then
    echo "✅ Зависимости установлены"
else
    echo "❌ Ошибка при установке зависимостей"
    exit 1
fi
echo ""

# Проверяем .env файл
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден"
    echo "📝 Создаём .env из .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  ВАЖНО: Откройте .env и добавьте ваш TOGETHER_API_KEY"
    echo ""
    echo "Получить ключ можно здесь:"
    echo "👉 https://api.together.xyz/settings/api-keys"
    echo ""
    read -p "Нажмите Enter после добавления ключа в .env..."
fi

echo ""
echo "🎉 Готово! Запускаем бота..."
echo ""
python main.py
