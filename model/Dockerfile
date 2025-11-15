# ML Service Dockerfile для модели text-to-SQL
FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements.txt
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование ML сервиса
COPY . /app

# Создание директории для моделей
RUN mkdir -p /app/models

# Expose порт
EXPOSE 8001

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')" || exit 1

# Запуск ML сервиса
CMD ["uvicorn", "ml_service:app", "--host", "0.0.0.0", "--port", "8001"]