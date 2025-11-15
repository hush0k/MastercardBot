import openai
import pandas as pd
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

print("✅ API ключ установлен!")


def process_question_gpt4(user_question, user_language, database_schema):
    """
    Обработка вопроса через GPT-4
    """
    print(f"\n{'='*50}")
    print(f"📝 Вопрос: {user_question}")
    print(f"🌍 Язык: {user_language}")
    

    lang_map = {
        'rus_Cyrl': 'Russian',
        'kaz_Cyrl': 'Kazakh',
        'eng_Latn': 'English'
    }
    language_name = lang_map.get(user_language, 'English')
    
    prompt = f"""You are a SQL expert for Mastercard analytics.

User's question (in {language_name}): {user_question}

Database schema:
{database_schema}

Tasks:
1. If the question is not in English, first translate it to English
2. Generate a valid SQL query to answer the question
3. Return ONLY valid SQL query, nothing else

Response format:
SQL: [your SQL query here]"""

    print(f"🔄 Отправляю запрос в GPT-4...")
    
    try:
        # Вызов GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a SQL expert. Generate only valid SQL queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        result = response.choices[0].message.content.strip()
        
        if "SQL:" in result:
            sql_query = result.split("SQL:")[-1].strip()
        else:
            sql_query = result
    
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        print(f"✅ SQL: {sql_query}")
        
        return {
            'original_question': user_question,
            'language': user_language,
            'sql_query': sql_query,
            'full_response': result
        }
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return {
            'original_question': user_question,
            'language': user_language,
            'sql_query': f"ERROR: {e}",
            'full_response': str(e)
        }


DATABASE_SCHEMA = """
CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    merchant_name TEXT,
    merchant_id TEXT,
    country TEXT,
    city TEXT,
    category TEXT,
    amount FLOAT,
    currency TEXT,
    transaction_date DATE,
    transaction_time TIME,
    status TEXT,
    card_type TEXT,
    customer_id TEXT
);
"""

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 MASTERCARD AI CHATBOT (GPT-4)")
    print("="*50)
    
    print("\n📊 Загрузка датасета...")
    try:
        df = pd.read_parquet('../data/example_dataset.parquet')
        print(f"✅ Загружено {len(df)} записей")
        print(f"📋 Колонки: {df.columns.tolist()}")
    except Exception as e:
        print(f"⚠️ Не удалось загрузить датасет: {e}")
        df = None

    test_questions = [
        {
            'question': 'Сколько всего транзакций для Silk Pay в первом квартале 2024?',
            'language': 'rus_Cyrl'
        },
        {
            'question': 'Show me top 5 merchants by revenue in Kazakhstan',
            'language': 'eng_Latn'
        },
        {
            'question': 'Казахстандағы ең үлкен 5 мерчант',
            'language': 'kaz_Cyrl'
        },
        {
            'question': 'Какой процент отказов в октябре?',
            'language': 'rus_Cyrl'
        }
    ]

    results = []
    for i, test in enumerate(test_questions, 1):
        print(f"\n📌 Вопрос {i}/{len(test_questions)}")
        result = process_question_gpt4(
            test['question'],
            test['language'],
            DATABASE_SCHEMA
        )
        results.append(result)

    df_results = pd.DataFrame(results)
    df_results.to_csv('test_results_gpt4.csv', index=False)
    print(f"\n✅ Результаты сохранены в test_results_gpt4.csv")
    
    print("\n" + "="*50)
    print("🎉 Тестирование завершено!")
    print("="*50)
    

    print("\n📊 РЕЗУЛЬТАТЫ:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['original_question']}")
        print(f"   SQL: {result['sql_query']}")