# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем папки для статики и медиа
RUN mkdir -p staticfiles media

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Открываем порт (обязательно 8000 для SnapDeploy)
EXPOSE 8000

# Запускаем приложение через Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "profinder_django.wsgi:application"]