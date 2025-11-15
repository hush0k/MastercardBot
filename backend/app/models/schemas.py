from typing import Any, Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
	text: str = Field(..., description="The text to be processed", min_length=1)

	class Config:
		json_schema_extra = {
			"example": {
				"text": "What is the capital of France?"
			}
		}


class QueryResponse(BaseModel):
	question: str = Field(..., description="The original question text")
	sql: Optional[str] = Field(None, description="The generated SQL query, if applicable")
	results: List[Dict[str, Any]] = Field(default_factory=list, description="The result of the query execution")
	columns: List[str] = Field (default_factory = list, description = "Names of the columns in the result set")
	row_count: int = Field (0, description = "Count of rows in the result set")
	execution_time: Optional[float] = Field (None, description = "Execution time of the query in seconds")
	error: Optional[str] = Field (None, description = "Error message if query failed")

	class Config:
		json_schema_extra = {
			"example": {
				"question": "Top 5 merchants by revenue",
				"sql": "SELECT merchant_name, SUM(amount) as revenue FROM transactions GROUP BY merchant_name ORDER BY revenue DESC LIMIT 5",
				"results": [
					{"merchant_name": "Yandex", "revenue": 1500000},
					{"merchant_name": "Silk Pay", "revenue": 1200000}
				],
				"columns": ["merchant_name", "revenue"],
				"row_count": 2,
				"execution_time": 0.15,
				"error": None
			}
		}


class ErrorResponse (BaseModel):
	"""Standard error format"""
	error: str = Field (..., description = "Error description")
	detail: Optional[str] = Field (None, description = "Error details")
	timestamp: datetime = Field (default_factory = datetime.now, description = "Error timestamp")

	class Config:
		json_schema_extra = {
			"example": {
				"error": "Failed to generate SQL",
				"detail": "ML service returned invalid response",
				"timestamp": "2024-11-15T10:30:00"
			}
		}


class HealthResponse (BaseModel):
	"""Response for healthcheck endpoint"""
	status: str = Field ("ok", description = "Service status")
	timestamp: datetime = Field (default_factory = datetime.now)
	database: str = Field ("connected", description = "Database status")
	ml_service: str = Field ("unknown", description = "ML service status")


class TableInfo (BaseModel):
	"""Information about a database table"""
	name: str = Field (..., description = "Table name")
	columns: List[str] = Field (..., description = "List of columns")
	row_count: Optional[int] = Field (None, description = "Number of rows")

	class Config:
		json_schema_extra = {
			"example": {
				"name": "transactions",
				"columns": ["id", "merchant_name", "amount", "date"],
				"row_count": 10000
			}
		}


class TableListResponse (BaseModel):
	"""List of tables in the database"""
	tables: List[str] = Field (..., description = "Names of all tables")
	count: int = Field (..., description = "Number of tables")


class TableSchemaResponse (BaseModel):
	"""Schema of a specific table"""
	table_name: str = Field (..., description = "Name of the table")
	columns: List[Dict[str, str]] = Field (..., description = "Columns with types")
	sample_data: Optional[List[Dict[str, Any]]] = Field (None, description = "Sample data rows")

	class Config:
		json_schema_extra = {
			"example": {
				"table_name": "transactions",
				"columns": [
					{"name": "id", "type": "INTEGER"},
					{"name": "merchant_name", "type": "VARCHAR"},
					{"name": "amount", "type": "DECIMAL"}
				],
				"sample_data": [
					{"id": 1, "merchant_name": "Yandex", "amount": 1500.50}
				]
			}
		}
