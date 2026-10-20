"""Where did the change land? One GROUP BY CUBE pass inside the database.

Every combination of six dimensions is a hypothesis ("the change is in Mumbai",
"the change is in Electronics bought through GW_B"). One CUBE query computes
today's value and the baseline for all of them in a single scan, which is the
kind of wide, parallel aggregation Exasol is built for.
"""

from __future__ import annotations

from datetime import date
from itertools import combinations

from .db import Backend
from .model import BASELINE_DAYS, CUBE_DIMS

SQL = """SELECT
  GROUPING_ID({{ dims|join(', ') }}) AS GID,
  {% for d in dims %}f.{{ d }},
  {% endfor %}SUM(CASE WHEN f.TXN_DAY = {{ D }} THEN f.REVENUE_INR ELSE 0 END) AS CUR_VALUE,
  SUM(CASE WHEN f.TXN_DAY < {{ D }} THEN f.REVENUE_INR ELSE 0 END) / {{ n }} AS BASE_VALUE,
  COUNT(*) AS N_ROWS
FROM {{ schema }}.FCT_REVENUE f
WHERE f.TXN_DAY >= {{ B0 }} AND f.TXN_DAY <= {{ D }}
GROUP BY CUBE ({% for d in dims %}f.{{ d }}{{ ", " if not loop.last }}{% endfor %})"""


def sql_for(be: Backend, day: date, schema: str = "PIPE") -> str:
    D = be.dialect.day(day)
    return be.render_string(SQL, dims=CUBE_DIMS, D=D, B0=be.dialect.add_days(D, -BASELINE_DAYS),
                            n=BASELINE_DAYS, schema=schema)


def decompose(be: Backend, day: date, schema: str = "PIPE", top_n: int = 8) -> dict:
    sql = sql_for(be, day, schema)
    rows, ms = be.timed_query(sql)
    k = len(CUBE_DIMS)
    total = None
    cells = []
    for r in rows:
        gid = int(r["gid"])
        # bit i (from the left, most significant first) is 1 when dimension i is aggregated away
        present = [CUBE_DIMS[i] for i in range(k) if not (gid >> (k - 1 - i)) & 1]
        delta = (r["cur_value"] or 0) - (r["base_value"] or 0)
        cell = {"dims": {d: r[d.lower()] for d in present}, "cur": r["cur_value"] or 0,
                "base": r["base_value"] or 0, "delta": delta, "n_rows": r["n_rows"]}
        if not present:
            total = cell
        cells.append(cell)
    total_delta = total["delta"] if total else 0.0
    rows_in_scope = total["n_rows"] if total else 0

    def share(c):
        return c["delta"] / total_delta if total_delta else 0.0

    singles = [c for c in cells if len(c["dims"]) == 1]
    pairs = [c for c in cells if len(c["dims"]) == 2]
    for c in cells:
        c["share"] = share(c)
        c["pct_change"] = c["delta"] / c["base"] if c["base"] else None
    # rank: biggest absolute contribution; break ties toward the simpler explanation
    singles.sort(key=lambda c: -abs(c["delta"]))
    pairs.sort(key=lambda c: -abs(c["delta"]))

    # per dimension: how concentrated is the change? (best single value's share)
    by_dim = {}
    for d in CUBE_DIMS:
        vals = [c for c in singles if d in c["dims"]]
        if vals:
            best = max(vals, key=lambda c: abs(c["delta"]))
            by_dim[d] = {"value": best["dims"][d], "share": best["share"], "pct_change": best["pct_change"],
                         "values": sorted(({"value": v["dims"][d], "delta": v["delta"], "cur": v["cur"],
                                            "base": v["base"], "pct_change": v["pct_change"]} for v in vals),
                                          key=lambda x: -abs(x["delta"]))}
    return {
        "sql": sql,
        "ms": round(ms, 1),
        "hypotheses": len(rows),
        "grouping_sets": 2 ** k,
        "rows_in_scope": rows_in_scope,
        "total": {"cur": total["cur"] if total else 0, "base": total["base"] if total else 0, "delta": total_delta},
        "top_single": [_slim(c) for c in singles[:top_n]],
        "top_pairs": [_slim(c) for c in pairs[:top_n]],
        "by_dimension": by_dim,
    }


def _slim(c):
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in c.items()}


def pairs_count() -> int:
    return len(list(combinations(CUBE_DIMS, 2)))
