"""The real-data backtest over a longer range: NYC TLC yellow taxi trips from January 2024 onward.

Uses the adapter, the planted faults, the warm-up and the thresholds of `receipts backtest` unchanged; only the range
is longer. Each judged day is appended to a JSON lines file as soon as it is judged, so a run that stops early still
leaves every finished day. The report covers whole calendar months only: a month counts when its last day was judged.

    python scripts/backtest_extended.py --backend exasol --until 2024-12 --stop-at "2026-10-30 07:00"
    python scripts/backtest_extended.py --report        # rebuild the report from the saved days

Downloads go to data/real/ one month at a time; free RAM and free disk are checked before each month.
Writes samples/exasol/real_backtest_extended.md and .json (or samples/real_backtest_extended.* on the stand-in).
"""

from __future__ import annotations

import argparse
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
from receipts.backtest import FAULTS, ZONES, _row, build, land, trip_url  # noqa: E402

DATA = ROOT / "data" / "real"


def months_from(first: str, last: str) -> list[str]:
    y, m = map(int, first.split("-"))
    out = []
    while f"{y:04d}-{m:02d}" <= last:
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def month_end(month: str) -> date:
    d = date.fromisoformat(month + "-01")
    return (d.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)


def free_ram_gib() -> float | None:
    try:
        if sys.platform == "win32":
            import ctypes

            class MS(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            s = MS(); s.dwLength = ctypes.sizeof(MS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s))
            return s.ullAvailPhys / 2**30
        import os
        return os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE") / 2**30
    except Exception:
        return None


def checks(log) -> bool:
    ram = free_ram_gib()
    d = shutil.disk_usage(DATA).free / 2**30
    c = shutil.disk_usage("C:/").free / 2**30 if sys.platform == "win32" else d
    log(f"check: free RAM {ram:.1f} GiB, free disk D: {d:.1f} GiB, C: {c:.1f} GiB" if ram is not None
        else f"check: free disk {d:.1f} GiB")
    if c < 3 or d < 5:
        log("stop: less than 3 GiB free on C: or 5 GiB on the data disk")
        return False
    if ram is not None and ram < 0.5:
        log("stop: less than 0.5 GiB of free RAM")
        return False
    return True


def run(backend: str, months: list[str], stop_at: datetime, rows_file: Path, log) -> None:
    files = []
    for m in months:  # one month at a time, checking room before each download
        if not checks(log):
            months = months[:len(files)]
            break
        files += backtest.download(DATA, (m,), log)[:1]
    files += backtest.download(DATA, (), log)  # the zone lookup
    start = date.fromisoformat(months[0] + "-01")
    end = month_end(months[-1])
    first_judged = start + timedelta(days=35)
    t = time.perf_counter()
    be = build(DATA / f"extended_{backend}.duckdb", files, start, end, first_judged, log, backend=backend)
    meta = {"backend": be.describe() | backtest.udf_status(be), "load_seconds": round(time.perf_counter() - t, 1),
            "trips": be.scalar("SELECT COUNT(*) FROM LANDING.PAYMENTS"), "start": start.isoformat(),
            "end": end.isoformat(), "first_judged": first_judged.isoformat(), "months": months,
            "urls": [trip_url(m) for m in months] + [ZONES], "warmup": 35,
            "trips_by_month": {f"{int(r['y']):04d}-{int(r['m']):02d}": int(r['n']) for r in be.query(
                "SELECT EXTRACT(YEAR FROM BATCH_DAY) AS Y, EXTRACT(MONTH FROM BATCH_DAY) AS M, COUNT(*) AS N "
                "FROM LANDING.PAYMENTS GROUP BY EXTRACT(YEAR FROM BATCH_DAY), EXTRACT(MONTH FROM BATCH_DAY)")}}
    rows_file.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")
    log(f"loaded {meta['trips']:,} trips in {meta['load_seconds']:.0f} s")
    plan = {}
    for d, label, cause, sql in FAULTS:
        plan.setdefault(d, []).append((label, cause, sql))
    rows_file.write_text("", encoding="utf-8")
    day = first_judged
    reconnects = 0
    while day <= end:
        if datetime.now() >= stop_at:
            log(f"stop: reached {stop_at:%Y-%m-%d %H:%M} before judging {day}")
            break
        if day.day == 1 and not checks(log):
            break
        try:
            for label, cause, sql in plan.get(day, []):
                land(be, day)
                truth = be.scalar(f"SELECT REVENUE_INR FROM PIPE.DAILY_REVENUE WHERE TXN_DAY = DATE '{day}'")
                for stmt in sql:
                    be.execute(be.render_string(stmt, incoming=day))
                c = gate.run(be, day, {"id": "planted", "title": label}, write_back=False)
                r = _row(c, day) | {"kind": "planted", "fault": label, "expected_cause": cause,
                                    "real_error_pct": (c["values"]["candidate"] - truth) / truth * 100,
                                    "caught": c["verdict"] == "PROVEN_FAULT" and c["confirmed"] == [cause],
                                    "held": c["trust_status"] == "HELD"}
                with rows_file.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(r, default=str) + "\n")
                log(f"{day} planted {label:32s} {c['verdict']:13s} {','.join(c['confirmed']) or '-'}")
            land(be, day)
            c = gate.run(be, day, {"id": "real", "title": "Real day"}, write_back=True)
        except Exception as e:  # the database stopped answering, or anything else: stop and keep what is done
            lost = "Communication" in type(e).__name__ or "lost" in str(e)
            if backend == "exasol" and lost and reconnects < 3:
                reconnects += 1  # a dropped session: connect again and judge the same day again, at most 3 times
                log(f"connection lost on {day}, reconnecting ({reconnects} of 3)")
                from dataclasses import replace

                from receipts.config import settings
                from receipts.db import connect
                be = connect(replace(settings(), backend="exasol"))
                continue
            log(f"stop: {type(e).__name__} on {day}: {str(e)[:300]}")
            break
        r = _row(c, day) | {"kind": "clean"}
        with rows_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(r, default=str) + "\n")
        log(f"{day} {day:%a} real {c['verdict']:13s} change {c['values']['change_pct']:+6.1%} {c['total_ms']:.0f} ms "
            f"fired {','.join(r['fired']) or '-'}")
        day += timedelta(days=1)
    try:
        be.close()
    except Exception:
        pass


