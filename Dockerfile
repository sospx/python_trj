# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости (если нужны)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем директорию для загрузок
RUN mkdir -p static/uploads

# Открываем порт
EXPOSE 8080

# Переменные окружения
ENV FLASK_APP=main.py
ENV PYTHONUNBUFFERED=1

# Команда запуска
CMD ["python", "main.py"]

