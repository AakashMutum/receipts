"""The gate: Receipts' three layers in one call.

  1. Gate (prevent)     check the incoming batch before anyone sees the number
  2. Investigate (prove) decompose, trace lineage, nominate suspects, undo them,
                         and let the evidence gate decide which are true
  3. Explain            restate the verdict in plain words (template or LLM)

Then write everything back into Exasol: the case, every piece of evidence, the
timings, and the published value that dashboards and agents read.
"""

from __future__ import annotations

import difflib
import json
import statistics
import time
import uuid
from datetime import date, datetime, timedelta
from itertools import combinations

from . import decompose as decomp
from . import detectors as det
from . import blast, explain, lineage
from .db import Backend, to_date
from .dialect import lit
from .load import PROD_SRC, udf_status
from .metrics import DEFAULT, Metric
from .model import BASELINE_DAYS, METRIC_LABEL, METRIC_NAME
from .undo import run_undo

MATERIAL = 0.015      # an undo must move today's number by at least 1.5% to count
EXPLAIN_MIN = 0.25    # in a partial explanation a cause must explain at least a quarter of the move


class Timer:
    def __init__(self, on_step=None, marker=None):
        self.steps = []
        self.t0 = time.perf_counter()
        self.on_step = on_step
        self.marker = marker or (lambda: None)
        self.marks = [self.marker()]  # database statement ids between steps, for Exasol's own timings

    def step(self, name, t, rows=None, detail=None):
        self.steps.append({"step": name, "ms": round((time.perf_counter() - t) * 1000, 1),
                           "rows": rows, "detail": detail})
        self.marks.append(self.marker())
        if self.on_step:  # the lab's live timeline shows each step as it finishes
            self.on_step(self.steps[-1])

    @property
    def total(self):
        return round((time.perf_counter() - self.t0) * 1000, 1)


SEASON_DAYS = 35   # five weeks of trusted history, so every weekday is seen five times
SEASON_MIN = 21    # with less history than this, fall back to the plain 14-day baseline


def _view_history(be: Backend, day: date, m: Metric, days: int) -> dict[date, float]:
    """Earlier days of a metric that is judged but not published: its own view is taken as trusted history."""
    D = be.dialect.day(day)
    rows = be.query(f"SELECT {m.day_column} AS TXN_DAY, {m.value_column} AS METRIC_VALUE FROM {m.view} "
                    f"WHERE {m.day_column} < {D} AND {m.day_column} >= {be.dialect.add_days(D, -days)} "
                    f"ORDER BY {m.day_column}")
    return {to_date(r["txn_day"]): r["metric_value"] for r in rows}


def _history(be: Backend, day: date, days: int = SEASON_DAYS, m: Metric = DEFAULT) -> dict[date, float]:
    if not m.publish:
        return _view_history(be, day, m, days)
    D = be.dialect.day(day)
    rows = be.query(f"SELECT TXN_DAY, METRIC_VALUE FROM PUB.DAILY_REVENUE_PUBLISHED WHERE TXN_DAY < {D} "
                    f"AND TXN_DAY >= {be.dialect.add_days(D, -days)} "
                    f"AND TRUST_STATUS IN ('TRUSTED', 'REAL_CHANGE', 'CORRECTED') ORDER BY TXN_DAY")
    return {to_date(r["txn_day"]): r["metric_value"] for r in rows}


def _counts(be: Backend, day: date, days: int = SEASON_DAYS) -> dict[date, float]:
    D = be.dialect.day(day)
    rows = be.query(f"SELECT TXN_DAY, TXN_COUNT FROM PIPE.DAILY_REVENUE WHERE TXN_DAY < {D} "
                    f"AND TXN_DAY >= {be.dialect.add_days(D, -days)} ORDER BY TXN_DAY")
    return {to_date(r["txn_day"]): r["txn_count"] for r in rows}


def _weekly_pattern(by_wd: dict[int, list[float]]) -> bool:
    """One-way ANOVA: do the weekday means differ by more than day-to-day noise explains?

    Without this test, a flat series would still get noisy weekday indices from five samples each,
    and the expected value would wobble for no reason. F above 3.5 is roughly a 1 percent chance
    of seeing such a pattern in noise.
    """
    groups = list(by_wd.values())
    n = sum(len(g) for g in groups)
    grand = sum(sum(g) for g in groups) / n
    ssb = sum(len(g) * (statistics.mean(g) - grand) ** 2 for g in groups)
    ssw = sum(sum((x - statistics.mean(g)) ** 2 for x in g) for g in groups)
    dfw = n - len(groups)
    if ssw <= 0:
        return ssb > 0
    return (ssb / (len(groups) - 1)) / (ssw / dfw) > 3.5


