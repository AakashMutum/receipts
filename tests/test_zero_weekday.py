"""A weekday with no trading history (index 0), found on real data: a shop that never trades on Saturdays.

A weekday whose index is 0 expects 0, and it is left out when the weekday-adjusted history is built. Zero on that day
is normal; anything else is held as UNEXPLAINED.
"""

import statistics
from datetime import date, timedelta

from hypothesis import given, settings
from hypothesis import strategies as st

from receipts import gate
from receipts.gate import expected
from receipts.load import ingest

from .conftest import DAY

SHAPE = (0.93, 0.95, 0.97, 1.00, 1.06, 1.16, 1.13)


def _history(factors, noise=0.01, days=35, level=1_000_000.0):
    hist = {}
    for i in range(days):
        d = DAY - timedelta(days=days - i)
        hist[d] = level * factors[d.weekday()] * (1 + noise * (-1) ** i)
    return hist


def _next(weekday: int) -> date:
    return DAY + timedelta(days=(weekday - DAY.weekday()) % 7)


def test_a_weekday_that_never_trades_expects_zero():
    f = SHAPE[:5] + (0.0, SHAPE[6])                  # no trading on Saturdays
    v, sd, seasonal = expected(_history(f), _next(5))
    assert seasonal and v == 0 and sd == 0


def test_the_other_weekdays_ignore_the_closed_day():
    f = SHAPE[:5] + (0.0, SHAPE[6])
    hist = _history(f)
    overall = statistics.mean(hist.values())
    idx = {w: statistics.mean(v / overall for d, v in hist.items() if d.weekday() == w) for w in range(7)}
    # the closed day is skipped, so the level is the mean of the open days, each without its weekday shape
    level = statistics.mean(v / idx[d.weekday()] for d, v in hist.items() if d.weekday() != 5)
    for wd in (0, 1, 2, 3, 4, 6):
        v, sd, seasonal = expected(hist, _next(wd))
        assert seasonal and sd > 0 and abs(v - level * idx[wd]) < 1e-6 * v


@settings(max_examples=60, deadline=None, derandomize=True)
@given(closed=st.integers(0, 6), factors=st.lists(st.floats(0.5, 2.0), min_size=7, max_size=7),
       noise=st.floats(0.0, 0.05), days=st.integers(21, 60), level=st.floats(1e3, 1e9))
def test_any_closed_weekday_never_crashes_and_expects_zero(closed, factors, noise, days, level):
    factors[closed] = 0.0
    hist = _history(factors, noise, days, level)
    for wd in range(7):
        v, sd, _ = expected(hist, _next(wd))
        assert v >= 0 and sd >= 0
        if wd == closed:
            assert v == 0 and sd == 0


def _closed_on_judged_day(monkeypatch, duck, today):
    f = list(SHAPE)
    f[DAY.weekday()] = 0.0
    monkeypatch.setattr(gate, "_history", lambda be, day, days=0, m=None: _history(f))
    if today is not None:
        real = gate._candidate
        monkeypatch.setattr(gate, "_candidate", lambda be, day, m=gate.DEFAULT: ({**real(be, day, m)[0], day: today},
                                                                                real(be, day, m)[1], {}))
    ingest(duck, DAY, "healthy")
    return gate.run(duck, DAY, write_back=False)


def test_zero_on_a_closed_weekday_is_normal(monkeypatch, duck):
    c = _closed_on_judged_day(monkeypatch, duck, 0.0)
    assert c["verdict"] == "NO_INCIDENT" and c["trust_status"] == "TRUSTED"


def test_revenue_on_a_closed_weekday_is_held_unexplained(monkeypatch, duck):
    c = _closed_on_judged_day(monkeypatch, duck, None)    # the healthy batch has revenue on a day that never trades
    assert c["verdict"] == "UNEXPLAINED" and c["trust_status"] == "HELD"
