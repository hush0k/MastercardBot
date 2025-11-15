from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from ..models.schemas import (
	QueryRequest,
	QueryResponse,
	HealthResponse,
	TableListResponse,
	TableSchemaResponse,
	ErrorResponse
)
from ..database import Database, get_database
from ..services.query_service import QueryService
from ..services.ml_service import MLService
from ..config import settings

logger = logging.getLogger (__name__)

router = APIRouter ()
ml_service = MLService ()


@router.get ("/health", response_model = HealthResponse, tags = ["Health"])
async def health_check (db: Database = Depends (get_database)):
	db_status = "connected"
	try:
		db.get_tables ()
	except Exception as e:
		db_status = f"error: {str (e)}"
		logger.error (f"Database health check failed: {e}")

	ml_status = "unknown"
	try:
		ml_available = await ml_service.check_health ()
		ml_status = "connected" if ml_available else "disconnected"
	except Exception as e:
		ml_status = f"error: {str (e)}"
		logger.error (f"ML service health check failed: {e}")

	return HealthResponse (
		status = "ok",
		database = db_status,
		ml_service = ml_status
	)


@router.get ("/tables", response_model = TableListResponse, tags = ["Database"])
async def get_tables (db: Database = Depends (get_database)):
	try:
		query_service = QueryService (db)
		tables = query_service.get_all_tables ()

		return TableListResponse (
			tables = tables,
			count = len (tables)
		)

	except Exception as e:
		logger.error (f"Error retrieving table list: {e}")
		raise HTTPException (status_code = 500, detail = f"Error retrieving tables: {str (e)}")


@router.get ("/schema/{table_name}", response_model = TableSchemaResponse, tags = ["Database"])
async def get_table_schema (table_name: str, db: Database = Depends (get_database)):
	try:
		query_service = QueryService (db)
		table_info = query_service.get_table_info (table_name)

		return TableSchemaResponse (**table_info)

	except Exception as e:
		logger.error (f"Error retrieving schema for table {table_name}: {e}")
		raise HTTPException (
			status_code = 404,
			detail = f"Table '{table_name}' not found or error occurred: {str (e)}"
		)


@router.post ("/query", response_model = QueryResponse, tags = ["Query"])
async def execute_query (
		request: QueryRequest,
		db: Database = Depends (get_database)
):
	question = request.text.strip ()

	logger.info (f"Received question: {question}")

	try:
		logger.info ("Generating SQL using ML service...")
		sql = await ml_service.text_to_sql (question)

		if not sql:
			logger.error ("ML service failed to generate SQL")
			return QueryResponse (
				question = question,
				sql = None,
				results = [],
				columns = [],
				row_count = 0,
				error = "Failed to generate SQL query. Try rephrasing the question."
			)

		sql = ml_service.clean_sql (sql)
		logger.info (f"Generated SQL: {sql}")

	except Exception as e:
		logger.error (f"SQL generation error: {e}")
		return QueryResponse (
			question = question,
			sql = None,
			results = [],
			columns = [],
			row_count = 0,
			error = f"Error generating SQL: {str (e)}"
		)

	# Execute SQL query
	try:
		logger.info ("Executing SQL query...")
		query_service = QueryService (db)
		result = query_service.execute_query (sql, question)

		return QueryResponse (
			question = result["question"],
			sql = result["sql"],
			results = result["results"],
			columns = result["columns"],
			row_count = result["row_count"],
			execution_time = result.get ("execution_time"),
			error = result.get ("error")
		)

	except Exception as e:
		logger.error (f"Query execution error: {e}")
		return QueryResponse (
			question = question,
			sql = sql,
			results = [],
			columns = [],
			row_count = 0,
			error = f"Error executing query: {str (e)}"
		)