def expected(hist: dict[date, float], day: date, weekday: str = "auto") -> tuple[float, float, bool]:
    """What this metric should be on `day`, the spread around it, and whether the weekday was used.

    Real business numbers have a weekly shape. With five weeks of trusted history we learn each
    weekday's index (its mean over the overall mean), remove it from the history, and put it back
    for `day`. The band then measures noise around the weekly shape, not the weekly shape itself.
    With less history, or too few of some weekday, we use the plain mean of the last 14 days.
    """
    days = sorted(hist)
    vals = [hist[d] for d in days]
    by_wd: dict[int, list[float]] = {}
    overall = statistics.mean(vals) if vals else 0.0
    if len(days) >= SEASON_MIN and overall:
        for d in days:
            by_wd.setdefault(d.weekday(), []).append(hist[d] / overall)
    if (weekday != "off" and len(by_wd) == 7 and all(len(x) >= 3 for x in by_wd.values())
            and (weekday == "on" or _weekly_pattern(by_wd))):
        idx = {w: statistics.mean(x) for w, x in by_wd.items()}
        flat = [hist[d] / idx[d.weekday()] for d in days]
        level = statistics.mean(flat)
        sd = statistics.pstdev(flat) * idx[day.weekday()]
        return level * idx[day.weekday()], sd, True
    recent = vals[-BASELINE_DAYS:]
    return (statistics.mean(recent) if recent else 0.0,
            statistics.pstdev(recent) if len(recent) > 1 else 0.0, False)


def _published(be: Backend, day: date, m: Metric = DEFAULT) -> dict[date, float]:
    if not m.publish:
        return _view_history(be, day, m, BASELINE_DAYS)
    D = be.dialect.day(day)
    rows = be.query(f"SELECT TXN_DAY, METRIC_VALUE FROM PUB.DAILY_REVENUE_PUBLISHED WHERE TXN_DAY < {D} "
                    f"AND TXN_DAY >= {be.dialect.add_days(D, -BASELINE_DAYS)} "
                    f"AND TRUST_STATUS IN ('TRUSTED', 'REAL_CHANGE', 'CORRECTED') ORDER BY TXN_DAY")
    return {to_date(r["txn_day"]): r["metric_value"] for r in rows}


def _candidate(be: Backend, day: date, m: Metric = DEFAULT) -> tuple[dict, dict, dict]:
    D = be.dialect.day(day)
    rows = be.query(f"SELECT TXN_DAY, REVENUE_INR, TXN_COUNT FROM PIPE.DAILY_REVENUE "
                    f"WHERE TXN_DAY >= {be.dialect.add_days(D, -BASELINE_DAYS)} ORDER BY TXN_DAY")
    if (m.view, m.value_column) != (DEFAULT.view, DEFAULT.value_column):
        mv = {to_date(r["d"]): r["v"] for r in be.query(
            f"SELECT {m.day_column} AS D, {m.value_column} AS V FROM {m.view} "
            f"WHERE {m.day_column} >= {be.dialect.add_days(D, -BASELINE_DAYS)}")}
    else:
        mv = {to_date(r["txn_day"]): r["revenue_inr"] for r in rows}
    vals = {d: v for d, v in sorted(mv.items()) if d <= day}
    counts = {to_date(r["txn_day"]): r["txn_count"] for r in rows if to_date(r["txn_day"]) <= day}
    spill = {d: v for d, v in sorted(mv.items()) if d > day}
    return vals, counts, spill


def _reconciliation(be: Backend, day: date) -> dict:
    D = be.dialect.day(day)
    sql = f"""SELECT r.BATCH_DAY, r.RAW_PAYMENTS, d.TXN_COUNT
FROM (SELECT BATCH_DAY, COUNT(DISTINCT PAYMENT_ID) AS RAW_PAYMENTS FROM RAW.PAYMENTS
      WHERE PAY_STATUS = 'CAPTURED' AND BATCH_DAY >= {be.dialect.add_days(D, -BASELINE_DAYS)} AND BATCH_DAY <= {D}
      GROUP BY BATCH_DAY) r
LEFT JOIN PIPE.DAILY_REVENUE d ON d.TXN_DAY = r.BATCH_DAY
ORDER BY r.BATCH_DAY"""
    rows, ms = be.timed_query(sql)
    ratios = {to_date(r["batch_day"]): (r["txn_count"] or 0) / max(r["raw_payments"], 1) for r in rows}
    today = ratios.pop(day, 0.0)
    base = statistics.mean(ratios.values()) if ratios else 1.0
    return {"ratio_today": round(today, 4), "ratio_baseline": round(base, 4),
            "ok": abs(today - base) <= 0.005, "sql": sql, "ms": round(ms, 1)}


