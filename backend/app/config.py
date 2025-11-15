from functools import lru_cache

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
	database_type: str = "duckdb"
	database_path: str = "app/data"
	ml_service_url: str = "http://ml-service:8001"
	log_level: str = "INFO"
	cors_origins: str = "http://localhost:3000,http://localhost"
	max_result_rows: int = 1000
	ml_service_timeout: int = 60


	duckdb_mode: str = ":memory:"  # Options: ":memory:", "persistent"
	duckdb_memory_limit: str = "4GB"  # e.g., "4GB", "512MB"
	duckdb_threads: int = 4  # Number of threads for DuckDB operations

	api_key: str = ""
	secret_key: str = ""
	rate_limit_enabled: bool = False
	rate_limit_requests: int = 100
	rate_limit_period: int = 60  # in seconds

	log_sql_queries: bool = True
	log_results: bool = False
	save_query_history: bool = True
	query_history_path: str = "app/data/query_history.json"

	dev_mode: bool = True
	enable_docs: bool = True
	verbose_errors: bool = True

	class Config:
		env_file = ".env"
		case_sensitive = False


	@property
	def cros_origins_list(self) -> list[str]:
		return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
	return Settings()

settings = get_settings()
