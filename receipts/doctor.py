"""`receipts doctor`: check the setup before a demo."""

from __future__ import annotations

import sqlglot

from .config import settings
from .dialect import Dialect, split_statements
from .faults import SCENARIOS
from .load import PROD_SRC
from .model import FESTIVAL_TABLES, INCOMING_DAY, SOURCE_TABLES
from .udf import clock_drift_ddl

IDENTIFIERS = sorted({c for cols in SOURCE_TABLES.values() for c, _ in cols} | set(SOURCE_TABLES) | {
    "TXN_DAY", "REVENUE_INR", "TXN_COUNT", "CAPTURED_AT_IST", "CATEGORY_NAME", "METRIC_VALUE", "CANDIDATE_VALUE",
    "TRUST_STATUS", "CASE_ID", "PUBLISHED_AT", "METRIC_NAME", "OPENED_AT", "VERDICT", "BASELINE_VALUE",
    "CORRECTED_VALUE", "SCENARIO", "ELAPSED_MS", "SUMMARY", "CASE_JSON", "SUSPECT", "DETECTOR_FIRED", "OUTCOME",
    "BLAMED_TABLE", "BLAMED_COLUMN", "SLICE_DESC", "UNDO_VALUE", "EXPLAINED_PCT", "HISTORY_CHECK", "REASON",
    "STEP_NAME", "ROWS_IN_SCOPE", "APPROVED_AT", "APPROVED_VALUE", "NOTE", "TRUSTED_VALUE", "LAST_TRUSTED_DAY",
    "AGENT_GUIDANCE", "SHOWN_VALUE", "IS_HELD", "SLICE_KEY", "IS_TODAY", "BIN_IDX", "CNT", "GID", "CUR_VALUE",
    "BASE_VALUE", "N_ROWS", "RN", "LANDING", "RAW", "PIPE", "PUB", "RECEIPTS", "RECEIPTS_SBX", "FIX_PAYMENTS_1",
    "STG_PAYMENTS", "STG_ORDERS", "DIM_MERCHANT", "DIM_CATEGORY", "FX_DAILY", "FCT_REVENUE", "DAILY_REVENUE",
    "METRIC_TRUST", "DASHBOARD_REVENUE", "CLOCK_DRIFT", "DUP_KEYS", "EXTRA_ROWS", "MED_TODAY", "MED_BASE", "N_TODAY",
    "TABLE_NAME", "KEY_COLUMN", "DIM_ROWS", "PAYMENTS_TODAY", "ORDERS_TODAY", "ORDERS_ON_DUP_KEYS", "DUP_ROWS",
    "RAW_PAYMENTS", "N", "CONFIRMED_CAUSES", "AGENT_READER"})


def exasol_statements() -> list[str]:
    d = Dialect("exasol")
    out = split_statements(d.render("schema.sql", tables=SOURCE_TABLES, festival=FESTIVAL_TABLES))
    out += split_statements(d.render("pipeline.sql", schema="PIPE", src=PROD_SRC))
    out += split_statements(d.render("pub.sql"))
    for s in SCENARIOS.values():
        out += [d.render_string(x, incoming=INCOMING_DAY) for x in s.inject]
    return out


