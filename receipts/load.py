"""Build the database: schemas, landing data, pipeline views, UDF, published history.

Also the ingest step used by the demo and the eval: restore RAW to the clean
state, land the incoming batch, then apply a scenario's fault statements.
"""

from __future__ import annotations

import json
import time
from datetime import date
from pathlib import Path

from .db import Backend, to_date
from .faults import SCENARIOS, Scenario
from .model import FESTIVAL_TABLES, SOURCE_TABLES
from .udf import clock_drift_ddl

PROD_SRC = {t: f"RAW.{t}" for t in SOURCE_TABLES}


def create_pipeline(be: Backend, schema: str = "PIPE", src: dict | None = None) -> None:
    be.run_script(be.render("pipeline.sql", schema=schema, src=src or PROD_SRC))


def install_udf(be: Backend) -> dict:
    """Install the Python UDF. Returns status so the UI can say where it ran."""
    if be.is_standin:
        return {"udf": "local-shim", "detail": "DuckDB stand-in runs the same run(ctx) source through a shim."}
    try:
        be.execute(clock_drift_ddl())
        be.query("SELECT RECEIPTS.CLOCK_DRIFT('probe', TRUE, 1, 1.0) FROM DUAL")
        return {"udf": "in-database", "detail": "RECEIPTS.CLOCK_DRIFT runs inside Exasol as a PYTHON3 SET script."}
    except Exception as e:  # SLC not installed, for example
        return {"udf": "unavailable", "detail": f"Python UDF could not run in Exasol ({e}). "
                                                f"Run `exasol slc install python3` and `make init` again."}


def udf_status(be: Backend) -> dict:
    if be.is_standin:
        return {"udf": "local-shim"}
    try:
        be.query("SELECT RECEIPTS.CLOCK_DRIFT('probe', TRUE, 1, 1.0) FROM DUAL")
        return {"udf": "in-database"}
    except Exception:
        return {"udf": "unavailable"}


def init_database(be: Backend, data_dir: Path, log=print) -> dict:
    manifest = json.loads((data_dir / "manifest.json").read_text())
    incoming = date.fromisoformat(manifest["incoming_day"])
    t0 = time.perf_counter()
    be.run_script(be.render("schema.sql", tables=SOURCE_TABLES, festival=FESTIVAL_TABLES))
    log("schemas created")
    for t in list(SOURCE_TABLES) + list(FESTIVAL_TABLES):
        f = data_dir / f"{t}.csv"
        t1 = time.perf_counter()
        be.load_csv(f, "LANDING", t)
        log(f"loaded LANDING.{t} from {f.name} in {time.perf_counter() - t1:.1f}s")
    create_pipeline(be)
    be.run_script(be.render("pub.sql"))
    udf = install_udf(be)
    log(f"udf: {udf['udf']}")
    reset_raw(be, incoming, full=True)
    # publish the trusted history: these days were reviewed before Receipts existed
    be.execute(f"""INSERT INTO PUB.DAILY_REVENUE_PUBLISHED
        SELECT d.TXN_DAY, d.REVENUE_INR, d.REVENUE_INR, 'TRUSTED', 'history', CURRENT_TIMESTAMP
        FROM PIPE.DAILY_REVENUE d WHERE d.TXN_DAY < {be.dialect.day(incoming)}""")
    n = be.scalar("SELECT COUNT(*) FROM PUB.DAILY_REVENUE_PUBLISHED")
    log(f"published {n} trusted history days")
    if not be.is_standin:
        log(f"agent user: {create_agent_reader(be)}")
    meta = {"incoming_day": incoming.isoformat(), "udf": udf, "seconds": round(time.perf_counter() - t0, 1),
            "manifest": manifest}
    return meta


def create_agent_reader(be: Backend) -> str:
    """A read-only Exasol user for AI agents (the MCP server logs in as it): it may read PUB and nothing else.

    PUB is dropped and created again on every init, which drops its grants, so they are given again here.
    The user is kept between inits (an agent may be connected), and its password is reset to the configured one.
    """
    from .config import settings
    cfg = settings()
    u, pw = cfg.agent_user, cfg.agent_password.replace('"', '')
    exists = be.scalar(f"SELECT COUNT(*) FROM SYS.EXA_DBA_USERS WHERE USER_NAME = '{u}'")
    be.execute(f'{"ALTER" if exists else "CREATE"} USER {u} IDENTIFIED BY "{pw}"')
    be.execute(f"GRANT CREATE SESSION TO {u}")
    be.execute(f"GRANT SELECT ON SCHEMA PUB TO {u}")
    return f"{u} can log in and SELECT from schema PUB only"


def reset_raw(be: Backend, incoming: date, full: bool = False) -> None:
    D = be.dialect.day(incoming)
    if full:
        for t in ("ORDERS", "PAYMENTS"):
            be.execute(f"DELETE FROM RAW.{t}")
            be.execute(f"INSERT INTO RAW.{t} SELECT * FROM LANDING.{t} WHERE BATCH_DAY < {D}")
    else:
        for t in ("ORDERS", "PAYMENTS"):
            be.execute(f"DELETE FROM RAW.{t} WHERE BATCH_DAY >= {D}")
    for t in ("MERCHANTS", "CATEGORY_MAP", "FX_RATES"):
        be.execute(f"DELETE FROM RAW.{t}")
        be.execute(f"INSERT INTO RAW.{t} SELECT * FROM LANDING.{t}")
    be.execute(f"DELETE FROM PUB.DAILY_REVENUE_PUBLISHED WHERE TXN_DAY >= {D}")


def ingest(be: Backend, incoming: date, scenario: Scenario | str) -> Scenario:
    """Reset RAW, land the incoming batch and apply the scenario's fault SQL."""
    sc = SCENARIOS[scenario] if isinstance(scenario, str) else scenario
    reset_raw(be, incoming)
    D = be.dialect.day(incoming)
    for t in ("ORDERS", "PAYMENTS"):
        be.execute(f"INSERT INTO RAW.{t} SELECT * FROM LANDING.{t} WHERE BATCH_DAY = {D}")
    if sc.festival:
        be.execute("INSERT INTO RAW.ORDERS SELECT * FROM LANDING.FESTIVAL_ORDERS")
        be.execute("INSERT INTO RAW.PAYMENTS SELECT * FROM LANDING.FESTIVAL_PAYMENTS")
    for stmt in sc.inject:
        be.execute(be.render_string(stmt, incoming=incoming))
    return sc


def incoming_day(be: Backend) -> date:
    return to_date(be.scalar("SELECT MAX(BATCH_DAY) FROM LANDING.ORDERS"))
