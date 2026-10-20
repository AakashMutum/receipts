"""SQL dialect helpers.

All SQL in Receipts is written once as Jinja templates. The few functions that
differ between Exasol and the local DuckDB stand-in are expressed as macros, so
the statements that run in Exasol are the same statements we test locally,
apart from these small spellings.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

SQL_DIR = Path(__file__).resolve().parent / "sql"


class Dialect:
    def __init__(self, name: str):
        if name not in ("exasol", "duckdb"):
            raise ValueError(f"unknown dialect {name}")
        self.name = name

    # date and time arithmetic -------------------------------------------
    def add_minutes(self, expr: str, minutes) -> str:
        if self.name == "exasol":
            return f"ADD_MINUTES({expr}, {minutes})"
        return f"({expr} + to_minutes(CAST({minutes} AS BIGINT)))"

    def add_days(self, expr: str, days) -> str:
        if self.name == "exasol":
            return f"ADD_DAYS({expr}, {days})"
        return f"CAST({expr} + CAST({days} AS INTEGER) AS DATE)"

    def from_dual(self) -> str:
        return " FROM DUAL" if self.name == "exasol" else ""

    def day(self, d: date | str) -> str:
        return f"DATE '{d}'"

    def half_hour_bin(self, expr: str) -> str:
        # 0..47, the half-hour of the day
        return f"CAST(EXTRACT(HOUR FROM {expr}) * 2 + FLOOR(EXTRACT(MINUTE FROM {expr}) / 30) AS INTEGER)"

    def env(self) -> Environment:
        env = Environment(loader=FileSystemLoader(str(SQL_DIR)), undefined=StrictUndefined,
                          trim_blocks=True, lstrip_blocks=True)
        env.globals.update(
            add_minutes=self.add_minutes,
            add_days=self.add_days,
            day=self.day,
            half_hour_bin=self.half_hour_bin,
            dialect=self.name,
        )
        return env

    def render(self, template: str, **ctx) -> str:
        return self.env().get_template(template).render(**ctx)

    def render_string(self, text: str, **ctx) -> str:
        return self.env().from_string(text).render(**ctx)


def split_statements(sql: str) -> list[str]:
    """Split a rendered script on lines that hold a single semicolon terminator.

    Templates end every statement with ';' at the end of a line. We do not split
    inside string literals because none of our templates put ';' inside one.
    """
    out, buf = [], []
    for line in sql.splitlines():
        buf.append(line)
        if line.rstrip().endswith(";"):
            stmt = "\n".join(buf).strip().rstrip(";").strip()
            if stmt and not all(l.strip().startswith("--") or not l.strip() for l in stmt.splitlines()):
                out.append(stmt)
            buf = []
    rest = "\n".join(buf).strip()
    if rest and not all(l.strip().startswith("--") or not l.strip() for l in rest.splitlines()):
        out.append(rest)
    return out


def lit(v) -> str:
    """Render a Python value as a SQL literal. Used for small write-backs only."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int,)):
        return str(v)
    if isinstance(v, float):
        if v != v:  # NaN
            return "NULL"
        return repr(float(v))
    if isinstance(v, datetime):
        return f"TIMESTAMP '{v.strftime('%Y-%m-%d %H:%M:%S')}'"
    if isinstance(v, date):
        return f"DATE '{v.isoformat()}'"
    s = str(v).replace("'", "''")
    return f"'{s}'"
