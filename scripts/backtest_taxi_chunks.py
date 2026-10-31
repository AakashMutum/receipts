"""The real-data backtest over 2023 and 2024, one month at a time, with trusted history carried forward.

The adapter, the gate and its thresholds are those of `receipts backtest`, unchanged. Two years of trips do not fit in
the database at once on one laptop, so each month is its own chunk: the database is rebuilt with that month's trips
and the month before (the detectors and the reconciliation read the raw batches of earlier days), and the published
history is replaced by the history carried forward from the chunks before, exactly as the gate wrote it: trusted days,
real changes and held days alike. The revenue metric reads its trusted history from PUB.DAILY_REVENUE_PUBLISHED (a
configured metric that is not published reads RECEIPTS.METRIC_HISTORY instead), so that is the table carried forward.
Only the first chunk publishes its first 35 days as trusted by assumption, as in `receipts backtest`.

Planted faults, fixed before the run: in every judged month, the CMT vendor sends cents (x100) on the second
Wednesday and payment file F05 is loaded twice on the third Tuesday. Each is judged without write-back, then the
clean batch is landed again and judged, so the clean history is not affected.

    python scripts/backtest_taxi_chunks.py --backend exasol
    python scripts/backtest_taxi_chunks.py --backend duckdb      # the stand-in, for the cross-check
    python scripts/backtest_taxi_chunks.py --report

Each finished month is saved outside the repository (D:/Hackathon/data/taxi), so a second start resumes after the
last finished month. Writes samples/exasol/real_backtest_taxi_2023_2024.md and .json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import statistics
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from receipts import backtest, gate  # noqa: E402
from receipts.backtest import ZONES, _row, build, land, trip_url  # noqa: E402
from receipts.variants import _dup, _scale  # noqa: E402

DATA = Path("D:/Hackathon/data/taxi") if sys.platform == "win32" else ROOT / "data" / "taxi"
OUT = ROOT / "samples" / "exasol"
FIRST, LAST = "2023-01", "2024-12"
WARMUP = 35
PUB_COLS = "TXN_DAY, METRIC_VALUE, CANDIDATE_VALUE, TRUST_STATUS, CASE_ID, PUBLISHED_AT"


def months(first: str = FIRST, last: str = LAST) -> list[str]:
    y, m = map(int, first.split("-"))
    out = []
    while f"{y:04d}-{m:02d}" <= last:
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def month_start(month: str) -> date:
    return date.fromisoformat(month + "-01")


def month_end(month: str) -> date:
    return (month_start(month).replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)


def nth_weekday(month: str, weekday: int, n: int) -> date:
    d = month_start(month)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)


def faults(month: str) -> list[tuple[date, str, str, list[str]]]:
    return [(nth_weekday(month, 2, 2), "CMT sends cents (x100)", "unit_scale", [_scale("CMT", 100)]),
            (nth_weekday(month, 1, 3), "Payment file F05 loaded twice", "duplicate_key", [_dup("LOAD_FILE = 'F05'")])]


def sampled(day: str) -> bool:
    """The 10% of days cross-checked on the stand-in, fixed before the run: every tenth day by ordinal."""
    return date.fromisoformat(day).toordinal() % 10 == 0


def first_judged() -> date:
    return month_start(FIRST) + timedelta(days=WARMUP)


def free_c_gib() -> float:
    return shutil.disk_usage("C:/" if sys.platform == "win32" else "/").free / 2**30


def _sql(v) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(float(v))
    return "'" + str(v).replace("'", "''") + "'"


def carry(be, rows: list[dict]) -> None:
    """Replace the published history with the rows carried forward from the earlier chunks."""
    be.execute("DELETE FROM PUB.DAILY_REVENUE_PUBLISHED")
    for i in range(0, len(rows), 200):
        vals = ", ".join(f"(DATE '{r['txn_day']}', {_sql(r['metric_value'])}, {_sql(r['candidate_value'])}, "
                         f"{_sql(r['trust_status'])}, {_sql(r['case_id'])}, TIMESTAMP '{r['published_at']}')"
                         for r in rows[i:i + 200])
        be.execute(f"INSERT INTO PUB.DAILY_REVENUE_PUBLISHED ({PUB_COLS}) VALUES {vals}")


def published(be) -> list[dict]:
    rows = be.query(f"SELECT {PUB_COLS} FROM PUB.DAILY_REVENUE_PUBLISHED ORDER BY TXN_DAY")
    return [{"txn_day": str(r["txn_day"])[:10], "metric_value": r["metric_value"],
             "candidate_value": r["candidate_value"], "trust_status": r["trust_status"], "case_id": r["case_id"],
             "published_at": str(r["published_at"])[:19]} for r in rows]


def run(backend: str, stop_at: datetime, log) -> None:
    store = DATA / backend
    store.mkdir(parents=True, exist_ok=True)
    rows_file = store / "days.jsonl"
    todo = months()[1:]  # the first month is warm-up and the first days of February
    for m in todo:
        hist_file = store / f"published_{m}.json"
        if hist_file.exists():
            log(f"{m} already done")
            continue
        if datetime.now() >= stop_at:
            log(f"stop: reached {stop_at:%Y-%m-%d %H:%M} before {m}")
            return
        if free_c_gib() < 2:
            log(f"stop: {free_c_gib():.1f} GiB free on C:, below 2 GiB")
            return
        prev = months()[months().index(m) - 1]
        files = backtest.download(DATA / "files", (prev, m), log)
        t = time.perf_counter()
        start = month_start(prev)
        judged_from = first_judged() if prev == FIRST else month_start(m)
        be = build(store / f"chunk_{backend}.duckdb", files, start, month_end(m), judged_from, log, backend=backend)
        if prev != FIRST:
            carry(be, json.loads((store / f"published_{prev}.json").read_text(encoding="utf-8")))
        info = {"month": m, "backend": be.describe() | backtest.udf_status(be),
                "load_seconds": round(time.perf_counter() - t, 1),
                "trips": be.scalar(f"SELECT COUNT(*) FROM LANDING.PAYMENTS WHERE BATCH_DAY >= DATE '{month_start(m)}'"),
                "free_c_gib": round(free_c_gib(), 1)}
        log(f"{m}: {info['trips']:,} trips loaded in {info['load_seconds']:.0f} s, C: {info['free_c_gib']} GiB free")
        plan = {}
        for d, label, cause, sql in faults(m):
            plan.setdefault(d, []).append((label, cause, sql))
        out = []
        day = judged_from
        while day <= month_end(m):
            for label, cause, sql in plan.get(day, []):
                land(be, day)
                truth = be.scalar(f"SELECT REVENUE_INR FROM PIPE.DAILY_REVENUE WHERE TXN_DAY = DATE '{day}'")
                for stmt in sql:
                    be.execute(be.render_string(stmt, incoming=day))
                c = gate.run(be, day, {"id": "planted", "title": label}, write_back=False)
                out.append(_row(c, day) | {"kind": "planted", "fault": label, "expected_cause": cause,
                                           "real_error_pct": (c["values"]["candidate"] - truth) / truth * 100,
                                           "caught": c["verdict"] == "PROVEN_FAULT" and c["confirmed"] == [cause],
                                           "held": c["trust_status"] == "HELD"})
                log(f"{day} planted {label:32s} {c['verdict']:13s} {','.join(c['confirmed']) or '-'}")
            land(be, day)
            c = gate.run(be, day, {"id": "real", "title": "Real day"}, write_back=True)
            out.append(_row(c, day) | {"kind": "clean"})
            log(f"{day} {day:%a} real {c['verdict']:13s} change {c['values']['change_pct']:+6.1%} "
                f"{c['total_ms']:.0f} ms fired {','.join(out[-1]['fired']) or '-'}")
            day += timedelta(days=1)
        info["seconds"] = round(time.perf_counter() - t, 1)
        hist = published(be)
        if backend == "exasol":  # the chunk's schemas are rebuilt by the next chunk; leave nothing large behind
            for tbl in ("ORDERS", "PAYMENTS"):
                be.execute(f"TRUNCATE TABLE LANDING.{tbl}")
                be.execute(f"TRUNCATE TABLE RAW.{tbl}")
        be.close()
        (store / f"chunk_{backend}.duckdb").unlink(missing_ok=True)
        with rows_file.open("a", encoding="utf-8") as f:
            for r in out:
                f.write(json.dumps(r | {"month": m}, default=str) + "\n")
        with (store / "months.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(info, default=str) + "\n")
        hist_file.write_text(json.dumps(hist, default=str), encoding="utf-8")  # written last: marks the month done
        log(f"{m} done in {info['seconds']:.0f} s")


def load(backend: str) -> tuple[list[dict], list[dict], list[dict]]:
    store = DATA / backend
    done = {json.loads(x)["month"] for x in (store / "months.jsonl").read_text(encoding="utf-8").splitlines() if x}
    done = {m for m in done if (store / f"published_{m}.json").exists()}
    rows = [json.loads(x) for x in (store / "days.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    rows = [r for r in rows if r["month"] in done]
    info = [json.loads(x) for x in (store / "months.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    strip = lambda r: {k: v for k, v in r.items() if k != "kind"}
    return ([strip(r) for r in rows if r["kind"] == "clean"], [strip(r) for r in rows if r["kind"] == "planted"],
            [i for i in info if i["month"] in done])


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while b := f.read(1 << 20):
            h.update(b)
    return h.hexdigest()


def report() -> None:
    clean, planted, info = load("exasol")
    done = [i["month"] for i in info]
    key = lambda r: (r["day"], r.get("fault", ""))
    compare = full = None
    if (DATA / "duckdb" / "months.jsonl").exists():
        dc, dp, _ = load("duckdb")
        theirs = {key(r): r for r in dc + dp}
        mine = clean + planted
        shared = [r for r in mine if key(r) in theirs]
        same = lambda r: (r["verdict"], r["confirmed"]) == (theirs[key(r)]["verdict"], theirs[key(r)]["confirmed"])
        full = (sum(map(same, shared)), len(shared))
        compare = {"clean": [r for r in dc if sampled(r["day"])], "planted": [r for r in dp if sampled(r["day"])],
                   "backend": json.loads((DATA / "duckdb" / "months.jsonl").read_text(encoding="utf-8")
                                         .splitlines()[0])["backend"]}
    rep = {"dataset": backtest.DATASET, "urls": [trip_url(m) for m in [FIRST] + done] + [ZONES],
           "start": f"{FIRST}-01", "end": month_end(done[-1]).isoformat(), "first_judged": first_judged().isoformat(),
           "warmup": WARMUP, "trips": sum(i["trips"] for i in info), "clean": clean, "planted": planted,
           "backend": info[0]["backend"], "load_seconds": sum(i["load_seconds"] for i in info),
           "timings": backtest._timings(clean + planted), "seconds": sum(i["seconds"] for i in info),
           "months": info}
    cmd = "python scripts/backtest_taxi_chunks.py --backend exasol"
    md = backtest.to_markdown(rep, cmd, compare)
    held = [r for r in clean if r["trust"] == "HELD"]
    ms = sorted(r["ms"] for r in clean + planted)
    caught = sum(r["caught"] for r in planted)
    files = sorted((DATA / "files").glob("*"))
    summary = [
        "## Two years in monthly chunks, in short", "",
        f"* Range judged: **{rep['first_judged']} to {rep['end']}**, {len(clean)} real days in {len(done)} monthly "
        f"chunks ({done[0]} to {done[-1]}). January 2023 and the first {WARMUP - 31} days of February 2023 are the "
        "warm-up, published as trusted by assumption; after that every day is judged against the history the gate "
        "itself published, carried forward from chunk to chunk.",
        f"* Trips in the judged months: {rep['trips']:,}.",
        f"* Gate runs: {len(clean) + len(planted)} ({len(clean)} real days, {len(planted)} with a planted fault).",
        f"* Real days held: **{len(held)}**" + (" (" + ", ".join(f"{r['day']} {r['verdict']}" for r in held) + ")"
                                                if held else "") + ".",
        f"* Real days published as a real change, no fault found: {sum(r['verdict'] == 'REAL_CHANGE' for r in clean)}.",
        f"* Planted faults caught with the right cause: **{caught} of {len(planted)}**"
        + ("" if caught == len(planted) else " (misses: " + ", ".join(
            f"{r['day']} {r['fault']} {r['verdict']} {','.join(r['confirmed']) or '-'}"
            for r in planted if not r["caught"]) + ")") + ".",
        f"* Gate run, end to end: median {statistics.median(ms):,.0f} ms, max {ms[-1]:,.0f} ms. Total time on "
        f"Exasol including the monthly loads: {rep['seconds'] / 3600:.1f} hours.",
        ("* Cross-check on the DuckDB stand-in, the 10% sample fixed before the run (every day whose ordinal is a "
         f"multiple of ten, with any fault planted on it): see the comparison below. Over every gate run both "
         f"backends judged: same verdict and causes in **{full[0]} of {full[1]}**." if full else
         "* Cross-check on the DuckDB stand-in: not run."),
        "* Planted faults, fixed before the run: in every judged month, CMT sends cents (x100) on the second "
        "Wednesday and file F05 is loaded twice on the third Tuesday.",
        "* Each chunk holds its month and the month before; a trip from a monthly file whose pickup date falls outside "
        "those two months is not loaded.",
        "", "### Source and terms", "",
        "Trip files and the zone lookup from the NYC Taxi and Limousine Commission (TLC Trip Record Data, "
        "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page). The TLC page states: \"The trip data was not "
        "created by the TLC, and TLC makes no representations as to the accuracy of these data.\" The NYC Open Data FAQ "
        "(https://www.nyc.gov/opendata/get-started/FAQs) states: \"Open Data belongs to all New Yorkers. There are no "
        "restrictions on the use of Open Data.\" Downloaded files, outside the repository (see also "
        "[`docs/DATA_MANIFEST.md`](../../docs/DATA_MANIFEST.md)):", "",
        "| File | Bytes | SHA-256 |", "|---|---|---|"]
    summary += [f"| {f.name} | {f.stat().st_size:,} | `{sha256(f)}` |" for f in files if f.suffix in (".parquet", ".csv")]
    summary += ["", "### Per month", "", "| Month | Trips | Days | Held | Real change | Planted caught | Load s | Month s |",
                "|---|---|---|---|---|---|---|---|"]
    for i in info:
        mc = [r for r in clean if r["month"] == i["month"]]
        mp = [r for r in planted if r["month"] == i["month"]]
        summary.append(f"| {i['month']} | {i['trips']:,} | {len(mc)} | {sum(r['trust'] == 'HELD' for r in mc)} | "
                       f"{sum(r['verdict'] == 'REAL_CHANGE' for r in mc)} | {sum(r['caught'] for r in mp)} of {len(mp)} | "
                       f"{i['load_seconds']:.0f} | {i['seconds']:.0f} |")
    summary.append("")
    i = md.index("## Real days, no faults planted")
    md = md[:i] + "\n".join(summary) + "\n" + md[i:]
    md = md.replace("# Real-data backtest", "# Real-data backtest, 2023 and 2024 in monthly chunks", 1)
    md = md.replace(f"Trips from {rep['start']} to", f"Trips from {month_start(done[0])} to", 1)  # the count starts there
    import re
    md = re.sub(r"Reproduce: .*", f"Reproduce: `{cmd}` (downloads about 50 to 80 MB per month into "
                "`D:/Hackathon/data/taxi`).", md, count=1)
    (OUT / "real_backtest_taxi_2023_2024.json").write_text(json.dumps(rep | {"summary": {
        "real_days": len(clean), "gate_runs": len(clean) + len(planted), "held": len(held),
        "planted_caught": [caught, len(planted)], "standin_agree_all": full}}, indent=2, default=str), encoding="utf-8")
    (OUT / "real_backtest_taxi_2023_2024.md").write_text(md, encoding="utf-8")
    print(f"report: {len(clean)} real days, {len(held)} held, {caught} of {len(planted)} planted caught, "
          f"stand-in {full}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="exasol", choices=("exasol", "duckdb"))
    ap.add_argument("--stop-at", help="local time to stop, YYYY-MM-DD HH:MM; a month in progress is not counted")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if a.report:
        report()
        return
    stop = datetime.fromisoformat(a.stop_at) if a.stop_at else datetime.max
    run(a.backend, stop, lambda m: print(f"{datetime.now():%H:%M:%S} {m}", flush=True))


if __name__ == "__main__":
    main()
