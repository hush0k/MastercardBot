#!/usr/bin/env python3
"""
Обновленный метод для database.py - поддержка CSV и Parquet
"""


# Добавьте этот метод в backend/app/database.py вместо _register_parquet_files

def _register_data_files (self):
	"""
	Регистрирует CSV и Parquet файлы как таблицы в DuckDB
	"""
	if not self.data_path.exists ():
		logger.warning (f"Data path {self.data_path} does not exist.")
		return

	# Находим CSV файлы
	csv_files = list (self.data_path.glob ("*.csv"))

	# Находим Parquet файлы
	parquet_files = list (self.data_path.glob ("*.parquet"))

	all_files = csv_files + parquet_files

	if not all_files:
		logger.warning (f"No CSV or Parquet files found in {self.data_path}.")
		return

	for data_file in all_files:
		table_name = data_file.stem

		try:
			if data_file.suffix == '.csv':
				# Для CSV используем read_csv_auto
				sql = f"""
                CREATE OR REPLACE VIEW {table_name} AS 
                SELECT * FROM read_csv_auto('{data_file}', 
                    header=true,
                    delim=',',
                    quote='"',
                    escape='"',
                    ignore_errors=true
                )
                """
			else:  # .parquet
				sql = f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM read_parquet('{data_file}')"

			self.connection.execute (sql)
			logger.info (f"✅ Registered {data_file.suffix} file as table '{table_name}'")

		except Exception as e:
			logger.error (f"❌ Failed to register {data_file}: {e}")


# ============================================================
# Полный скрипт конвертации CSV в Parquet
# ============================================================

import pandas as pd
import sys
from pathlib import Path


def convert_csv_to_parquet (csv_path: str, output_name: str = "transactions"):
	"""
	Конвертирует CSV в Parquet формат

	Args:
		csv_path: путь к CSV файлу
		output_name: имя выходного файла (без расширения)
	"""
	try:
		print (f"📂 Читаю CSV файл: {csv_path}")

		# Читаем CSV
		df = pd.read_csv (csv_path)

		print (f"✅ Загружено {len (df)} строк, {len (df.columns)} колонок")
		print (f"📋 Колонки: {', '.join (df.columns.tolist ())}")

		# Показываем первые строки
		print ("\n📊 Первые 3 строки:")
		print (df.head (3))

		# Информация о типах данных
		print ("\n🔍 Типы данных:")
		print (df.dtypes)

		# Конвертируем в Parquet
		data_dir = Path ("data")
		data_dir.mkdir (exist_ok = True)

		output_path = data_dir / f"{output_name}.parquet"

		print (f"\n💾 Сохраняю в Parquet: {output_path}")
		df.to_parquet (output_path, index = False, engine = 'pyarrow')

		# Проверяем размер файла
		file_size = output_path.stat ().st_size / (1024 * 1024)  # MB
		print (f"✅ Успешно сохранено!")
		print (f"📦 Размер файла: {file_size:.2f} MB")

		# Проверяем что файл читается
		print (f"\n🔍 Проверяю Parquet файл...")
		df_check = pd.read_parquet (output_path)
		print (f"✅ Файл читается корректно: {len (df_check)} строк")

		return True

	except FileNotFoundError:
		print (f"❌ Ошибка: Файл {csv_path} не найден!")
		return False

	except Exception as e:
		print (f"❌ Ошибка при конвертации: {e}")
		import traceback
		traceback.print_exc ()
		return False


if __name__ == "__main__":
	# Путь к вашему CSV файлу
	csv_file = "data/bank_transactions_data_2.csv"

	# Имя таблицы в базе данных
	table_name = "transactions"

	if len (sys.argv) > 1:
		csv_file = sys.argv[1]
	if len (sys.argv) > 2:
		table_name = sys.argv[2]

	print ("=" * 60)
	print ("🚀 CSV to Parquet Converter")
	print ("=" * 60)

	success = convert_csv_to_parquet (csv_file, table_name)

	if success:
		print ("\n" + "=" * 60)
		print ("🎉 Конвертация завершена успешно!")
		print ("=" * 60)
		print (f"\n📝 Следующие шаги:")
		print (f"1. Проверьте файл: data/{table_name}.parquet")
		print (f"2. Запустите Docker: make up")
		print (f"3. Откройте http://localhost:3000")
	else:
		print ("\n" + "=" * 60)
		print ("❌ Конвертация не удалась")
		print ("=" * 60)
		sys.exit (1)