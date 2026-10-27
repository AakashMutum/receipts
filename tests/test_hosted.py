"""Public demo guards: rate limits on writing actions, automatic reset, and the usual lab rules still apply."""

import importlib

import pytest
from fastapi.testclient import TestClient

from receipts import hosted
from receipts.config import ROOT


def test_rate_limiter_per_client_and_total():
    now = [0.0]
    rl = hosted.RateLimiter(per_client=2, total=3, window=60, clock=lambda: now[0])
    assert rl.allow("a")[0] and rl.allow("a")[0]
    ok, wait = rl.allow("a")
    assert not ok and 0 < wait <= 60
    assert rl.allow("b")[0]
    assert not rl.allow("c")[0]  # the server-wide limit
    now[0] = 61
    assert rl.allow("a")[0]


def test_auto_reset_after_idle_minutes():
    now, calls = [0.0], []
    ar = hosted.AutoReset(lambda: calls.append(1), idle_min=10, clock=lambda: now[0])
    assert not ar.tick()  # nothing happened yet
    ar.touched()
    now[0] = 599
    assert not ar.tick()
    now[0] = 600
    assert ar.tick() and calls == [1]
    assert not ar.tick()  # once per idle period


def test_dockerfile_public_target_is_locked_down():
    text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "AS public" in text and "RECEIPTS_PUBLIC_DEMO=1" in text and "ANTHROPIC_API_KEY=" in text
    assert "USER demo" in text and text.rstrip().endswith("FROM local")
    assert 'build-target = "public"' in (ROOT / "fly.toml").read_text(encoding="utf-8")


def _client(data_dir, tmp_path_factory, mp, lab: bool):
    mp.setenv("RECEIPTS_BACKEND", "duckdb")
    mp.setenv("RECEIPTS_DUCKDB", str(tmp_path_factory.mktemp("pubdb") / "p.duckdb"))
    mp.setenv("RECEIPTS_DATA", str(data_dir))
    mp.setenv("RECEIPTS_PUBLIC_DEMO", "1")
    mp.setenv("RECEIPTS_DEMO_PER_MIN", "1")
    mp.setenv("RECEIPTS_LAB", "1" if lab else "0")
    from receipts.db import connect
    from receipts.load import init_database
    b = connect()
    init_database(b, data_dir, log=lambda *a: None)
    b.close()
    import receipts.api as api
    importlib.reload(api)
    return TestClient(api.app), api


@pytest.fixture()
def mp():
    m = pytest.MonkeyPatch()
    yield m
    m.undo()
    import receipts.api as api
    importlib.reload(api)


def test_public_demo_rate_limits_reset(data_dir, tmp_path_factory, mp):
    c, api = _client(data_dir, tmp_path_factory, mp, lab=True)
    assert c.post("/api/lab/reset").status_code == 200
    r = c.post("/api/lab/reset")
    assert r.status_code == 429 and "Retry-After" in r.headers
    assert c.post("/api/lab/reset", headers={"x-forwarded-for": "10.0.0.9"}).status_code == 200
    assert api._auto["reset"] is not None  # the automatic reset is scheduled by the first action


def test_public_demo_keeps_normal_mode_write_protection(data_dir, tmp_path_factory, mp):
    c, _ = _client(data_dir, tmp_path_factory, mp, lab=False)
    assert c.post("/api/lab/break", json={"fault": "clock_shift", "share": 1.0}).status_code == 403
    assert c.post("/api/lab/reset").status_code == 403
    assert c.get("/badge.svg").status_code == 200
