"""Database access for Exasol (the target) and DuckDB (a local stand-in).

Every query goes through `Backend.query` or `Backend.execute`, which time it and
keep a statement log. The log is what lets each piece of evidence in a case
carry the exact SQL that produced it, and how long it took inside the database.
"""

from __future__ import annotations

import decimal
import ssl
import threading
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from .config import Settings, settings
from .dialect import Dialect, split_statements


@dataclass
class Executed:
    sql: str
    ms: float
    rows: int


def _norm(v):
    if isinstance(v, decimal.Decimal):
        return float(v)
    return v


class Backend:
    name = "base"
    is_standin = False

    def __init__(self):
        self.dialect = Dialect(self.name)
        self.log: list[Executed] = []
        self._lock = threading.RLock()

    # implemented by subclasses ------------------------------------------
    def _execute(self, sql: str) -> tuple[list[str], list[tuple]] | None:
        raise NotImplementedError

    # public ---------------------------------------------------------------
    def execute(self, sql: str) -> None:
        with self._lock:
            t = time.perf_counter()
            self._execute(sql)
            self.log.append(Executed(sql, (time.perf_counter() - t) * 1000, 0))

    def run_script(self, sql: str) -> int:
        stmts = split_statements(sql)
        for s in stmts:
            self.execute(s)
        return len(stmts)

    def query(self, sql: str) -> list[dict]:
        with self._lock:
            t = time.perf_counter()
            cols, rows = self._execute(sql)
            ms = (time.perf_counter() - t) * 1000
            self.log.append(Executed(sql, ms, len(rows)))
        cols = [c.lower() for c in cols]
        return [{c: _norm(v) for c, v in zip(cols, r)} for r in rows]

    def timed_query(self, sql: str) -> tuple[list[dict], float]:
        t = time.perf_counter()
        rows = self.query(sql)
        return rows, (time.perf_counter() - t) * 1000

    def scalar(self, sql: str):
        rows = self.query(sql)
        if not rows:
            return None
        return next(iter(rows[0].values()))

    def render(self, template: str, **ctx) -> str:
        return self.dialect.render(template, **ctx)

    def render_string(self, text: str, **ctx) -> str:
        return self.dialect.render_string(text, **ctx)

    def view_definitions(self, schema: str) -> dict[str, str]:
        raise NotImplementedError

    def load_csv(self, path: Path, schema: str, table: str) -> None:
        raise NotImplementedError

    def close(self) -> None:
        pass

    def describe(self) -> dict:
        return {"backend": self.name, "standin": self.is_standin}

    # what the database itself measured (Exasol only) ---------------------------------------------------
    def server_marker(self) -> int | None:
        """The database's id for a statement run now, so later statements can be found in its statistics."""
        return None

    def server_stats(self, first: int, last: int) -> tuple[str, list[dict]] | None:
        """(source, per-statement statistics) recorded by the database for ids strictly between first and last."""
        return None


class DuckDBBackend(Backend):
    """Local stand-in used for development, tests and CI where Exasol is not running."""

    name = "duckdb"
    is_standin = True

    def __init__(self, path: str | None = None):
        super().__init__()
        import duckdb

        self.path = path or ":memory:"
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.con = duckdb.connect(self.path)
        self.con.execute("SET threads TO 4")

    def _execute(self, sql: str):
        cur = self.con.execute(sql)
        if cur.description is None:
            return [], []
        cols = [d[0] for d in cur.description]
        return cols, cur.fetchall()

    def view_definitions(self, schema: str) -> dict[str, str]:
        rows = self.query(
            f"SELECT view_name, sql FROM duckdb_views() WHERE upper(schema_name) = '{schema.upper()}' AND NOT internal")
        return {r["view_name"].upper(): r["sql"] for r in rows}

    def load_csv(self, path: Path, schema: str, table: str) -> None:
        cols = self.query(
            f"SELECT column_name, data_type FROM duckdb_columns() WHERE upper(schema_name)='{schema.upper()}' "
            f"AND upper(table_name)='{table.upper()}' ORDER BY column_index")
        spec = ", ".join(f"'{c['column_name']}': '{c['data_type']}'" for c in cols)
        self.execute(
            f"INSERT INTO {schema}.{table} SELECT * FROM read_csv('{path.as_posix()}', header=true, "
            f"auto_detect=false, columns={{{spec}}})")

    def close(self) -> None:
        self.con.close()


