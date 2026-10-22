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
    "RAW_PAYMENTS", "N"})


def exasol_statements() -> list[str]:
    d = Dialect("exasol")
    out = split_statements(d.render("schema.sql", tables=SOURCE_TABLES, festival=FESTIVAL_TABLES))
    out += split_statements(d.render("pipeline.sql", schema="PIPE", src=PROD_SRC))
    out += split_statements(d.render("pub.sql"))
    for s in SCENARIOS.values():
        out += [d.render_string(x, incoming=INCOMING_DAY) for x in s.inject]
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
    try:
        n = be.scalar("SELECT COUNT(*) FROM RAW.PAYMENTS")
        line(n and n > 0, f"data loaded ({n:,} payment rows in RAW)")
    except Exception:
        line(False, "data loaded. Run `make init`.")
    print("\n" + ("All good." if ok else "Fix the items marked FAIL."))
    return 0 if ok else 1
