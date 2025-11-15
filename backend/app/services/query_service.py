import time
import logging
from typing import Dict, Any, List
from ..database import Database
from ..config import settings

logger = logging.getLogger (__name__)


class QueryService:
	def __init__ (self, db: Database):
		self.db = db

	def execute_query (self, sql: str, original_question: str) -> Dict[str, Any]:
		start_time = time.time ()

		try:
			is_valid, error_msg = self.db.validate_sql (sql)
			if not is_valid:
				logger.warning (f"Invalid SQL: {error_msg}")
				return {
					"question": original_question,
					"sql": sql,
					"results": [],
					"columns": [],
					"row_count": 0,
					"execution_time": None,
					"error": f"Invalid SQL query: {error_msg}"
				}

			results, columns = self.db.execute_query (sql)
			execution_time = round (time.time () - start_time, 3)

			response = {
				"question": original_question,
				"sql": sql,
				"results": results,
				"columns": columns,
				"row_count": len (results),
				"execution_time": execution_time,
				"error": None
			}

			if settings.log_sql_queries:
				logger.info (f"Query executed successfully: {len (results)} rows in {execution_time}s")

			return response

		except Exception as e:
			execution_time = round (time.time () - start_time, 3)
			error_msg = str (e)

			logger.error (f"Query execution error: {error_msg}")

			return {
				"question": original_question,
				"sql": sql,
				"results": [],
				"columns": [],
				"row_count": 0,
				"execution_time": execution_time,
				"error": f"SQL execution error: {error_msg}"
			}

	def get_all_tables (self) -> List[str]:
		try:
			tables = self.db.get_tables ()
			logger.info (f"Retrieved table list: {len (tables)}")
			return tables
		except Exception as e:
			logger.error (f"Error retrieving tables: {e}")
			return []

	def get_table_info (self, table_name: str) -> Dict[str, Any]:
		try:
			schema = self.db.get_table_schema (table_name)
			sample_data = self.db.get_sample_data (table_name, limit = 3)
			return {
				"table_name": table_name,
				"columns": schema,
				"sample_data": sample_data
			}
		except Exception as e:
			logger.error (f"Error retrieving table info {table_name}: {e}")
			raise

	def validate_and_sanitize_sql (self, sql: str) -> str:
		sql = sql.strip ()

		if sql.endswith (';'):
			sql = sql[:-1]

		if not sql.upper ().startswith ('SELECT'):
			raise ValueError ("Only SELECT queries are allowed")

		return sql
