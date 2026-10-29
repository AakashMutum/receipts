"""Every scenario, through both SQL paths, must reach the expected verdict and causes."""

import pytest

from receipts import gate
from receipts.faults import SCENARIOS
from receipts.load import ingest

from .conftest import DAY


@pytest.mark.parametrize("sid", list(SCENARIOS))
def test_duckdb_path(duck, sid):
    sc = ingest(duck, DAY, sid)
    c = gate.run(duck, DAY, {"id": sid})
    assert c["verdict"] == sc.expected_verdict, c["explanation"]["text"]
    assert set(c["confirmed"]) == set(sc.expected_causes)


@pytest.mark.parametrize("sid", list(SCENARIOS))
def test_exasol_sql_path(shadow, sid):
    """Same scenarios with every statement rendered for Exasol and parsed by the Exasol grammar."""
    sc = ingest(shadow, DAY, sid)
    c = gate.run(shadow, DAY, {"id": sid})
    assert c["verdict"] == sc.expected_verdict
    assert set(c["confirmed"]) == set(sc.expected_causes)


def test_held_value_not_trusted_for_agents(duck):
    ingest(duck, DAY, "unit_paise")
    gate.run(duck, DAY)
    r = duck.query(f"SELECT TRUST_STATUS, TRUSTED_VALUE FROM PUB.METRIC_TRUST WHERE TXN_DAY = DATE '{DAY}'")[0]
    assert r["trust_status"] == "HELD" and r["trusted_value"] is None
    d = duck.query(f"SELECT IS_HELD, SHOWN_VALUE FROM PUB.DASHBOARD_REVENUE WHERE TXN_DAY = DATE '{DAY}'")[0]
    prev = duck.scalar("SELECT METRIC_VALUE FROM PUB.DAILY_REVENUE_PUBLISHED WHERE TXN_DAY = DATE '2026-10-19'")
    assert d["is_held"] and d["shown_value"] == pytest.approx(prev)


def test_approve_publishes_corrected_value(duck):
    ingest(duck, DAY, "stale_fx")
    c = gate.run(duck, DAY)
    gate.approve(duck, c["case_id"], "test")
    r = duck.query(f"SELECT TRUST_STATUS, TRUSTED_VALUE FROM PUB.METRIC_TRUST WHERE TXN_DAY = DATE '{DAY}'")[0]
    assert r["trust_status"] == "CORRECTED"
    assert r["trusted_value"] == pytest.approx(c["values"]["corrected"])


def test_corrected_value_matches_clean_truth(duck):
    ingest(duck, DAY, "healthy")
    truth = duck.scalar(f"SELECT REVENUE_INR FROM PIPE.DAILY_REVENUE WHERE TXN_DAY = DATE '{DAY}'")
    for sid in ("unit_paise", "duplicate_load", "join_fanout", "stale_fx", "ist_utc", "new_code"):
        ingest(duck, DAY, sid)
        c = gate.run(duck, DAY, write_back=False)
        assert c["values"]["corrected"] == pytest.approx(truth, rel=1e-3), sid


def test_festival_retry_burst_is_ruled_out(duck):
    ingest(duck, DAY, "festival")
    c = gate.run(duck, DAY, write_back=False)
    dup = next(s for s in c["suspects"] if s["id"] == "duplicate_key")
    assert dup["fired"] and dup["outcome"] == "REJECTED"
