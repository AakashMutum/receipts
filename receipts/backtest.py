"""Backtest the gate on real public data: NYC TLC yellow taxi trip records.

The daily total of `total_amount` over all trips is the metric. A thin adapter maps every trip
onto the marketplace tables the pipeline already reads, so the six detectors, the CUBE, lineage
and the undo test run unchanged:

    trip            one order and one payment, PAYMENT_ID = ORDER_ID = a running trip number
    GATEWAY         the vendor (CMT, CURB, OTHER)
    CITY            the pickup borough, from the TLC zone lookup
    CATEGORY_CODE   the rate code (standard, JFK, Newark, negotiated, ...)
    CHANNEL         the payment type (card, cash, no charge, dispute, ...)
    MERCHANT_ID     the pickup zone; TIER is the zone's service area
    AMOUNT          total_amount in dollars, stored in the pipeline's base currency column
    CAPTURED_AT     the pickup time moved back 330 minutes, so the pipeline's IST day boundary
                    falls at New York midnight and TXN_DAY is the local pickup date
    LOAD_FILE       F01 to F12 by trip number, so a duplicated file can be planted

The first `warmup` days are published as trusted history by assumption (the weekday baseline
needs five weeks). After that each night's trips land in RAW and the gate judges that day.
Held days are not published, so they never enter the baseline, as in production.

Faults are planted on chosen real days with the same SQL as the synthetic variants, judged, and
then the clean batch is landed again and judged, so the clean history is not affected.

Runs on Exasol with `--backend exasol` (the adapter still reads the parquet files with DuckDB, then
the mapped tables are bulk loaded with IMPORT) and on the DuckDB stand-in by default.
"""

from __future__ import annotations

import statistics
import time
import urllib.request
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path

from . import gate
from .config import settings
from .db import Backend, DuckDBBackend, connect
from .load import create_pipeline, install_udf, udf_status
from .model import FESTIVAL_TABLES, SOURCE_TABLES
from .variants import _dup, _scale

DATASET = "NYC TLC Trip Record Data, yellow taxi trip records"
BASE = "https://d37ci6vzurychx.cloudfront.net"
MONTHS = ("2024-01", "2024-02", "2024-03")
ZONES = f"{BASE}/misc/taxi_zone_lookup.csv"

# planted faults: (day, label, expected cause, SQL statements)
FAULTS = [
    (date(2024, 2, 14), "CMT sends cents (x100)", "unit_scale", [_scale("CMT", 100)]),
    (date(2024, 3, 6), "CMT sends cents (x100)", "unit_scale", [_scale("CMT", 100)]),
    (date(2024, 3, 23), "CMT sends cents (x100)", "unit_scale", [_scale("CMT", 100)]),
    (date(2024, 2, 21), "Payment file F05 loaded twice", "duplicate_key", [_dup("LOAD_FILE = 'F05'")]),
    (date(2024, 3, 12), "Payment file F05 loaded twice", "duplicate_key", [_dup("LOAD_FILE = 'F05'")]),
    (date(2024, 3, 30), "Payment file F05 loaded twice", "duplicate_key", [_dup("LOAD_FILE = 'F05'")]),
]


def trip_url(month: str) -> str:
    return f"{BASE}/trip-data/yellow_tripdata_{month}.parquet"


def download(dest: Path, months=MONTHS, log=print) -> list[Path]:
    """Download each file once into dest, with a progress line about every 10 percent."""
    dest.mkdir(parents=True, exist_ok=True)
    out = []
    for url in [trip_url(m) for m in months] + [ZONES]:
        f = dest / url.rsplit("/", 1)[1]
        out.append(f)
        if f.exists() and f.stat().st_size > 0:
            log(f"already downloaded: {f.name}")
            continue
        part = f.with_suffix(f.suffix + ".part")
        with urllib.request.urlopen(url, timeout=60) as r, part.open("wb") as w:
            total = int(r.headers.get("Content-Length") or 0)
            done, step = 0, 10
            log(f"downloading {f.name} ({total / 1e6:.0f} MB)" if total else f"downloading {f.name}")
            while chunk := r.read(1 << 20):
                w.write(chunk)
                done += len(chunk)
                if total and done * 100 // total >= step:
                    log(f"  {f.name}: {done * 100 // total}%")
                    step += 10
        part.replace(f)
    return out


