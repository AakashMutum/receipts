"""Lab mode: planting faults, Break it and its Reset are refused unless lab mode is on, on synthetic data."""

import importlib
import json
import time

import pytest
from fastapi.testclient import TestClient

from receipts import faults, lab
from receipts.faults import FAULT_CLASSES, fault_sql

LAB_ONLY = [("post", "/api/run", {"scenario": "ist_utc"}),
            ("post", "/api/lab/break", {"fault": "clock_shift", "share": 1.0}),
            ("post", "/api/lab/reset", None),
            ("get", "/api/lab/job/nope", None)]


@pytest.fixture(scope="module")
def mp():
    m = pytest.MonkeyPatch()
    yield m
    m.undo()


@pytest.fixture(scope="module")
def client(data_dir, tmp_path_factory, mp):
    mp.setenv("RECEIPTS_BACKEND", "duckdb")
    mp.setenv("RECEIPTS_DUCKDB", str(tmp_path_factory.mktemp("labdb") / "lab.duckdb"))
    mp.setenv("RECEIPTS_DATA", str(data_dir))
    mp.setenv("RECEIPTS_ALERTS", str(tmp_path_factory.mktemp("alerts")))
    mp.delenv("ANTHROPIC_API_KEY", raising=False)
    from receipts.db import connect
    from receipts.load import init_database
    be = connect()
    init_database(be, data_dir, log=lambda *a: None)
    be.close()
    import receipts.api as api
    importlib.reload(api)
    return TestClient(api.app)


@pytest.mark.parametrize("method,path,body", LAB_ONLY)
def test_lab_endpoints_are_403_without_lab(client, mp, method, path, body):
    mp.delenv("RECEIPTS_LAB", raising=False)
    r = getattr(client, method)(path, **({"json": body} if body else {}))
    assert r.status_code == 403 and "Lab mode is off" in r.json()["detail"]


def test_page_has_no_lab_panel_without_lab(client, mp):
    mp.delenv("RECEIPTS_LAB", raising=False)
    html = client.get("/").text
    for marker in ('id="lab"', "Break the pipeline", 'id="lab-reset"', 'id="scenarios"', 'id="redteam"', "<!-- lab -->"):
        assert marker not in html
    assert "Normal mode" in html and "cannot change data" in html
    assert client.get("/static/index.html").status_code == 404
    o = client.get("/api/overview").json()
    assert o["lab"] is False and o["scenarios"] == [] and o["faults"] == []


def test_page_has_lab_panel_with_lab(client, mp):
    mp.setenv("RECEIPTS_LAB", "1")
    html = client.get("/").text
    assert 'id="lab"' in html and 'id="lab-reset"' in html and "Normal mode" not in html
    assert client.get("/api/overview").json()["lab"] is True


def _wait(client, job):
    for _ in range(600):
        j = client.get(f"/api/lab/job/{job}").json()
        if j["status"] != "running":
            return j
        time.sleep(0.1)
    raise AssertionError("gate did not finish")


def test_break_shows_every_step_then_held_and_reset(client, mp):
    mp.setenv("RECEIPTS_LAB", "1")
    r = client.post("/api/lab/break", json={"fault": "clock_shift", "share": 1.0, "gateway": "GW_B"})
    assert r.status_code == 200, r.text
    j = _wait(client, r.json()["job"])
    assert j["status"] == "done", j.get("error")
    names = [s["step"] for s in j["steps"]]
    assert names[0].startswith("Land the batch") and names[-1] == "Write receipts back to the database"
    assert any("detectors" in n for n in names) and any("GROUP BY CUBE" in n for n in names)
    assert any("lineage" in n for n in names) and any("Undo" in n for n in names)
    c = j["case"]
    assert c["trust_status"] == "HELD" and c["confirmed"] == ["clock_shift"] and j["server_ms"] > 0
    assert client.post(f"/api/case/{c['case_id']}/approve", json={"note": "lab"}).json()["case"]["trust_status"] == "CORRECTED"
    board = client.post("/api/lab/reset").json()["board"]
    day = client.get("/api/overview").json()["incoming_day"]
    assert all(p["day"] < day for p in board["points"])  # nothing published for tonight, demo can repeat
    j = _wait(client, client.post("/api/lab/break", json={"fault": "unit_scale", "share": 1.0}).json()["job"])
    assert j["case"]["confirmed"] == ["unit_scale"]