class ExasolShadowBackend(DuckDBBackend):
    """Exasol-dialect SQL, executed on DuckDB through sqlglot.

    Every statement is rendered exactly as it would be sent to Exasol, parsed by
    sqlglot's Exasol grammar (so a syntax error fails loudly) and translated to
    DuckDB to execute. Used by the test suite to prove that the Exasol SQL path
    produces the same verdicts as the stand-in, on machines without Exasol.
    """

    name = "exasol"
    is_standin = True

    def __init__(self, path: str | None = None):
        super().__init__(path)
        self.dialect = Dialect("exasol")
        self._views: dict[tuple[str, str], str] = {}
        self.translated = 0
        self.con.execute("CREATE OR REPLACE VIEW DUAL AS SELECT 'X' AS DUMMY")

    def _execute(self, sql: str):
        import sqlglot
        from sqlglot import exp

        tree = sqlglot.parse_one(sql, read="exasol")
        if isinstance(tree, exp.Create) and (tree.args.get("kind") or "").upper() == "VIEW":
            t = tree.this if isinstance(tree.this, exp.Table) else tree.this.find(exp.Table)
            self._views[(t.db.upper(), t.name.upper())] = sql
        if isinstance(tree, exp.Drop) and (tree.args.get("kind") or "").upper() == "SCHEMA":
            t = tree.find(exp.Table)
            s = (t.db or t.name).upper()
            self._views = {k: v for k, v in self._views.items() if k[0] != s}
        self.translated += 1
        return super()._execute(tree.sql(dialect="duckdb"))

    def view_definitions(self, schema: str) -> dict[str, str]:
        return {n: s for (sch, n), s in self._views.items() if sch == schema.upper()}

    def load_csv(self, path: Path, schema: str, table: str) -> None:
        # bulk loading is the one step that is not SQL we send to Exasol (pyexasol IMPORT is used there)
        cols = self.con.execute(
            f"SELECT column_name, data_type FROM duckdb_columns() WHERE upper(schema_name)='{schema.upper()}' "
            f"AND upper(table_name)='{table.upper()}' ORDER BY column_index").fetchall()
        spec = ", ".join(f"'{c}': '{t}'" for c, t in cols)
        self.con.execute(f"INSERT INTO {schema}.{table} SELECT * FROM read_csv('{path.as_posix()}', header=true, "
                         f"auto_detect=false, columns={{{spec}}})")

    def describe(self) -> dict:
        return {"backend": "exasol-shadow", "standin": True,
                "detail": "Exasol SQL parsed by sqlglot and executed on DuckDB"}


class ExasolBackend(Backend):
    """The real target: Exasol Personal (or any Exasol 8 database)."""

    name = "exasol"

    def __init__(self, cfg: Settings):
        super().__init__()
        import pyexasol

        kwargs = dict(dsn=cfg.exa_dsn, user=cfg.exa_user, password=cfg.exa_password,
                      compression=True, encryption=True, fetch_mapper=pyexasol.exasol_mapper)
        if cfg.exa_insecure:
            kwargs["websocket_sslopt"] = {"cert_reqs": ssl.CERT_NONE}
        self.con = pyexasol.connect(**kwargs)
        self.dsn = cfg.exa_dsn

    def _execute(self, sql: str):
        stmt = self.con.execute(sql)
        if stmt.result_type != "resultSet":
            return [], []
        return stmt.column_names(), stmt.fetchall()

    def view_definitions(self, schema: str) -> dict[str, str]:
        rows = self.query(
            f"SELECT VIEW_NAME, VIEW_TEXT FROM SYS.EXA_ALL_VIEWS WHERE VIEW_SCHEMA = '{schema.upper()}'")
        return {r["view_name"].upper(): r["view_text"] for r in rows}

    def load_csv(self, path: Path, schema: str, table: str) -> None:
        t = time.perf_counter()
        self.con.import_from_file(str(path), (schema.upper(), table.upper()),
                                  import_params={"column_separator": ",", "row_separator": "LF", "skip": 1})
        self.log.append(Executed(f"IMPORT INTO {schema}.{table} FROM CSV {path.name}",
                                 (time.perf_counter() - t) * 1000, 0))

    def close(self) -> None:
        self.con.close()

    # Exasol records every statement in EXA_STATISTICS.EXA_SQL_LAST_DAY: its duration inside the database,
    # CPU and peak temporary memory. Rows appear once the statistics are flushed. CURRENT_STATEMENT is the
    # id of the statement that reads it, so two markers bracket the statements in between. With auditing on,
    # EXA_DBA_AUDIT_SQL has the same columns and is the fallback. Neither the markers nor the statistics
    # reads go through the statement log, so they do not change the case.
    STATS_SOURCES = ("EXA_STATISTICS.EXA_SQL_LAST_DAY", "EXA_STATISTICS.EXA_DBA_AUDIT_SQL")
    STATS_SQL = ("SELECT STMT_ID, COMMAND_NAME, DURATION, CPU, TEMP_DB_RAM_PEAK, ROW_COUNT FROM {src} "
                 "WHERE SESSION_ID = CURRENT_SESSION AND STMT_ID > {first} AND STMT_ID < {last} ORDER BY STMT_ID")

    def server_marker(self) -> int | None:
        try:
            with self._lock:
                return int(self.con.execute("SELECT CURRENT_STATEMENT FROM DUAL").fetchval())
        except Exception:  # pragma: no cover, depends on server
            return None

    def server_stats(self, first: int, last: int) -> tuple[str, list[dict]] | None:
        with self._lock:
            try:
                self.con.execute("FLUSH STATISTICS")
            except Exception:
                return None
            for src in self.STATS_SOURCES:
                try:
                    stmt = self.con.execute(self.STATS_SQL.format(src=src, first=int(first), last=int(last)))
                    cols = [c.lower() for c in stmt.column_names()]
                    rows = [{c: _norm(v) for c, v in zip(cols, r)} for r in stmt.fetchall()]
                except Exception:  # not readable for this user, for example
                    continue
                if rows:
                    return src, rows
        return None

    def describe(self) -> dict:
        d = super().describe()
        try:
            d["version"] = self.scalar("SELECT PARAM_VALUE FROM SYS.EXA_METADATA WHERE PARAM_NAME = 'databaseProductVersion'")
        except Exception:  # pragma: no cover, depends on server
            pass
        return d


def connect(cfg: Settings | None = None) -> Backend:
    cfg = cfg or settings()
    if cfg.backend == "exasol":
        return ExasolBackend(cfg)
    if cfg.backend == "shadow":
        return ExasolShadowBackend(cfg.duckdb_path)
    return DuckDBBackend(cfg.duckdb_path)


def to_date(v) -> date:
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    return date.fromisoformat(str(v)[:10])
