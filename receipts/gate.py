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
from . import explain, lineage
from .db import Backend, to_date
from .dialect import lit
from .load import PROD_SRC, udf_status
from .model import BASELINE_DAYS, METRIC_LABEL, METRIC_NAME
from .undo import run_undo

MATERIAL = 0.015      # an undo must move today's number by at least 1.5% to count
EXPLAIN_MIN = 0.25    # in a partial explanation a cause must explain at least a quarter of the move


class Timer:
    def __init__(self):
        self.steps = []
        self.t0 = time.perf_counter()

    def step(self, name, t, rows=None, detail=None):
        self.steps.append({"step": name, "ms": round((time.perf_counter() - t) * 1000, 1),
                           "rows": rows, "detail": detail})

    @property
    def total(self):
        return round((time.perf_counter() - self.t0) * 1000, 1)


def _published(be: Backend, day: date) -> dict[date, float]:
    D = be.dialect.day(day)
    rows = be.query(f"SELECT TXN_DAY, METRIC_VALUE FROM PUB.DAILY_REVENUE_PUBLISHED WHERE TXN_DAY < {D} "
                    f"AND TXN_DAY >= {be.dialect.add_days(D, -BASELINE_DAYS)} "
                    f"AND TRUST_STATUS IN ('TRUSTED', 'REAL_CHANGE', 'CORRECTED') ORDER BY TXN_DAY")
    return {to_date(r["txn_day"]): r["metric_value"] for r in rows}


def _candidate(be: Backend, day: date) -> tuple[dict, dict, dict]:
    D = be.dialect.day(day)
    rows = be.query(f"SELECT TXN_DAY, REVENUE_INR, TXN_COUNT FROM PIPE.DAILY_REVENUE "
                    f"WHERE TXN_DAY >= {be.dialect.add_days(D, -BASELINE_DAYS)} ORDER BY TXN_DAY")
    vals = {to_date(r["txn_day"]): r["revenue_inr"] for r in rows if to_date(r["txn_day"]) <= day}
    counts = {to_date(r["txn_day"]): r["txn_count"] for r in rows if to_date(r["txn_day"]) <= day}
    spill = {to_date(r["txn_day"]): r["revenue_inr"] for r in rows if to_date(r["txn_day"]) > day}
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


def run(be: Backend, day: date, scenario: dict | None = None, write_back: bool = True) -> dict:
    tm = Timer()
    be.log.clear()
    case_id = f"RC-{day:%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"

    # 0. the number and its history ----------------------------------------------------
    t = time.perf_counter()
    published = _published(be, day)
    cand_series, counts, spill = _candidate(be, day)
    A = cand_series.get(day, 0.0)
    hist = [published[d] for d in sorted(published)]
    B = statistics.mean(hist)
    sd = statistics.pstdev(hist) if len(hist) > 1 else 0.0
    band = max(3 * sd, 0.04 * B)
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
    lin = lineage.build(be)
    tm.step("Read lineage from view definitions", t, rows=len(lin.views))

    # 3. decomposition: every slice in one CUBE pass ----------------------------------------------
    t = time.perf_counter()
    dec = decomp.decompose(be, day)
    tm.step(f"Test {dec['hypotheses']:,} slices in one GROUP BY CUBE", t, rows=dec["rows_in_scope"])

    # 4. volume and reconciliation checks ------------------------------------------------------
    t = time.perf_counter()
    recon = _reconciliation(be, day)
    base_cnt = statistics.mean(counts[d] for d in counts if d < day) if len(counts) > 1 else 1
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
                           "detail": (f"{infl} lineage to {METRIC_NAME}" if infl else
                                      f"{f.blamed_table} feeds the metric's rows") if r2 else "not in lineage"})
        u = run_undo(be, day, [f.correction], cand_series, published) if f.correction else None
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
                                                             cand_series, published)
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

    # where to look when unexplained: the most concentrated single slice
    where = None
    if dec["top_single"]:
        top = dec["top_single"][0]
        dname, dval = next(iter(top["dims"].items()))
        where = f"{dname.lower().replace('_', ' ')} {dval} carries {top['share']:.0%} of the change"

    case = {
        "case_id": case_id,
        "metric": METRIC_NAME,
        "metric_label": METRIC_LABEL,
        "day": day.isoformat(),
        "day_label": f"{day:%a %d %b %Y}",
        "opened_at": datetime.now().isoformat(timespec="seconds"),
        "scenario": scenario,
        "verdict": verdict,
        "trust_status": trust,
        "anomaly": anomaly,
        "values": {
            "candidate": A, "baseline": B, "sd": sd, "band_low": B - band, "band_high": B + band,
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
    if write_back:
        t = time.perf_counter()
        write(be, case)
        case["timings"].append({"step": "Write receipts back to the database", "ms": round((time.perf_counter() - t) * 1000, 1),
                                "rows": None, "detail": None})
        case["total_ms"] = tm.total
        # keep the stored JSON complete, including the write-back step
        be.execute(f"UPDATE RECEIPTS.CASES SET CASE_JSON = {lit(json.dumps(case, default=str))}, "
                   f"ELAPSED_MS = {case['total_ms']} WHERE CASE_ID = {lit(case_id)}")
    return case


def write(be: Backend, case: dict) -> None:
    D = date.fromisoformat(case["day"])
    v = case["values"]
    sc = (case.get("scenario") or {}).get("id")
    be.execute(f"""INSERT INTO RECEIPTS.CASES VALUES ({lit(case['case_id'])}, {lit(case['metric'])}, {lit(D)},
        CURRENT_TIMESTAMP, {lit(case['verdict'])}, {lit(v['candidate'])}, {lit(v['baseline'])},
        {lit(v['corrected'])}, {lit(sc)}, {lit(case['total_ms'])}, {lit(case['explanation']['text'][:2000])},
        {lit(json.dumps(case, default=str))})""")
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
