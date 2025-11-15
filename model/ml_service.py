"""
ML Service для text-to-SQL преобразования
FastAPI приложение с использованием Google Gemini
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
import os
import google.generativeai as genai

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="ML Service API",
    description="Text-to-SQL generation using Google Gemini",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация Google Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    # Используем gemini-pro - стабильная модель с хорошей поддержкой
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    model = None

# Database schema
DATABASE_SCHEMA = """
Table: transactions

Columns:
- TransactionID (TEXT) - Unique transaction identifier
- AccountID (TEXT) - Account identifier  
- TransactionAmount (NUMERIC) - Transaction amount
- TransactionDate (DATE) - Transaction date
- TransactionType (TEXT) - Type of transaction
- Location (TEXT) - Transaction location
- DeviceID (TEXT) - Device identifier
- IP Address (TEXT) - IP address (use "IP Address" with quotes in SQL!)
- MerchantID (TEXT) - Merchant identifier
- Channel (TEXT) - Transaction channel

Important:
- Use EXACT column names with correct capitalization
- For "IP Address" use: SELECT "IP Address" FROM transactions
- TransactionDate is DATE type, use: ORDER BY TransactionDate DESC
"""

def generate_sql(question: str):
    prompt = f"""You are a SQL expert. Generate valid SQL query.

{DATABASE_SCHEMA}

Question: {question}

Return ONLY the SQL query, nothing else."""


class SQLRequest(BaseModel):
    question: str
    schema: Optional[str] = None
    language: Optional[str] = "eng_Latn"


class SQLResponse(BaseModel):
    sql: str
    original_question: str


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ml-service",
        "model": "gemini-pro",
        "api_configured": GOOGLE_API_KEY != ""
    }


@app.get("/model-info")
async def model_info():
    """Return model information"""
    return {
        "model_name": "gemini-2.5-flash",
        "provider": "Google",
        "version": "1.0.0"
    }


@app.post("/generate-sql", response_model=SQLResponse)
async def generate_sql(request: SQLRequest):
    """
    Generate SQL query from natural language question
    """
    logger.info(f"Received question: {request.question}")

    if not GOOGLE_API_KEY or not model:
        logger.error("Google API key not configured")
        raise HTTPException(
            status_code=500,
            detail="Google API key not configured"
        )

    # Language mapping
    lang_map = {
        'rus_Cyrl': 'Russian',
        'kaz_Cyrl': 'Kazakh',
        'eng_Latn': 'English'
    }
    language_name = lang_map.get(request.language, 'English')

    # Use provided schema or default
    schema = request.schema or DATABASE_SCHEMA

    # Construct prompt
    prompt = f"""You are a SQL expert for Mastercard analytics.

User's question (in {language_name}): {request.question}

Database schema:
{schema}

Tasks:
1. If the question is not in English, first translate it to English
2. Generate a valid SQL query to answer the question
3. Return ONLY valid SQL query, nothing else
4. DO NOT include any explanation, markdown formatting, or SQL: prefix
5. Return only the raw SQL query

Example good response:
SELECT * FROM transactions WHERE transaction_date >= '2023-08-01' AND transaction_date < '2023-09-01'

Example bad response:
SQL: SELECT * FROM...
```sql
SELECT * FROM...
```
Here's the query: SELECT * FROM..."""

    try:
        logger.info("Calling Google Gemini...")

        # Call Gemini
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=1000,
            )
        )

        # Проверяем, был ли ответ заблокирован или обрезан
        if not response.text:
            logger.error("Empty response from Gemini")
            raise HTTPException(
                status_code=500,
                detail="Empty response from model"
            )

        result = response.text.strip()
        logger.info(f"Raw Gemini response: {result}")

        # Extract SQL from response (in case model didn't follow instructions)
        if "SQL:" in result:
            sql_query = result.split("SQL:")[-1].strip()
        else:
            sql_query = result

        # Clean SQL query - remove markdown code blocks
        if "```sql" in sql_query:
            sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql_query:
            sql_query = sql_query.split("```")[1].split("```")[0].strip()

        # Remove any explanatory text after the SQL (like "This query will...")
        lines = sql_query.split('\n')
        sql_lines = []
        for line in lines:
            line = line.strip()
            # Stop if we hit explanatory text
            if line and not line.upper().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH', 'FROM', 'WHERE', 'AND', 'OR', 'ORDER', 'GROUP', 'HAVING', 'LIMIT', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'AS')):
                if sql_lines:  # Only break if we already have SQL
                    break
            if line:
                sql_lines.append(line)

        sql_query = ' '.join(sql_lines).strip()

        logger.info(f"Generated SQL: {sql_query}")

        if not sql_query:
            raise HTTPException(
                status_code=500,
                detail="Failed to extract valid SQL from response"
            )

        return SQLResponse(
            sql=sql_query,
            original_question=request.question
        )

    except Exception as e:
        logger.error(f"Error generating SQL: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating SQL: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ML Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "generate_sql": "/generate-sql",
            "model_info": "/model-info"
        }
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting ML Service...")
    uvicorn.run(
        "ml_service:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )