"""
Agentic Analyst Backend
FastAPI приложение для text-to-SQL чат-бота
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from logging.config import dictConfig

from .config import settings
from .database import get_database
from .api import router

# Настройка логирования
dictConfig ({
	"version": 1,
	"disable_existing_loggers": False,
	"formatters": {
		"default": {
			"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
		},
	},
	"handlers": {
		"console": {
			"class": "logging.StreamHandler",
			"formatter": "default",
		},
	},
	"root": {
		"level": settings.log_level,
		"handlers": ["console"],
	},
})

logger = logging.getLogger (__name__)


@asynccontextmanager
async def lifespan (app: FastAPI):
	"""
	Lifecycle events для FastAPI
	Выполняется при старте и остановке приложения
	"""
	# Startup
	logger.info ("🚀 Запуск Agentic Analyst Backend...")
	logger.info (f"⚙️  Режим: {'DEV' if settings.dev_mode else 'PRODUCTION'}")
	logger.info (f"📊 База данных: {settings.database_type}")
	logger.info (f"🤖 ML сервис: {settings.ml_service_url}")

	# Подключаемся к БД
	try:
		db = get_database ()
		tables = db.get_tables ()
		logger.info (f"✅ База данных подключена. Таблиц: {len (tables)}")
		if tables:
			logger.info (f"📋 Доступные таблицы: {', '.join (tables)}")
		else:
			logger.warning ("⚠️  Нет доступных таблиц в БД")
	except Exception as e:
		logger.error (f"❌ Ошибка подключения к БД: {e}")

	yield

	# Shutdown
	logger.info ("🛑 Остановка Agentic Analyst Backend...")
	try:
		db = get_database ()
		db.close ()
		logger.info ("✅ База данных закрыта")
	except Exception as e:
		logger.error (f"❌ Ошибка при закрытии БД: {e}")


# Создание FastAPI приложения
app = FastAPI (
	title = "Agentic Analyst API",
	description = "Text-to-SQL чат-бот для аналитики данных",
	version = "1.0.0",
	docs_url = "/docs" if settings.enable_docs else None,
	redoc_url = "/redoc" if settings.enable_docs else None,
	lifespan = lifespan
)

# Настройка CORS
app.add_middleware (
	CORSMiddleware,
	allow_origins = settings.cors_origins_list,
	allow_credentials = True,
	allow_methods = ["*"],
	allow_headers = ["*"],
)

# Подключение роутов
app.include_router (router, prefix = "")


# Root endpoint
@app.get ("/", tags = ["Root"])
async def root ():
	"""
	Корневой endpoint
	Возвращает информацию об API
	"""
	return {
		"name": "Agentic Analyst API",
		"version": "1.0.0",
		"description": "Text-to-SQL chatbot for data analytics",
		"endpoints": {
			"docs": "/docs",
			"health": "/health",
			"query": "/query",
			"tables": "/tables",
			"schema": "/schema/{table_name}"
		}
	}


# Middleware для логирования запросов
@app.middleware ("http")
async def log_requests (request, call_next):
	"""Логирование всех HTTP запросов"""
	logger.info (f"📨 {request.method} {request.url.path}")
	response = await call_next (request)
	logger.info (f"📤 {request.method} {request.url.path} - {response.status_code}")
	return response


if __name__ == "__main__":
	import uvicorn

	uvicorn.run (
		"app.main:app",
		host = "0.0.0.0",
		port = 8000,
		reload = settings.dev_mode,
		log_level = settings.log_level.lower ()
	)