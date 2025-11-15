# Database Schema

## Раздел 1: Список таблиц

1. `transactions` – основная таблица с транзакциями по банковским картам.

---

## Раздел 2: Описание таблицы `transactions`

**Назначение таблицы:**  
Хранит все операции по картам клиентов: покупки, снятия наличных, онлайн-платежи, переводы и т.д.

**Список колонок:**

| Column name             | Type        | Description                                                    | Example                          |
|-------------------------|------------|----------------------------------------------------------------|----------------------------------|
| transaction_id          | TEXT (UUID)| Уникальный идентификатор транзакции                           | `24f425b8-dc61-4537-a480-...`    |
| transaction_timestamp   | TIMESTAMP   | Дата и время проведения транзакции                            | `2023-08-12T17:57:52.941Z`       |
| expiry_date             | TEXT        | Срок действия карты в формате MM/YY                           | `09/26`                          |
| card_id                 | BIGINT      | Внутренний ID карты (обезличенный)                            | `10000`                          |
| issuer_bank_name        | TEXT        | Название банка-эмитента карты                                 | `My Favorite Bank`               |
| issuer_country_iso      | TEXT        | Страна банка-эмитента (ISO-код)                               | `KAZ`                            |
| merchant_id             | INT         | Внутренний ID торговой точки                                  | `50359`                          |
| merchant_mcc            | INT         | MCC-код категории мерчанта                                    | `5499`                           |
| mcc_category            | TEXT        | Описание категории MCC                                        | `Grocery & Food Markets`         |
| merchant_city           | TEXT        | Город, где находится торговая точка                           | `Almaty`                         |
| transaction_type        | TEXT        | Тип транзакции (POS, ECOM, ATM_WITHDRAWAL, BILL_PAYMENT и др.)| `POS`                            |
| transaction_amount_kzt  | NUMERIC     | Сумма операции в тенге (локальная валюта)                     | `238203`                         |
| original_amount         | NUMERIC     | Сумма операции в исходной валюте                              | `500`                            |
| transaction_currency    | TEXT        | Валюта исходной операции                                      | `KZT` / `USD`                    |
| acquirer_country_iso    | TEXT        | Страна банка-эквайера (обслуживает терминал мерчанта)         | `KAZ`                            |
| pos_entry_mode          | TEXT        | Способ проведения (Chip, Contactless, QR_Code, ECOM и т.п.)   | `Contactless`                    |
| wallet_type             | TEXT        | Тип кошелька (Apple Pay, Samsung Pay, Bank's QR и др.)        | `Apple Pay`                      |
| _index_level_0_         | INT         | Технический индекс (служебное поле, можно не использовать)    | `0`                              |

---

## Раздел 3: Связи между таблицами

Сейчас используется одна таблица `transactions`, поэтому явных связей нет.

**Потенциальные связи на будущее:**

- `card_id` → таблица `cards` (информация о карте/клиенте)
- `merchant_id` → таблица `merchants` (подробности о мерчанте)
- `issuer_bank_name` → таблица `banks` (справочник банков)

---

## Раздел 4: Важные колонки для запросов чат-бота

Колонки, которые чаще всего будут использоваться в запросах пользователей:

- **Фильтрация по времени:**
  - `transaction_timestamp`

- **Идентификация клиента / карты:**
  - `card_id`

- **Мерчанты и категории:**
  - `merchant_id`
  - `merchant_mcc`
  - `mcc_category`
  - `merchant_city`

- **Суммы и валюта:**
  - `transaction_amount_kzt`
  - `original_amount`
  - `transaction_currency`

- **Типы операций:**
  - `transaction_type`

- **География:**
  - `issuer_country_iso`
  - `acquirer_country_iso`

- **Способ оплаты:**
  - `pos_entry_mode`
  - `wallet_type`