def load_rows(rows_file: Path) -> tuple[dict, list[dict]]:
    meta = json.loads(rows_file.with_suffix(".meta.json").read_text(encoding="utf-8"))
    rows = [json.loads(x) for x in rows_file.read_text(encoding="utf-8").splitlines() if x.strip()]
    last = {(r["day"], r["kind"], r.get("fault", "")): r for r in rows}  # a day judged again after a reconnect
    return meta, list(last.values())


def whole_months(meta: dict, rows: list[dict]) -> tuple[list[dict], date | None]:
    """Keep the judged days up to the end of the last calendar month whose last day was judged."""
    judged = {r["day"] for r in rows if r["kind"] == "clean"}
    last = None
    for m in meta["months"]:
        if month_end(m).isoformat() in judged:
            last = month_end(m)
    if last is None:
        return [], None
    return [r for r in rows if date.fromisoformat(r["day"]) <= last], last


def report(backend: str, rows_file: Path, other_file: Path | None) -> Path | None:
    meta, rows = load_rows(rows_file)
    rows, last = whole_months(meta, rows)
    if not rows:
        print("no whole month judged yet")
        return None
    clean = [{k: v for k, v in r.items() if k != "kind"} for r in rows if r["kind"] == "clean"]
    planted = [{k: v for k, v in r.items() if k != "kind"} for r in rows if r["kind"] == "planted"]
    months = [m for m in meta["months"] if month_end(m) <= last]
    rep = {"dataset": backtest.DATASET, "urls": [trip_url(m) for m in months] + [ZONES], "start": meta["start"],
           "end": last.isoformat(), "first_judged": meta["first_judged"], "warmup": meta["warmup"],
           "trips_loaded": meta["trips"], "months_loaded": meta["months"], "clean": clean, "planted": planted,
           "backend": meta["backend"], "load_seconds": meta["load_seconds"],
           "timings": backtest._timings(clean + planted), "seconds": 0}
    rep["trips"] = sum(n for m, n in meta["trips_by_month"].items() if m <= last.isoformat()[:7])
    compare = None
    if other_file and other_file.exists() and other_file.with_suffix(".meta.json").exists():
        om, orows = load_rows(other_file)
        orows = [r for r in orows if date.fromisoformat(r["day"]) <= last]
        compare = {"clean": [r for r in orows if r["kind"] == "clean"],
                   "planted": [r for r in orows if r["kind"] == "planted"], "backend": om["backend"]}
    cmd = f"python scripts/backtest_extended.py --backend {backend} --until {meta['months'][-1]}"
    md = backtest.to_markdown(rep, cmd, compare)
    held = sum(r["trust"] == "HELD" for r in clean)
    real_change = sum(r["verdict"] == "REAL_CHANGE" for r in clean)
    published = sum(r["trust"] != "HELD" for r in clean)
    ms = sorted(r["ms"] for r in clean + planted)
    covered = len({r["day"] for r in clean}) == len(clean)
    agree = None
    if compare:
        key = lambda r: (r["day"], r.get("fault", ""))
        theirs = {key(r): r for r in compare["clean"] + compare["planted"]}
        shared = [r for r in clean + planted if key(r) in theirs]
        agree = (sum((r["verdict"], r["confirmed"]) == (theirs[key(r)]["verdict"], theirs[key(r)]["confirmed"])
                     for r in shared), len(shared), len(clean + planted))
    summary = ["## The extended range in short", "",
               f"* Range judged: **{meta['first_judged']} to {last}** ({len(clean)} real days, whole months only; the "
               f"35 days before are warm-up history). Months loaded: {', '.join(meta['months'])}; the report stops at "
               f"the last month whose last day was judged.",
               f"* Trips in the range {meta['start']} to {last}: {rep['trips']:,}.",
               f"* Gate runs: {len(clean) + len(planted)} ({len(clean)} real days, {len(planted)} with a planted fault).",
               f"* Real days held: **{held}**; published: {published}, of which flagged as a real change with no fault "
               f"found: {real_change}.",
               f"* Gate run, end to end: median {statistics.median(ms):,.0f} ms, max {ms[-1]:,.0f} ms.",
               "* Same verdict and causes as the DuckDB stand-in: " +
               (f"**{agree[0]} of {agree[1]}** gate runs compared" + ("" if agree[1] == agree[2] else
                f" (the stand-in run covered {agree[1]} of the {agree[2]} gate runs)") if agree else
                "not compared; the stand-in was not run over this range."),
               "* The first 62 gate runs repeat the January to March range of the main backtest; days in that range can "
               "differ slightly from it, because later monthly files contain a few trips with earlier pickup dates.",
               ""]
    assert covered
    i = md.index("## Real days, no faults planted")
    md = md[:i] + "\n".join(summary) + "\n" + md[i:]
    md = md.replace("# Real-data backtest", "# Real-data backtest, extended range", 1)
    import re
    md = re.sub(r"Reproduce: .*", f"Reproduce: `{cmd}` (downloads about 50 to 80 MB per month into `data/real/`).", md, count=1)
    out = ROOT / "samples" / ("exasol" if backend == "exasol" else "") / "real_backtest_extended.md"
    out.with_suffix(".json").write_text(json.dumps(rep | {"summary": {
        "range": [meta["first_judged"], last.isoformat()], "real_days": len(clean), "gate_runs": len(clean + planted),
        "held": held, "published": published, "real_change": real_change, "median_ms": round(statistics.median(ms)),
        "max_ms": round(ms[-1]), "standin_agree": agree}}, indent=2, default=str), encoding="utf-8")
    out.write_text(md, encoding="utf-8")
    print(f"report: {out} ({meta['first_judged']} to {last}, {len(clean)} real days, {held} held)")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="exasol", choices=("exasol", "duckdb"))
    ap.add_argument("--until", default="2024-12", help="last month to load, YYYY-MM")
    ap.add_argument("--stop-at", help="local time to stop judging, YYYY-MM-DD HH:MM")
    ap.add_argument("--report", action="store_true", help="only rebuild the report from the saved days")
    a = ap.parse_args()
    rows_file = DATA / f"extended_{a.backend}.jsonl"
    if not a.report:
        stop = datetime.fromisoformat(a.stop_at) if a.stop_at else datetime.max
        log = lambda m: print(f"{datetime.now():%H:%M:%S} {m}", flush=True)
        run(a.backend, months_from("2024-01", a.until), stop, rows_file, log)
    exa = DATA / "extended_exasol.jsonl"
    if exa.exists() and exa.with_suffix(".meta.json").exists():
        report("exasol", exa, DATA / "extended_duckdb.jsonl")
    else:
        report(a.backend, rows_file, None)


if __name__ == "__main__":
    main()
