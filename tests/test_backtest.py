"""The real-data backtest adapter, on a tiny file in the TLC layout (no download)."""

from datetime import date

import duckdb

from receipts import backtest
from receipts.faults import SCENARIOS


def _tiny_tlc(tmp_path):
    trips = tmp_path / "yellow_tripdata_2024-01.parquet"
    duckdb.connect().execute(f"""COPY (
        SELECT * FROM (VALUES
          (1, TIMESTAMP '2024-01-01 08:00:00', 132, 1, 1, 70.0),
          (2, TIMESTAMP '2024-01-01 23:59:00', 161, 1, 2, 20.0),
          (2, TIMESTAMP '2024-01-02 00:01:00', 161, 2, 1, 50.0),
          (2, TIMESTAMP '2024-01-02 12:00:00', 237, 99, 4, -5.0)
        ) t(VendorID, tpep_pickup_datetime, PULocationID, RatecodeID, payment_type, total_amount)
    ) TO '{trips.as_posix()}' (FORMAT PARQUET)""")
    zones = tmp_path / "taxi_zone_lookup.csv"
    zones.write_text('"LocationID","Borough","Zone","service_zone"\n'
                     '132,"Queens","JFK Airport","Airports"\n161,"Manhattan","Midtown Center","Yellow Zone"\n'
                     '237,"Manhattan","Upper East Side South","Yellow Zone"\n', encoding="utf-8")
    return [trips, zones]


def test_adapter_maps_trips_onto_the_pipeline(tmp_path):
    be = backtest.build(tmp_path / "bt.duckdb", _tiny_tlc(tmp_path), date(2024, 1, 1), date(2024, 1, 2),
                        first_judged=date(2024, 1, 2), log=lambda *a: None)
    backtest.land(be, date(2024, 1, 2))
    daily = {str(r["txn_day"])[:10]: r["revenue_inr"] for r in be.query(
        "SELECT TXN_DAY, REVENUE_INR FROM PIPE.DAILY_REVENUE ORDER BY TXN_DAY")}
    assert daily == {"2024-01-01": 90.0, "2024-01-02": 50.0}  # local pickup day; the refund is not captured
    assert be.scalar("SELECT COUNT(*) FROM PUB.DAILY_REVENUE_PUBLISHED") == 1  # only the warm-up day
    gws = {r["gateway"] for r in be.query("SELECT DISTINCT GATEWAY FROM RAW.PAYMENTS")}
    assert gws == {"CMT", "CURB"}
    be.close()


def test_planted_faults_are_valid():
    for day, label, cause, sql in backtest.FAULTS:
        assert date(2024, 2, 5) <= day <= date(2024, 3, 31)
        assert cause in {c for s in SCENARIOS.values() for c in s.expected_causes}
        assert sql and all("{{ day(incoming) }}" in s for s in sql)


def test_report_has_no_em_dashes():
    row = {"day": "2024-02-13", "weekday": "Tue", "value": 1.7e6, "expected": 2.6e6, "change_pct": -0.34,
           "band_pct": 0.2, "seasonal": True, "anomaly": True, "verdict": "REAL_CHANGE", "trust": "REAL_CHANGE",
           "confirmed": [], "fired": [], "ms": 1.0}
    rep = {"dataset": backtest.DATASET, "urls": ["u"], "start": "2024-01-01", "end": "2024-03-31",
           "first_judged": "2024-02-05", "warmup": 35, "trips": 10, "clean": [row], "planted": [], "seconds": 60}
    md = backtest.to_markdown(rep, "receipts backtest")
    assert chr(0x2014) not in md and "Days judged: **1**" in md and "REAL_CHANGE" in md


def test_report_with_timings_and_comparison():
    import json
    from pathlib import Path
    duck = json.loads((Path(__file__).resolve().parent.parent / "samples" / "real_backtest.json").read_text(encoding="utf-8"))
    rep = json.loads(json.dumps(duck))
    rep["backend"] = {"backend": "exasol", "standin": False, "version": "2026.2.0-nano.3", "udf": "in-database"}
    rep["load_seconds"] = 150.0
    for r in rep["clean"] + rep["planted"]:
        r["db_ms"], r["statements"] = r["ms"] * 0.8, 30
    rep["timings"] = backtest._timings(rep["clean"] + rep["planted"])
    rep["clean"][0]["verdict"] = "UNEXPLAINED"
    md = backtest.to_markdown(rep, "receipts backtest --backend exasol", duck)
    assert "on Exasol 2026.2.0-nano.3" in md and "## Timings" in md and "150 s" in md
    assert f"Same verdict and same causes: **{len(duck['clean']) + len(duck['planted']) - 1} of" in md
    assert "Differs on 2024-02-05" in md and chr(0x2014) not in md
