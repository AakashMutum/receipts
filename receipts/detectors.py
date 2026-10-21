"""Six fault detectors. Each runs as SQL inside the database against the raw
incoming batch, not against the finished metric, because the gate's job is to
catch a bad batch before anyone sees the number.

A detector only nominates a suspect. Firing is cheap and allowed to be wrong.
The evidence gate (gate.py) decides what is true, by undoing the suspected
fault and checking the number comes back.

Each finding carries:
  blamed      the exact table and column the evidence points at
  level       'value' (a column's content is wrong) or 'row' (rows are wrong)
  slice       the part of the batch the evidence is about
  correction  how to build a corrected version of one source, for the undo test
  sql         the statement that produced the evidence, shown in the receipt
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from datetime import date

from .db import Backend, to_date
from .model import BASELINE_DAYS
from .udf import CLOCK_DRIFT_OUT, clock_drift_source, run_set_script_locally

PAY_COLS = ["PAYMENT_ID", "ORDER_ID", "BATCH_DAY", "LOAD_FILE", "GATEWAY", "CURRENCY_CODE", "AMOUNT", "PAY_STATUS",
            "CAPTURED_AT"]


@dataclass
class Correction:
    source: str            # which source table the corrected relation replaces
    sql: str               # SELECT over {{ inp }} producing the corrected rows
    note: str = ""


@dataclass
class Finding:
    id: str
    title: str
    fired: bool
    summary: str
    blamed_table: str = ""
    blamed_column: str = ""
    level: str = "value"
    slice: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)
    rows: list = field(default_factory=list)
    correction: Correction | None = None
    sql: str = ""
    ms: float = 0.0
    engine: str = "sql"


DETECTOR_TITLES = {
    "unit_scale": "Unit change",
    "duplicate_key": "Duplicate rows",
    "key_fanout": "Join fan-out",
    "stale_feed": "Stale reference feed",
    "clock_shift": "Clock shift",
    "orphan_code": "Unmapped codes",
}


class Ctx:
    def __init__(self, be: Backend, day: date):
        self.be = be
        self.day = day
        d = be.dialect
        self.D = d.day(day)
        self.B0 = d.add_days(self.D, -BASELINE_DAYS)

    def q(self, sql: str):
        sql = self.be.render_string(sql, D=self.D, B0=self.B0)
        rows, ms = self.be.timed_query(sql)
        return rows, ms, sql


def _sel(cols, override: dict) -> str:
    return ",\n  ".join(override.get(c, c) for c in cols)


# 1. unit change -----------------------------------------------------------------
def unit_scale(c: Ctx) -> Finding:
    rows, ms, sql = c.q("""SELECT p.GATEWAY, p.CURRENCY_CODE,
  MEDIAN(CASE WHEN p.BATCH_DAY = {{ D }} THEN p.AMOUNT END) AS MED_TODAY,
  MEDIAN(CASE WHEN p.BATCH_DAY < {{ D }} THEN p.AMOUNT END) AS MED_BASE,
  SUM(CASE WHEN p.BATCH_DAY = {{ D }} THEN 1 ELSE 0 END) AS N_TODAY