def _adapt(be: DuckDBBackend, files: list[Path], start: date, end: date, log=print) -> None:
    """Map the trips onto LANDING in DuckDB, which reads the parquet files directly."""
    be.run_script(be.render("schema.sql", tables=SOURCE_TABLES, festival=FESTIVAL_TABLES))
    trips = ", ".join(f"'{f.as_posix()}'" for f in files if f.suffix == ".parquet")
    zones = next(f for f in files if f.suffix == ".csv").as_posix()
    t = time.perf_counter()
    be.execute(f"""CREATE TEMP TABLE TRIPS AS
        SELECT ROW_NUMBER() OVER (ORDER BY tpep_pickup_datetime, VendorID, PULocationID) AS ID,
               VendorID, tpep_pickup_datetime AS PICKUP, CAST(tpep_pickup_datetime AS DATE) AS DAY,
               PULocationID, RatecodeID, payment_type, total_amount
        FROM read_parquet([{trips}])
        WHERE CAST(tpep_pickup_datetime AS DATE) BETWEEN DATE '{start}' AND DATE '{end}'""")
    be.execute(f"CREATE TEMP TABLE ZONES AS SELECT * FROM read_csv('{zones}', header = true)")
    be.execute("""INSERT INTO LANDING.ORDERS
        SELECT t.ID, t.DAY, t.PULocationID, LEFT(COALESCE(z.Borough, 'Unknown'), 20),
               CASE t.RatecodeID WHEN 1 THEN 'STD' WHEN 2 THEN 'JFK' WHEN 3 THEN 'NWK' WHEN 4 THEN 'NAS'
                    WHEN 5 THEN 'NEG' WHEN 6 THEN 'GRP' ELSE 'UNK' END,
               CASE t.payment_type WHEN 1 THEN 'CARD' WHEN 2 THEN 'CASH' WHEN 3 THEN 'NOCHG'
                    WHEN 4 THEN 'DISPUTE' ELSE 'OTHER' END
        FROM TRIPS t LEFT JOIN ZONES z ON z.LocationID = t.PULocationID""")
    be.execute("""INSERT INTO LANDING.PAYMENTS
        SELECT t.ID, t.ID, t.DAY, 'F' || LPAD(CAST((t.ID - 1) % 12 + 1 AS VARCHAR), 2, '0'),
               CASE t.VendorID WHEN 1 THEN 'CMT' WHEN 2 THEN 'CURB' ELSE 'OTHER' END,
               'INR', t.total_amount, CASE WHEN t.total_amount > 0 THEN 'CAPTURED' ELSE 'VOIDED' END,
               t.PICKUP - INTERVAL 330 MINUTE
        FROM TRIPS t""")
    be.execute(f"""INSERT INTO LANDING.MERCHANTS
        SELECT LocationID, LEFT(COALESCE(Zone, 'Unknown'), 40),
               CASE service_zone WHEN 'Yellow Zone' THEN 'YELLOW' WHEN 'Boro Zone' THEN 'BORO'
                    WHEN 'Airports' THEN 'AIRPORT' WHEN 'EWR' THEN 'EWR' ELSE 'NA' END, DATE '{start}'
        FROM ZONES""")
    be.execute("""INSERT INTO LANDING.CATEGORY_MAP VALUES ('STD', 'Standard rate'), ('JFK', 'JFK'),
        ('NWK', 'Newark'), ('NAS', 'Nassau or Westchester'), ('NEG', 'Negotiated fare'), ('GRP', 'Group ride'),
        ('UNK', 'Unknown rate code')""")
    n = be.scalar("SELECT COUNT(*) FROM TRIPS")
    log(f"mapped {n:,} trips from {start} to {end} in {time.perf_counter() - t:.0f}s")


