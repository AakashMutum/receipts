"""The red team: classification, the shrinking search, the report, and one real attack on the stand-in."""

from receipts import redteam
from receipts.faults import FAULT_CLASSES

from .conftest import DAY


def _case(verdict, confirmed, trust, value):
    return {"verdict": verdict, "confirmed": confirmed, "trust_status": trust, "values": {"candidate": value},
            "total_ms": 1.0}


def test_classify_names_every_outcome():
    c = redteam.classify
    assert c(_case("PROVEN_FAULT", ["unit_scale"], "HELD", 200), {"unit_scale"}, 100)["outcome"] == "caught"
    assert c(_case("UNEXPLAINED", [], "HELD", 200), {"unit_scale"}, 100)["outcome"] == "held"
    assert c(_case("PROVEN_FAULT", ["orphan_code"], "HELD", 99), {"orphan_code", "duplicate_key"}, 100)["outcome"] == "held_partial"
    assert c(_case("PROVEN_FAULT", ["stale_feed"], "HELD", 90), {"clock_shift"}, 100)["outcome"] == "wrong_cause"
    small = c(_case("NO_INCIDENT", [], "TRUSTED", 103), {"clock_shift"}, 100)
    assert small["outcome"] == "small" and not small["wrong_published"]
    wrong = c(_case("NO_INCIDENT", [], "TRUSTED", 110), {"clock_shift"}, 100)
    assert wrong["outcome"] == "WRONG" and wrong["wrong_published"] and wrong["outcome"] in redteam.HOLES


def test_ladder_keeps_looking_below_the_floor_for_holes(monkeypatch):
    # caught at 100 and 50, held at 25 with a big error, published WRONG at 10, then too small to matter
    script = {1.0: ("caught", 300), 0.5: ("held", 150), 0.25: ("caught", 60), 0.10: ("WRONG", 9), 0.05: ("small", 3),
              0.02: ("small", 1)}

    def fake(be, day, kinds, truth):
        out, err = script[kinds[0][1]]
        return {"outcome": out, "error_pct": err, "verdict": "x", "faults": [{"fault": kinds[0][0], "share": kinds[0][1],
                "gateway": None}], "confirmed": [], "trust": "HELD"}
    monkeypatch.setattr(redteam, "attack", fake)
    lad = redteam.ladder(None, DAY, "duplicate_key", 100.0, log=lambda *a: None)
    assert lad["floor"] == 1.0  # 25% was caught again, but the floor is the unbroken run from the top
    assert [s["faults"][0]["share"] for s in lad["steps"]] == [1.0, 0.5, 0.25, 0.10, 0.05]  # stopped under 4%
    assert [h["outcome"] for h in lad["holes"]] == ["WRONG"]
    assert len(redteam.ladder(None, DAY, "stale_feed", 100.0, log=lambda *a: None)["steps"]) == 1  # binary


def test_one_real_attack_restores_tonight(duck):
    truth = redteam.clean_value(duck, DAY)
    r = redteam.attack(duck, DAY, [("clock_shift", 1.0, "GW_B")], truth)
    assert r["outcome"] == "caught" and r["confirmed"] == ["clock_shift"] and r["error_pct"] < -4
    assert duck.scalar(f"SELECT COUNT(*) FROM RAW.PAYMENTS WHERE BATCH_DAY = DATE '{DAY}'") == 0
    assert duck.scalar(f"SELECT COUNT(*) FROM PUB.DAILY_REVENUE_PUBLISHED WHERE TXN_DAY = DATE '{DAY}'") == 0


def test_report_lists_holes_and_has_no_em_dashes():
    step = {"outcome": "WRONG", "verdict": "NO_INCIDENT", "trust": "TRUSTED", "confirmed": [], "right_cause": False,
            "wrong_published": True, "held_no_cause": False, "error_pct": 6.1, "ms": 1.0,
            "faults": [{"fault": "orphan_code", "share": 0.1, "gateway": None}]}
    ladders = [{"fault": k, "gateway": None, "steps": [step], "floor": None, "binary": k == "stale_feed",
                "holes": [step]} for k in FAULT_CLASSES]
    runs = [{"seed": 1, "clean_value": 1.0, "ladders": ladders, "unit_gateways": [], "combos": []}]
    rep = {"backend": {"backend": "duckdb", "standin": True}, "seeds": [1], "orders_per_day": 100, "shares": redteam.SHARES,
           "wrong_pct": 4.0, "runs": runs, "summary": redteam.summarise(runs), "seconds": 60, "generated_at": "now"}
    md = redteam.to_markdown(rep, "receipts redteam")
    assert "never on live production tables" in md and "published a number +6.10% off as trusted" in md
    assert chr(0x2014) not in md
