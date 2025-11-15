# Agentic Analyst - Text-to-SQL Chatbot

Чат-бот для выполнения SQL запросов на естественном языке.

## 🚀 Быстрый старт с Docker

### Предварительные требования
- Docker (версия 20.10+)
- Docker Compose (версия 2.0+)
- 8GB RAM минимум (для ML модели)

### Запуск проекта

```bash
# 1. Клонировать репозиторий
git clone <your-repo-url>
cd agentic-analyst

# 2. Скопировать .env файл
cp .env .env

# 3. Собрать и запустить все сервисы
make init

# ИЛИ вручную:
docker-compose build
docker-compose up -d
```

### Доступ к сервисам

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs
- **ML Service**: http://localhost:8001

## 📦 Структура проекта

```
agentic-analyst/
├── backend/           # FastAPI бэкенд
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── ml/               # ML сервис (text-to-SQL)
│   ├── ml_service.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/         # Веб интерфейс
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── Dockerfile
├── data/            # Parquet файлы с данными
├── docker-compose.yml
└── Makefile
```

## 🛠 Команды Makefile

```bash
make help           # Показать все доступные команды
make build          # Собрать все Docker образы
make up             # Запустить все сервисы
make down           # Остановить все сервисы
make logs           # Показать логи всех сервисов
make logs-backend   # Показать логи бэкенда
make logs-ml        # Показать логи ML сервиса
make restart        # Перезапустить сервисы
make clean          # Удалить все контейнеры и образы
make rebuild        # Пересобрать все с нуля
make status         # Показать статус сервисов
```

## 🔧 Разработка

### Запуск в dev режиме (с логами)
```bash
make dev
# ИЛИ
docker-compose up
```

### Остановка сервисов
```bash
make down
# ИЛИ
docker-compose down
```

### Просмотр логов
```bash
# Все сервисы
make logs

# Только бэкенд
make logs-backend

# Только ML
make logs-ml
```

### Shell в контейнере
```bash
# Backend
make shell-backend

# ML Service
make shell-ml
```

## 📊 Примеры запросов

После запуска, вы можете задавать вопросы:

- "Total transactions for Silk Pay in Q1 2024"
- "Top 5 merchants by revenue in Kazakhstan last year"
- "Average check for merchant Yandex from 2022 to 2025"

## 🐛 Troubleshooting

### ML модель не загружается
```bash
# Проверить логи
make logs-ml

# Увеличить память для Docker (в настройках Docker Desktop)
```

### Backend не подключается к ML сервису
```bash
# Проверить что ML сервис запущен
docker-compose ps

# Проверить сеть
docker network inspect agentic-analyst_agentic-network
```

### Frontend не отображается
```bash
# Проверить логи nginx
make logs-frontend

# Пересобрать frontend
docker-compose build frontend
docker-compose up -d frontend
```

## 📝 Переменные окружения

Скопируйте `.env.example` в `.env` и настройте:

```bash
# Backend
DATABASE_PATH=/app/data
ML_SERVICE_URL=http://ml-service:8001

# ML Service
MODEL_NAME=NumbersStation/nsql-llama-2-7B
MODEL_CACHE_DIR=/app/models
```

## 🚢 Production деплой

Для production используйте:

```bash
# Production docker-compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📄 Лицензия

MIT License

## 👥 Команда

- **Каныш** - Backend разработка
- **Акнур** - ML инженер
- **Сабина** - Данные и схема БД
- **Самал** - Frontend разработка