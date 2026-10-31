"""Backtest the gate on UCI Online Retail II, converted to rupees with the ECB euro reference rates.

Sources (downloaded once into D:/Hackathon/data/retail, never committed):
  * Online Retail II, UCI Machine Learning Repository, CC BY 4.0. Chen, D. (2012). Online Retail II [Dataset].
    https://doi.org/10.24432/C5CG6D. All transactions of a UK-based online retailer, 1 Dec 2009 to 9 Dec 2011, prices in
    pounds sterling.
  * Euro foreign exchange reference rates, European Central Bank, eurofxref-hist.zip from ecb.europa.eu (source: ECB).

These are UK retail sales converted to rupees for the test. They are not Indian transaction data.

How the adapter maps the data onto the pipeline tables (the pipeline, detectors and thresholds are unchanged):

    invoice         one order and one payment; PAYMENT_ID = ORDER_ID = the invoice number (cancellations, 'C...',
                    get 10,000,000 added; bad-debt adjustments, 'A...', 20,000,000)
    AMOUNT          the invoice total, sum of Quantity x Price, in pounds; CURRENCY_CODE 'GBP'
    PAY_STATUS      CAPTURED when the total is positive; cancellations, adjustments and totals of zero or less VOIDED
    GATEWAY         the customer's country group: UK, EU (an EU member state then) or OTHER
    CITY            the customer's country; MERCHANT_ID a number per country, TIER the country group
    CATEGORY_CODE   GOODS, or SERVICE when every line is postage, carriage, manual or a fee code
    CHANNEL         MEMBER with a customer ID, GUEST without
    LOAD_FILE       F01 to F12 by invoice number, so a duplicated file can be planted
    CAPTURED_AT     the invoice time moved back 330 minutes, so TXN_DAY is the UK invoice date
    FX_RATES        one GBP row per calendar day: INR per GBP = (INR per EUR) / (GBP per EUR), the ECB cross rate.
                    On days the ECB did not publish (weekends, TARGET closing days) the last published rate is carried
                    forward. The rates land one day at a time, like a real feed.

The two sheets of the workbook overlap on 1 to 9 December 2010 with identical rows; one copy is kept. The last day,
9 December 2011, ends at 12:50 in the file and is not judged.

    python scripts/backtest_retail.py --backend exasol
    python scripts/backtest_retail.py --report
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import time
from dataclasses import replace
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from receipts import backtest, gate  # noqa: E402
from receipts.backtest import _row as _backtest_row  # noqa: E402
from receipts.config import settings  # noqa: E402
from receipts.db import DuckDBBackend, connect  # noqa: E402
from receipts.load import create_pipeline, install_udf, udf_status  # noqa: E402
from receipts.model import FESTIVAL_TABLES, SOURCE_TABLES  # noqa: E402
from receipts.variants import _dup, _scale  # noqa: E402

DATA = Path("D:/Hackathon/data/retail") if sys.platform == "win32" else ROOT / "data" / "retail"
UCI = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
ECB = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip"
START, END = date(2009, 12, 1), date(2011, 12, 8)
WARMUP = 35
EU = ("Austria", "Belgium", "Cyprus", "Czech Republic", "Denmark", "Finland", "France", "Germany", "Greece", "Ireland",
      "EIRE", "Italy", "Lithuania", "Malta", "Netherlands", "Poland", "Portugal", "Spain", "Sweden", "Channel Islands",
      "European Community")
STALE = "DELETE FROM RAW.FX_RATES WHERE RATE_DAY = {{ day(incoming) }} AND CURRENCY_CODE = 'GBP'"
# planted faults, all on Wednesdays with normal trading: (day, label, expected cause, SQL)
FAULTS = [(date(2010, 3, 10), "UK prices in pence (x100)", "unit_scale", [_scale("UK", 100)]),
          (date(2010, 10, 13), "UK prices in pence (x100)", "unit_scale", [_scale("UK", 100)]),
          (date(2011, 5, 11), "UK prices in pence (x100)", "unit_scale", [_scale("UK", 100)]),
          (date(2010, 4, 14), "Payment file F05 loaded twice", "duplicate_key", [_dup("LOAD_FILE = 'F05'")]),
          (date(2010, 11, 10), "Payment file F05 loaded twice", "duplicate_key", [_dup("LOAD_FILE = 'F05'")]),
          (date(2011, 6, 15), "Payment file F05 loaded twice", "duplicate_key", [_dup("LOAD_FILE = 'F05'")]),
          (date(2010, 5, 12), "ECB GBP rate missing today", "stale_feed", [STALE]),
          (date(2011, 1, 12), "ECB GBP rate missing today", "stale_feed", [STALE]),
          (date(2011, 7, 13), "ECB GBP rate missing today", "stale_feed", [STALE])]
NOT_APPLIED = {
    "clock_shift": "the detector looks for one gateway's times written in UTC instead of IST; the shop records UK "
                   "local time and has no gateways, so a planted shift would test the adapter, not a real failure",
    "key_fanout": "the merchant table is made by the adapter (one row per country), not a real reference table",
    "orphan_code": "the category codes are made by the adapter (GOODS and SERVICE), not a real code list"}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def adapt(duck: DuckDBBackend, log) -> None:
    """Sheets (converted to CSV) and ECB rates to LANDING, in DuckDB."""
    duck.run_script(duck.render("schema.sql", tables=SOURCE_TABLES, festival=FESTIVAL_TABLES))
    a, b = (DATA / "sheet_Year_2009-2010.csv").as_posix(), (DATA / "sheet_Year_2010-2011.csv").as_posix()
    eu = ", ".join(f"'{c}'" for c in EU)
    duck.execute(f"""CREATE TEMP TABLE LINES AS
        SELECT Invoice AS INV, StockCode AS CODE, CAST(Quantity AS DOUBLE) AS QTY, CAST(Price AS DOUBLE) AS PRICE,
               CAST(InvoiceDate AS TIMESTAMP) AS TS, "Customer ID" AS CUST, Country AS COUNTRY
        FROM read_csv('{a}', header = true, all_varchar = true)
        UNION ALL
        SELECT Invoice, StockCode, CAST(Quantity AS DOUBLE), CAST(Price AS DOUBLE), CAST(InvoiceDate AS TIMESTAMP),
               "Customer ID", Country
        FROM read_csv('{b}', header = true, all_varchar = true) WHERE CAST(InvoiceDate AS TIMESTAMP) >= TIMESTAMP '2010-12-10'""")
    duck.execute(f"""CREATE TEMP TABLE INV AS
        SELECT CASE WHEN INV LIKE 'C%' THEN 10000000 + CAST(SUBSTR(INV, 2) AS BIGINT)
                    WHEN INV LIKE 'A%' THEN 20000000 + CAST(SUBSTR(INV, 2) AS BIGINT) ELSE CAST(INV AS BIGINT) END AS ID,
               LEFT(INV, 1) IN ('C', 'A') AS CANCELLED, MIN(TS) AS TS, CAST(MIN(TS) AS DATE) AS DAY,
               ANY_VALUE(COUNTRY) AS COUNTRY, ANY_VALUE(CUST) AS CUST, SUM(QTY * PRICE) AS TOTAL,
               BOOL_AND(CODE IN ('POST', 'DOT', 'M', 'C2', 'BANK CHARGES', 'AMAZONFEE', 'CRUK', 'ADJUST', 'ADJUST2',
                                 'D', 'S', 'B', 'TEST001', 'TEST002', 'PADS', 'SP1002')) AS SERVICE
        FROM LINES GROUP BY 1, 2
        HAVING CAST(MIN(TS) AS DATE) BETWEEN DATE '{START}' AND DATE '{END}'""")
    duck.execute("CREATE TEMP TABLE CTRY AS SELECT ROW_NUMBER() OVER (ORDER BY COUNTRY) AS MID, COUNTRY "
                 "FROM (SELECT DISTINCT COALESCE(COUNTRY, 'Unspecified') AS COUNTRY FROM INV)")
    grp = f"CASE WHEN c.COUNTRY = 'United Kingdom' THEN 'UK' WHEN c.COUNTRY IN ({eu}) THEN 'EU' ELSE 'OTHER' END"
    duck.execute("""INSERT INTO LANDING.ORDERS
        SELECT i.ID, i.DAY, c.MID, LEFT(c.COUNTRY, 20), CASE WHEN i.SERVICE THEN 'SERVICE' ELSE 'GOODS' END,
               CASE WHEN i.CUST IS NULL OR i.CUST = '' THEN 'GUEST' ELSE 'MEMBER' END
        FROM INV i JOIN CTRY c ON c.COUNTRY = COALESCE(i.COUNTRY, 'Unspecified')""")
    duck.execute(f"""INSERT INTO LANDING.PAYMENTS
        SELECT i.ID, i.ID, i.DAY, 'F' || LPAD(CAST(i.ID % 12 + 1 AS VARCHAR), 2, '0'), {grp}, 'GBP',
               ROUND(i.TOTAL, 2), CASE WHEN i.CANCELLED OR i.TOTAL <= 0 THEN 'VOIDED' ELSE 'CAPTURED' END,
               i.TS - INTERVAL 330 MINUTE
        FROM INV i JOIN CTRY c ON c.COUNTRY = COALESCE(i.COUNTRY, 'Unspecified')""")
    duck.execute(f"""INSERT INTO LANDING.MERCHANTS SELECT c.MID, LEFT(c.COUNTRY, 40), {grp}, DATE '{START}' FROM CTRY c""")
    duck.execute("INSERT INTO LANDING.CATEGORY_MAP VALUES ('GOODS', 'Goods'), ('SERVICE', 'Postage, fees and manual')")
    ecb = (DATA / "eurofxref-hist.csv").as_posix()
    duck.execute(f"""CREATE TEMP TABLE ECBR AS
        SELECT CAST(Date AS DATE) AS D, CAST(INR AS DOUBLE) / CAST(GBP AS DOUBLE) AS INR_PER_GBP
        FROM read_csv('{ecb}', header = true, all_varchar = true) WHERE INR <> 'N/A' AND GBP <> 'N/A'""")
    duck.execute(f"""INSERT INTO LANDING.FX_RATES
        SELECT d.D, 'GBP', (SELECT e.INR_PER_GBP FROM ECBR e WHERE e.D <= d.D ORDER BY e.D DESC LIMIT 1)
        FROM (SELECT CAST(x AS DATE) AS D FROM range(DATE '{START}', DATE '{END}' + 1, INTERVAL 1 DAY) t(x)) d""")
    log(f"adapted {duck.scalar('SELECT COUNT(*) FROM INV'):,} invoices from {duck.scalar('SELECT COUNT(*) FROM LINES'):,} "
        f"lines; {duck.scalar('SELECT COUNT(*) FROM LANDING.FX_RATES')} daily GBP rates")


def _row(case: dict, day: date) -> dict:
    """The row of `receipts backtest`; a day expected to be 0 (Saturday, when the shop never trades) has a band of 0."""
    v = case["values"]
    if v["baseline"]:
        return _backtest_row(case, day)
    return _backtest_row({**case, "values": {**v, "baseline": 1.0, "band_high": 1.0}}, day) | {"expected": 0.0}


def build(backend: str, log):
    db = DATA / f"retail_{backend}.duckdb"
    db.unlink(missing_ok=True)
    duck = DuckDBBackend(str(db))
    adapt(duck, log)
    if backend == "duckdb":
        be = duck
    else:
        csvs = backtest._export(duck, DATA / "exasol_csv", log)
        duck.close()
        db.unlink(missing_ok=True)
        be = connect(replace(settings(), backend="exasol"))
        be.run_script(be.render("schema.sql", tables=SOURCE_TABLES, festival=FESTIVAL_TABLES))
        for tbl, f in csvs:
            be.load_csv(f, "LANDING", tbl)
            f.unlink()
            log(f"IMPORT INTO LANDING.{tbl}")
    create_pipeline(be)
    be.run_script(be.render("pub.sql"))
    log(f"udf: {install_udf(be)['udf']}")
    first = START + timedelta(days=WARMUP)
    for tbl in ("MERCHANTS", "CATEGORY_MAP"):
        be.execute(f"INSERT INTO RAW.{tbl} SELECT * FROM LANDING.{tbl}")
    for tbl, col in (("ORDERS", "BATCH_DAY"), ("PAYMENTS", "BATCH_DAY"), ("FX_RATES", "RATE_DAY")):
        be.execute(f"INSERT INTO RAW.{tbl} SELECT * FROM LANDING.{tbl} WHERE {col} < DATE '{first}'")
    be.execute(f"""INSERT INTO PUB.DAILY_REVENUE_PUBLISHED
        SELECT d.TXN_DAY, d.REVENUE_INR, d.REVENUE_INR, 'TRUSTED', 'warm-up', CURRENT_TIMESTAMP
        FROM PIPE.DAILY_REVENUE d WHERE d.TXN_DAY < DATE '{first}'""")
    return be, first


def land(be, day: date, rate: bool = True) -> None:
    for tbl in ("ORDERS", "PAYMENTS"):
        be.execute(f"DELETE FROM RAW.{tbl} WHERE BATCH_DAY = DATE '{day}'")
        be.execute(f"INSERT INTO RAW.{tbl} SELECT * FROM LANDING.{tbl} WHERE BATCH_DAY = DATE '{day}'")
    be.execute(f"DELETE FROM RAW.FX_RATES WHERE RATE_DAY = DATE '{day}'")
    if rate:
        be.execute(f"INSERT INTO RAW.FX_RATES SELECT * FROM LANDING.FX_RATES WHERE RATE_DAY = DATE '{day}'")


def run(backend: str, rows_file: Path, log) -> None:
    t0 = time.perf_counter()
    be, first = build(backend, log)
    meta = {"backend": be.describe() | udf_status(be), "build_seconds": round(time.perf_counter() - t0, 1),
            "invoices": be.scalar("SELECT COUNT(*) FROM LANDING.PAYMENTS"),
            "captured": be.scalar("SELECT COUNT(*) FROM LANDING.PAYMENTS WHERE PAY_STATUS = 'CAPTURED'"),
            "first_judged": first.isoformat(), "start": START.isoformat(), "end": END.isoformat()}
    rows_file.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")
    rows_file.write_text("", encoding="utf-8")
    plan = {}
    for d, label, cause, sql in FAULTS:
        plan.setdefault(d, []).append((label, cause, sql))
    day = first
    while day <= END:
        for label, cause, sql in plan.get(day, []):
            land(be, day)
            truth = be.scalar(f"SELECT REVENUE_INR FROM PIPE.DAILY_REVENUE WHERE TXN_DAY = DATE '{day}'")
            for stmt in sql:
                be.execute(be.render_string(stmt, incoming=day))
            c = gate.run(be, day, {"id": "planted", "title": label}, write_back=False)
            r = _row(c, day) | {"kind": "planted", "fault": label, "expected_cause": cause,
                                "real_error_pct": (c["values"]["candidate"] - truth) / truth * 100 if truth else None,
                                "caught": c["verdict"] == "PROVEN_FAULT" and c["confirmed"] == [cause],
                                "held": c["trust_status"] == "HELD"}
            with rows_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(r, default=str) + "\n")
            log(f"{day} planted {label:30s} {c['verdict']:13s} {','.join(c['confirmed']) or '-'}")
        land(be, day)
        c = gate.run(be, day, {"id": "real", "title": "Real day"}, write_back=True)
        r = _row(c, day) | {"kind": "clean"}
        with rows_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(r, default=str) + "\n")
        log(f"{day} {day:%a} real {c['verdict']:13s} change {c['values']['change_pct']:+7.1%} {c['total_ms']:.0f} ms "
            f"fired {','.join(r['fired']) or '-'}")
        day += timedelta(days=1)
    be.close()
    meta["seconds"] = round(time.perf_counter() - t0)
    rows_file.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")


def load(rows_file: Path):
    meta = json.loads(rows_file.with_suffix(".meta.json").read_text(encoding="utf-8"))
    rows = [json.loads(x) for x in rows_file.read_text(encoding="utf-8").splitlines() if x.strip()]
    strip = lambda r: {k: v for k, v in r.items() if k != "kind"}
    return meta, [strip(r) for r in rows if r["kind"] == "clean"], [strip(r) for r in rows if r["kind"] == "planted"]


def report(backend: str) -> None:
    meta, clean, planted = load(DATA / f"retail_{backend}.jsonl")
    if clean[-1]["day"] != END.isoformat():
        raise SystemExit(f"the run stopped at {clean[-1]['day']}; no report for an incomplete run")
    rep = {"dataset": "UCI Online Retail II (CC BY 4.0) with ECB euro reference rates", "urls": [UCI, ECB],
           "start": meta["start"], "end": meta["end"], "first_judged": meta["first_judged"], "warmup": WARMUP,
           "trips": meta["captured"], "clean": clean, "planted": planted, "seconds": meta.get("seconds", 0),
           "backend": meta["backend"], "load_seconds": meta["build_seconds"],
           "timings": backtest._timings(clean + planted)}
    other = DATA / f"retail_{'duckdb' if backend == 'exasol' else 'exasol'}.jsonl"
    compare = None
    if backend == "exasol" and other.exists() and other.with_suffix(".meta.json").exists():
        om, oc, op = load(other)
        compare = {"clean": oc, "planted": op, "backend": om["backend"]}
    md = backtest.to_markdown(rep, "python scripts/backtest_retail.py --backend exasol", compare)
    md = md.replace("# Real-data backtest", "# Real-data backtest: UCI Online Retail II with ECB rates", 1)
    md = md.replace("Trips from", "Captured invoices from").replace("daily total of `total_amount` by pickup date",
                                                                   "daily invoice total in rupees by UK invoice date")
    md = md.replace("(downloads about 150 MB once into `data/real/`, then runs in about",
                    "(needs the two source files in the data folder, see the script; runs in about")
    md = md.replace("published by the NYC Taxi and Limousine Commission, no login needed",
                    "from the UCI Machine Learning Repository and the European Central Bank, no login needed")
    md = md.replace("How trips map onto the pipeline tables is described in `receipts/backtest.py`.",
                    "How invoices map onto the pipeline tables is described in `scripts/backtest_retail.py`.")
    files = {f.name: (f.stat().st_size, sha256(f)) for f in (DATA / "online_retail_ii.zip", DATA / "eurofxref-hist.zip")}
    held = [r for r in clean if r["trust"] == "HELD"]
    head = ["## Sources, licences and what was changed", "",
            "* **UCI Online Retail II**, Chen, D. (2012), UCI Machine Learning Repository, https://doi.org/10.24432/C5CG6D. "
            "The dataset page states: \"This dataset is licensed under a Creative Commons Attribution 4.0 International "
            "(CC BY 4.0) license.\" All transactions of a UK-based online retailer, 1 Dec 2009 to 9 Dec 2011, prices in "
            "pounds sterling.",
            "* **Euro foreign exchange reference rates**, source: European Central Bank (ecb.europa.eu, "
            "eurofxref-hist.zip). The ECB page states: \"The reference rates are published for information purposes "
            "only.\" Its disclaimer and copyright page sets the terms of reuse.",
            "* **These are UK retail sales converted to rupees for the test. They are not Indian transaction data.**",
            "* Changes made: invoice lines summed to invoice totals; GBP converted to INR with the ECB cross rate "
            "(INR per EUR divided by GBP per EUR); a rate for every calendar day, with the last published rate carried "
            "forward over weekends and TARGET closing days; cancellations (`C` invoices), bad-debt adjustments (`A`) and "
            "totals of zero or less not counted as revenue; the 22,523 rows that appear in both workbook sheets (1 to 9 "
            "December 2010) kept once; 9 December 2011 not judged because the file ends at 12:50 that day. The mapping "
            "onto the pipeline tables is in [`scripts/backtest_retail.py`](../../scripts/backtest_retail.py).",
            "", "Files used (not committed):", "", "| File | Bytes | SHA-256 | Source |", "|---|---|---|---|"]
    head += [f"| {n} | {s:,} | `{h}` | {UCI if 'retail' in n else ECB} |" for n, (s, h) in files.items()]
    head += ["", "## Detectors that do not apply", ""]
    head += [f"* `{k}`: {v}." for k, v in NOT_APPLIED.items()]
    missed = [r for r in planted if not r["caught"]]
    empty = [r for r in held if r["value"] == 0]
    head += ["", "## In short", "",
             f"* Real days held: **{len(held)} of {len(clean)}**. Of these, {len(empty)} had no captured invoice at all "
             f"(change -100%), and {sum(r['change_pct'] > 0.4 for r in held)} were more than 40% above the expected "
             "value. A wholesale shop's daily total swings far more than the synthetic data: the median normal range "
             "here is wide (see below), and the gate still holds a day it cannot explain.",
             f"* Planted faults caught with the right cause: **{len(planted) - len(missed)} of {len(planted)}**. "
             "Missed, by name: " + ("; ".join(
                 f"{r['day']} {r['fault']} ({r['verdict']}, {'held' if r['held'] else 'PUBLISHED'}, real error "
                 f"{r['real_error_pct']:+.1f}%)" for r in missed) or "none") + ".",
             "* Saturdays: the shop never trades on Saturdays, so the Saturday weekday index is 0. The first run on the "
             "stand-in stopped on 2010-01-24 with a division by zero in the weekday baseline. The fix (a weekday whose "
             "index is 0 expects 0, and anything else on it is held as UNEXPLAINED) is its own commit, and the run was "
             "started again from the first day. The second start stopped on 2010-02-06 in this report's row helper "
             "(the band as a percent of an expected 0); the band of such a day is reported as 0%, and the run was "
             "started again from the first day. Every number below is from the complete run.",
             "", "## Every held real day", ""]
    head += ([f"* {r['day']} {r['weekday']}: {r['verdict']}, change {r['change_pct']:+.1%}, fired "
              f"{', '.join(r['fired']) or 'nothing'}" for r in held] or ["* none"])
    head += [""]
    i = md.index("## Real days, no faults planted")
    md = md[:i] + "\n".join(head) + "\n" + md[i:]
    out = ROOT / "samples" / "exasol" / "real_backtest_retail.md"
    out.with_suffix(".json").write_text(json.dumps(rep | {"files": files, "not_applied": NOT_APPLIED},
                                                   indent=2, default=str), encoding="utf-8")
    out.write_text(md, encoding="utf-8")
    caught = sum(r["caught"] for r in planted)
    print(f"report: {len(clean)} days, {len(held)} held, planted caught {caught} of {len(planted)}; "
          f"median {statistics.median(r['ms'] for r in clean):.0f} ms")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="exasol", choices=["exasol", "duckdb"])
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if not a.report:
        log = lambda m: print(f"{datetime.now():%H:%M:%S} {m}", flush=True)
        run(a.backend, DATA / f"retail_{a.backend}.jsonl", log)
    report("exasol" if (DATA / "retail_exasol.jsonl").exists() else a.backend)


if __name__ == "__main__":
    main()
