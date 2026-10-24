"""receipts scale on the stand-in, at two tiny sizes."""

from receipts import scale


def test_scale_records_each_size_and_stops_on_failure(monkeypatch):
    rep = scale.run([2000, 3000], backend="duckdb", log=lambda *a: None)
    assert [r["orders_per_day"] for r in rep["results"]] == [2000, 3000]
    r = rep["results"][0]
    assert r["payment_rows"] > 2000 * 40 and r["cube_ms"] > 0 and r["load_s"] >= 0
    md = scale.to_markdown(rep)
    assert "Largest size measured: **3,000 orders a day" in md and chr(0x2014) not in md

    def boom(*a, **k):
        raise MemoryError("out of memory")
    monkeypatch.setattr(scale, "one", boom)
    rep = scale.run([2000, 4000], backend="duckdb", log=lambda *a: None)
    assert rep["results"] == [] and "failed at 2,000" in rep["stopped"]
