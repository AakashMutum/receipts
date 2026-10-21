"""Held-out fault variants: the same six fault classes, but not the scripted scenarios.

The ten scenarios in faults.py are the ones the detectors were built and tuned on, so a perfect score
on them proves consistency, not generality. These variants change the gateway, the size of the
factor, the share of rows affected, or the weekday, and they were written after the detectors were
fixed. Some are expected to fail. The question is HOW they fail:

  caught       right verdict and exactly the right causes
  held         held for a person, cause not proven (safe)
  small        published, and the real error is under 4 percent, inside the normal noise
  WRONG        published a number that is more than 4 percent wrong  (the failure that matters)
"""

from __future__ import annotations

from .faults import D, Scenario

DUPCOLS = "PAYMENT_ID, ORDER_ID, BATCH_DAY, LOAD_FILE, GATEWAY, CURRENCY_CODE, AMOUNT, PAY_STATUS, CAPTURED_AT"


def _pay(extra: str) -> str:
    return f"UPDATE RAW.PAYMENTS SET {extra}"


def _dup(where: str) -> str:
    return f"INSERT INTO RAW.PAYMENTS SELECT {DUPCOLS} FROM RAW.PAYMENTS WHERE BATCH_DAY = {D} AND {where}"


def _shift(gw: str, minutes: int) -> str:
    return _pay(f"CAPTURED_AT = {{{{ add_minutes('CAPTURED_AT', {minutes}) }}}} WHERE BATCH_DAY = {D} AND GATEWAY = '{gw}'")


def _fan(where: str) -> str:
    return (f"INSERT INTO RAW.MERCHANTS SELECT MERCHANT_ID, MERCHANT_NAME, "
            f"CASE WHEN TIER = 'BRONZE' THEN 'SILVER' ELSE 'GOLD' END, {D} FROM RAW.MERCHANTS WHERE {where}")


def _scale(gw: str, factor: int, where: str = "1 = 1") -> str:
    return _pay(f"AMOUNT = AMOUNT * {factor} WHERE BATCH_DAY = {D} AND GATEWAY = '{gw}' AND {where}")


def _v(id_, title, cause, *sql):
    return Scenario(id_, title, "", "PROVEN_FAULT", frozenset(cause.split("+")), list(sql), kind="variant")


VARIANTS = [
    _v("unit_x10_b", "Unit change x10 on GW_B", "unit_scale", _scale("GW_B", 10)),
    _v("unit_x1000_c", "Unit change x1000 on GW_C", "unit_scale", _scale("GW_C", 1000)),
    _v("unit_x100_a", "Unit change x100 on GW_A (largest gateway)", "unit_scale", _scale("GW_A", 100)),
    _v("unit_x100_part25", "Unit change x100 on 25% of GW_A rows", "unit_scale", _scale("GW_A", 100, "MOD(PAYMENT_ID, 4) = 0")),
    _v("unit_x100_part5", "Unit change x100 on 5% of GW_A rows", "unit_scale", _scale("GW_A", 100, "MOD(PAYMENT_ID, 20) = 0")),
    _v("dup_3_files", "Three payment files loaded twice", "duplicate_key", _dup("LOAD_FILE IN ('F01', 'F02', 'F03')")),
    _v("dup_2_files", "Two other files loaded twice", "duplicate_key", _dup("LOAD_FILE IN ('F02', 'F07')")),
    _v("dup_part", "A quarter of one file loaded twice", "duplicate_key", _dup("LOAD_FILE = 'F05' AND MOD(PAYMENT_ID, 4) = 0")),
    _v("clock_a", "IST written as UTC on GW_A (largest gateway)", "clock_shift", _shift("GW_A", 330)),
    _v("clock_c", "IST written as UTC on GW_C (smallest gateway)", "clock_shift", _shift("GW_C", 330)),
    _v("clock_1h", "One hour clock shift on GW_B", "clock_shift", _shift("GW_B", 60)),
    _v("clock_12h", "Twelve hour clock shift on GW_B", "clock_shift", _shift("GW_B", 720)),
    _v("code_10pct", "New code on 10% of Electronics orders", "orphan_code",
       f"UPDATE RAW.ORDERS SET CATEGORY_CODE = 'ELC2' WHERE BATCH_DAY = {D} AND CATEGORY_CODE = 'ELEC' AND MOD(ORDER_ID, 10) = 0"),
    _v("code_fashion", "New code for all Fashion orders", "orphan_code",
       f"UPDATE RAW.ORDERS SET CATEGORY_CODE = 'FSH2' WHERE BATCH_DAY = {D} AND CATEGORY_CODE = 'FASH'"),
    _v("fan_5pct", "Merchant table fans out for 5% of merchants", "key_fanout", _fan("MOD(MERCHANT_ID, 20) = 0")),
    _v("fan_40pct", "Merchant table fans out for 40% of merchants", "key_fanout", _fan("MOD(MERCHANT_ID, 5) < 2")),
    _v("pair_unit_dup", "Two faults at once: paise on GW_C and a file loaded twice", "unit_scale+duplicate_key",
       _scale("GW_C", 100), _dup("LOAD_FILE = 'F05'")),
]


def classify(sc: Scenario, case: dict, truth: float) -> tuple[str, float]:
    """Return (outcome, real error in percent) for one run, judged against the clean value."""
    err = (case["values"]["candidate"] - truth) / truth * 100
    if case["verdict"] == "PROVEN_FAULT" and set(case["confirmed"]) == set(sc.expected_causes):
        return "caught", err
    if case["trust_status"] == "HELD":
        return "held", err
    return ("small" if abs(err) < 4 else "WRONG"), err
