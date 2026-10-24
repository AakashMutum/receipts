import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client(data_dir, tmp_path_factory, monkeypatch_module):
    db = tmp_path_factory.mktemp("db") / "api.duckdb"
    monkeypatch_module.setenv("RECEIPTS_BACKEND", "duckdb")
    monkeypatch_module.setenv("RECEIPTS_DUCKDB", str(db))
    monkeypatch_module.setenv("RECEIPTS_DATA", str(data_dir))
    monkeypatch_module.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch_module.setenv("RECEIPTS_ALERTS", str(tmp_path_factory.mktemp("alerts")))
    monkeypatch_module.setenv("RECEIPTS_LAB", "1")
    from receipts.db import connect
    from receipts.load import init_database
    be = connect()
    init_database(be, data_dir, log=lambda *a: None)
    be.close()
    import receipts.api as api
    importlib.reload(api)
    return TestClient(api.app)


@pytest.fixture(scope="module")
def monkeypatch_module():
    mp = pytest.MonkeyPatch()
    yield mp
    mp.undo()


def test_overview_and_page(client):
    assert client.get("/").status_code == 200
    o = client.get("/api/overview").json()
    assert o["incoming_day"] == "2026-10-20" and len(o["scenarios"]) == 10


def test_run_agent_approve(client):
    c = client.post("/api/run", json={"scenario": "ist_utc"}).json()["case"]
    assert c["verdict"] == "PROVEN_FAULT" and c["trust_status"] == "HELD"
    a = client.get("/api/agent").json()
    assert "held" in a["trusted"]["answer"] and a["trusted"]["status"] == "HELD"
    assert "was" in a["naive"]["answer"]
    r = client.post(f"/api/case/{c['case_id']}/approve", json={"note": "ok"}).json()
    assert r["case"]["trust_status"] == "CORRECTED"
    assert client.get("/api/agent").json()["trusted"]["status"] == "CORRECTED"
    e = client.post(f"/api/case/{c['case_id']}/explain").json()
    assert e["source"] == "template" and e["text"]


def test_unknown_scenario(client):
    assert client.post("/api/run", json={"scenario": "nope"}).status_code == 404


def test_alerts_endpoint_and_dismiss(client):
    assert client.get("/api/alerts").json() == []
    assert client.post("/api/alerts/RC-NOPE/dismiss").status_code == 404