def _slice_text(s: dict) -> str:
    return ", ".join(f"{k.lower().replace('_', ' ')} {v}" for k, v in s.items()) or "whole batch"


def _fix_diff(be: Backend, corrections: list) -> str:
    if not corrections:
        return ""
    prod = be.render("pipeline.sql", schema="PIPE", src=PROD_SRC)
    src = dict(PROD_SRC)
    for c in corrections:
        body = be.render_string(c.sql, inp=src[c.source])
        src[c.source] = "(\n" + "\n".join("  " + l for l in body.splitlines()) + "\n)"
    fixed = be.render("pipeline.sql", schema="PIPE", src=src)
    return "".join(difflib.unified_diff(prod.splitlines(True), fixed.splitlines(True),
                                        "pipeline.sql (production)", "pipeline.sql (proven by the undo test)", n=2))


def run(be: Backend, day: date, scenario: dict | None = None, write_back: bool = True, on_step=None,
        metric: Metric | None = None) -> dict:
    m = metric or DEFAULT
    write_back = write_back and m.publish  # only the published metric is written to PUB
    tm = Timer(on_step, be.server_marker)
    be.log.clear()
    case_id = f"RC-{day:%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"

    # 0. the number and its history ----------------------------------------------------
    t = time.perf_counter()
    published = _published(be, day, m)
    cand_series, counts, spill = _candidate(be, day, m)
    A = cand_series.get(day, 0.0)
    hist_long = _history(be, day, m=m)
    B, sd, seasonal = expected(hist_long, day, m.weekday_baseline)
    band = max(3 * sd, 0.04 * B)
    hist = list(hist_long.values())
    anomaly = abs(A - B) > band
    chg = (A - B) / B if B else 0.0
    tm.step("Read candidate and trusted history", t, rows=len(hist) + 1)

    def in_band(v):
        return abs(v - B) <= band

    # 1. gate: detectors on the raw incoming batch ------------------------------------------
    t = time.perf_counter()
    udf_mode = udf_status(be)["udf"]
    findings = det.run_all(be, day, udf_mode)
    tm.step("Run six detectors on the incoming batch", t, detail=f"clock check: {findings[4].engine}")

    # 2. lineage from the catalog -----------------------------------------------------------
    t = time.perf_counter()
    lin = lineage.build(be, m.schema, (m.view_name, m.value_column))
    all_views = blast.read_views(be)
    tm.step("Read lineage from view definitions", t, rows=len(all_views))

    # 3. decomposition: every slice in one CUBE pass ----------------------------------------------
    t = time.perf_counter()
    dec = decomp.decompose(be, day)
    tm.step(f"Test {dec['hypotheses']:,} slices in one GROUP BY CUBE", t, rows=dec["rows_in_scope"])

    # 4. volume and reconciliation checks ------------------------------------------------------
    t = time.perf_counter()
    recon = _reconciliation(be, day)
    prior_counts = _counts(be, day)
    base_cnt = expected(prior_counts, day)[0] if len(prior_counts) > 1 else 1
    vol_ratio = counts.get(day, 0) / base_cnt if base_cnt else 0
    val_ratio = A / B if B else 0
    ticket_ratio = val_ratio / vol_ratio if vol_ratio else 0
    volume = {"volume_ratio": round(vol_ratio, 4), "value_ratio": round(val_ratio, 4),
              "ticket_ratio": round(ticket_ratio, 4), "ok": abs(ticket_ratio - 1) <= 0.06}
    tm.step("Reconcile raw payments to revenue rows", t)

    # 5. undo test for every suspect ----------------------------------------------------------
    t = time.perf_counter()
    suspects = []
    for f in findings:
        s = {"id": f.id, "title": f.title, "fired": f.fired, "summary": f.summary, "engine": f.engine,
             "blamed": {"table": f.blamed_table, "column": f.blamed_column}, "level": f.level,
             "slice": f.slice, "slice_text": _slice_text(f.slice), "metrics": f.metrics, "sql": f.sql,
             "ms": round(f.ms, 1), "outcome": "NOT_FIRED", "rules": [], "undo": None, "reason": "",
             "correction_note": f.correction.note if f.correction else ""}
        suspects.append(s)
        if not f.fired:
            continue
        r1 = bool(f.blamed_table and f.blamed_column and f.slice)
        infl = lin.influences(f.blamed_table, f.blamed_column)
        r2 = infl is not None or (f.level == "row" and f.blamed_table in lin.tables)
        s["rules"].append({"rule": "Evidence names a column and a slice", "passed": r1,
                           "detail": f"{f.blamed_table}.{f.blamed_column}, {s['slice_text']}"})
        s["rules"].append({"rule": "That column feeds this metric", "passed": r2,
                           "detail": (f"{infl} lineage to {m.name}" if infl else
                                      f"{f.blamed_table} feeds the metric's rows") if r2 else "not in lineage"})
        u = run_undo(be, day, [f.correction], cand_series, published, m) if f.correction else None
        s["undo"] = u
        move = (u["value"] - A) / A if (u and A) else 0.0
        r3 = abs(move) >= MATERIAL
        r4 = bool(u) and u["history_check"] in ("UNCHANGED", "RESTORED")
        s["move_pct"] = move
        s["rules"].append({"rule": "Undoing it moves today's number", "passed": r3,
                           "detail": f"{move:+.2%} when undone in the sandbox"})
        s["rules"].append({"rule": "History stays as published", "passed": r4,
                           "detail": (u["history_check"].lower() + f", max difference {u['history_max_diff_pct']:.3f}%")
                           if u else "no correction"})
        s["eligible"] = r1 and r2 and r3 and r4
        if not s["eligible"]:
            s["outcome"] = "REJECTED"
            if not r3:
                s["reason"] = (f"Undoing it changes today's revenue by {move:+.2%}, so it cannot explain a "
                               f"{chg:+.1%} move.")
            elif not r4:
                s["reason"] = "Undoing it would rewrite history that was already published and trusted."
            else:
                s["reason"] = "The evidence does not point at anything this metric depends on."
    tm.step("Undo each suspect in a sandbox schema", t, rows=sum(1 for s in suspects if s["undo"]))

    # 6. evidence gate: which combination of suspects brings the number back? ---------------------
    t = time.perf_counter()
    eligible = [s for s in suspects if s.get("eligible")]
    corr = {f.id: f.correction for f in findings}
    chosen, combined = [], None
    tried = 0
    if eligible:
        pool = eligible[:4]
        best = None
        for k in range(len(pool), 0, -1):
            for combo in combinations(pool, k):
                tried += 1
                u = combo[0]["undo"] if k == 1 else run_undo(be, day, [corr[c["id"]] for c in combo],
                                                             cand_series, published, m)
                ok = in_band(u["value"]) and u["history_check"] in ("UNCHANGED", "RESTORED")
                if ok and (best is None or abs(u["value"] - B) < abs(best[1]["value"] - B)):
                    best = (combo, u)
            if best:
                break
        if best:
            chosen, combined = list(best[0]), best[1]
    tm.step("Evidence gate: find the causes that bring it back", t, rows=tried)

    chosen_ids = {c["id"] for c in chosen}
    for s in eligible:
        if s["id"] in chosen_ids:
            s["outcome"] = "CONFIRMED"
            s["reason"] = "Passes every rule, and undoing the confirmed causes together puts revenue back in range."
        else:
            s["outcome"] = "REJECTED"
            s["reason"] = "Real, but not needed to explain the change: the number comes back without it."

    if chosen:
        verdict = "PROVEN_FAULT"
    elif eligible and anomaly:
        verdict = "UNEXPLAINED"
        for s in eligible:
            frac = (A - s["undo"]["value"]) / (A - B) if A != B else 0
            if frac >= EXPLAIN_MIN:
                s["outcome"] = "PARTIAL"
                s["reason"] = f"Explains {frac:.0%} of the move on its own, but the rest is still unexplained."
    elif anomaly:
        verdict = "REAL_CHANGE" if (volume["ok"] and recon["ok"]) else "UNEXPLAINED"
    elif eligible:
        verdict = "UNEXPLAINED"
    else:
        verdict = "NO_INCIDENT"

    trust = {"NO_INCIDENT": "TRUSTED", "REAL_CHANGE": "REAL_CHANGE"}.get(verdict, "HELD")
    corrected = combined["value"] if combined else None
    last_trusted_day = max(published) if published else None

    # who could have read tonight's number before the gate decided
    blamed = {(s["blamed"]["table"], s["blamed"]["column"]) for s in suspects
              if s["outcome"] == "CONFIRMED" and s["blamed"]["table"] and s["blamed"]["column"]}
    radius = blast.radius(all_views, lin.metric, blamed, lin.tables)
    since = f"(SELECT MAX(PUBLISHED_AT) FROM PUB.DAILY_REVENUE_PUBLISHED WHERE TXN_DAY < {be.dialect.day(day)})"
    radius["reads"] = blast.reads_in_window(be, radius["exposed"], since)

    # where to look when unexplained: the most concentrated single slice
    where = None
    if dec["top_single"]:
        top = dec["top_single"][0]
        dname, dval = next(iter(top["dims"].items()))
        where = f"{dname.lower().replace('_', ' ')} {dval} carries {top['share']:.0%} of the change"

    case = {
        "case_id": case_id,
        "metric": m.name if metric else METRIC_NAME,
        "metric_label": (m.label or m.name) if metric else METRIC_LABEL,
        "day": day.isoformat(),
        "day_label": f"{day:%a %d %b %Y}",
        "opened_at": datetime.now().isoformat(timespec="seconds"),
        "scenario": scenario,
        "verdict": verdict,
        "trust_status": trust,
        "anomaly": anomaly,
        "values": {
            "candidate": A, "baseline": B, "seasonal": seasonal, "sd": sd, "band_low": B - band, "band_high": B + band,
            "corrected": corrected, "change_pct": chg, "z": (A - B) / sd if sd else None,
            "last_trusted_value": published.get(last_trusted_day), "last_trusted_day":
                last_trusted_day.isoformat() if last_trusted_day else None,
        },
        "checks": {"volume": volume, "reconciliation": recon},
        "suspects": suspects,
        "confirmed": sorted(chosen_ids),
        "combined_undo": combined,
        "decomposition": dec,
        "where_text": where,
        "lineage": lin.to_json(),
        "blast_radius": radius,
        "series": {
            "published": {d.isoformat(): v for d, v in published.items()},
            "candidate": {d.isoformat(): v for d, v in cand_series.items()},
            "corrected": combined["series"] if combined else None,
        },
        "spill": {d.isoformat(): v for d, v in spill.items()},
        "fix_diff": _fix_diff(be, [corr[i] for i in [s["id"] for s in suspects] if i in chosen_ids]),
        "backend": be.describe() | {"udf": udf_mode},
        "statements": len(be.log),
        "db_ms": round(sum(e.ms for e in be.log), 1),
    }
    case["explanation"] = {"source": "template", "text": explain.template(case)}
    case["timings"] = tm.steps
    case["total_ms"] = tm.total
    if not write_back:
        case["exasol_measured"] = measured(be, tm)
    if write_back:
        t = time.perf_counter()
        write(be, case)
        tm.step("Write receipts back to the database", t)
        case["total_ms"] = tm.total
        case["exasol_measured"] = measured(be, tm)
        # keep the stored JSON complete, including the write-back step
        be.execute(f"UPDATE RECEIPTS.CASES SET CASE_JSON = {lit(json.dumps(case, default=str))}, "
                   f"ELAPSED_MS = {case['total_ms']} WHERE CASE_ID = {lit(case_id)}")
    return case


