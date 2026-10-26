"""The trust badge: status, metric name and last trusted day, no values, readable in normal mode."""

import importlib
import re
from datetime import date

import pytest
from fastapi.testclient import TestClient

from receipts import badge, gate
from receipts.load import ingest

from .conftest import DAY


def test_svg_shows_status_metric_and_last_day_only():
    s = badge.svg("daily_revenue_inr", "HELD", date(2026, 10, 19))
    assert s.startswith("<svg") and "daily_revenue_inr" in s and "HELD | last trusted 2026-10-19" in s
    assert badge.COLORS["HELD"] in s
    assert not re.search(r">[^<]*\d{5,}", s)  # no amounts in the visible text


def test_svg_escapes_text():
    assert "<script>" not in badge.svg("<script>", "TRUSTED", None)


def test_latest_follows_the_gate(duck):
    ingest(duck, DAY, "unit_paise")
    gate.run(duck, DAY)
    got = badge.latest(duck)
    assert got["status"] == "HELD" and got["day"] == DAY and got["last_trusted"] < DAY
    ingest(duck, DAY, "healthy")
    gate.run(duck, DAY)
    got = badge.latest(duck, "daily_revenue_inr")
    assert got["status"] == "TRUSTED" and got["last_trusted"] == DAY
    assert badge.latest(duck, "no_such_metric") is None


@pytest.fixture(scope="module")
def client(data_dir, tmp_path_factory):
    mp = pytest.MonkeyPatch()
    mp.setenv("RECEIPTS_BACKEND", "duckdb")
    mp.setenv("RECEIPTS_DUCKDB", str(tmp_path_factory.mktemp("badgedb") / "b.duckdb"))
    mp.setenv("RECEIPTS_DATA", str(data_dir))
    mp.delenv("RECEIPTS_LAB", raising=False)
    from receipts.db import connect
    from receipts.load import init_database
    be = connect()
    init_database(be, data_dir, log=lambda *a: None)
    be.close()
    import receipts.api as api
    importlib.reload(api)
    yield TestClient(api.app)
    mp.undo()


def test_badge_endpoints_in_normal_mode(client):
    r = client.get("/badge.svg")
    assert r.status_code == 200 and r.headers["content-type"].startswith("image/svg+xml")
    assert "daily_revenue_inr" in r.text and "TRUSTED" in r.text
    assert client.get("/badge/daily_revenue_inr.svg").status_code == 200
    assert client.get("/badge/nope.svg").status_code == 404
