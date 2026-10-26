"""Wrong-fix control: deliberately wrong corrections go through the gate's own rules."""

from receipts import gate, redteam, wrongfix
from receipts.load import ingest

from .conftest import DAY


def test_the_right_fix_is_never_among_the_wrong_ones(duck):
    fixes = wrongfix.wrong_fixes(duck, DAY, {"unit_scale": "GW_C"})
    labels = [f[1] for f in fixes]
    assert "unit fix (divide by 100) on GW_C" not in labels
    assert {"unit fix (divide by 100) on GW_A", "divide GW_C by 10 instead of 100"} <= set(labels)
    assert "remove duplicate payments in tonight's batch" in labels
    dup = wrongfix.wrong_fixes(duck, DAY, {"duplicate_key": None})
    assert "remove duplicate payments in tonight's batch" not in [f[1] for f in dup]


def test_wrong_factor_wrong_gateway_and_every_day_are_rejected(duck):
    ingest(duck, DAY, "unit_paise")
    c = gate.run(duck, DAY, write_back=False)
    assert c["confirmed"] == ["unit_scale"]
    rows = {r["fix"]: r for r in wrongfix.control(duck, DAY, c, wrongfix.planted_of(["unit_scale"], c))}
    assert not rows["divide GW_C by 10 instead of 100"]["accepted"]
    assert not rows["unit fix (divide by 100) on GW_A"]["accepted"]
    every = rows["divide GW_C by 100 on every day, not only tonight"]
    assert every["history"] == "ALTERED" and not every["accepted"]
    assert not rows["remove duplicate payments in tonight's batch"]["accepted"]


def test_summary_lists_accepted_fixes_by_name():
    rows = [{"kind": "wrong_gateway", "fix": "a", "accepted": False}, {"kind": "different_cause", "fix": "b", "accepted": True}]
    s = wrongfix.summary(rows)
    assert (s["tried"], s["rejected"], s["accepted"]) == (2, 1, 1) and s["accepted_list"][0]["fix"] == "b"


def test_redteam_attack_runs_the_control_and_restores_tonight(duck):
    truth = redteam.clean_value(duck, DAY)
    r = redteam.attack(duck, DAY, [("clock_shift", 1.0, "GW_B")], truth, control=True)
    assert r["outcome"] == "caught" and r["wrong_fixes"]
    assert all("clock fix (shift back 5.5 hours) on GW_B" != w["fix"] for w in r["wrong_fixes"])
    assert duck.scalar(f"SELECT COUNT(*) FROM RAW.PAYMENTS WHERE BATCH_DAY = DATE '{DAY}'") == 0


def test_report_has_no_em_dashes():
    rep = {"backend": {"backend": "duckdb", "standin": True}, "seeds": [1], "orders_per_day": 100, "seconds": 1,
           "generated_at": "now", "rows": [], "summary": wrongfix.summary([])}
    md = wrongfix.to_markdown(rep, "receipts wrongfix")
    assert "accepted 0" in md and chr(0x2014) not in md