def _export(duck: DuckDBBackend, out: Path, log=print) -> list[tuple[str, Path]]:
    """Write the adapted LANDING tables as CSV in the layout `receipts init` loads into Exasol."""
    out.mkdir(parents=True, exist_ok=True)
    files = []
    for tbl, cols in SOURCE_TABLES.items():
        if not duck.scalar(f"SELECT COUNT(*) FROM LANDING.{tbl}"):
            continue
        sel = ", ".join(f"strftime({c}, '%Y-%m-%d %H:%M:%S') || '.000' AS {c}" if typ == "TIMESTAMP" else c
                        for c, typ in cols)
        f = out / f"{tbl}.csv"
        duck.execute(f"COPY (SELECT {sel} FROM LANDING.{tbl}) TO '{f.as_posix()}' (HEADER, DELIMITER ',')")
        files.append((tbl, f))
        log(f"exported LANDING.{tbl} ({f.stat().st_size / 1e6:,.0f} MB)")
    return files


def build(db_path: Path, files: list[Path], start: date, end: date, first_judged: date, log=print,
          backend: str = "duckdb") -> Backend:
    """Load the trips into LANDING through the adapter and publish the warm-up days as trusted.

    On Exasol the adapter still runs in DuckDB (it reads parquet), the result is written to CSV and
    bulk loaded with IMPORT, and everything after that, the pipeline, the UDF, the gate, runs in Exasol.
    """
    db_path.unlink(missing_ok=True)
    t = time.perf_counter()
    duck = DuckDBBackend(str(db_path))
    _adapt(duck, files, start, end, log)
    if backend == "duckdb":
        be: Backend = duck
    else:
        csvs = _export(duck, db_path.parent / "exasol_csv", log)
        duck.close()
        db_path.unlink(missing_ok=True)  # the staging copy is not needed once the CSVs exist
        be = connect(replace(settings(), backend="exasol"))
        be.run_script(be.render("schema.sql", tables=SOURCE_TABLES, festival=FESTIVAL_TABLES))
        for tbl, f in csvs:
            t1 = time.perf_counter()
            be.load_csv(f, "LANDING", tbl)
            f.unlink()  # about 1 GB in all; free the disk as soon as Exasol has the rows
            log(f"IMPORT INTO LANDING.{tbl} in {time.perf_counter() - t1:.0f}s")
    create_pipeline(be)
    be.run_script(be.render("pub.sql"))
    udf = install_udf(be)
    log(f"udf: {udf['udf']}")
    for tbl in ("MERCHANTS", "CATEGORY_MAP", "FX_RATES"):
        be.execute(f"INSERT INTO RAW.{tbl} SELECT * FROM LANDING.{tbl}")
    for tbl in ("ORDERS", "PAYMENTS"):
        be.execute(f"INSERT INTO RAW.{tbl} SELECT * FROM LANDING.{tbl} WHERE BATCH_DAY < DATE '{first_judged}'")
    be.execute(f"""INSERT INTO PUB.DAILY_REVENUE_PUBLISHED
        SELECT d.TXN_DAY, d.REVENUE_INR, d.REVENUE_INR, 'TRUSTED', 'warm-up', CURRENT_TIMESTAMP
        FROM PIPE.DAILY_REVENUE d WHERE d.TXN_DAY < DATE '{first_judged}'""")
    log(f"database ready in {time.perf_counter() - t:.0f}s")
    return be


def land(be: Backend, day: date) -> None:
    """Land (or land again) one night's trips in RAW."""
    for tbl in ("ORDERS", "PAYMENTS"):
        be.execute(f"DELETE FROM RAW.{tbl} WHERE BATCH_DAY = DATE '{day}'")
        be.execute(f"INSERT INTO RAW.{tbl} SELECT * FROM LANDING.{tbl} WHERE BATCH_DAY = DATE '{day}'")


