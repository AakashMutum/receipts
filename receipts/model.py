"""The data model: source tables of a fictional Indian fintech marketplace.

Column names are deliberately prefixed or compound (PAY_STATUS, TXN_DAY) so none
of them collide with SQL reserved words in Exasol. `receipts doctor` checks this
against SYS.EXA_SQL_KEYWORDS on a live Exasol database.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

METRIC_NAME = "daily_revenue_inr"
METRIC_LABEL = "Daily revenue (INR)"

# history days published before the incoming batch, and the fixed incoming batch day that tests,
# judge-check, eval and the exported SQL use so their results stay reproducible
DEFAULT_HISTORY_DAYS = 42
INCOMING_DAY = date(2026, 10, 20)
BASELINE_DAYS = 14
IST_OFFSET_MIN = 330
IST = timezone(timedelta(minutes=IST_OFFSET_MIN))  # India has no daylight saving, so a fixed offset is exact


def default_incoming_day(now: datetime | None = None) -> date:
    """Yesterday in India: the latest full day a nightly batch would have landed for. Used by init and serve."""
    now = now or datetime.now(IST)
    return now.astimezone(IST).date() - timedelta(days=1)

def expected_day() -> date:
    """The day the command center should show: the pinned --day (RECEIPTS_DAY), else yesterday in India."""
    import os
    pinned = os.environ.get("RECEIPTS_DAY")
    return date.fromisoformat(pinned) if pinned else default_incoming_day()


def stale_message(data_day: date | None) -> str:
    if data_day is None:
        return "No data yet. Run receipts demo to build it."
    return f"The data is for {data_day:%a %d %b %Y}. Run receipts demo to refresh."


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