def test_break_refuses_data_that_is_not_synthetic(client, mp, monkeypatch, tmp_path):
    mp.setenv("RECEIPTS_LAB", "1")
    monkeypatch.setenv("RECEIPTS_DATA", str(tmp_path))  # this test only
    r = client.post("/api/lab/break", json={"fault": "clock_shift"})
    assert r.status_code == 409 and "synthetic" in r.json()["detail"]
    (tmp_path / "manifest.json").write_text(json.dumps({"config": {"seed": 1}, "rows": {"PAYMENTS": 1, "ORDERS": 1}}))
    r = client.post("/api/lab/reset")
    assert r.status_code == 409 and "Run `receipts init`" in r.json()["detail"]


def test_bad_break_requests(client, mp):
    mp.setenv("RECEIPTS_LAB", "1")
    assert client.post("/api/lab/break", json={"fault": "nope"}).status_code == 404
    assert client.post("/api/lab/break", json={"fault": "unit_scale", "share": 0}).status_code == 422
    assert client.post("/api/lab/break", json={"fault": "unit_scale", "gateway": "GW_X"}).status_code == 422


def test_fault_sql_dial():
    assert "MOD(PAYMENT_ID, 1000) < 50" in fault_sql("clock_shift", 0.05)[0]
    assert "1 = 1" in fault_sql("unit_scale", 1.0, "GW_A")[0] and "GW_A" in fault_sql("unit_scale", 1.0, "GW_A")[0]
    assert fault_sql("stale_feed", 0.1) == [faults.STALE]
    assert set(FAULT_CLASSES) == {c for s in faults.SCENARIOS.values() for c in s.expected_causes}
    assert lab.OFF.startswith("Lab mode is off")


def test_serve_lab_flag_turns_lab_on(mp):
    import argparse

    import uvicorn

    from receipts import cli
    mp.delenv("RECEIPTS_LAB", raising=False)
    mp.setattr(cli, "_ensure_day", lambda day: None)
    mp.setattr(cli, "_data_day", lambda: None)
    seen = []
    mp.setattr(uvicorn, "run", lambda *a, **k: seen.append(lab.enabled()))
    args = argparse.Namespace(day=None, host="127.0.0.1", port=0, watch=False, lab=False)
    cli._serve(args, browser=False)
    cli._serve(argparse.Namespace(**{**vars(args), "lab": True}), browser=False)
    assert seen == [False, True]


def test_redteam_endpoints(client, mp):
    mp.setenv("RECEIPTS_LAB", "1")
    client.post("/api/lab/reset")
    r = client.post("/api/lab/redteam/attack", json={"fault": "orphan_code", "share": 0.5})
    assert r.status_code == 200, r.text
    assert r.json()["outcome"] == "caught" and r.json()["meaning"]
    rep = client.get("/api/lab/redteam")
    assert rep.status_code in (200, 404)
    if rep.status_code == 200:
        assert set(rep.json()["summary"]["classes"]) == set(FAULT_CLASSES)
    mp.delenv("RECEIPTS_LAB")
    assert client.get("/api/lab/redteam").status_code == 403
    assert client.post("/api/lab/redteam/attack", json={"fault": "orphan_code"}).status_code == 403


def test_cli_run_refuses_data_that_is_not_synthetic(monkeypatch, tmp_path, data_dir):
    from receipts import cli
    monkeypatch.setenv("RECEIPTS_BACKEND", "duckdb")
    monkeypatch.setenv("RECEIPTS_DUCKDB", str(tmp_path / "x.duckdb"))
    monkeypatch.setenv("RECEIPTS_DATA", str(tmp_path))  # no manifest here
    from receipts.db import connect
    from receipts.load import init_database
    be = connect()
    init_database(be, data_dir, log=lambda *a: None)
    be.close()
    with pytest.raises(SystemExit) as e:
        cli.main(["run", "ist_utc"])
    assert e.value.code == 3
