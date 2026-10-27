"""Which metrics the gate judges, from receipts.yaml.

A metric is a daily view in the database plus the raw tables behind it. The config names:

  view              the view that holds one row per day, for example PIPE.DAILY_REVENUE
  value_column      the number people read, for example REVENUE_INR
  day_column        the day column of that view (default TXN_DAY)
  raw_tables        the source tables the batch lands in
  amount, id, time  the amount, row ID and timestamp columns of the main raw table, as TABLE.COLUMN
  weekday_baseline  auto (use a weekly pattern when the history shows one), on, or off
  publish           true only for the metric the gate writes to PUB; others are judged and reported

`receipts connect --check` validates the file against the database. Pointing the gate at a new metric is an
edit to this file, not to the code. What is not covered: the six detectors are written for the payments layout
of the sample pipeline, and the slice breakdown runs on revenue.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .config import ROOT

CONFIG = ROOT / "receipts.yaml"
NUMERIC = ("DOUBLE", "DECIMAL", "INTEGER", "BIGINT", "HUGEINT", "FLOAT", "REAL", "NUMERIC", "SMALLINT", "TINYINT")
DATEISH = ("DATE", "TIMESTAMP")


@dataclass(frozen=True)
class Metric:
    name: str
    view: str
    value_column: str
    label: str = ""
    day_column: str = "TXN_DAY"
    raw_tables: tuple[str, ...] = ()
    amount: str = ""
    id: str = ""
    time: str = ""
    weekday_baseline: str = "auto"
    publish: bool = False
    extra: dict = field(default_factory=dict, compare=False, hash=False)

    @property
    def schema(self) -> str:
        return self.view.split(".")[0].upper()

    @property
    def view_name(self) -> str:
        return self.view.split(".")[-1].upper()


DEFAULT = Metric("daily_revenue_inr", "PIPE.DAILY_REVENUE", "REVENUE_INR", "Daily revenue (INR)",
                 raw_tables=("RAW.PAYMENTS", "RAW.ORDERS", "RAW.MERCHANTS", "RAW.CATEGORY_MAP", "RAW.FX_RATES"),
                 amount="RAW.PAYMENTS.AMOUNT", id="RAW.PAYMENTS.PAYMENT_ID", time="RAW.PAYMENTS.CAPTURED_AT",
                 publish=True)


class ConfigError(ValueError):
    pass


def load(path: Path | str | None = None) -> list[Metric]:
    import yaml
    p = Path(path or CONFIG)
    if not p.exists():
        return [DEFAULT]
    try:
        doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        raise ConfigError(f"{p.name} is not valid YAML: {e}")
    items = doc.get("metrics")
    if not isinstance(items, list) or not items:
        raise ConfigError(f"{p.name} needs a list under 'metrics:' with at least one metric.")
    out = []
    for i, m in enumerate(items, 1):
        if not isinstance(m, dict):
            raise ConfigError(f"metric {i} in {p.name} is not a mapping of names to values.")
        missing = [k for k in ("name", "view", "value_column") if not m.get(k)]
        if missing:
            raise ConfigError(f"metric {i} ({m.get('name', 'unnamed')}) is missing: {', '.join(missing)}.")
        wb = str(m.get("weekday_baseline", "auto")).lower()
        wb = {"true": "on", "false": "off"}.get(wb, wb)
        if wb not in ("auto", "on", "off"):
            raise ConfigError(f"metric {m['name']}: weekday_baseline must be auto, on or off, not {wb!r}.")
        known = {"name", "view", "value_column", "label", "day_column", "raw_tables", "amount", "id", "time",
                 "weekday_baseline", "publish"}
        out.append(Metric(str(m["name"]), str(m["view"]).upper(), str(m["value_column"]).upper(),
                          str(m.get("label") or m["name"]), str(m.get("day_column", "TXN_DAY")).upper(),
                          tuple(str(t).upper() for t in m.get("raw_tables") or ()), str(m.get("amount", "")).upper(),
                          str(m.get("id", "")).upper(), str(m.get("time", "")).upper(), wb, bool(m.get("publish")),
                          {k: v for k, v in m.items() if k not in known}))
    names = [m.name for m in out]
    if len(set(names)) != len(names):
        raise ConfigError(f"metric names must be unique: {', '.join(names)}.")
    if sum(m.publish for m in out) > 1:
        raise ConfigError("only one metric can have publish: true (the one the gate writes to PUB).")
    if any(m.publish and m.name != DEFAULT.name for m in out):
        raise ConfigError(f"publish: true is supported for {DEFAULT.name} only; other metrics are judged and reported.")
    return out


def _columns(be, table: str) -> dict[str, str] | None:
    """Column name -> type of a table or view, or None when it does not exist."""
    s, t = table.split(".") if "." in table else ("", table)
    if be.name == "exasol" and not be.is_standin:
        rows = be.query(f"SELECT COLUMN_NAME, COLUMN_TYPE FROM SYS.EXA_ALL_COLUMNS WHERE COLUMN_SCHEMA = '{s}' "
                        f"AND COLUMN_TABLE = '{t}'")
        cols = {r["column_name"].upper(): str(r["column_type"]).upper() for r in rows}
    else:
        rows = be.query(f"SELECT column_name, data_type FROM duckdb_columns() WHERE upper(schema_name) = '{s}' "
                        f"AND upper(table_name) = '{t}'")
        cols = {r["column_name"].upper(): str(r["data_type"]).upper() for r in rows}
    return cols or None


def check(be, metrics: list[Metric]) -> list[tuple[bool, str]]:
    """Plain-English checks of every metric against the database: tables exist, columns exist, types fit."""
    out: list[tuple[bool, str]] = []
    for m in metrics:
        p = f"{m.name}:"
        if m.view.count(".") != 1:
            out.append((False, f"{p} view should be written as SCHEMA.VIEW, got {m.view!r}."))
            continue
        cols = _columns(be, m.view)
        if cols is None:
            out.append((False, f"{p} the view {m.view} does not exist in the database. Run receipts init, or fix the name."))
            continue
        out.append((True, f"{p} view {m.view} exists ({len(cols)} columns)."))
        for role, col, kinds in (("value", m.value_column, NUMERIC), ("day", m.day_column, DATEISH)):
            t = cols.get(col)
            if t is None:
                out.append((False, f"{p} the {role} column {col} is not in {m.view}. It has: {', '.join(sorted(cols))}."))
            elif not t.startswith(kinds):
                out.append((False, f"{p} the {role} column {m.view}.{col} is {t}; a {role} column should be "
                                   f"{'a number' if role == 'value' else 'a date'}."))
            else:
                out.append((True, f"{p} {role} column {col} is {t}."))
        raw: dict[str, dict | None] = {}
        for t in m.raw_tables:
            raw[t] = _columns(be, t)
            out.append((raw[t] is not None, f"{p} raw table {t} " + ("exists." if raw[t] is not None else
                                                                    "does not exist. Check the schema and name.")))
        for role, ref, kinds in (("amount", m.amount, NUMERIC), ("id", m.id, None), ("time", m.time, DATEISH)):
            if not ref:
                out.append((True, f"{p} no {role} column named (optional)."))
                continue
            if ref.count(".") != 2:
                out.append((False, f"{p} {role} should be written as SCHEMA.TABLE.COLUMN, got {ref!r}."))
                continue
            tbl, col = ref.rsplit(".", 1)
            cols_t = raw.get(tbl) if tbl in raw else _columns(be, tbl)
            if cols_t is None:
                out.append((False, f"{p} the {role} column {ref} is in a table that does not exist."))
            elif col not in cols_t:
                out.append((False, f"{p} the {role} column {col} is not in {tbl}."))
            elif kinds and not cols_t[col].startswith(kinds):
                out.append((False, f"{p} the {role} column {ref} is {cols_t[col]}; it should be "
                                   f"{'a number' if role == 'amount' else 'a date or timestamp'}."))
            else:
                out.append((True, f"{p} {role} column {ref} is {cols_t[col]}."))
    return out
