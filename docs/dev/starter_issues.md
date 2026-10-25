> Working note for contributors, not part of the user documentation.

# Good first issues

Six concrete, self-contained tasks for a first contribution. Each says where to start and how to know it
is done. `gh` was not available when this file was written, so they are not opened as GitHub issues yet;
copy one into a new issue when you pick it up.

## 1. A detector for a doubled discount

**Why:** the `unknown_discount` scenario (a coupon applied twice on part of Electronics) has no detector on
purpose, so it is held as `UNEXPLAINED`. A detector would turn it into a proven fault.
**Where:** `receipts/detectors.py` (add a seventh function and register it in `run_all`), `receipts/faults.py`.
**Done when:** a median ticket per category check fires on `unknown_discount`, its correction passes the undo
test, `receipts judge-check` still passes, and the scenario's expected verdict is updated with a test.

## 2. Configuration instead of an adapter for a new metric

**Why:** connecting another metric today needs an adapter like `receipts/backtest.py`. The table in
`docs/ARCHITECTURE.md` lists what a company would have to describe.
**Where:** start with a `metric.yaml` read by `receipts/model.py` for the amount, ID and timestamp columns.
**Done when:** the backtest runs from a config file with no change to its output.

## 3. A holiday calendar for the baseline

**Why:** the weekday baseline has no holidays, so a real holiday can look like an anomaly and a verified real
change shifts later expectations (the 13 Feb 2024 snow day in the real-data backtest).
**Where:** `expected()` in `receipts/gate.py`.
**Done when:** a list of known days is excluded from the baseline, with a test using a synthetic holiday.

## 4. Keyboard and screen reader pass on the lab panel

**Why:** the Break the pipeline panel and the red team tab were added late and have only been checked by hand.
**Where:** `web/index.html`, `web/app.js`.
**Done when:** every control works from the keyboard, the live timeline is announced once per step, and the
floor chart has a text equivalent (a table) for screen readers.

## 5. Show the red team floors over time

**Why:** `receipts redteam` writes one report. Saving each run would show whether a change to a detector moves
a floor, which is the honest way to tell whether it got better.
**Where:** `receipts/redteam.py`, `samples/`.
**Done when:** each run appends to a small history file and the red team tab can show the last few runs.

## 6. A `--json` flag for `receipts doctor`

**Why:** `receipts doctor` prints a checklist for people. A scheduler or CI job would rather read the same
checks as JSON (each check, passed or not, and its message), including the read-only agent user checks.
**Where:** `receipts/doctor.py`, the `doctor` parser in `receipts/cli.py`.
**Done when:** `receipts doctor --json` prints one JSON object, the exit code is unchanged, and a test covers
the stand-in output.
