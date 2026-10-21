"""The incoming day: yesterday in India by default, or --day. Tests never depend on the wall clock."""

from datetime import date, datetime, timezone

import pytest

from receipts import agent, gate, model
from receipts.cli import main
from receipts.db import connect
from receipts.load import incoming_day, ingest


def test_default_day_is_yesterday_in_india():
    # 20:00 UTC on 21 Oct is 01:30 on 22 Oct in India, so yesterday there is 21 Oct, not 20 Oct
    assert model.default_incoming_day(datetime(2026, 10, 21, 20, 0, tzinfo=timezone.utc)) == date(2026, 10, 21)
    assert model.default_incoming_day(datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)) == date(2026, 10, 20)


def _init(*args):
    with pytest.raises(SystemExit) as e:
        main(["init", "--orders-per-day", "1500", *args])
    assert e.value.code == 0


def test_init_builds_for_the_chosen_day(tmp_path, monkeypatch):
    monkeypatch.setenv("RECEIPTS_BACKEND", "duckdb")
    monkeypatch.setenv("RECEIPTS_DUCKDB", str(tmp_path / "day.duckdb"))
    monkeypatch.setenv("RECEIPTS_DATA", str(tmp_path / "data"))
    monkeypatch.setattr(model, "default_incoming_day", lambda now=None: date(2026, 3, 2))

    _init()  # no --day: "yesterday", patched above
    be = connect()
    assert incoming_day(be) == date(2026, 3, 2)
    ingest(be, date(2026, 3, 2), "healthy")
    case = gate.run(be, date(2026, 3, 2), {"id": "healthy"}, write_back=False)
    assert case["case_id"].startswith("RC-20260302-")
    assert agent.ask(be, date(2026, 3, 2))["question"] == "What was our revenue on Mon 02 Mar?"
    be.close()

    _init("--day", "2026-03-09")  # another day regenerates the data even without --fresh
    be = connect()
    assert incoming_day(be) == date(2026, 3, 9)
    be.close()


def test_bad_day_is_rejected():
    with pytest.raises(SystemExit) as e:
        main(["init", "--day", "20-10-2026"])
    assert e.value.code == 2
