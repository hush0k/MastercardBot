.PHONY: help build up down restart logs clean test

help: ## Показать эту помощь
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Собрать все Docker образы
	docker-compose build

up: ## Запустить все сервисы
	docker-compose up -d

down: ## Остановить все сервисы
	docker-compose down

restart: ## Перезапустить все сервисы
	docker-compose restart

logs: ## Показать логи всех сервисов
	docker-compose logs -f

logs-backend: ## Показать логи бэкенда
	docker-compose logs -f backend

logs-ml: ## Показать логи ML сервиса
	docker-compose logs -f ml-service

logs-frontend: ## Показать логи фронтенда
	docker-compose logs -f frontend

clean: ## Удалить контейнеры, образы и volumes
	docker-compose down -v --rmi all

test: ## Запустить тесты
	docker-compose exec backend pytest

shell-backend: ## Открыть shell в бэкенд контейнере
	docker-compose exec backend /bin/bash

shell-ml: ## Открыть shell в ML контейнере
	docker-compose exec ml-service /bin/bash

dev: ## Запустить в dev режиме с логами
	docker-compose up

rebuild: ## Пересобрать и запустить все
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

status: ## Показать статус сервисов
	docker-compose ps

init: ## Первоначальная настройка проекта
	cp .env.example .env
	mkdir -p data models
	docker-compose build
	docker-compose up -d
	@echo "Проект инициализирован! Откройте http://localhost:3000"