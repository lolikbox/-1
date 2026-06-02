#!/bin/bash

# Скрипт для развертывания Django-приложения "Контейнер валидации транзакций"
# Автор: Сватков Тихон Леонидович, группа КН-23-10
# Дата: 2025

echo "========================================="
echo "  Развертывание приложения валидации транзакций"
echo "========================================="

# Проверка наличия Python 3
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python 3 не установлен."
    exit 1
fi

echo "1. Установка зависимостей из requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Файл requirements.txt не найден. Устанавливаем базовые пакеты..."
    pip install django pandas matplotlib jsonschema
fi

echo "2. Проверка наличия переменных окружения (секретов)..."
# Список необходимых секретов (опционально)
REQUIRED_SECRETS=("REGISTRY_USER" "REGISTRY_PASSWORD" "SIGN_KEY" "DB_USER" "DB_PASS")
for secret in "${REQUIRED_SECRETS[@]}"; do
    if [ -z "${!secret}" ]; then
        echo "Предупреждение: переменная $secret не установлена. Приложение может работать некорректно."
    fi
done

echo "3. Применение миграций базы данных..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "4. Сбор статических файлов (если необходимо)..."
python manage.py collectstatic --noinput || echo "collectstatic не настроен, пропускаем."

echo "5. Запуск сервера разработки..."
echo "Сервер запущен на 0.0.0.0:8000"
echo "Откройте в браузере: http://localhost:8000"
exec python manage.py runserver 0.0.0.0:8000