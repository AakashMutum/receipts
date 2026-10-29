"""Checks against a real Exasol database. Skipped unless RECEIPTS_LIVE_EXASOL=1 (the `exasol` CI job sets it).

    RECEIPTS_LIVE_EXASOL=1 EXA_DSN=127.0.0.1:8563 pytest -q tests/test_exasol_live.py

Needs the demo data built with `receipts init` on that database. Lands the IST case, runs the gate without
write-back, and restores tonight afterwards, so the published history is untouched.
"""

import os
from dataclasses import replace

import pytest

pytestmark = pytest.mark.skipif(os.environ.get("RECEIPTS_LIVE_EXASOL") != "1", reason="needs a running Exasol")


@pytest.fixture(scope="module")
def exa():
    from receipts.config import settings
    from receipts.db import connect
    be = connect(replace(settings(), backend="exasol"))
    yield be
    be.close()


def test_gate_reports_exasol_measured_timings(exa):
    from receipts import gate
    from receipts.load import incoming_day, ingest, reset_raw
    day = incoming_day(exa)
    ingest(exa, day, "ist_utc")
    try:
        c = gate.run(exa, day, write_back=False)
    finally:
        reset_raw(exa, day)
    m = c["exasol_measured"]
    assert c["confirmed"] == ["clock_shift"]
    assert m["source"].startswith("EXA_STATISTICS."), m
    # the client also counts statements Exasol's statistics leave out: two commented SELECTs, and since the blast
    # radius, FLUSH STATISTICS and the audit-log read
    assert m["statements"] >= c["statements"] - 4 and m["db_ms"] > 0 and m["temp_ram_peak_mib"] > 0
    cube = next(s for s in m["steps"] if "GROUP BY CUBE" in s["step"])
    assert cube["statements"] == 1 and cube["db_ms"] > 0


def test_agent_reader_is_read_only():
    from receipts.doctor import agent_reader_checks
    checks = agent_reader_checks()
    assert checks and all(ok for ok, _ in checks), checks
