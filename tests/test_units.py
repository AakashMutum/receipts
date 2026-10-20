import re
from datetime import date
from pathlib import Path

import sqlglot

from receipts.dialect import Dialect, lit, split_statements
from receipts.doctor import exasol_statements
from receipts.lineage import build
from receipts.udf import CLOCK_DRIFT_OUT, clock_drift_ddl, clock_drift_source, run_set_script_locally

ROOT = Path(__file__).resolve().parent.parent


def _profile(shift_bins=0, n=4000):
    rows = []
    base = [1 + (8 if 36 <= i <= 44 else 0) + (3 if 22 <= i <= 30 else 0) for i in range(48)]
    for i, w in enumerate(base):
        rows.append({"slice_key": "G", "is_today": False, "bin_idx": i, "cnt": float(w * 100)})
        rows.append({"slice_key": "G", "is_today": True, "bin_idx": (i + shift_bins) % 48, "cnt": float(w * 10)})
    return rows


def test_udf_finds_ist_shift():
    out = run_set_script_locally(clock_drift_source(), _profile(11), "slice_key", CLOCK_DRIFT_OUT)[0]
    assert out["best_shift_bins"] == 11 and out["tvd"] > 0.2 and out["tvd_after_shift"] < 1e-9


def test_udf_quiet_on_same_profile():
    out = run_set_script_locally(clock_drift_source(), _profile(0), "slice_key", CLOCK_DRIFT_OUT)[0]
    assert out["tvd"] < 1e-9


def test_udf_ddl_is_exasol_set_script():
    ddl = clock_drift_ddl()
    assert ddl.startswith("CREATE OR REPLACE PYTHON3 SET SCRIPT RECEIPTS.CLOCK_DRIFT(")
    assert "EMITS (" in ddl and "def run(ctx)" in ddl


def test_every_exasol_statement_parses():
    stmts = exasol_statements()
    assert len(stmts) > 20
    for s in stmts:
        sqlglot.parse_one(s, read="exasol")


def test_exasol_spellings():
    d = Dialect("exasol")
    assert d.add_minutes("t", 330) == "ADD_MINUTES(t, 330)"
    assert d.add_days("x", -14) == "ADD_DAYS(x, -14)"
    assert d.from_dual() == " FROM DUAL"


def test_split_and_literals():
    assert split_statements("-- c\nSELECT 1;\nSELECT 2;\n") == ["-- c\nSELECT 1", "SELECT 2"]
    assert lit("it's") == "'it''s'" and lit(None) == "NULL" and lit(date(2026, 1, 2)) == "DATE '2026-01-02'"


def test_lineage_reaches_raw_columns(duck):
    lin = build(duck)
    assert lin.influences("RAW.PAYMENTS", "AMOUNT") == "value"
    assert lin.influences("RAW.PAYMENTS", "CAPTURED_AT") == "row"
    assert lin.influences("RAW.FX_RATES", "RATE_DAY") == "row"
    assert lin.influences("RAW.MERCHANTS", "MERCHANT_NAME") is None


def test_no_em_dashes_anywhere():
    bad = []
    for p in ROOT.rglob("*"):
        if p.is_file() and p.suffix in {".py", ".md", ".html", ".css", ".js", ".sql", ".json", ".toml", ".txt", ""} \
                and not any(x in p.parts for x in (".git", "data", "__pycache__", ".pytest_cache", ".venv", "venv", "site-packages", "node_modules")):
            try:
                if chr(0x2014) in p.read_text(encoding="utf-8"):
                    bad.append(str(p.relative_to(ROOT)))
            except UnicodeDecodeError:
                pass
    assert not bad, f"em dashes found in {bad}"