FROM RAW.PAYMENTS p
WHERE p.BATCH_DAY >= {{ B0 }} AND p.BATCH_DAY <= {{ D }} AND p.PAY_STATUS = 'CAPTURED'
GROUP BY p.GATEWAY, p.CURRENCY_CODE
ORDER BY p.GATEWAY, p.CURRENCY_CODE""")
    hits = []
    for r in rows:
        if not r["med_today"] or not r["med_base"] or r["n_today"] < 30:
            continue
        ratio = r["med_today"] / r["med_base"]
        r["ratio"] = round(ratio, 3)
        k = math.log10(ratio)
        # a unit change moves the median by a power of ten (10, 100, 1000, or the inverse), within about 40%
        if 1 <= abs(round(k)) <= 3 and abs(k - round(k)) <= 0.15:
            r["factor"] = 10 ** round(k)
            hits.append(r)
    f = Finding("unit_scale", DETECTOR_TITLES["unit_scale"], bool(hits), "", "RAW.PAYMENTS", "AMOUNT", "value",
                rows=rows, sql=sql, ms=ms)
    if not hits:
        f.summary = "Median payment amount per gateway is within the usual range everywhere."
        return f
    h = max(hits, key=lambda r: abs(math.log10(r["ratio"])))
    f.slice = {"GATEWAY": h["gateway"], "CURRENCY_CODE": h["currency_code"]}
    f.metrics = {"median_today": h["med_today"], "median_baseline": h["med_base"], "ratio": h["ratio"],
                 "factor": h["factor"], "rows_today": h["n_today"]}
    f.summary = (f"Median amount on {h['gateway']} ({h['currency_code']}) is {h['ratio']:,.1f}x its baseline, "
                 f"almost exactly a factor of {h['factor']:g}. That is a unit change, not a price change.")
    cond = " OR ".join(f"(GATEWAY = '{r['gateway']}' AND CURRENCY_CODE = '{r['currency_code']}')" for r in hits)
    fac = {(r["gateway"], r["currency_code"]): r["factor"] for r in hits}
    case = "CASE " + " ".join(
        f"WHEN BATCH_DAY = {c.D} AND GATEWAY = '{g}' AND CURRENCY_CODE = '{cc}' THEN AMOUNT / {v:g}"
        for (g, cc), v in fac.items()) + " ELSE AMOUNT END"
    f.correction = Correction("PAYMENTS", f"SELECT\n  {_sel(PAY_COLS, {'AMOUNT': case + ' AS AMOUNT'})}\nFROM {{{{ inp }}}}",
                              f"Divide amounts by the detected factor for {cond}.")
    return f


# 2. duplicate rows ---------------------------------------------------------------
def duplicate_key(c: Ctx) -> Finding:
    rows, ms, sql = c.q("""SELECT x.IS_TODAY, COUNT(*) AS DUP_KEYS, SUM(x.N - 1) AS EXTRA_ROWS
FROM (
  SELECT p.PAYMENT_ID, CASE WHEN p.BATCH_DAY = {{ D }} THEN 1 ELSE 0 END AS IS_TODAY, COUNT(*) AS N
  FROM RAW.PAYMENTS p
  WHERE p.BATCH_DAY >= {{ B0 }} AND p.BATCH_DAY <= {{ D }}
  GROUP BY p.PAYMENT_ID, CASE WHEN p.BATCH_DAY = {{ D }} THEN 1 ELSE 0 END
  HAVING COUNT(*) > 1
) x
GROUP BY x.IS_TODAY""")
    today = next((r for r in rows if r["is_today"] == 1), {"dup_keys": 0, "extra_rows": 0})
    hist = next((r for r in rows if r["is_today"] == 0), {"dup_keys": 0, "extra_rows": 0})
    base_rate = (hist["dup_keys"] or 0) / BASELINE_DAYS
    n_today = today["dup_keys"] or 0
    fired = n_today > max(3 * base_rate, base_rate + 25)
    f = Finding("duplicate_key", DETECTOR_TITLES["duplicate_key"], fired, "", "RAW.PAYMENTS", "PAYMENT_ID", "row",
                rows=rows, sql=sql, ms=ms)
    f.metrics = {"dup_keys_today": n_today, "extra_rows_today": today["extra_rows"] or 0,
                 "dup_keys_per_day_baseline": round(base_rate, 1)}
    if not fired:
        f.summary = (f"{n_today:,} repeated payment IDs today against a usual {base_rate:,.0f} a day "
                     f"(payment retries). Nothing unusual.")
        return f
    files, ms2, sql2 = c.q("""SELECT p.LOAD_FILE, COUNT(*) AS DUP_ROWS
FROM RAW.PAYMENTS p
JOIN (SELECT PAYMENT_ID FROM RAW.PAYMENTS WHERE BATCH_DAY = {{ D }} GROUP BY PAYMENT_ID HAVING COUNT(*) > 1) k
  ON k.PAYMENT_ID = p.PAYMENT_ID