def _row(case: dict, day: date) -> dict:
    v = case["values"]
    return {"day": day.isoformat(), "weekday": f"{day:%a}", "value": v["candidate"], "expected": v["baseline"],
            "change_pct": v["change_pct"], "band_pct": (v["band_high"] - v["baseline"]) / v["baseline"],
            "seasonal": bool(v.get("seasonal")), "anomaly": case["anomaly"],
            "verdict": case["verdict"], "trust": case["trust_status"], "confirmed": case["confirmed"],
            "fired": [f"{s['id']}:{s['outcome']}" for s in case["suspects"] if s["fired"]],
            "ms": case["total_ms"], "db_ms": case["db_ms"], "statements": case["statements"]}


def run(data_dir: Path, months=MONTHS, warmup: int = 35, faults=FAULTS, log=print, backend: str = "duckdb") -> dict:
    t0 = time.perf_counter()
    files = download(data_dir, months, log)
    start = date.fromisoformat(months[0] + "-01")
    last = date.fromisoformat(months[-1] + "-01")
    end = (last.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    first_judged = start + timedelta(days=warmup)
    t = time.perf_counter()
    be = build(data_dir / "backtest.duckdb", files, start, end, first_judged, log, backend=backend)
    load_s = round(time.perf_counter() - t, 1)
    desc = be.describe() | udf_status(be)
    plan = {}
    for d, label, cause, sql in faults:
        plan.setdefault(d, []).append((label, cause, sql))
    clean, planted = [], []
    day = first_judged
    while day <= end:
        for label, cause, sql in plan.get(day, []):
            land(be, day)
            truth = be.scalar(f"SELECT REVENUE_INR FROM PIPE.DAILY_REVENUE WHERE TXN_DAY = DATE '{day}'")
            for stmt in sql:
                be.execute(be.render_string(stmt, incoming=day))
            c = gate.run(be, day, {"id": "planted", "title": label}, write_back=False)
            r = _row(c, day) | {"fault": label, "expected_cause": cause,
                                "real_error_pct": (c["values"]["candidate"] - truth) / truth * 100,
                                "caught": c["verdict"] == "PROVEN_FAULT" and c["confirmed"] == [cause],
                                "held": c["trust_status"] == "HELD"}
            planted.append(r)
            log(f"{day} planted {label:32s} {c['verdict']:13s} {','.join(c['confirmed']) or '-'}")
        land(be, day)
        c = gate.run(be, day, {"id": "real", "title": "Real day"}, write_back=True)
        clean.append(_row(c, day))
        log(f"{day} {day:%a} real {c['verdict']:13s} change {c['values']['change_pct']:+6.1%} "
            f"fired {','.join(clean[-1]['fired']) or '-'}")
        day += timedelta(days=1)
    trips = be.scalar("SELECT COUNT(*) FROM LANDING.PAYMENTS")
    be.close()
    return {"dataset": DATASET, "urls": [trip_url(m) for m in months] + [ZONES], "start": start.isoformat(),
            "end": end.isoformat(), "first_judged": first_judged.isoformat(), "warmup": warmup, "trips": trips,
            "clean": clean, "planted": planted, "seconds": round(time.perf_counter() - t0),
            "backend": desc, "load_seconds": load_s, "timings": _timings(clean + planted)}


def _timings(rows: list[dict]) -> dict:
    ms = sorted(r["ms"] for r in rows)
    db = sorted(r["db_ms"] for r in rows)
    return {"gate_runs": len(rows), "median_ms": round(statistics.median(ms)), "max_ms": round(ms[-1]),
            "median_db_ms": round(statistics.median(db)), "max_db_ms": round(db[-1]),
            "median_statements": round(statistics.median(r["statements"] for r in rows))}


def _money(x: float) -> str:
    return f"${x / 1e6:,.2f}M"


def _where(rep: dict) -> str:
    b = rep.get("backend") or {"backend": "duckdb", "standin": True}
    if b["backend"] == "exasol" and not b.get("standin"):
        return f"on Exasol {b.get('version', '')}".rstrip() + f" (Python UDF: {b.get('udf', '?')})"
    return "on the DuckDB stand-in"


def to_markdown(rep: dict, command: str, compare: dict | None = None) -> str:
    clean, planted = rep["clean"], rep["planted"]
    held = [r for r in clean if r["trust"] == "HELD"]
    by_verdict = {}
    for r in clean:
        by_verdict[r["verdict"]] = by_verdict.get(r["verdict"], 0) + 1
    out = ["# Real-data backtest", "",
           f"Dataset: **{rep['dataset']}**, published by the NYC Taxi and Limousine Commission, no login needed.", ""]
    out += [f"* {u}" for u in rep["urls"]]
    out += ["", f"Trips from {rep['start']} to {rep['end']}: {rep['trips']:,}. The metric is the daily total of "
                f"`total_amount` by pickup date. The first {rep['warmup']} days ({rep['start']} to "
                f"{(date.fromisoformat(rep['first_judged']) - timedelta(days=1)).isoformat()}) are published as "
                f"trusted history by assumption; the gate then judges {len(clean)} days, "
                f"{rep['first_judged']} to {rep['end']}, one night at a time, {_where(rep)}. "
                "No threshold was changed for this data. How trips map onto the pipeline tables is described in "
                "`receipts/backtest.py`.", "",
            f"Reproduce: `{command}` (downloads about 150 MB once into `data/real/`, then runs in about "
            f"{max(1, round(rep['seconds'] / 60))} minutes).", "",
            "## Real days, no faults planted", "",
            f"* Days judged: **{len(clean)}**",
            f"* Held: **{len(held)}**",
            "* Verdicts: " + ", ".join(f"{k} {v}" for k, v in sorted(by_verdict.items())),
            f"* Days where the weekday-aware baseline was used: {sum(r['seasonal'] for r in clean)} of {len(clean)}",
            f"* Normal range around the expected value: median plus or minus "
            f"{sorted(r['band_pct'] for r in clean)[len(clean) // 2]:.1%}, from "
            f"{min(r['band_pct'] for r in clean):.1%} to {max(r['band_pct'] for r in clean):.1%}",
            f"* Real days called PROVEN_FAULT: **{by_verdict.get('PROVEN_FAULT', 0)}**"]
    ruled_out = [(r["day"], r["weekday"], f) for r in clean for f in r["fired"] if not f.endswith(":CONFIRMED")]
    if ruled_out:
        out.append(f"* Detector firings on real days that the undo test ruled out: {len(ruled_out)} ("
                   + ", ".join(f"{f.split(':')[0]} on {d} {w}" for d, w, f in ruled_out) + ")")
    out.append("")
    if held:
        out += ["Held days (no fault was planted, so each is either a false hold or a real change the volume "
                "check did not accept):", "",
                "| Day | Revenue | Expected | Change | Verdict | Detectors that fired |", "|---|---|---|---|---|---|"]
        for r in held:
            out.append(f"| {r['day']} {r['weekday']} | {_money(r['value'])} | {_money(r['expected'])} | "
                       f"{r['change_pct']:+.1%} | {r['verdict']} | {', '.join(r['fired']) or '-'} |")
        out.append("")
    moved = [r for r in clean if r["verdict"] == "REAL_CHANGE"]
    if moved:
        out += ["Published as a verified real change: " + ", ".join(f"{r['day']} ({r['change_pct']:+.1%})"
                                                                     for r in moved) + ".", ""]
    out += ["## Planted faults on real days", "",
            "| Day | Fault | Real error | Outside the normal range | Verdict | Causes named | Caught |",
            "|---|---|---|---|---|---|---|"]
    for r in planted:
        out.append(f"| {r['day']} {r['weekday']} | {r['fault']} | {r['real_error_pct']:+.1f}% | "
                   f"{'yes' if r['anomaly'] else 'no'} | {r['verdict']} | {', '.join(r['confirmed']) or 'none'} | "
                   f"{'yes' if r['caught'] else ('held, cause not proven' if r['held'] else 'NO')} |")
    caught = sum(r["caught"] for r in planted)
    out += ["", f"Caught with the right cause: **{caught} of {len(planted)}**.", ""]
    tm = rep.get("timings")
    if tm:
        out += ["## Timings", "",
                f"Measured {_where(rep)}, from the client. Building the database (adapter, load, pipeline, UDF, "
                f"warm-up history) took {rep['load_seconds']:,.0f} s.", "",
                "| Measure | Median | Max |", "|---|---|---|",
                f"| Gate run, end to end ({tm['gate_runs']} runs) | {tm['median_ms']:,} ms | {tm['max_ms']:,} ms |",
                f"| Of which inside the database (sum over statements) | {tm['median_db_ms']:,} ms | {tm['max_db_ms']:,} ms |",
                f"| SQL statements per gate run | {tm['median_statements']} | |", ""]
    if compare:
        out += _comparison(rep, compare)
    out += ["## All judged days", "",
            "| Day | Revenue | Expected | Change | Normal range | Weekday baseline | Verdict | Fired |",
            "|---|---|---|---|---|---|---|---|"]
    for r in clean:
        out.append(f"| {r['day']} {r['weekday']} | {_money(r['value'])} | {_money(r['expected'])} | "
                   f"{r['change_pct']:+.1%} | +/-{r['band_pct']:.1%} | {'yes' if r['seasonal'] else 'no'} | {r['verdict']} | "
                   f"{', '.join(r['fired']) or '-'} |")
    return "\n".join(out) + "\n"


def _comparison(rep: dict, other: dict) -> list[str]:
    """Day by day, does this run reach the same verdict and causes as another backend's run?"""
    def key(r):
        return r["day"], r.get("fault", "")

    mine = {key(r): r for r in rep["clean"] + rep["planted"]}
    theirs = {key(r): r for r in other["clean"] + other["planted"]}
    shared = sorted(set(mine) & set(theirs))
    diff = [k for k in shared
            if (mine[k]["verdict"], mine[k]["confirmed"]) != (theirs[k]["verdict"], theirs[k]["confirmed"])]
    fired = [k for k in shared if sorted(mine[k]["fired"]) != sorted(theirs[k]["fired"])]
    vals = [abs(mine[k]["value"] - theirs[k]["value"]) / max(abs(theirs[k]["value"]), 1) for k in shared]
    out = [f"## Compared with the run {_where(other)}", "",
           f"* Gate runs compared: {len(shared)} (same days, same planted faults)",
           f"* Same verdict and same causes: **{len(shared) - len(diff)} of {len(shared)}**",
           f"* Same detectors fired: {len(shared) - len(fired)} of {len(shared)}",
           f"* Largest relative difference in the metric value between the two databases: {max(vals, default=0):.2e}"]
    for k in diff:
        a, b = mine[k], theirs[k]
        out.append(f"* Differs on {k[0]}{' (' + k[1] + ')' if k[1] else ''}: {a['verdict']} "
                   f"{','.join(a['confirmed']) or '-'} here, {b['verdict']} {','.join(b['confirmed']) or '-'} there")
    for k in fired:
        if k not in diff:
            out.append(f"* Detectors differ on {k[0]}{' (' + k[1] + ')' if k[1] else ''}: "
                       f"{', '.join(mine[k]['fired']) or '-'} here, {', '.join(theirs[k]['fired']) or '-'} there")
    return out + [""]
