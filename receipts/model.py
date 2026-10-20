"""The data model: source tables of a fictional Indian fintech marketplace.

Column names are deliberately prefixed or compound (PAY_STATUS, TXN_DAY) so none
of them collide with SQL reserved words in Exasol. `receipts doctor` checks this
against SYS.EXA_SQL_KEYWORDS on a live Exasol database.
"""

from __future__ import annotations

from datetime import date

METRIC_NAME = "daily_revenue_inr"
METRIC_LABEL = "Daily revenue (INR)"

# history days published before the incoming batch, and the incoming batch day
DEFAULT_HISTORY_DAYS = 42
INCOMING_DAY = date(2026, 10, 20)
BASELINE_DAYS = 14
IST_OFFSET_MIN = 330

# schema -> table -> [(column, type)]
SOURCE_TABLES: dict[str, list[tuple[str, str]]] = {
    "ORDERS": [
        ("ORDER_ID", "BIGINT"),
        ("BATCH_DAY", "DATE"),
        ("MERCHANT_ID", "INTEGER"),
        ("CITY", "VARCHAR(20)"),
        ("CATEGORY_CODE", "VARCHAR(8)"),
        ("CHANNEL", "VARCHAR(8)"),
    ],
    "PAYMENTS": [
        ("PAYMENT_ID", "BIGINT"),
        ("ORDER_ID", "BIGINT"),
        ("BATCH_DAY", "DATE"),
        ("LOAD_FILE", "VARCHAR(12)"),
        ("GATEWAY", "VARCHAR(10)"),
        ("CURRENCY_CODE", "VARCHAR(3)"),
        ("AMOUNT", "DECIMAL(18,2)"),
        ("PAY_STATUS", "VARCHAR(10)"),
        ("CAPTURED_AT", "TIMESTAMP"),
    ],
    "MERCHANTS": [
        ("MERCHANT_ID", "INTEGER"),
        ("MERCHANT_NAME", "VARCHAR(40)"),
        ("TIER", "VARCHAR(8)"),
        ("VALID_FROM", "DATE"),
    ],
    "CATEGORY_MAP": [
        ("CATEGORY_CODE", "VARCHAR(8)"),
        ("CATEGORY_NAME", "VARCHAR(30)"),
    ],
    "FX_RATES": [
        ("RATE_DAY", "DATE"),
        ("CURRENCY_CODE", "VARCHAR(3)"),
        ("INR_PER_UNIT", "DOUBLE"),
    ],
}

# extra rows used only by the "real festival surge" control scenario
FESTIVAL_TABLES = {"FESTIVAL_ORDERS": "ORDERS", "FESTIVAL_PAYMENTS": "PAYMENTS"}

PIPE_VIEWS = ["STG_PAYMENTS", "STG_ORDERS", "DIM_MERCHANT", "DIM_CATEGORY", "FX_DAILY", "FCT_REVENUE", "DAILY_REVENUE"]

# dimensions the decomposition cube runs over
CUBE_DIMS = ["CITY", "CATEGORY_NAME", "CHANNEL", "GATEWAY", "CURRENCY_CODE", "TIER"]
