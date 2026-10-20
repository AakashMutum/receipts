"""In-database Python UDF: did a slice's time-of-day profile slide sideways?

This file is deployed verbatim as the body of an Exasol PYTHON3 SET script:

    CREATE OR REPLACE PYTHON3 SET SCRIPT RECEIPTS.CLOCK_DRIFT(
        slice_key VARCHAR(40), is_today BOOLEAN, bin_idx INTEGER, cnt DOUBLE)
    EMITS (slice_key VARCHAR(40), n_today DOUBLE, tvd DOUBLE,
           best_shift_bins INTEGER, tvd_after_shift DOUBLE) AS <this file>

Exasol calls run(ctx) once per group (one payment gateway), in parallel across
groups. Input rows are 48 half-hour bins for today and for the baseline window.
We compare the two distributions with total variation distance (TVD), then try
every circular shift of today's profile and report the shift that best lines it
up with the baseline. A clock bug moves the whole profile by a fixed amount, so
the TVD collapses after shifting back. A real change in behaviour (a festival
evening) does not collapse under any shift.

Only the standard library is used, so the same file also runs unchanged in the
local stand-in through a small ctx shim (see receipts/udf/__init__.py).
"""

BINS = 48


def _tvd(a, b):
    return 0.5 * sum(abs(x - y) for x, y in zip(a, b))


def run(ctx):
    today = [0.0] * BINS
    base = [0.0] * BINS
    key = ctx.slice_key
    while True:
        b = int(ctx.bin_idx) % BINS
        if ctx.is_today:
            today[b] += float(ctx.cnt)
        else:
            base[b] += float(ctx.cnt)
        if not ctx.next():
            break
    n_today = sum(today)
    n_base = sum(base)
    if n_today <= 0 or n_base <= 0:
        ctx.emit(key, n_today, None, None, None)
        return
    p = [x / n_today for x in today]
    q = [x / n_base for x in base]
    tvd0 = _tvd(p, q)
    best_k, best_tvd = 0, tvd0
    for k in range(-BINS // 2, BINS // 2 + 1):
        if k == 0:
            continue
        # shift today's profile back by k bins
        shifted = [p[(i + k) % BINS] for i in range(BINS)]
        t = _tvd(shifted, q)
        if t < best_tvd - 1e-12:
            best_k, best_tvd = k, t
    ctx.emit(key, n_today, tvd0, best_k, best_tvd)