WHERE p.BATCH_DAY = {{ D }}
GROUP BY p.LOAD_FILE
ORDER BY DUP_ROWS DESC""")
    f.ms += ms2
    f.sql += ";\n\n" + sql2
    top = [r["load_file"] for r in files[:3]]
    f.slice = {"LOAD_FILE": ", ".join(top)}
    f.metrics["by_load_file"] = files[:8]
    f.summary = (f"{n_today:,} payment IDs appear more than once in today's batch, {n_today / max(base_rate, 1):,.1f}x "
                 f"the usual rate. Most repeats sit in {', '.join(top)}.")
    dedup = (f"SELECT\n  {_sel(PAY_COLS, {})}\nFROM {{{{ inp }}}}\nWHERE BATCH_DAY <> {c.D}\nUNION ALL\n"
             f"SELECT\n  {_sel(PAY_COLS, {})}\nFROM (\n  SELECT i.*, ROW_NUMBER() OVER (PARTITION BY i.PAYMENT_ID "
             f"ORDER BY i.LOAD_FILE DESC, i.CAPTURED_AT DESC) AS RN\n  FROM {{{{ inp }}}} i\n  WHERE i.BATCH_DAY = {c.D}\n) z\n"
             f"WHERE z.RN = 1")
    f.correction = Correction("PAYMENTS", dedup, "Keep one row per PAYMENT_ID in today's batch, the latest attempt.")
    return f


# 3. join fan-out -------------------------------------------------------------------
DIM_KEYS = [("RAW.MERCHANTS", "MERCHANT_ID", "VALID_FROM"), ("RAW.CATEGORY_MAP", "CATEGORY_CODE", None)]


def key_fanout(c: Ctx) -> Finding:
    parts = [f"SELECT '{t}' AS TABLE_NAME, '{k}' AS KEY_COLUMN, COUNT(*) AS DUP_KEYS, COALESCE(SUM(x.N), 0) AS DIM_ROWS "
             f"FROM (SELECT {k}, COUNT(*) AS N FROM {t} GROUP BY {k} HAVING COUNT(*) > 1) x" for t, k, _ in DIM_KEYS]
    rows, ms, sql = c.q("\nUNION ALL\n".join(parts))
    hits = [r for r in rows if r["dup_keys"] > 0]
    f = Finding("key_fanout", DETECTOR_TITLES["key_fanout"], bool(hits), "", "RAW.MERCHANTS", "MERCHANT_ID", "row",
                rows=rows, sql=sql, ms=ms)
    if not hits:
        f.summary = "Every dimension key the revenue joins on is unique."
        return f
    h = max(hits, key=lambda r: r["dup_keys"])
    tbl, key = h["table_name"], h["key_column"]
    f.blamed_table, f.blamed_column = tbl, key
    impact, ms2, sql2 = c.q(f"""SELECT COUNT(*) AS ORDERS_TODAY,
  SUM(CASE WHEN k.{key} IS NOT NULL THEN 1 ELSE 0 END) AS ORDERS_ON_DUP_KEYS
FROM RAW.ORDERS o
LEFT JOIN (SELECT {key} FROM {tbl} GROUP BY {key} HAVING COUNT(*) > 1) k ON k.{key} = o.{key}
WHERE o.BATCH_DAY = {{{{ D }}}}""")
    f.ms += ms2
    f.sql += ";\n\n" + sql2
    share = (impact[0]["orders_on_dup_keys"] or 0) / max(impact[0]["orders_today"], 1)
    f.slice = {tbl.split(".")[1]: f"{h['dup_keys']:,} keys with more than one row"}
    f.metrics = {"dup_keys": h["dup_keys"], "dim_rows_on_dup_keys": h["dim_rows"], "share_of_orders_affected": round(share, 4)}
    f.summary = (f"{h['dup_keys']:,} values of {tbl}.{key} have more than one row. {share:.1%} of today's orders "
                 f"join to them, so their revenue is counted more than once, today and in history.")
    order_col = next((o for t, k, o in DIM_KEYS if t == tbl), None)
    src = tbl.split(".")[1]
    cols = {"RAW.MERCHANTS": ["MERCHANT_ID", "MERCHANT_NAME", "TIER", "VALID_FROM"],
            "RAW.CATEGORY_MAP": ["CATEGORY_CODE", "CATEGORY_NAME"]}[tbl]
    order = f"{order_col} DESC" if order_col else key
    f.correction = Correction(src, f"SELECT\n  {_sel(cols, {})}\nFROM (\n  SELECT i.*, ROW_NUMBER() OVER "
                                   f"(PARTITION BY i.{key} ORDER BY i.{order}) AS RN\n  FROM {{{{ inp }}}} i\n) z\n"
                                   f"WHERE z.RN = 1",
                              f"Keep one row per {key}, the most recent version.")
    return f


# 4. stale reference feed --------------------------------------------------------------
def stale_feed(c: Ctx) -> Finding:
    rows, ms, sql = c.q("""SELECT p.CURRENCY_CODE, COUNT(*) AS PAYMENTS_TODAY, MAX(f.LAST_RATE_DAY) AS LAST_RATE_DAY
