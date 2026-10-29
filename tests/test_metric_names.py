"""Hostile names in receipts.yaml are rejected when the file is loaded, before any SQL is built or run."""

import pytest
import yaml

from receipts import metrics
from receipts.metrics import ConfigError

GOOD = {"name": "daily_revenue_inr", "view": "PIPE.DAILY_REVENUE", "value_column": "REVENUE_INR",
        "day_column": "TXN_DAY", "raw_tables": ["RAW.PAYMENTS"], "amount": "RAW.PAYMENTS.AMOUNT",
        "id": "RAW.PAYMENTS.PAYMENT_ID", "time": "RAW.PAYMENTS.CAPTURED_AT", "publish": True}

HOSTILE = [
    ("view", "PIPE.DAILY_REVENUE; DROP TABLE RAW.PAYMENTS"),
    ("view", "PIPE.DAILY_REVENUE WHERE 1=1 --"),
    ("view", 'PIPE."DAILY_REVENUE"'),
    ("view", "PIPE.DAILY_REVENUE'"),
    ("view", "PIPE.SELECT"),
    ("view", "PIPE." + "X" * 129),
    ("view", "A.B.C"),
    ("value_column", "REVENUE_INR) FROM PIPE.DAILY_REVENUE --"),
    ("value_column", "1"),
    ("value_column", "REVENUE INR"),
    ("value_column", "ORDER"),
    ("day_column", "TXN_DAY = TXN_DAY OR 1=1"),
    ("day_column", "DATE"),
    ("raw_tables", ["RAW.PAYMENTS", "RAW.ORDERS; DELETE FROM PUB.DAILY_REVENUE_PUBLISHED"]),
    ("amount", "RAW.PAYMENTS.AMOUNT'||'"),
    ("time", "RAW.PAYMENTS.CAPTURED_AT/*"),
    ("id", "RAW.PAYMENTS.PAYMENT_ID.X"),
    ("name", "x'); DROP TABLE RAW.PAYMENTS; --"),
    ("name", "revenue inr"),
    ("name", "n" * 129),
]


def write(tmp_path, **override):
    p = tmp_path / "receipts.yaml"
    p.write_text(yaml.safe_dump({"metrics": [GOOD | override]}), encoding="utf-8")
    return p


def test_the_shipped_config_loads():
    assert [m.name for m in metrics.load()][0] == "daily_revenue_inr"


@pytest.mark.parametrize("key,value", HOSTILE, ids=[f"{k}-{i}" for i, (k, _) in enumerate(HOSTILE)])
def test_hostile_names_are_rejected_on_load(tmp_path, key, value):
    with pytest.raises(ConfigError, match="plain name|letters, digits and underscores"):
        metrics.load(write(tmp_path, **{key: value}))


def test_mixed_case_is_folded_and_long_names_up_to_the_limit_load(tmp_path):
    long = "V" * 128
    m = metrics.load(write(tmp_path, view=f"pipe.{long}", value_column="Revenue_Inr"))[0]
    assert (m.view, m.value_column) == (f"PIPE.{long}", "REVENUE_INR")


def test_connect_check_refuses_a_hostile_file_before_connecting(tmp_path, monkeypatch, capsys):
    """`receipts connect --check` stops at the loader with exit code 2; no database connection is opened."""
    from receipts import cli, db
    monkeypatch.setattr(db, "connect", lambda *a, **k: pytest.fail("connected to the database"))
    bad = write(tmp_path, view="PIPE.DAILY_REVENUE; DROP TABLE RAW.PAYMENTS")
    try:
        code = cli.main(["connect", "--check", "--config", str(bad)])
    except SystemExit as e:
        code = e.code
    assert code == 2 and "Config problem" in capsys.readouterr().err
