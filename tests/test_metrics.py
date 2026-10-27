"""Configurable metrics: receipts.yaml, `receipts connect --check`, and a second metric through the same gate."""

import pytest

from receipts import gate, metrics
from receipts.config import ROOT
from receipts.connect import outcome
from receipts.load import ingest

from .conftest import DAY


def _yaml(tmp_path, text):
    p = tmp_path / "m.yaml"
    p.write_text(text, encoding="utf-8")
    return p


def test_shipped_config_loads_with_one_published_metric():
    ms = metrics.load(ROOT / "receipts.yaml")
    assert [m.name for m in ms] == ["daily_revenue_inr", "daily_order_count", "avg_basket_inr"]
    assert [m.publish for m in ms] == [True, False, False]


def test_missing_config_falls_back_to_revenue(tmp_path):
    assert metrics.load(tmp_path / "none.yaml") == [metrics.DEFAULT]


@pytest.mark.parametrize("text,msg", [
    ("metrics: []", "at least one metric"),
    ("metrics:\n  - name: x\n    view: PIPE.V", "missing: value_column"),
    ("metrics:\n  - {name: x, view: PIPE.V, value_column: V, weekday_baseline: sometimes}", "auto, on or off"),
    ("metrics:\n  - {name: x, view: PIPE.V, value_column: V}\n  - {name: x, view: PIPE.W, value_column: V}", "unique"),
    ("metrics:\n  - {name: x, view: PIPE.V, value_column: V, publish: true}", "supported for daily_revenue_inr only"),
    ("metrics: [", "not valid YAML"),
])
def test_bad_configs_get_plain_english_errors(tmp_path, text, msg):
    with pytest.raises(metrics.ConfigError, match=msg):
        metrics.load(_yaml(tmp_path, text))


def test_check_passes_on_the_shipped_config(duck):
    res = metrics.check(duck, metrics.load(ROOT / "receipts.yaml"))
    assert all(ok for ok, _ in res), [m for ok, m in res if not ok]


def test_check_names_each_problem(duck):
    bad = [metrics.Metric("a", "PIPE.NO_SUCH_VIEW", "V"),
           metrics.Metric("b", "PIPE.DAILY_ORDERS", "NOPE", raw_tables=("RAW.MISSING",)),
           metrics.Metric("c", "PIPE.DAILY_ORDERS", "TXN_DAY", amount="RAW.PAYMENTS.GATEWAY", time="RAW.PAYMENTS.AMOUNT")]
    msgs = [m for ok, m in metrics.check(duck, bad) if not ok]
    assert any("PIPE.NO_SUCH_VIEW does not exist" in m for m in msgs)
    assert any("value column NOPE is not in PIPE.DAILY_ORDERS" in m for m in msgs)
    assert any("RAW.MISSING does not exist" in m for m in msgs)
    assert any("value column PIPE.DAILY_ORDERS.TXN_DAY is DATE" in m and "a number" in m for m in msgs)
    assert any("amount column RAW.PAYMENTS.GATEWAY" in m for m in msgs)
    assert any("time column RAW.PAYMENTS.AMOUNT" in m for m in msgs)


def test_order_count_goes_through_the_same_gate_without_write_back(duck):
    ms = {m.name: m for m in metrics.load(ROOT / "receipts.yaml")}
    ingest(duck, DAY, "ist_utc")
    before = duck.scalar("SELECT COUNT(*) FROM PUB.DAILY_REVENUE_PUBLISHED")
    c = gate.run(duck, DAY, metric=ms["daily_order_count"])
    assert c["metric"] == "daily_order_count" and c["verdict"] == "PROVEN_FAULT" and c["confirmed"] == ["clock_shift"]
    basket = gate.run(duck, DAY, metric=ms["avg_basket_inr"])
    assert basket["trust_status"] == "TRUSTED"  # a clock shift moves rows between days, not the basket size
    assert duck.scalar("SELECT COUNT(*) FROM PUB.DAILY_REVENUE_PUBLISHED") == before


def test_history_snapshot_keeps_a_fan_out_from_moving_the_baseline(duck):
    """A fan-out rewrites past days in the views; the baseline comes from the snapshot taken at build time."""
    ms = {m.name: m for m in metrics.load(ROOT / "receipts.yaml")}
    assert duck.scalar("SELECT COUNT(*) FROM RECEIPTS.METRIC_HISTORY WHERE METRIC_NAME = 'avg_basket_inr'") > 30
    ingest(duck, DAY, "join_fanout")
    c = gate.run(duck, DAY, metric=ms["avg_basket_inr"])
    assert c["verdict"] == "PROVEN_FAULT" and c["confirmed"] == ["key_fanout"]
    assert c["combined_undo"]["history_check"] == "RESTORED"


def test_shadow_exasol_path_runs_the_second_metric(shadow):
    ms = {m.name: m for m in metrics.load(ROOT / "receipts.yaml")}
    ingest(shadow, DAY, "ist_utc")
    assert gate.run(shadow, DAY, metric=ms["daily_order_count"])["confirmed"] == ["clock_shift"]


def test_weekday_option_off_uses_the_flat_baseline():
    from datetime import date, timedelta
    hist = {date(2026, 9, 1) + timedelta(days=i): (200.0 if (date(2026, 9, 1) + timedelta(days=i)).weekday() == 5 else 100.0)
            for i in range(35)}
    sat = date(2026, 10, 10)
    assert gate.expected(hist, sat, "auto")[2] is True
    assert gate.expected(hist, sat, "off")[2] is False


def test_outcome_labels():
    assert outcome(True, 10, False) == "held, right"
    assert outcome(False, 10, False) == "published WRONG"
    assert outcome(True, 1, False) == "held, metric was fine"
    assert outcome(False, 30, True) == "published, right"
