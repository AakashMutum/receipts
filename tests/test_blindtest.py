"""Blind test kit: the guided prompt, the gate run, and the results file."""

from receipts import blindtest
from receipts.cli import main

from .conftest import DAY


def test_prompt_validates_answers():
    answers = iter(["9", "1", "abc", "250", "5", "GW_X", "GW_A", "AB", "first try"])
    fault, share, gw, tester, note = blindtest.ask(lambda _: next(answers))
    assert (fault, share, gw, tester, note) == ("unit_scale", 0.05, "GW_A", "AB", "first try")
    clean = iter(["7", "", ""])
    assert blindtest.ask(lambda _: next(clean))[0] is None


def test_planted_fault_is_judged_and_tonight_restored(duck):
    r = blindtest.judge(duck, DAY, "clock_shift", 1.0, "GW_B")
    assert r["correct"] == "yes" and r["confirmed"] == ["clock_shift"]
    assert duck.scalar(f"SELECT COUNT(*) FROM RAW.PAYMENTS WHERE BATCH_DAY = DATE '{DAY}'") == 0


def test_clean_night_is_published(duck):
    r = blindtest.judge(duck, DAY, None, 1.0, None)
    assert r["outcome"] == "clean, published" and r["correct"] == "yes"


def test_results_file_gets_a_header_once_and_one_line_per_run(tmp_path):
    f = tmp_path / "r.md"
    r = {"verdict": "UNEXPLAINED", "confirmed": [], "outcome": "held, nothing proven",
         "correct": "safe miss (held, no cause)", "error_pct": 8.7}
    blindtest.append(f, blindtest.row("A|B", "unit_scale", 0.02, "GW_A", r, "note"))
    blindtest.append(f, blindtest.row("C", None, 1.0, None, r))
    text = f.read_text(encoding="utf-8")
    assert text.count("| When |") == 1 and text.count("\n| 20") == 2
    assert "A/B" in text and "| none | - |" in text and chr(0x2014) not in text


def test_refused_without_lab_mode(monkeypatch, capsys):
    monkeypatch.delenv("RECEIPTS_LAB", raising=False)
    try:
        main(["blindtest", "--fault", "none"])
    except SystemExit as e:
        assert e.code == 3
    assert "lab mode only" in capsys.readouterr().err