FROM RAW.PAYMENTS p
LEFT JOIN (SELECT CURRENCY_CODE, MAX(RATE_DAY) AS LAST_RATE_DAY FROM RAW.FX_RATES GROUP BY CURRENCY_CODE) f
  ON f.CURRENCY_CODE = p.CURRENCY_CODE
WHERE p.BATCH_DAY = {{ D }} AND p.CURRENCY_CODE <> 'INR' AND p.PAY_STATUS = 'CAPTURED'
GROUP BY p.CURRENCY_CODE""")
    stale = [r for r in rows if r["last_rate_day"] is None or to_date(r["last_rate_day"]) < c.day]
    f = Finding("stale_feed", DETECTOR_TITLES["stale_feed"], bool(stale), "", "RAW.FX_RATES", "RATE_DAY", "value",
                rows=rows, sql=sql, ms=ms)
    if not stale:
        f.summary = "Every foreign currency paid in today has a rate for today."
        return f
    s = stale[0]
    last = to_date(s["last_rate_day"]) if s["last_rate_day"] else None
    f.slice = {"CURRENCY_CODE": s["currency_code"]}
    f.metrics = {"payments_today": s["payments_today"], "last_rate_day": last.isoformat() if last else None,
                 "days_stale": (c.day - last).days if last else None}
    f.summary = (f"{s['payments_today']:,} {s['currency_code']} payments today, but the newest "
                 f"{s['currency_code']} rate is for {last:%a %d %b}. The pipeline falls back to a rate of 1 "
                 f"when the rate is missing.")
    unions = []
    for r in stale:
        if r["last_rate_day"] is None:
            continue
        lr = c.be.dialect.day(to_date(r["last_rate_day"]))
        unions.append(f"SELECT {c.D} AS RATE_DAY, f.CURRENCY_CODE, f.INR_PER_UNIT FROM {{{{ inp }}}} f "
                      f"WHERE f.CURRENCY_CODE = '{r['currency_code']}' AND f.RATE_DAY = {lr}")
    f.correction = Correction("FX_RATES", "SELECT RATE_DAY, CURRENCY_CODE, INR_PER_UNIT FROM {{ inp }}\nUNION ALL\n"
                              + "\nUNION ALL\n".join(unions), "Carry the last known rate forward to today.")
    return f


# 5. clock shift (in-database Python UDF) ------------------------------------------------
CLOCK_INPUT = """SELECT x.SLICE_KEY, x.IS_TODAY, x.BIN_IDX, CAST(COUNT(*) AS DOUBLE) AS CNT
FROM (
  SELECT p.GATEWAY AS SLICE_KEY,
    CASE WHEN p.BATCH_DAY = {{ D }} THEN TRUE ELSE FALSE END AS IS_TODAY,
    {{ half_hour_bin(add_minutes('p.CAPTURED_AT', 330)) }} AS BIN_IDX
  FROM RAW.PAYMENTS p
  WHERE p.BATCH_DAY >= {{ B0 }} AND p.BATCH_DAY <= {{ D }} AND p.PAY_STATUS = 'CAPTURED'
) x
GROUP BY x.SLICE_KEY, x.IS_TODAY, x.BIN_IDX"""


def clock_shift(c: Ctx, udf_mode: str) -> Finding:
    t = time.perf_counter()
    if udf_mode == "in-database":
        rows, _, sql = c.q("SELECT RECEIPTS.CLOCK_DRIFT(a.SLICE_KEY, a.IS_TODAY, a.BIN_IDX, a.CNT)\nFROM (\n"
                           + CLOCK_INPUT + "\n) a\nGROUP BY a.SLICE_KEY")
        engine = "Python UDF inside Exasol"
    else:
        agg, _, sql = c.q(CLOCK_INPUT)
        rows = run_set_script_locally(clock_drift_source(), agg, "slice_key", CLOCK_DRIFT_OUT)
        engine = "same UDF source, local shim" if c.be.is_standin else "same UDF source, client side (UDF unavailable)"
    ms = (time.perf_counter() - t) * 1000
    rows = sorted(rows, key=lambda r: str(r["slice_key"]))
    hits = [r for r in rows if r["tvd"] is not None and r["n_today"] >= 200 and r["tvd"] >= 0.12
            and abs(r["best_shift_bins"] or 0) >= 2 and r["tvd_after_shift"] <= 0.5 * r["tvd"]]
    f = Finding("clock_shift", DETECTOR_TITLES["clock_shift"], bool(hits), "", "RAW.PAYMENTS", "CAPTURED_AT", "value",
                rows=rows, sql=sql, ms=ms, engine=engine)
    if not hits:
        worst = max((r for r in rows if r["tvd"] is not None), key=lambda r: r["tvd"], default=None)
        f.summary = ("Each gateway's time-of-day profile matches its baseline." if not worst or worst["tvd"] < 0.12 else
                     f"{worst['slice_key']}'s time-of-day profile changed (distance {worst['tvd']:.2f}), but no clock "
                     f"shift lines it back up. Customers behaved differently; the clock is fine.")
        return f
    h = max(hits, key=lambda r: r["tvd"])
    shift_min = int(h["best_shift_bins"]) * 30
    f.slice = {"GATEWAY": h["slice_key"]}
    f.metrics = {"distance_before": round(h["tvd"], 3), "distance_after_shift": round(h["tvd_after_shift"], 3),
                 "shift_minutes": shift_min, "rows_today": h["n_today"]}
    hrs = abs(shift_min) / 60
    f.summary = (f"{h['slice_key']}'s time-of-day profile sits {hrs:g} hours {'later' if shift_min > 0 else 'earlier'} "
                 f"than usual. Shifting it back by exactly {hrs:g} hours makes it match its baseline "
                 f"(distance {h['tvd']:.2f} to {h['tvd_after_shift']:.2f}). IST is UTC + 5.5 hours.")
    ts = c.be.dialect.add_minutes("CAPTURED_AT", -shift_min)
    case = f"CASE WHEN BATCH_DAY = {c.D} AND GATEWAY = '{h['slice_key']}' THEN {ts} ELSE CAPTURED_AT END AS CAPTURED_AT"
    f.correction = Correction("PAYMENTS", f"SELECT\n  {_sel(PAY_COLS, {'CAPTURED_AT': case})}\nFROM {{{{ inp }}}}",
                              f"Shift {h['slice_key']} timestamps in today's batch back by {shift_min} minutes.")
    return f


# 6. unmapped codes --------------------------------------------------------------------
def orphan_code(c: Ctx) -> Finding:
    rows, ms, sql = c.q("""SELECT o.CATEGORY_CODE, COUNT(*) AS ORDERS_TODAY
