"""The receipt text for two faults that partly cancel: only say the total looked normal when it really did."""

from receipts import explain, gate
from receipts.load import ingest

from .conftest import DAY


def _case(anomaly: bool, moves: list[float]) -> dict:
    sus = [{"title": t, "outcome": "CONFIRMED", "fired": True, "blamed": {"table": "RAW.PAYMENTS", "column": c},
            "slice_text": "whole batch", "move_pct": m}
           for (t, c), m in zip([("Duplicate rows", "PAYMENT_ID"), ("Clock shift", "CAPTURED_AT")], moves)]
    return {"day_label": "Tue 20 Oct 2026", "verdict": "PROVEN_FAULT", "anomaly": anomaly, "suspects": sus,
            "values": {"candidate": 100.0, "corrected": 96.0, "change_pct": 0.047}}


def test_inside_the_range_says_a_threshold_alert_stays_silent():
    text = explain.template(_case(False, [-0.12, 0.08]))
    assert "stayed inside the normal range" in text and "stay silent" in text
    assert "opposite directions" not in text


def test_outside_the_range_says_a_threshold_alert_holds_without_a_cause():
    text = explain.template(_case(True, [-0.12, 0.08]))
    assert "push in opposite directions" in text and "+4.7%" in text
    assert "hold the number without naming a cause" in text and "names both" in text
    assert "stayed inside the normal range" not in text and "looked normal" not in text


def test_a_single_cause_gets_neither_sentence():
    text = explain.template(_case(True, [-0.12]))
    assert "opposite directions" not in text and "stayed inside" not in text


def test_masked_pair_receipt_matches_its_own_range(duck):
    ingest(duck, DAY, "masked_pair")
    c = gate.run(duck, DAY, write_back=False)
    text = c["explanation"]["text"]
    assert c["confirmed"] == ["clock_shift", "duplicate_key"]
    if c["anomaly"]:
        assert "push in opposite directions" in text and "stayed inside" not in text
    else:
        assert "stayed inside the normal range" in text
