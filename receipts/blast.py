"""Blast radius: who could have seen tonight's number before the gate decided.

Lineage (receipts/lineage.py) walks backwards from the metric to the raw columns. This walks forwards,
over every view the database knows in PIPE, PUB and MART, from the metric column and from the columns a
confirmed cause blames. A view is downstream if one of its output columns, or the rows it keeps, depends
on an affected column. Two groups come out:

  exposed    views that read the pipeline directly, so they showed the candidate value
  protected  views that read what the gate publishes (PUB.DAILY_REVENUE_PUBLISHED), so they showed
             the last trusted value while the number was held

Views that build the metric itself are not listed: they are the pipeline, not its readers.

Optionally, on Exasol, the audit log says which sessions actually read an exposed view since the previous
publish. Other backends have no such log, and the receipt says so instead of guessing.
"""

from __future__ import annotations

from .db import Backend
from .lineage import ViewInfo, parse_view

SCHEMAS = ("PIPE", "PUB", "MART")
PUBLISHED = "PUB.DAILY_REVENUE_PUBLISHED"


def read_views(be: Backend, schemas=SCHEMAS) -> dict[str, ViewInfo]:
    out = {}
    for s in schemas:
        for n, sql in be.view_definitions(s).items():
            out[f"{s}.{n.upper()}"] = parse_view(n, sql, be.dialect.name, s)
    return out


def _star(v: ViewInfo) -> bool:
    return "*" in v.columns


def downstream(views: dict[str, ViewInfo], start: set[tuple[str, str]]) -> set[str]:
    """Every view with an output column or a row filter that depends on one of the start columns."""
    affected = {(t.upper(), c.upper()) for t, c in start}

    def hit(cols) -> bool:
        return any(k in affected or (k[0], "*") in affected for k in cols)

    changed = True
    while changed:
        changed = False
        for name, v in views.items():
            if _star(v):  # SELECT * passes every column of its sources through
                star_hit = any((t, "*") in affected or any(a[0] == t for a in affected) for t in v.sources.values())
                if star_hit and (name, "*") not in affected:
                    affected.add((name, "*"))
                    changed = True
            rows_hit = hit(v.row_refs)
            for col, refs in v.columns.items():
                if col == "*":
                    continue
                if (name, col) not in affected and (rows_hit or hit(refs)):
                    affected.add((name, col))
                    changed = True
    return {t for t, _ in affected if t in views}


def readers_of(views: dict[str, ViewInfo], table: str) -> set[str]:
    """Every view that reads `table`, directly or through other views (object level)."""
    found, todo = set(), {table.upper()}
    while todo:
        t = todo.pop()
        for name, v in views.items():
            if name not in found and t in v.sources.values():
                found.add(name)
                todo.add(name)
    return found


def radius(views: dict[str, ViewInfo], metric: tuple[str, str], blamed: set[tuple[str, str]],
           pipeline: set[str]) -> dict:
    exposed = downstream(views, {metric} | set(blamed)) - set(pipeline) - {metric[0]}
    protected = readers_of(views, PUBLISHED) - exposed
    return {"exposed": sorted(exposed), "protected": sorted(protected), "count": len(exposed),
            "views_read": len(views), "start": sorted(".".join(c) for c in {metric} | set(blamed))}


def audit_reads_sql(objects: list[str], since_sql: str) -> str:
    """Exasol: sessions other than this one that ran a SELECT naming an exposed view since `since_sql`."""
    like = " OR ".join(f"UPPER(a.SQL_TEXT) LIKE '%{o.upper()}%'" for o in objects)
    return (f"SELECT s.USER_NAME, s.CLIENT, MIN(a.START_TIME) AS FIRST_READ, COUNT(*) AS READS "
            f"FROM EXA_DBA_AUDIT_SQL a JOIN EXA_DBA_AUDIT_SESSIONS s ON s.SESSION_ID = a.SESSION_ID "
            f"WHERE a.COMMAND_NAME = 'SELECT' AND a.START_TIME >= {since_sql} "
            f"AND a.SESSION_ID <> CURRENT_SESSION AND ({like}) "
            f"GROUP BY s.USER_NAME, s.CLIENT ORDER BY FIRST_READ")


def reads_in_window(be: Backend, objects: list[str], since_sql: str) -> dict:
    """Who read an exposed view during the bad window, if the backend keeps a query log."""
    if be.is_standin:
        return {"available": False, "note": "not available on this backend (the stand-in keeps no query log)"}
    if not objects:
        return {"available": True, "readers": [], "note": "no exposed views to look for"}
    try:
        rows = be.query(audit_reads_sql(objects, since_sql))
    except Exception as e:
        return {"available": False, "note": f"Exasol audit log not readable ({str(e).splitlines()[0][:120]})"}
    return {"available": True, "readers": [{k: str(v) for k, v in r.items()} for r in rows],
            "note": "from EXA_DBA_AUDIT_SQL since the previous publish"}