FROM RAW.ORDERS o
LEFT JOIN RAW.CATEGORY_MAP m ON m.CATEGORY_CODE = o.CATEGORY_CODE
WHERE o.BATCH_DAY = {{ D }} AND m.CATEGORY_CODE IS NULL
GROUP BY o.CATEGORY_CODE
ORDER BY ORDERS_TODAY DESC""")
    f = Finding("orphan_code", DETECTOR_TITLES["orphan_code"], bool(rows), "", "RAW.ORDERS", "CATEGORY_CODE", "value",
                rows=rows, sql=sql, ms=ms)
    if not rows:
        f.summary = "Every category code in today's orders exists in the mapping table."
        return f
    codes = [r["category_code"] for r in rows]
    n = sum(r["orders_today"] for r in rows)
    f.slice = {"CATEGORY_CODE": ", ".join(codes)}
    f.metrics = {"unmapped_codes": codes, "orders_today": n}
    f.summary = (f"{n:,} of today's orders carry category code{'s' if len(codes) > 1 else ''} "
                 f"{', '.join(codes)}, which the mapping table does not know. The inner join drops them silently.")
    dual = c.be.dialect.from_dual()
    adds = "\nUNION ALL\n".join(f"SELECT '{code}' AS CATEGORY_CODE, 'Unmapped ({code})' AS CATEGORY_NAME{dual}"
                                for code in codes)
    f.correction = Correction("CATEGORY_MAP", "SELECT CATEGORY_CODE, CATEGORY_NAME FROM {{ inp }}\nUNION ALL\n" + adds,
                              "Keep unmapped orders, labelled as unmapped, instead of dropping them.")
    return f


def run_all(be: Backend, day: date, udf_mode: str) -> list[Finding]:
    c = Ctx(be, day)
    return [unit_scale(c), duplicate_key(c), key_fanout(c), stale_feed(c), clock_shift(c, udf_mode), orphan_code(c)]
