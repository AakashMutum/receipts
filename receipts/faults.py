"""The scenario catalog: six seeded faults, two controls, a masked pair and an
unknown fault class. Every scenario is a list of plain SQL statements applied to
RAW after the clean incoming batch has been ingested, so the faults happen
inside the database, exactly where a broken upstream feed would put them.

Ground truth lives here and only here. The investigation engine never imports
this module; it only sees the database.
"""

from __future__ import annotations

from dataclasses import dataclass, field

D = "{{ day(incoming) }}"


@dataclass
class Scenario:
    id: str
    title: str
    story: str
    expected_verdict: str  # NO_INCIDENT, REAL_CHANGE, PROVEN_FAULT, UNEXPLAINED
    expected_causes: frozenset = field(default_factory=frozenset)
    inject: list[str] = field(default_factory=list)
    festival: bool = False
    kind: str = "fault"  # fault, control, unknown


UNIT = f"UPDATE RAW.PAYMENTS SET AMOUNT = AMOUNT * 100 WHERE BATCH_DAY = {D} AND GATEWAY = 'GW_C'"
DUP = (f"INSERT INTO RAW.PAYMENTS SELECT PAYMENT_ID, ORDER_ID, BATCH_DAY, LOAD_FILE, GATEWAY, CURRENCY_CODE, AMOUNT, "
       f"PAY_STATUS, CAPTURED_AT FROM RAW.PAYMENTS WHERE BATCH_DAY = {D} AND LOAD_FILE = 'F05'")
FANOUT = (f"INSERT INTO RAW.MERCHANTS SELECT MERCHANT_ID, MERCHANT_NAME, "
          f"CASE WHEN TIER = 'BRONZE' THEN 'SILVER' ELSE 'GOLD' END, {D} "
          f"FROM RAW.MERCHANTS WHERE MOD(MERCHANT_ID, 5) = 0")
STALE = f"DELETE FROM RAW.FX_RATES WHERE RATE_DAY = {D}"
TZ = (f"UPDATE RAW.PAYMENTS SET CAPTURED_AT = {{{{ add_minutes('CAPTURED_AT', 330) }}}} "
      f"WHERE BATCH_DAY = {D} AND GATEWAY = 'GW_B'")
DUP2 = (f"INSERT INTO RAW.PAYMENTS SELECT PAYMENT_ID, ORDER_ID, BATCH_DAY, LOAD_FILE, GATEWAY, CURRENCY_CODE, AMOUNT, "
        f"PAY_STATUS, CAPTURED_AT FROM RAW.PAYMENTS WHERE BATCH_DAY = {D} AND LOAD_FILE IN ('F05', 'F06')")
ORPHAN = (f"UPDATE RAW.ORDERS SET CATEGORY_CODE = 'ELC2' "
          f"WHERE BATCH_DAY = {D} AND CATEGORY_CODE = 'ELEC' AND MOD(ORDER_ID, 2) = 0")
DISCOUNT = (f"UPDATE RAW.PAYMENTS SET AMOUNT = ROUND(AMOUNT * 0.5, 2) WHERE BATCH_DAY = {D} AND ORDER_ID IN "
            f"(SELECT ORDER_ID FROM RAW.ORDERS WHERE BATCH_DAY = {D} AND CATEGORY_CODE = 'ELEC' AND MOD(ORDER_ID, 5) < 3)")

SCENARIOS: dict[str, Scenario] = {s.id: s for s in [
    Scenario("healthy", "Healthy day",
             "A normal batch. Nothing is wrong, and Receipts must not invent a problem.",
             "NO_INCIDENT", kind="control"),
    Scenario("festival", "Real festival surge",
             "Demand really is up about 22% on a festival evening, with a burst of payment retries. "
             "The number is right, and Receipts must say so.",
             "REAL_CHANGE", festival=True, kind="control"),
    Scenario("unit_paise", "Paise sent as rupees",
             "A smaller gateway changed its export to paise without telling anyone. Every row is valid, "
             "no nulls, row counts normal. Revenue jumps.",
             "PROVEN_FAULT", frozenset({"unit_scale"}), [UNIT]),
    Scenario("duplicate_load", "File loaded twice",
             "One of eight payment files was re-delivered and loaded a second time.",
             "PROVEN_FAULT", frozenset({"duplicate_key"}), [DUP]),
    Scenario("join_fanout", "Merchant table fans out",
             "A tier upgrade inserted new rows for one in five merchants without closing the old ones. "
             "The join now counts their sales twice, today and in every past day.",
             "PROVEN_FAULT", frozenset({"key_fanout"}), [FANOUT]),
    Scenario("stale_fx", "FX feed went stale",
             "Today's USD to INR rate never arrived. The pipeline silently falls back to a rate of 1, "
             "so international sales count as a few rupees each.",
             "PROVEN_FAULT", frozenset({"stale_feed"}), [STALE]),
    Scenario("ist_utc", "IST written as UTC",
             "A gateway connector started writing IST timestamps into a UTC column. The pipeline adds "
             "five and a half hours again, and the evening's sales slide into tomorrow.",
             "PROVEN_FAULT", frozenset({"clock_shift"}), [TZ]),
    Scenario("new_code", "New category code",
             "The catalogue team split Electronics and started sending a new code the mapping table "
             "does not know. An inner join drops those orders without a sound.",
             "PROVEN_FAULT", frozenset({"orphan_code"}), [ORPHAN]),
    Scenario("masked_pair", "Two faults that cancel out",
             "Two payment files are loaded twice and a gateway shifts to IST on the same night. "
             "The errors cancel and the total looks normal. A threshold alert stays silent.",
             "PROVEN_FAULT", frozenset({"duplicate_key", "clock_shift"}), [DUP2, TZ]),
    Scenario("unknown_discount", "A fault Receipts has no detector for",
             "A coupon is applied twice on many Electronics orders. None of the six detectors covers "
             "this. The honest answer is: held, cause not proven, a person needs to look.",
             "UNEXPLAINED", kind="unknown", inject=[DISCOUNT]),
]}

DEMO_ORDER = ["healthy", "ist_utc", "unit_paise", "duplicate_load", "join_fanout", "stale_fx", "new_code",
              "masked_pair", "festival", "unknown_discount"]