def measured(be: Backend, tm: Timer) -> dict:
    """What the database itself recorded for this gate run: per step, the time and peak memory of its statements.

    On Exasol this comes from EXA_STATISTICS.EXA_SQL_LAST_DAY after FLUSH STATISTICS. If the statistics
    cannot be read, the receipt says so and shows the client-side timing instead. On the stand-in: n/a.
    """
    if be.is_standin or tm.marks[0] is None:
        return {"source": "n/a", "note": "Only Exasol reports its own statement timings."}
    t = time.perf_counter()
    got = be.server_stats(tm.marks[0], tm.marks[-1])
    if not got:
        return {"source": "client", "note": "Exasol statistics were not readable, so these are client-side timings.",
                "db_ms": round(sum(s["ms"] for s in tm.steps), 1)}
    src, rows = got
    marks = {m for m in tm.marks if m is not None}
    # every statement autocommits, and the commit gets its own id: commits count as database time, not as
    # statements, and the commits of the marker reads themselves are left out
    by_id = {int(r["stmt_id"]): r for r in rows if int(r["stmt_id"]) not in marks
             and not (r["command_name"] == "COMMIT" and int(r["stmt_id"]) - 1 in marks)}

    def agg(rs):
        return {"statements": sum(r["command_name"] != "COMMIT" for r in rs),
                "db_ms": round(sum((r["duration"] or 0) * 1000 for r in rs), 1),
                "cpu_pct_max": max((r["cpu"] or 0 for r in rs), default=None),
                "temp_ram_peak_mib": max((r["temp_db_ram_peak"] or 0 for r in rs), default=None)}
    steps = []
    for st, a, b in zip(tm.steps, tm.marks, tm.marks[1:]):
        mine = [by_id[i] for i in range(a + 1, b) if i in by_id] if a is not None and b is not None else []
        steps.append({"step": st["step"]} | agg(mine))
    return {"source": src} | agg(list(by_id.values())) | {"steps": steps, "read_ms": round((time.perf_counter() - t) * 1000, 1)}


