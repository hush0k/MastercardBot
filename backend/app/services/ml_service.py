import httpx
import logging
from typing import Optional, Dict, Any
from ..config import settings

logger = logging.getLogger (__name__)


class MLService:
	def __init__ (self):
		self.ml_url = settings.ml_service_url
		self.timeout = settings.ml_service_timeout

	async def text_to_sql (self, question: str, schema_context: Optional[str] = None) -> Optional[str]:
		try:
			logger.info (f"Sending request to ML service: {question}")

			payload = {"question": question}
			if schema_context:
				payload["schema"] = schema_context

			async with httpx.AsyncClient (timeout = self.timeout) as client:
				response = await client.post (
					f"{self.ml_url}/generate-sql",
					json = payload
				)

				response.raise_for_status ()
				data = response.json ()
				sql = data.get ("sql")

				if not sql:
					logger.error ("ML service returned empty SQL")
					return None

				logger.info (f"ML service returned SQL: {sql[:100]}...")
				return sql

		except httpx.TimeoutException:
			logger.error (f"Timeout while contacting ML service ({self.timeout}s)")
			return None

		except httpx.HTTPError as e:
			logger.error (f"HTTP error while contacting ML service: {e}")
			return None

		except Exception as e:
			logger.error (f"Unexpected error while contacting ML service: {e}")
			return None

	async def check_health (self) -> bool:
		try:
			async with httpx.AsyncClient (timeout = 5) as client:
				response = await client.get (f"{self.ml_url}/health")
				return response.status_code == 200
		except Exception as e:
			logger.warning (f"ML service is unavailable: {e}")
			return False

	def clean_sql (self, sql: str) -> str:
		if "```sql" in sql:
			sql = sql.split ("```sql")[1].split ("```")[0]
		elif "```" in sql:
			sql = sql.split ("```")[1].split ("```")[0]

		sql = " ".join (sql.split ())
		sql = sql.strip ().rstrip (';')
		return sql

	async def get_model_info (self) -> Dict[str, Any]:
		try:
			async with httpx.AsyncClient (timeout = 5) as client:
				response = await client.get (f"{self.ml_url}/model-info")
				response.raise_for_status ()
				return response.json ()
		except Exception as e:
			logger.error (f"Error retrieving model info: {e}")
			return {"error": str (e)}
