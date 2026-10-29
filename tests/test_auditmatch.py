"""Audit-log match: the matcher itself, and the command refusing on the stand-in."""

from receipts import auditmatch
from receipts.cli import main


def test_exact_whitespace_and_semicolon_are_ignored():
    m = auditmatch.match(["SELECT 1 FROM DUAL;", "select  a\nfrom t"], ["select 1 from dual", "SELECT A FROM T"])
    assert (m["issued"], m["matched"], m["different"], m["missing"], m["extra"]) == (2, 2, 0, 0, 0)


def test_long_statement_with_a_changed_tail_is_different_not_missing():
    head = "SELECT TXN_DAY, TRUST_STATUS, TRUSTED_VALUE, LAST_TRUSTED_DAY, CASE_ID FROM PUB.METRIC_TRUST WHERE "
    m = auditmatch.match([head + "TXN_DAY = DATE '2026-10-20'"], [head + "TXN_DAY = DATE '2026-10-20' LIMIT 100"])
    assert (m["matched"], m["different"], m["missing"]) == (0, 1, 0)


def test_missing_and_extra_are_counted_and_extras_are_named():
    m = auditmatch.match(["DELETE FROM RAW.X", "SELECT 2"],
                         ["SELECT 2", "SELECT CURRENT_STATEMENT FROM DUAL", "FLUSH STATISTICS"])
    assert (m["matched"], m["missing"], m["extra"]) == (1, 1, 2)
    assert m["extra_kinds"] == {"timing marker (SELECT CURRENT_STATEMENT)": 1, "FLUSH STATISTICS": 1}


def test_each_audit_row_is_used_once():
    m = auditmatch.match(["SELECT 1", "SELECT 1"], ["SELECT 1"])
    assert (m["matched"], m["missing"]) == (1, 1)


def test_report_has_no_em_dashes():
    m = auditmatch.match(["SELECT 1"], ["SELECT 1"])
    md = auditmatch.to_markdown({"exasol": "x", "day": "d", "case": "c", "verdict": "v", "seconds": 1, "gate": m,
                                 "mcp": None}, "receipts audit-match")
    assert "| 1 | 1 | 0 | 0 | 0 |" in md and chr(0x2014) not in md


def test_report_has_one_row_per_run_and_names_a_difference():
    a = auditmatch.match(["SELECT 1"], ["SELECT 1"])
    b = auditmatch.match(["SELECT 1", "SELECT 2"], ["SELECT 1"])
    rep = lambda m, c: {"exasol": "x", "day": "d", "case": c, "verdict": "v", "seconds": 1, "gate": m, "mcp": None}
    md = auditmatch.to_markdown([rep(a, "c1"), rep(b, "c2")], "receipts audit-match --runs 2")
    assert "| 1 | c1 | v | 1 | 1 | 1 | 0 | 0 | 0 |" in md and "| 2 | c2 | v | 1 | 2 | 1 | 0 | 1 | 0 |" in md
    assert "Not matched exactly in run 2" in md and "2 full runs" in md


def test_refused_on_the_stand_in(monkeypatch, capsys):
    monkeypatch.setenv("RECEIPTS_BACKEND", "duckdb")
    try:
        main(["audit-match"])
    except SystemExit as e:
        assert e.code == 2
    assert "needs Exasol" in capsys.readouterr().err