def write(be: Backend, case: dict) -> None:
    D = date.fromisoformat(case["day"])
    v = case["values"]
    sc = (case.get("scenario") or {}).get("id")
    be.execute(f"""INSERT INTO RECEIPTS.CASES VALUES ({lit(case['case_id'])}, {lit(case['metric'])}, {lit(D)},
        CURRENT_TIMESTAMP, {lit(case['verdict'])}, {lit(v['candidate'])}, {lit(v['baseline'])},
        {lit(v['corrected'])}, {lit(sc)}, {lit(case['total_ms'])}, {lit(case['explanation']['text'][:2000])},
        {lit(json.dumps(case, default=str))}, {lit(case['blast_radius']['count'])},
        {lit(', '.join(case['blast_radius']['exposed'])[:2000])})""")
    for s in case["suspects"]:
        u = s["undo"] or {}
        be.execute(f"""INSERT INTO RECEIPTS.EVIDENCE VALUES ({lit(case['case_id'])}, {lit(s['id'])}, {lit(s['fired'])},
            {lit(s['outcome'])}, {lit(s['blamed']['table'])}, {lit(s['blamed']['column'])}, {lit(s['slice_text'][:200])},
            {lit(u.get('value'))}, {lit(s.get('move_pct'))}, {lit(u.get('history_check'))}, {lit((s['reason'] or s['summary'])[:600])})""")
    if case["timings"]:
        vals = ",\n".join(f"({lit(case['case_id'])}, {lit(st['step'][:40])}, {lit(st['ms'])}, {lit(st['rows'])})"
                          for st in case["timings"])
        be.execute(f"INSERT INTO RECEIPTS.STEP_TIMINGS VALUES {vals}")
    be.execute(f"DELETE FROM PUB.DAILY_REVENUE_PUBLISHED WHERE TXN_DAY = {lit(D)}")
    be.execute(f"""INSERT INTO PUB.DAILY_REVENUE_PUBLISHED VALUES ({lit(D)}, {lit(v['candidate'])}, {lit(v['candidate'])},
        {lit(case['trust_status'])}, {lit(case['case_id'])}, CURRENT_TIMESTAMP)""")


