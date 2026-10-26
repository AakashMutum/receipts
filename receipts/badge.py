"""A trust badge for a README, a wiki or a dashboard header: is today's number safe to quote?

Read-only. It shows the metric name, the trust status of the latest day and the last trusted day, read from
PUB.METRIC_TRUST. No values and no raw data.
"""

from __future__ import annotations

from datetime import date
from html import escape

from .db import Backend, to_date
from .dialect import lit

COLORS = {"TRUSTED": "#2e7d32", "REAL_CHANGE": "#1565c0", "CORRECTED": "#00796b", "HELD": "#c62828"}
OK = ("TRUSTED", "REAL_CHANGE", "CORRECTED")


def latest(be: Backend, metric: str | None = None) -> dict | None:
    where = f"WHERE METRIC_NAME = {lit(metric)} " if metric else ""
    rows = be.query(f"SELECT METRIC_NAME, TXN_DAY, TRUST_STATUS, LAST_TRUSTED_DAY FROM PUB.METRIC_TRUST {where}"
                    f"ORDER BY TXN_DAY DESC LIMIT 1")
    if not rows:
        return None
    r = rows[0]
    day = to_date(r["txn_day"])
    last = day if r["trust_status"] in OK else (to_date(r["last_trusted_day"]) if r["last_trusted_day"] else None)
    return {"metric": r["metric_name"], "day": day, "status": r["trust_status"], "last_trusted": last}


def _w(text: str) -> int:
    return int(len(text) * 6.6) + 12


def svg(metric: str, status: str, last_trusted: date | None) -> str:
    right = f"{status.replace('_', ' ')} | last trusted {last_trusted.isoformat() if last_trusted else 'none'}"
    lw, rw = _w(metric), _w(right)
    color = COLORS.get(status, "#555")
    m, r = escape(metric), escape(right)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{lw + rw}" height="20" role="img" '
            f'aria-label="{m}: {r}"><title>{m}: {r}</title>'
            f'<rect width="{lw}" height="20" fill="#3b3b3b"/><rect x="{lw}" width="{rw}" height="20" fill="{color}"/>'
            f'<g fill="#fff" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11">'
            f'<text x="6" y="14">{m}</text><text x="{lw + 6}" y="14">{r}</text></g></svg>')


def unknown(metric: str) -> str:
    return svg(metric, "UNKNOWN", None).replace("UNKNOWN | last trusted none", "no data")
