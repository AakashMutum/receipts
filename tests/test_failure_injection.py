"""The database fails in the middle of a gate run: in the undo test, in the write-back, in the lineage read.

After each failure: the error reaches the caller, no trusted value is left for the day, every published row still
points at a case that exists, no stray schema is left behind, and the next run on the same batch works and gives the
right verdict. On the stand-in always; on Exasol as well with RECEIPTS_LIVE_EXASOL=1 (needs the demo data; the
published history is restored afterwards).

RECEIPTS_SBX is the scratch schema the undo test rebuilds from scratch on every run, so a half-built sandbox is
replaced by the next run rather than dropped on failure.
"""

import os
import re
from dataclasses import replace

import pytest

from receipts import gate
from receipts.db import DuckDBBackend
from receipts.load import incoming_day, ingest, init_database, reset_raw

LIVE = os.environ.get("RECEIPTS_LIVE_EXASOL") == "1"
WRITE_STEPS = ["INSERT INTO RECEIPTS.CASES", "INSERT INTO RECEIPTS.EVIDENCE", "INSERT INTO RECEIPTS.STEP_TIMINGS",
               "DELETE FROM PUB.DAILY_REVENUE_PUBLISHED", "INSERT INTO PUB.DAILY_REVENUE_PUBLISHED"]


class Injected(RuntimeError):
    pass


def fail_on(be, pattern: str):
    """Make the backend raise on the first statement matching pattern; return a function that disarms it."""
    real = be._execute
    state = {"armed": True}

    def _execute(sql):
        if state["armed"] and re.search(pattern, sql, re.I):
            state["armed"] = False
            raise Injected(f"injected failure on: {sql[:80]}")
        return real(sql)

    be._execute = _execute
    return lambda: be.__dict__.pop("_execute", None)


@pytest.fixture(scope="module", params=["duckdb"] + (["exasol"] if LIVE else []))
def be(request, data_dir):
    if request.param == "duckdb":
        b = DuckDBBackend(":memory:")
        init_database(b, data_dir, log=lambda *a: None)
    else:
        from receipts.config import settings
        from receipts.db import connect
        b = connect(replace(settings(), backend="exasol"))
    yield b
    b.close()


def schemas(be) -> set[str]:
    sql = ("SELECT SCHEMA_NAME AS S FROM SYS.EXA_SCHEMAS" if be.name == "exasol" else
           "SELECT DISTINCT upper(schema_name) AS S FROM duckdb_schemas() WHERE NOT internal")
    return {r["s"].upper() for r in be.query(sql)}


def published(be, day) -> list[dict]:
    return be.query(f"SELECT TXN_DAY, METRIC_VALUE, CANDIDATE_VALUE, TRUST_STATUS, CASE_ID, PUBLISHED_AT "
                    f"FROM PUB.DAILY_REVENUE_PUBLISHED WHERE TXN_DAY = {be.dialect.day(day)}")


@pytest.fixture
def day(be):
    """Tonight's day; the published row and the cases written by a test are put back afterwards."""
    d = incoming_day(be)
    before = published(be, d)
    cases = {r["c"] for r in be.query("SELECT CASE_ID AS C FROM RECEIPTS.CASES")}
    yield d
    reset_raw(be, d)
    new = [r["c"] for r in be.query("SELECT CASE_ID AS C FROM RECEIPTS.CASES") if r["c"] not in cases]
    for t in ("RECEIPTS.EVIDENCE", "RECEIPTS.STEP_TIMINGS", "RECEIPTS.CASES"):
        for c in new:
            be.execute(f"DELETE FROM {t} WHERE CASE_ID = '{c}'")
    be.execute(f"DELETE FROM PUB.DAILY_REVENUE_PUBLISHED WHERE TXN_DAY = {be.dialect.day(d)}")
    for r in before:
        vals = ", ".join("NULL" if r[k] is None else f"'{r[k]}'" if isinstance(r[k], str) else
                         be.dialect.day(r[k]) if k == "txn_day" else
                         f"TIMESTAMP '{r[k]:%Y-%m-%d %H:%M:%S}'" if k == "published_at" else repr(float(r[k]))
                         for k in ("txn_day", "metric_value", "candidate_value", "trust_status", "case_id",
                                   "published_at"))
        be.execute(f"INSERT INTO PUB.DAILY_REVENUE_PUBLISHED VALUES ({vals})")


def no_trusted_value_and_no_dangling_case(be, d):
    rows = be.query(f"SELECT TRUST_STATUS, TRUSTED_VALUE, CASE_ID FROM PUB.METRIC_TRUST WHERE TXN_DAY = "
                    f"{be.dialect.day(d)}")
    cases = {r["c"] for r in be.query("SELECT CASE_ID AS C FROM RECEIPTS.CASES")}
    for r in rows:
        assert r["trusted_value"] is None, r
        assert r["case_id"] is None or r["case_id"] in cases, r


def next_run_works(be, d):
    c = gate.run(be, d, {"id": "unit_paise"}, write_back=True)
    assert c["verdict"] == "PROVEN_FAULT" and c["confirmed"] == ["unit_scale"]
    rows = be.query(f"SELECT TRUST_STATUS, TRUSTED_VALUE, CASE_ID FROM PUB.METRIC_TRUST WHERE TXN_DAY = "
                    f"{be.dialect.day(d)}")
    assert len(rows) == 1 and rows[0]["trust_status"] == "HELD" and rows[0]["trusted_value"] is None
    assert rows[0]["case_id"] == c["case_id"]


def clear_day(be, d):
    be.execute(f"DELETE FROM PUB.DAILY_REVENUE_PUBLISHED WHERE TXN_DAY = {be.dialect.day(d)}")


@pytest.mark.parametrize("where", ["undo", "lineage"] + WRITE_STEPS)
def test_failure_leaves_no_trusted_value_and_the_next_run_works(be, day, where):
    pattern = {"undo": r"CREATE OR REPLACE VIEW RECEIPTS_SBX\.",
               "lineage": r"EXA_ALL_VIEWS|duckdb_views\(\)"}.get(where, re.escape(where))
    clear_day(be, day)
    ingest(be, day, "unit_paise")
    before = schemas(be) | {"RECEIPTS_SBX"}
    disarm = fail_on(be, pattern)
    try:
        with pytest.raises(Injected):
            gate.run(be, day, {"id": "unit_paise"}, write_back=True)
    finally:
        disarm()
    no_trusted_value_and_no_dangling_case(be, day)
    assert schemas(be) <= before
    next_run_works(be, day)
    assert schemas(be) <= before