def approve(be: Backend, case_id: str, note: str = "") -> dict:
    """A person approves the proven correction. Publishes the corrected value."""
    raw = be.scalar(f"SELECT CASE_JSON FROM RECEIPTS.CASES WHERE CASE_ID = {lit(case_id)}")
    if not raw:
        raise KeyError(case_id)
    case = json.loads(raw)
    if case["verdict"] != "PROVEN_FAULT" or case["values"]["corrected"] is None:
        raise ValueError("Only a proven fault with a tested correction can be approved.")
    D = date.fromisoformat(case["day"])
    val = case["values"]["corrected"]
    be.execute(f"INSERT INTO RECEIPTS.APPROVALS VALUES ({lit(case_id)}, CURRENT_TIMESTAMP, {lit(val)}, {lit(note[:400])})")
    be.execute(f"DELETE FROM PUB.DAILY_REVENUE_PUBLISHED WHERE TXN_DAY = {lit(D)}")
    be.execute(f"""INSERT INTO PUB.DAILY_REVENUE_PUBLISHED VALUES ({lit(D)}, {lit(val)}, {lit(case['values']['candidate'])},
        'CORRECTED', {lit(case_id)}, CURRENT_TIMESTAMP)""")
    case["trust_status"] = "CORRECTED"
    case["approved"] = {"value": val, "note": note, "at": datetime.now().isoformat(timespec="seconds")}
    be.execute(f"UPDATE RECEIPTS.CASES SET CASE_JSON = {lit(json.dumps(case, default=str))} WHERE CASE_ID = {lit(case_id)}")
    return case
