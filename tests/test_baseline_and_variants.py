from datetime import date, timedelta

import pytest

from receipts import gate
from receipts.gate import expected
from receipts.load import ingest
from receipts.variants import VARIANTS, classify

DAY = date(2026, 10, 20)


def _history(factors, noise=0.0, days=35, level=1_000_000.0):
    hist = {}
    for i in range(days):
        d = DAY - timedelta(days=days - i)
        hist[d] = level * (factors[d.weekday()] if factors else 1.0) * (1 + noise * (-1) ** i)
    return hist


def test_flat_history_is_not_called_seasonal():
    # day-to-day noise only, no weekly shape: the plain 14 day baseline must be used
    v, sd, seasonal = expected(_history(None, noise=0.01), DAY)
    assert not seasonal and abs(v - 1_000_000) < 20_000


def test_weekly_shape_is_learned_and_removed():
    f = (0.93, 0.95, 0.97, 1.00, 1.06, 1.16, 1.13)
    sat = DAY + timedelta(days=(5 - DAY.weekday()) % 7)
    v, sd, seasonal = expected(_history(f, noise=0.01), sat)
    assert seasonal
    assert abs(v - 1_000_000 * 1.16) / (1_000_000 * 1.16) < 0.03   # a Saturday is expected to look like a Saturday


def test_short_history_falls_back():
    v, sd, seasonal = expected(_history((0.9, 1, 1, 1, 1, 1.2, 1.2), days=14), DAY)
    assert not seasonal


@pytest.mark.parametrize("vid", ["unit_x10_b", "unit_x1000_c", "unit_x100_a", "dup_3_files", "clock_a", "code_fashion",
                                 "fan_40pct", "pair_unit_dup"])
def test_variants_are_caught(duck, vid):
    sc = next(v for v in VARIANTS if v.id == vid)
    ingest(duck, DAY, "healthy")
    truth = duck.scalar(f"SELECT REVENUE_INR FROM PIPE.DAILY_REVENUE WHERE TXN_DAY = {duck.dialect.day(DAY)}")
    ingest(duck, DAY, sc)
    c = gate.run(duck, DAY, {"id": sc.id, "title": sc.title}, write_back=False)
    outcome, _ = classify(sc, c, truth)
    assert outcome == "caught", (vid, c["verdict"], c["confirmed"])


@pytest.mark.parametrize("vid", ["unit_x100_part25", "unit_x100_part5", "clock_12h"])
def test_known_gaps_fail_safe(duck, vid):
    """These are not caught with a named cause. The requirement is that they are never published as fine."""
    sc = next(v for v in VARIANTS if v.id == vid)
    ingest(duck, DAY, "healthy")
    truth = duck.scalar(f"SELECT REVENUE_INR FROM PIPE.DAILY_REVENUE WHERE TXN_DAY = {duck.dialect.day(DAY)}")
    ingest(duck, DAY, sc)
    c = gate.run(duck, DAY, {"id": sc.id, "title": sc.title}, write_back=False)
    outcome, _ = classify(sc, c, truth)
    assert outcome in ("caught", "held", "small"), (vid, outcome)
