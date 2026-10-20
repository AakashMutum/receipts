"""The undo test: prove a cause by removing it.

For a suspected fault we build a sandbox schema holding the same pipeline, with
one source swapped for a corrected relation built from the detector's evidence.
Then we re-run the metric there. A real cause passes two checks:

  1. today's number comes back into the normal band (or moves materially
     toward it when several faults are tangled together), and
  2. history does not change, or changes back to exactly what was published.

Rebuilding a whole pipeline and re-aggregating it is the expensive part, and
it is cheap here because the views are re-planned and re-run in the database.
"""

from __future__ import annotations

import time
from datetime import date

from .db import Backend, to_date
from .detectors import Correction
from .load import PROD_SRC, create_pipeline
from .model import BASELINE_DAYS

SANDBOX = "RECEIPTS_SBX"


def build_sandbox(be: Backend, corrections: list[Correction], schema: str = SANDBOX) -> dict[str, str]:
    be.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
    be.execute(f"CREATE SCHEMA {schema}")
    src = dict(PROD_SRC)
    counter: dict[str, int] = {}
    for c in corrections:
        counter[c.source] = counter.get(c.source, 0) + 1
        name = f"{schema}.FIX_{c.source}_{counter[c.source]}"
        body = be.render_string(c.sql, inp=src[c.source])
        be.execute(f"CREATE OR REPLACE VIEW {name} AS\n{body}")
        src[c.source] = name
    create_pipeline(be, schema, src)
    return src


def series(be: Backend, schema: str, day: date, days_back: int = BASELINE_DAYS) -> dict[date, float]:
    D = be.dialect.day(day)
    rows = be.query(f"SELECT TXN_DAY, REVENUE_INR FROM {schema}.DAILY_REVENUE "
                    f"WHERE TXN_DAY >= {be.dialect.add_days(D, -days_back)} AND TXN_DAY <= {D} ORDER BY TXN_DAY")
    return {to_date(r["txn_day"]): r["revenue_inr"] for r in rows}


def history_check(fixed: dict, candidate: dict, published: dict, day: date, tol: float = 0.001) -> tuple[str, float]:
    days = [d for d in published if d < day]
    if not days:
        return "UNCHANGED", 0.0

    def maxdiff(a, b):
        return max(abs((a.get(d) or 0) - (b.get(d) or 0)) / max(abs(b.get(d) or 0), 1) for d in days)

    vs_cand = maxdiff(fixed, candidate)
    vs_pub = maxdiff(fixed, published)
    if vs_cand <= tol:
        return "UNCHANGED", vs_cand
    if vs_pub <= tol:
        return "RESTORED", vs_pub
    return "ALTERED", min(vs_cand, vs_pub)


def run_undo(be: Backend, day: date, corrections: list[Correction], candidate: dict, published: dict) -> dict:
    t = time.perf_counter()
    src = build_sandbox(be, corrections)
    fixed = series(be, SANDBOX, day)
    status, diff = history_check(fixed, candidate, published, day)
    return {
        "value": fixed.get(day, 0.0),
        "history_check": status,
        "history_max_diff_pct": round(diff * 100, 4),
        "series": {d.isoformat(): v for d, v in fixed.items()},
        "sources": {k: v for k, v in src.items() if v != PROD_SRC[k]},
        "ms": round((time.perf_counter() - t) * 1000, 1),
    }
