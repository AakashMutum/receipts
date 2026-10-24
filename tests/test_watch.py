"""The watcher behind `receipts serve --watch` and `receipts watch --once`, on the DuckDB stand-in."""

import json
import threading
import time

import pytest

from receipts import gate
from receipts.db import DuckDBBackend
from receipts.load import ingest, init_database
from receipts.watch import Watcher, dismiss, open_alerts, pending_day

from .conftest import DAY


@pytest.fixture(scope="module")
def be(data_dir):
    b = DuckDBBackend(":memory:")
    init_database(b, data_dir, log=lambda *a: None)
    yield b
    b.close()


def watcher(be, tmp_path, **kw):
    logs = []
    w = Watcher(lambda: be, alerts_dir=tmp_path / "alerts", log=logs.append, **kw)
    return w, logs


def alert_files(tmp_path):
    return sorted(p.name for p in (tmp_path / "alerts").glob("*")) if (tmp_path / "alerts").exists() else []


def test_nothing_pending_right_after_init(be, tmp_path):
    assert pending_day(be) is None
    w, _ = watcher(be, tmp_path)
    assert w.check_once() == []


def test_clean_batch_raises_no_alert(be, tmp_path):
    ingest(be, DAY, "healthy")
    assert pending_day(be) == DAY
    w, logs = watcher(be, tmp_path)
    cases = w.check_once()
    assert [c["verdict"] for c in cases] == ["NO_INCIDENT"]
    assert alert_files(tmp_path) == []
    assert any("published" in m for m in logs)
    assert w.check_once() == []  # judged once, not again


def test_bad_batch_raises_one_alert_until_approved(be, tmp_path):
    ingest(be, DAY, "ist_utc")
    w, logs = watcher(be, tmp_path)
    (case,) = w.check_once()
    assert case["verdict"] == "PROVEN_FAULT"
    cid = case["case_id"]
    assert alert_files(tmp_path) == [f"{cid}.json", f"{cid}.txt"]
    a = json.loads((tmp_path / "alerts" / f"{cid}.json").read_text(encoding="utf-8"))
    assert "clock shift" in a["cause"] and a["last_trusted_value"] and a["link"].endswith(f"?case={cid}")
    assert f"Receipt: {a['link']}" in (tmp_path / "alerts" / f"{cid}.txt").read_text(encoding="utf-8")
    assert sum(m.startswith("ALERT") for m in logs) == 1
    assert w.check_once() == [] and len(alert_files(tmp_path)) == 2  # no second alert
    assert [x["case_id"] for x in open_alerts(be, tmp_path / "alerts")] == [cid]
    gate.approve(be, cid, "test")
    assert open_alerts(be, tmp_path / "alerts") == []


def test_dismissed_alert_is_no_longer_open(be, tmp_path):
    ingest(be, DAY, "duplicate_load")
    w, _ = watcher(be, tmp_path)
    (case,) = w.check_once()
    assert len(open_alerts(be, tmp_path / "alerts")) == 1
    assert dismiss(tmp_path / "alerts", case["case_id"])
    assert open_alerts(be, tmp_path / "alerts") == []


def test_failing_slack_does_not_stop_the_alert(be, tmp_path):
    ingest(be, DAY, "unit_paise")
    w, logs = watcher(be, tmp_path, slack_url="http://127.0.0.1:9/no-slack-here")
    (case,) = w.check_once()
    assert case["verdict"] == "PROVEN_FAULT"
    assert len(alert_files(tmp_path)) == 2
    assert any("could not post to Slack" in m for m in logs)


def test_inbox_scenarios_are_lab_only(be, tmp_path, data_dir):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "ist_utc.batch").write_text("", encoding="utf-8")
    w, logs = watcher(be, tmp_path, inbox_dir=inbox, lab_mode=False, data_dir=data_dir)
    assert w.check_once() == []
    assert (inbox / "ignored" / "ist_utc.batch").exists() and any("lab mode is off" in m for m in logs)
    (inbox / "ist_utc.batch").write_text("", encoding="utf-8")
    w, logs = watcher(be, tmp_path, inbox_dir=inbox, lab_mode=True, data_dir=tmp_path)  # no manifest there
    assert w.check_once() == [] and any("does not look like the built-in synthetic data" in m for m in logs)


def test_inbox_file_lands_a_batch(be, tmp_path, data_dir):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "join_fanout.batch").write_text("", encoding="utf-8")
    w, logs = watcher(be, tmp_path, inbox_dir=inbox, lab_mode=True, data_dir=data_dir)
    (case,) = w.check_once()
    assert case["verdict"] == "PROVEN_FAULT" and case["confirmed"] == ["key_fanout"]
    assert (inbox / "processed" / "join_fanout.batch").exists() and not (inbox / "join_fanout.batch").exists()
    (inbox / "not_a_scenario.txt").write_text("", encoding="utf-8")
    assert w.check_once() == []
    assert (inbox / "ignored" / "not_a_scenario.txt").exists()
    assert any("ignored inbox file" in m for m in logs)


def test_a_failing_check_never_raises():
    logs = []

    def broken():
        raise RuntimeError("database is down")

    w = Watcher(broken, log=logs.append)
    assert w.tick() is False
    assert "database is down" in logs[-1]


def test_loop_sleeps_between_checks_and_stops(tmp_path):
    calls = []
    w = Watcher(lambda: None, log=lambda m: None)
    w.check_once = lambda: calls.append(time.monotonic()) or []
    stop = threading.Event()
    t = threading.Thread(target=w.run_forever, args=(0.2, stop))
    t.start()
    time.sleep(0.5)
    stop.set()
    t.join(2)
    assert not t.is_alive()
    assert 2 <= len(calls) <= 4  # one check right away, then one per interval, nothing in between
