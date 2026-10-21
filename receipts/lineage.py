"""Column lineage read from the database's own catalog.

Receipts does not need an external data catalog. It reads the view definitions
of the pipeline from Exasol's SYS.EXA_ALL_VIEWS (or duckdb_views() in the
stand-in), parses them with sqlglot and walks backwards from the metric column
to the raw source columns.

Two kinds of influence are tracked:
  value   the column feeds the metric's expression (AMOUNT feeds REVENUE_INR)
  row     the column decides which rows exist or how they group (join keys,
          filters, group keys), like CAPTURED_AT deciding which day a sale is in
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import sqlglot
from sqlglot import exp

from .db import Backend


@dataclass
class ViewInfo:
    name: str
    sources: dict[str, str]                       # alias -> SCHEMA.TABLE
    columns: dict[str, set[tuple[str, str]]]      # output column -> {(SCHEMA.TABLE, COL)}
    row_refs: set[tuple[str, str]] = field(default_factory=set)
    sql: str = ""


def _qualified(t: exp.Table, schema_default: str) -> str:
    db = (t.db or schema_default).upper()
    return f"{db}.{t.name.upper()}"


def parse_view(name: str, sql: str, dialect: str, schema: str) -> ViewInfo:
    tree = sqlglot.parse_one(sql, read=dialect)
    sel = tree.find(exp.Select)
    sources: dict[str, str] = {}
    for t in sel.find_all(exp.Table):
        sources[(t.alias_or_name).upper()] = _qualified(t, schema)

    def refs(node) -> set[tuple[str, str]]:
        out = set()
        for col in node.find_all(exp.Column):
            alias = (col.table or "").upper()
            tbl = sources.get(alias) or (next(iter(sources.values())) if len(sources) == 1 else None)
            if tbl:
                out.add((tbl, col.name.upper()))
        return out

    columns = {}
    for e in sel.expressions:
        columns[e.alias_or_name.upper()] = refs(e)
    row_refs = set()
    # newer DuckDB prints joins nested in parentheses, so the ON conditions are not all in sel.args["joins"]
    for j in sel.find_all(exp.Join):
        row_refs |= refs(j)
    for key in ("joins", "where", "group", "having", "qualify"):
        v = sel.args.get(key)
        if v is None:
            continue
        for node in (v if isinstance(v, list) else [v]):
            row_refs |= refs(node)
    return ViewInfo(name, sources, columns, row_refs, sql)


@dataclass
class Lineage:
    metric: tuple[str, str]
    value_cols: set[tuple[str, str]]
    row_cols: set[tuple[str, str]]
    tables: set[str]
    edges: list[tuple[str, str]]
    views: dict[str, ViewInfo]
    ms: float

    def influences(self, table: str, column: str) -> str | None:
        k = (table.upper(), column.upper())
        if k in self.value_cols:
            return "value"
        if k in self.row_cols:
            return "row"
        return None

    def to_json(self) -> dict:
        raw = sorted(t for t in self.tables if t.startswith("RAW."))
        return {
            "metric": ".".join(self.metric),
            "edges": sorted(set(self.edges)),
            "raw_tables": raw,
            "value_columns": sorted(".".join(c) for c in self.value_cols if c[0].startswith("RAW.")),
            "row_columns": sorted(".".join(c) for c in self.row_cols - self.value_cols if c[0].startswith("RAW.")),
            "views_parsed": len(self.views),
            "ms": round(self.ms, 1),
        }


def build(be: Backend, schema: str = "PIPE", metric=("DAILY_REVENUE", "REVENUE_INR")) -> Lineage:
    t = time.perf_counter()
    defs = be.view_definitions(schema)
    views = {f"{schema}.{n}": parse_view(n, s, be.dialect.name, schema) for n, s in defs.items()}
    value, rows, tables, edges = set(), set(), set(), []
    seen_views = set()

    def walk(table: str, col: str, mode: str):
        key = (table, col)
        target = value if mode == "value" else rows
        if key in target:
            return
        target.add(key)
        tables.add(table)
        v = views.get(table)
        if not v:
            return
        if table not in seen_views:
            seen_views.add(table)
            for src in set(v.sources.values()):
                edges.append((src, table))
                tables.add(src)
            for (st, sc) in v.row_refs:
                walk(st, sc, "row")
        for (st, sc) in v.columns.get(col, set()):
            walk(st, sc, mode)

    m = (f"{schema}.{metric[0]}", metric[1])
    walk(m[0], m[1], "value")
    return Lineage(m, value, rows, tables, edges, views, (time.perf_counter() - t) * 1000)
