import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import duckdb

from .config import settings

logger = logging.getLogger(__name__)

class Database:

	def __init__(self):
		self.connection = None
		self.data_path = Path(settings.database_path)

	def connect(self) -> duckdb.DuckDBPyConnection:
		try:
			self.connection = duckdb.connect(database=settings.duckdb_mode, read_only=False)

			self.connection.execute(f"SET memory_limit='{settings.duckdb_memory_limit}';")
			self.connection.execute(f"SET threads={settings.duckdb_threads};")

			logger.info("Connected to DuckDB database in %s mode", settings.duckdb_mode)

			self._register_parquet_files()

			return self.connection

		except Exception as e:
			logger.error("Failed to connect to DuckDB database: %s", e)
			raise

	def _register_parquet_files(self):

		if not self.data_path.exists():
			logger.warning(f"Data path {self.data_path} does not exist.")
			return

		parquet_files = list(self.data_path.glob("*.parquet"))

		if not parquet_files:
			logger.warning(f"No Parquet files found in {self.data_path}.")
			return

		for parquet_file in parquet_files:
			table_name = parquet_file.stem
			try:
				sql = f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM read_parquet('{parquet_file}')"
				self.connection.execute(sql)
				logger.info(f"Registered Parquet file {parquet_file} as table {table_name}")
			except Exception as e:
				logger.error(f"Failed to register Parquet file {parquet_file}: {e}")

	def execute_query(self, query: str) -> Tuple[List[Dict[str, Any]], List[str]]:
		if not self.connection:
			self.connect()

		try:
			if settings.log_sql_queries:
				logger.info("Executing SQL query: %s", query)

			result = self.connection.execute(query)
			columns = [desc[0] for desc in result.description] if result.description else []

			rows = result.fetchall()

			if len(rows) > settings.max_result_rows:
				logger.warning("Query result exceeds max rows (%d). Truncating to %d rows.", len(rows), settings.max_result_rows)
				rows = rows[:settings.max_result_rows]

			results = [dict(zip(columns, row)) for row in rows]

			logger.info(f"Query executed successfully, returned {len(results)} rows.")
			return results, columns
		except Exception as e:
			logger.error("Failed to execute query: %s", e)
			raise

	def get_tables(self) -> List[str]:
		if not self.connection:
			self.connect()

		try:
			sql = """
				SELECT table_name
				FROM information_schema.tables
				WHERE table_schema = 'main'
				ORDER BY table_name
			"""
			result = self.connection.execute(sql).fetchall()
			tables = [row[0] for row in result]

			logger.info(f"📋 Found tables: {len(tables)}")
			return tables

		except Exception as e:
			logger.error(f"❌ Error getting table list: {e}")
			return []

	def get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
		if not self.connection:
			self.connect()

		try:
			sql = f"DESCRIBE {table_name}"
			result = self.connection.execute(sql).fetchall()

			schema = [
				{"name": row[0], "type": row[1]}
				for row in result
			]

			logger.info(f"📊 Schema of table {table_name}: {len(schema)} columns")
			return schema

		except Exception as e:
			logger.error(f"❌ Error getting schema for table {table_name}: {e}")
			raise

	def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
		if not self.connection:
			self.connect()

		try:
			sql = f"SELECT * FROM {table_name} LIMIT {limit}"
			results, columns = self.execute_query(sql)
			return results

		except Exception as e:
			logger.error(f"❌ Error getting samples from {table_name}: {e}")
			return []

	def validate_sql(self, sql: str) -> Tuple[bool, Optional[str]]:
		sql_upper = sql.strip().upper()
		dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']

		for keyword in dangerous_keywords:
			if keyword in sql_upper:
				return False, f"Forbidden operation: {keyword}. Only SELECT queries are allowed."

		if not sql_upper.startswith('SELECT'):
			return False, "Only SELECT queries are allowed."

		if not self.connection:
			self.connect()

		try:
			self.connection.execute(f"EXPLAIN {sql}")
			return True, None

		except Exception as e:
			return False, f"Invalid SQL: {str(e)}"

	def close(self):
		if self.connection:
			self.connection.close()
			logger.info("🔌 DuckDB connection closed")


_db_instance: Optional[Database] = None


def get_database () -> Database:
	global _db_instance

	if _db_instance is None:
		_db_instance = Database ()
		_db_instance.connect ()

	return _db_instance

