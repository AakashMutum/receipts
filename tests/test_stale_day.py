"""The demo data is for one day. demo rebuilds it when the day turns; serve says so instead of an empty page."""

import argparse
import importlib
from datetime import date

import pytest
from fastapi.testclient import TestClient

from receipts import cli
from receipts.model import stale_message

DAY = date(2026, 10, 20)


def _args(**kw):
    return argparse.Namespace(**({"day": None, "host": "127.0.0.1", "port": 0, "watch": False, "lab": False} | kw))


@pytest.fixture
def quiet(monkeypatch):
    import uvicorn
    monkeypatch.setattr(uvicorn, "run", lambda *a, **k: None)
    for k in ("RECEIPTS_DAY", "RECEIPTS_AUTO_REBUILD"):
        monkeypatch.delenv(k, raising=False)
    built = []
    monkeypatch.setattr(cli, "_ensure_day", lambda d: built.append(d) or True)
    monkeypatch.setattr(cli, "preland_headline", lambda: built.append("ist_utc") or
                        {"verdict": "PROVEN_FAULT", "trust_status": "HELD"})
    monkeypatch.setattr(cli, "_data_day", lambda: DAY)
    monkeypatch.setattr("receipts.model.default_incoming_day", lambda now=None: date(2026, 10, 23))
    return built


def test_serve_says_the_data_is_stale_and_does_not_rebuild(quiet, capsys):
    cli._serve(_args(), browser=False)
    assert quiet == []
    assert "The data is for Tue 20 Oct 2026. Run receipts demo to refresh." in capsys.readouterr().out


def test_demo_rebuilds_for_yesterday_and_keeps_watching_the_day(quiet, monkeypatch):
    import os
    cli._serve(_args(), browser=False, rebuild=True)
    try:
        assert quiet == [date(2026, 10, 23)] and os.environ.get("RECEIPTS_AUTO_REBUILD") == "1"  # normal: no batch
    finally:
        os.environ.pop("RECEIPTS_AUTO_REBUILD", None)


def test_lab_demo_prelands_the_ist_batch_after_rebuilding(quiet, monkeypatch):
    import os
    monkeypatch.delenv("RECEIPTS_LAB", raising=False)
    cli._serve(_args(lab=True), browser=False, rebuild=True)
    try:
        assert quiet == [date(2026, 10, 23), "ist_utc"]
    finally:
        os.environ.pop("RECEIPTS_AUTO_REBUILD", None)
        os.environ.pop("RECEIPTS_LAB", None)


def test_a_pinned_day_is_built_and_never_called_stale(quiet):
    import os
    cli._serve(_args(day=DAY), browser=False)
    try:
        assert quiet == [DAY] and os.environ["RECEIPTS_DAY"] == "2026-10-20"
    finally:
        os.environ.pop("RECEIPTS_DAY", None)


def test_stale_message():
    assert stale_message(None) == "No data yet. Run receipts demo to build it."


@pytest.fixture
def client(data_dir, tmp_path, monkeypatch):
    monkeypatch.setenv("RECEIPTS_BACKEND", "duckdb")
    monkeypatch.setenv("RECEIPTS_DUCKDB", str(tmp_path / "s.duckdb"))
    monkeypatch.setenv("RECEIPTS_DATA", str(data_dir))
    monkeypatch.delenv("RECEIPTS_AUTO_REBUILD", raising=False)
    from receipts.db import connect
    from receipts.load import init_database
    be = connect()
    init_database(be, data_dir, log=lambda *a: None)
    be.close()
    import receipts.api as api
    importlib.reload(api)
    return TestClient(api.app)


def test_overview_flags_stale_data_and_the_page_says_no_run_yet(client, monkeypatch):
    monkeypatch.delenv("RECEIPTS_DAY", raising=False)
    o = client.get("/api/overview").json()
    assert o["case"] is None
    assert o["stale"]["data_day"] == "2026-10-20" and o["stale"]["message"].startswith("The data is for Tue 20 Oct 2026.")
    monkeypatch.setenv("RECEIPTS_DAY", "2026-10-20")
    assert client.get("/api/overview").json()["stale"] is None
    html = client.get("/").text
    assert "No run yet" in html


def test_preland_holds_the_number(data_dir, tmp_path, monkeypatch):
    monkeypatch.setenv("RECEIPTS_BACKEND", "duckdb")
    monkeypatch.setenv("RECEIPTS_DUCKDB", str(tmp_path / "p.duckdb"))
    from receipts.db import connect
    from receipts.load import init_database
    be = connect()
    init_database(be, data_dir, log=lambda *a: None)
    be.close()
    c = cli.preland_headline()
    assert c["trust_status"] == "HELD" and c["confirmed"] == ["clock_shift"]


def test_normal_mode_waiting_text_says_what_to_do():
    from pathlib import Path
    js = (Path(__file__).resolve().parent.parent / "web" / "app.js").read_text(encoding="utf-8")
    assert "Run receipts demo, or load a batch." in js
