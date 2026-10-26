"""Blast radius: which views read the affected metric or column, and which the gate protected."""

import sqlglot

from receipts import blast, gate
from receipts.lineage import parse_view
from receipts.load import ingest

from .conftest import DAY

METRIC = ("PIPE.M", "V")


def _views(defs: dict[str, str]):
    out = {}
    for full, sql in defs.items():
        s, n = full.split(".")
        out[full] = parse_view(n, sql, "duckdb", s)
    return out


def test_chain_of_views():
    v = _views({"MART.A": "SELECT m.D, m.V FROM PIPE.M m",
                "MART.B": "SELECT a.D, a.V * 2 AS V2 FROM MART.A a",
                "MART.C": "SELECT b.V2 FROM MART.B b"})
    r = blast.radius(v, METRIC, set(), {"PIPE.M"})
    assert r["exposed"] == ["MART.A", "MART.B", "MART.C"] and r["count"] == 3


def test_diamond_counts_each_view_once():
    v = _views({"MART.L": "SELECT m.D, m.V FROM PIPE.M m",
                "MART.R": "SELECT m.D, m.V + 1 AS V FROM PIPE.M m",
                "MART.J": "SELECT l.D, l.V + r.V AS V FROM MART.L l JOIN MART.R r ON r.D = l.D"})
    r = blast.radius(v, METRIC, set(), {"PIPE.M"})
    assert r["exposed"] == ["MART.J", "MART.L", "MART.R"]


def test_view_that_does_not_depend_on_the_metric():
    v = _views({"MART.A": "SELECT m.D, m.V FROM PIPE.M m",
                "MART.OTHER": "SELECT c.CODE, c.NAME FROM PIPE.CATS c",
                "MART.ONLY_DAY": "SELECT m.D FROM PIPE.M m"})
    r = blast.radius(v, METRIC, set(), {"PIPE.M"})
    assert r["exposed"] == ["MART.A"]


def test_row_filter_on_an_affected_column_counts():
    v = _views({"MART.BIG_DAYS": "SELECT m.D FROM PIPE.M m WHERE m.V > 100"})
    assert blast.radius(v, METRIC, set(), {"PIPE.M"})["exposed"] == ["MART.BIG_DAYS"]


def test_no_downstream_objects():
    v = _views({"MART.OTHER": "SELECT c.CODE FROM PIPE.CATS c"})
    r = blast.radius(v, METRIC, set(), {"PIPE.M"})
    assert r["exposed"] == [] and r["count"] == 0 and r["protected"] == []


def test_blamed_raw_column_reaches_views_beside_the_metric():
    v = _views({"PIPE.F": "SELECT r.D, r.AMT FROM RAW.P r",
                "MART.BY_DAY": "SELECT f.D, f.AMT FROM PIPE.F f"})
    r = blast.radius(v, METRIC, {("RAW.P", "AMT")}, {"PIPE.M", "PIPE.F", "RAW.P"})
    assert r["exposed"] == ["MART.BY_DAY"]


def test_readers_of_published_values_are_protected():
    v = _views({"PUB.T": "SELECT p.D, p.V FROM PUB.DAILY_REVENUE_PUBLISHED p",
                "MART.EXEC": "SELECT t.D FROM PUB.T t"})
    r = blast.radius(v, METRIC, set(), {"PIPE.M"})
    assert r["exposed"] == [] and r["protected"] == ["MART.EXEC", "PUB.T"]


def test_held_case_lists_readers_and_publishes_count(duck):
    ingest(duck, DAY, "ist_utc")
    c = gate.run(duck, DAY)
    b = c["blast_radius"]
    assert b["exposed"] == ["MART.AVG_TICKET", "MART.CITY_REVENUE", "MART.FINANCE_DAILY"]
    assert "MART.CATEGORY_LIST" not in b["exposed"] + b["protected"]
    assert {"PUB.METRIC_TRUST", "PUB.DASHBOARD_REVENUE", "MART.EXEC_SUMMARY"} <= set(b["protected"])
    assert b["reads"] == {"available": False, "note": "not available on this backend (the stand-in keeps no query log)"}
    r = duck.query(f"SELECT DOWNSTREAM_COUNT, DOWNSTREAM_OBJECTS FROM PUB.METRIC_TRUST WHERE TXN_DAY = DATE '{DAY}'")[0]
    assert r["downstream_count"] == 3 and "MART.FINANCE_DAILY" in r["downstream_objects"]


def test_exasol_sql_path_gives_the_same_readers(shadow):
    ingest(shadow, DAY, "ist_utc")
    c = gate.run(shadow, DAY)
    assert c["blast_radius"]["exposed"] == ["MART.AVG_TICKET", "MART.CITY_REVENUE", "MART.FINANCE_DAILY"]


def test_audit_query_parses_as_exasol():
    since = "(SELECT MAX(PUBLISHED_AT) FROM PUB.DAILY_REVENUE_PUBLISHED WHERE TXN_DAY < DATE '2026-10-20')"
    sql = blast.audit_reads_sql(["MART.FINANCE_DAILY", "MART.AVG_TICKET"], since)
    tree = sqlglot.parse_one(sql, read="exasol")
    assert {t.name for t in tree.find_all(sqlglot.exp.Table)} >= {"EXA_DBA_AUDIT_SQL", "EXA_DBA_AUDIT_SESSIONS"}
