# Contributing to Receipts

Thanks for taking a look. Receipts is maintained by Aakash Singh Mutum. Issues and pull requests are welcome.

Please follow the [code of conduct](CODE_OF_CONDUCT.md). Security issues: see [SECURITY.md](SECURITY.md).

## Set up and run the tests

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m pytest -q                # every scenario on the stand-in and on the Exasol SQL path
receipts judge-check               # the headline claims on fresh data
```

What the suite contains besides the scenario tests:

* `tests/test_properties.py`: property-based tests with [Hypothesis](https://hypothesis.readthedocs.io). Each example plants a generated fault (class, share, gateway) and checks rules that hold for any fault, for example that a held number never reaches the trusted value agents read. Examples are fixed (`derandomize=True`, 30 of them) so every run and every system sees the same cases.
* `tests/test_failure_injection.py`: the database raises in the undo test, the lineage read and each write-back statement; the test checks what is left behind and that the next run works.
* `tests/test_metric_names.py`: hostile names in `receipts.yaml` are rejected before any SQL runs.

Run one file with `python -m pytest -q tests/test_properties.py`. CI also runs these two:

```bash
ruff check .                                   # syntax errors and unused imports only, no formatting rules
python -m pytest -q --cov=receipts             # coverage of the receipts package
```

Against a running Exasol with the demo data (`receipts init` first):

```bash
RECEIPTS_LIVE_EXASOL=1 python -m pytest -q tests/test_exasol_live.py tests/test_failure_injection.py
```

Changes to SQL or the UDF should also be checked on Exasol Personal: set `RECEIPTS_BACKEND=exasol` and the `EXA_*` variables, then run `receipts init`, `receipts doctor` and `receipts run ist_utc` (see [docs/RUN_GUIDE.md](docs/RUN_GUIDE.md)).

## Add a detector

1. Write a function in [`receipts/detectors.py`](receipts/detectors.py) that takes the context and returns a `Finding`: whether it fired, a one-line summary, the blamed table and column, the slice, and a `Correction` that the undo test can apply in the sandbox schema.
2. Give it a title in `DETECTOR_TITLES` and add it to `run_all`.
3. Keep the SQL dialect-neutral: use the helpers in [`receipts/dialect.py`](receipts/dialect.py) so it renders for Exasol and the stand-in.
4. Add a scenario that plants the fault (below), so the detector is tested end to end.

A detector only nominates a suspect. It never decides the verdict; the evidence gate in [`receipts/gate.py`](receipts/gate.py) does.

## Add a scenario

1. Add a `Scenario` to `SCENARIOS` in [`receipts/faults.py`](receipts/faults.py) with its SQL `inject` statements, the expected verdict and the expected causes. The engine never imports this file, so ground truth stays separate.
2. Add its id to `DEMO_ORDER` if it should appear in the command center.
3. `tests/test_scenarios.py` picks up every scenario automatically, on both SQL paths.

Held-out variants that test generalisation go in [`receipts/variants.py`](receipts/variants.py) instead.

## Code style

* Plain, readable Python 3.10+. Match the surrounding code: short functions, few comments, comments that say why.
* No em dashes anywhere in the repository. `tests/test_units.py` fails if one appears.
* LF line endings.
* Keep the UI dependency-free: plain HTML, CSS and JavaScript, no build step.
* Every number shown to a person must come from a query that really ran.

## Pull requests

Keep them small and focused, describe what changed and how you tested it, and make sure `pytest` and `receipts judge-check` pass. The pull request template lists the checks.
