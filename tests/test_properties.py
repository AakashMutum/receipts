"""Properties the gate guarantees for any planted fault, checked with Hypothesis on the DuckDB stand-in.

Each example plants one fault class at a share on a gateway (or lands a whole scenario), runs the gate and checks
what must hold whatever the fault: the verdict and trust status come from fixed sets and match each other, a
published number is inside the normal range unless it is published as a real change, a proven correction lands in
the normal range and is no further from the clean value than the number it corrects, the same batch gives the same
verdict twice, and a held number never reaches the trusted value agents read.
"""

from datetime import date

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from receipts import gate
from receipts.db import DuckDBBackend
from receipts.faults import FAULT_CLASSES, SCENARIOS, fault_sql
from receipts.load import ingest, init_database, reset_raw
from receipts.redteam import SHARES

from .conftest import DAY

VERDICTS = {"NO_INCIDENT", "REAL_CHANGE", "PROVEN_FAULT", "UNEXPLAINED"}
TRUST = {"NO_INCIDENT": "TRUSTED", "REAL_CHANGE": "REAL_CHANGE", "PROVEN_FAULT": "HELD", "UNEXPLAINED": "HELD"}
SETTINGS = settings(max_examples=30, deadline=None, derandomize=True,
                    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow])


@pytest.fixture(scope="module")
def be(data_dir):
    b = DuckDBBackend(":memory:")
    init_database(b, data_dir, log=lambda *a: None)
    yield b
    b.close()


@pytest.fixture(scope="module")
def clean(be):
    ingest(be, DAY, "healthy")
    v = be.scalar(f"SELECT REVENUE_INR FROM PIPE.DAILY_REVENUE WHERE TXN_DAY = DATE '{DAY}'")
    reset_raw(be, DAY)
    return v


@st.composite
def faults(draw):
    kind = draw(st.sampled_from(sorted(FAULT_CLASSES)))
    gws = FAULT_CLASSES[kind][2]
    gw = draw(st.sampled_from(gws)) if gws else None
    share = 1.0 if kind == "stale_feed" else draw(st.sampled_from(SHARES))
    return kind, share, gw


def plant(be: DuckDBBackend, day: date, kind: str, share: float, gw: str | None) -> dict:
    ingest(be, day, "healthy")
    for s in fault_sql(kind, share, gw):
        be.execute(be.render_string(s, incoming=day))
    return gate.run(be, day, {"id": "property", "title": kind}, write_back=False)


def check_case(c: dict, clean_value: float | None) -> None:
    v = c["values"]
    assert c["verdict"] in VERDICTS
    assert c["trust_status"] == TRUST[c["verdict"]]
    in_band = v["band_low"] <= v["candidate"] <= v["band_high"]
    assert c["anomaly"] == (not in_band)
    if c["trust_status"] != "HELD":  # published: inside the range, or outside it as a checked real change
        assert in_band or c["verdict"] == "REAL_CHANGE"
        assert not c["confirmed"]
    if c["verdict"] == "PROVEN_FAULT":
        assert c["confirmed"] and v["corrected"] is not None
        assert v["band_low"] <= v["corrected"] <= v["band_high"]
        if clean_value is not None:
            assert abs(v["corrected"] - clean_value) <= abs(v["candidate"] - clean_value) + 1e-6 * abs(clean_value)
    else:
        assert v["corrected"] is None


@SETTINGS
@given(f=faults())
def test_any_planted_fault_keeps_the_gate_rules(be, clean, f):
    kind, share, gw = f
    try:
        a = plant(be, DAY, kind, share, gw)
        b = plant(be, DAY, kind, share, gw)
    finally:
        reset_raw(be, DAY)
    check_case(a, clean)
    check_case(b, clean)
    assert (a["verdict"], sorted(a["confirmed"])) == (b["verdict"], sorted(b["confirmed"]))
    # the values may differ in the last bits: the stand-in sums in parallel, in no fixed order
    assert a["values"]["candidate"] == pytest.approx(b["values"]["candidate"], rel=1e-9)
    assert (a["values"]["corrected"] is None) == (b["values"]["corrected"] is None)
    if a["values"]["corrected"] is not None:
        assert a["values"]["corrected"] == pytest.approx(b["values"]["corrected"], rel=1e-9)


@settings(max_examples=len(SCENARIOS), deadline=None, derandomize=True,
          suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow])
@given(sid=st.sampled_from(sorted(SCENARIOS)))
def test_write_back_never_publishes_a_held_number(be, sid):
    try:
        ingest(be, DAY, sid)
        c = gate.run(be, DAY, {"id": sid}, write_back=True)
        row = be.query(f"SELECT TRUST_STATUS, TRUSTED_VALUE FROM PUB.METRIC_TRUST WHERE TXN_DAY = DATE '{DAY}'")
    finally:
        reset_raw(be, DAY)
    check_case(c, None)
    assert len(row) == 1 and row[0]["trust_status"] == c["trust_status"]
    assert row[0]["trust_status"] in {"TRUSTED", "REAL_CHANGE", "CORRECTED", "HELD"}
    if c["trust_status"] == "HELD":
        assert row[0]["trusted_value"] is None
    else:
        assert row[0]["trusted_value"] == pytest.approx(c["values"]["candidate"])