def agent_reader_checks(cfg=None) -> list[tuple[bool, str]]:
    """Log in as the read-only agent user and prove what it can and cannot do. Exasol only."""
    import ssl

    import pyexasol
    cfg = cfg or settings()
    u = cfg.agent_user
    try:
        kw = {"websocket_sslopt": {"cert_reqs": ssl.CERT_NONE}} if cfg.exa_insecure else {}
        con = pyexasol.connect(dsn=cfg.exa_dsn, user=u, password=cfg.agent_password, encryption=True, **kw)
    except Exception as e:
        return [(False, f"{u} can log in ({type(e).__name__}). Run `receipts init` to create it.")]
    out = []

    def refused(sql):
        try:
            con.execute(sql)
            return False
        except Exception as e:
            return "insufficient privileges" in str(e).lower()  # refused for the right reason, not a typo

    try:
        n = con.execute("SELECT COUNT(*) FROM PUB.METRIC_TRUST").fetchval()
        out.append((True, f"{u} reads PUB.METRIC_TRUST ({n} rows)"))
    except Exception as e:
        out.append((False, f"{u} reads PUB.METRIC_TRUST: {str(e).splitlines()[0][:120]}"))
    out.append((refused("SELECT COUNT(*) FROM RAW.PAYMENTS"), f"{u} cannot read RAW.PAYMENTS"))
    out.append((refused("SELECT COUNT(*) FROM PIPE.DAILY_REVENUE"), f"{u} cannot read PIPE.DAILY_REVENUE"))
    out.append((refused("SELECT COUNT(*) FROM RECEIPTS.CASES"), f"{u} cannot read RECEIPTS.CASES"))
    try:
        n = con.execute("SELECT COUNT(*) FROM PUB.CONFIRMED_CAUSES").fetchval()
        out.append((True, f"{u} reads PUB.CONFIRMED_CAUSES ({n} rows)"))
    except Exception as e:
        out.append((False, f"{u} reads PUB.CONFIRMED_CAUSES: {str(e).splitlines()[0][:120]}"))
    out.append((refused("DELETE FROM PUB.DAILY_REVENUE_PUBLISHED"), f"{u} cannot delete from PUB"))
    out.append((refused("UPDATE PUB.DAILY_REVENUE_PUBLISHED SET METRIC_VALUE = 0"), f"{u} cannot update PUB"))
    out.append((refused("INSERT INTO PUB.DAILY_REVENUE_PUBLISHED (TXN_DAY) VALUES (DATE '2000-01-01')"),
                f"{u} cannot insert into PUB"))
    out.append((refused("CREATE SCHEMA AGENT_SCRATCH"), f"{u} cannot create a schema"))
    con.close()
    return out


def run_doctor() -> int:
    ok = True

    def line(good, msg):
        nonlocal ok
        ok &= bool(good)
        print(f"  {'ok  ' if good else 'FAIL'}  {msg}")

    print("Receipts doctor\n")
    stmts = exasol_statements()
    bad = []
    for s in stmts:
        try:
            sqlglot.parse_one(s, read="exasol")
        except Exception as e:
            bad.append((s[:60], e))
    line(not bad, f"{len(stmts)} Exasol statements parse with sqlglot's Exasol grammar")
    for s, e in bad:
        print(f"        {s}... {e}")
    line("def run(ctx)" in clock_drift_ddl(), "UDF source present (RECEIPTS.CLOCK_DRIFT)")

    cfg = settings()
    print(f"\n  backend: {cfg.backend}" + (f" ({cfg.exa_dsn})" if cfg.backend == "exasol" else ""))
    try:
        from .db import connect
        be = connect(cfg)
        line(be.scalar("SELECT 1" + be.dialect.from_dual()) == 1, "database reachable")
    except Exception as e:
        if type(e).__name__ == "ExaConnectionFailedError":
            line(False, f"database reachable: nothing answers at {cfg.exa_dsn}")
            print("        Check with `exasol status`, start it with `exasol start`, then run doctor again.")
        else:
            line(False, f"database reachable: {e}")
        return 1
    if be.name == "exasol" and not be.is_standin:
        info = be.describe()
        print(f"        Exasol {info.get('version', '?')}")
        kw = {r["keyword"] for r in be.query("SELECT KEYWORD FROM SYS.EXA_SQL_KEYWORDS WHERE RESERVED")}
        clash = [i for i in IDENTIFIERS if i in kw]
        line(not clash, f"{len(IDENTIFIERS)} identifiers checked against SYS.EXA_SQL_KEYWORDS"
             + (f": reserved {clash}" if clash else ""))
        from .load import udf_status
        u = udf_status(be)["udf"]
        line(u == "in-database", f"Python UDF runs inside Exasol ({u})"
             + ("" if u == "in-database" else ". Run `exasol slc install python3`, then `make init`."))
        for good, msg in agent_reader_checks(cfg):
            line(good, msg)
    try:
        n = be.scalar("SELECT COUNT(*) FROM RAW.PAYMENTS")
        line(n and n > 0, f"data loaded ({n:,} payment rows in RAW)")
    except Exception:
        line(False, "data loaded. Run `make init`.")
    print("\n" + ("All good." if ok else "Fix the items marked FAIL."))
    return 0 if ok else 1
