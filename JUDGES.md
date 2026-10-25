# Brief for judges

| | |
|---|---|
| Project | **Receipts: Proof for Every Number That Moves** |
| Author | Aakash Singh Mutum |
| Track | ExaThon India 2026, Track 4: The Work Behind the Work |
| Repository | https://github.com/AakashMutum/receipts |
| Licence | MIT ([`LICENSE`](LICENSE)) |
| Platform | Exasol Personal 2026.2.0-nano.3; a DuckDB stand-in exists only for CI and for people without Exasol |

**One line:** when a daily business number moves, Receipts holds it back, proves inside Exasol which upstream fault caused it by undoing that fault in a sandbox, and tells dashboards and AI agents whether to trust it.

**The problem (from the README):** a finance analyst at an Indian fintech marketplace cannot tell whether a sudden change in daily revenue is real or a silent data bug, because the number passes through several tables and every check says green.

Every number on this page is copied from a committed report in [`samples/`](samples/) and names that file. Unless a line says otherwise, they were measured on one Windows 11 laptop (Intel Core 5, Podman on WSL2, about 7.7 GiB visible to the VM).

## The judging criteria and the evidence

| Criterion (weight) | Claim | Where to verify | Command to reproduce |
|---|---|---|---|
| Innovation and problem impact (25%) | A cause is named only after undoing it in a sandbox schema brings the number back in range with published history unchanged. A held number is never shown as trusted; agents are told what to quote instead. | README [The problem](README.md#the-problem) and [Three layers](README.md#three-layers); [`receipts/undo.py`](receipts/undo.py), [`receipts/gate.py`](receipts/gate.py); [`NOVELTY.md`](NOVELTY.md) | `receipts judge-check` (the ablation check shows a wrong cause being named without the undo test) |
| Effective use of Exasol Personal (25%) | Detectors, the `GROUP BY CUBE`, the Python SET UDF, lineage from `EXA_ALL_VIEWS`, the sandbox rebuild, the write-back and the timings Exasol records itself all run inside Exasol. Agents read only `PUB` through a read-only user. | [How Exasol is used](#how-exasol-is-used) below; [`sql/exasol/`](sql/exasol/); [`samples/exasol/`](samples/exasol/) | `receipts init` then `receipts doctor` with `RECEIPTS_BACKEND=exasol` |
| Technical excellence (20%) | 50 of 50 scored runs; a red team that shrinks every fault until it is no longer proven, with its hole and the fix reported before and after; held-out cases frozen before the fix; a real-data backtest on 9,554,757 taxi trips. | [`samples/exasol/eval_report.md`](samples/exasol/eval_report.md), [`redteam_report.md`](samples/exasol/redteam_report.md), [`heldout_unit_after.md`](samples/exasol/heldout_unit_after.md), [`real_backtest.md`](samples/exasol/real_backtest.md); [`tests/`](tests/) | `receipts eval --backend exasol --out samples/exasol`; `receipts redteam --backend exasol --seeds 11 --orders-per-day 20000` |
| Solution design and user experience (15%) | A command center with the held banner, the receipt (evidence, proof, fix as a diff), one-click approval, and two agents side by side. Normal mode cannot change data; planting faults is lab-only. | README [The demo in 30 seconds](README.md#the-demo-in-30-seconds); [`docs/tour.gif`](docs/tour.gif); [`docs/screenshots/`](docs/screenshots/); [`web/`](web/); [`receipts/lab.py`](receipts/lab.py) | `run.bat`, `run.command` or `./run.sh` |
| Documentation and reproducibility (10%) | One-click scripts per OS, a run guide, an evaluation card, and reports that each state the command that produced them. | [`docs/RUN_GUIDE.md`](docs/RUN_GUIDE.md), [`docs/EVAL_CARD.md`](docs/EVAL_CARD.md), [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | the "Reproduce:" line at the top of each report |
| Open-source quality (5%) | MIT licence, contributing guide, security notes, CI workflow, pull request and issue templates. | [`LICENSE`](LICENSE), [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md), [`.github/`](.github/) | `pytest -q` |

## How Exasol is used

| Exasol feature | Where in the code |
|---|---|
| `GROUP BY CUBE` with `GROUPING_ID` over six dimensions (11,074 slices) | [`receipts/decompose.py`](receipts/decompose.py) |
| `PYTHON3 SET SCRIPT` UDF `RECEIPTS.CLOCK_DRIFT` (clock-shift check, inside the database) | [`receipts/udf/clock_drift.py`](receipts/udf/clock_drift.py), DDL in [`receipts/udf/__init__.py`](receipts/udf/__init__.py), installed by [`receipts/load.py`](receipts/load.py) |
| Lineage from `SYS.EXA_ALL_VIEWS` | [`receipts/lineage.py`](receipts/lineage.py) |
| Views and a sandbox schema for the undo test | [`receipts/undo.py`](receipts/undo.py) |
| `EXA_STATISTICS.EXA_SQL_LAST_DAY` after `FLUSH STATISTICS`, bracketed with `CURRENT_STATEMENT` | [`receipts/db.py`](receipts/db.py), [`receipts/gate.py`](receipts/gate.py) |
| Users and grants: `AGENT_READER` can `SELECT` on `PUB` only | created in [`receipts/load.py`](receipts/load.py), checked in [`receipts/doctor.py`](receipts/doctor.py) |
| `IMPORT` through pyexasol (synthetic data, 9.5 million taxi trips) | [`receipts/db.py`](receipts/db.py), [`receipts/load.py`](receipts/load.py), [`receipts/backtest.py`](receipts/backtest.py) |
| `SYS.EXA_SQL_KEYWORDS` (reserved-word check) | [`receipts/doctor.py`](receipts/doctor.py) |
| Exasol MCP server, logged in as `AGENT_READER` | [`mcp/`](mcp/), [`docs/MCP_DEMO.md`](docs/MCP_DEMO.md) |

## Metrics

| Test | Result | Report |
|---|---|---|
| Scored evaluation, 10 scenarios x 5 seeds, 20,000 orders a day | 50 of 50 right verdict and exactly the right causes; cause precision and recall 100%. Without the undo test: 5 wrong causes. Threshold alert: 0% of causes found. Corrected values: mean error 0.001%, max 0.017%. Gate latency median 3,410 ms, max 11,667 ms | [`samples/exasol/eval_report.md`](samples/exasol/eval_report.md) |
| Fault variants, 17, written after the detectors were fixed | caught 15, held 1, published under 4% off 1, published wrong 0 (before the unit tail check: caught 13, held 3) | [`samples/exasol/variants_report.md`](samples/exasol/variants_report.md), [`variants_report_before.md`](samples/exasol/variants_report_before.md) |
| Red team, seed 11, before the unit tail check | unit floor 100%, **1 hole**: x100 on 2% of GW_C published as REAL_CHANGE, +6.47% off | [`samples/exasol/redteam_report_before.md`](samples/exasol/redteam_report_before.md) |
| Red team, seed 11, after the unit tail check | floors: unit 2%, duplicates 2%, fan-out 2%, new codes 5%, clock 100%, stale FX caught; **0 holes**; 8 of 9 opposite-direction pairs caught | [`samples/exasol/redteam_report.md`](samples/exasol/redteam_report.md) |
| Held-out partial unit changes, 24, frozen before the fix | before: caught 0, held 24; after: caught 12, held 12; published 0 both times | [`heldout_unit_before.md`](samples/exasol/heldout_unit_before.md), [`heldout_unit_after.md`](samples/exasol/heldout_unit_after.md) |
| Scaling, IST case (24 Oct, before the unit tail check) | right verdict at 20k, 100k, 200k, 400k orders a day; at 17,346,085 payment rows the gate took 27.5 s (26.3 s measured by Exasol), CUBE 5.9 s, peak temporary memory 353 MiB | [`samples/exasol/scaling.md`](samples/exasol/scaling.md) |
| Timings, IST case, one session on an idle laptop | median 5.6 s end to end over 4 repeats, 4.6 s measured by Exasol; 6.6 s on the first run after a fresh load | [`samples/exasol/timings.md`](samples/exasol/timings.md) |
| Click Break the pipeline to HELD | median 8.4 s over 5 runs (6.8 to 20.5 s) | [`samples/exasol/timings.md`](samples/exasol/timings.md) |
| Real-data backtest, NYC taxi Jan to Mar 2024, **run before the unit tail check** | 56 days judged, 0 held, 54 NO_INCIDENT, 2 REAL_CHANGE; 6 of 6 planted faults caught; 62 of 62 gate runs agree with the DuckDB run; gate median 14,804 ms | [`samples/exasol/real_backtest.md`](samples/exasol/real_backtest.md) |

## Verify in 3 minutes

No Exasol needed for the first three.

| Step | Command | What to expect |
|---|---|---|
| Demo | Windows: double-click `run.bat`. macOS: double-click `run.command`. Linux: `./run.sh` | Sets up `.venv` on the first run (a few minutes on a slow connection), builds the stand-in data, opens the command center in lab mode. The header says **Local stand-in**. Click **Break the pipeline**: the steps appear one by one, then **HELD** and the receipt |
| Headline claims | `receipts judge-check` | 20 runs on fresh data, 8 checks, ending in `ALL CHECKS PASSED (20/20 runs, ...)`; about 51 s on the laptop above |
| Tests | `pytest -q` | all pass; 2 tests are skipped unless a live Exasol is set up |
| Setup check | `receipts doctor` | on the stand-in: SQL parse and UDF checks `ok`, then `data loaded` once the demo has run |
| On Exasol (needs Exasol Personal running) | `run-exasol.bat`, `run-exasol.command` or `./run-exasol.sh`; or `RECEIPTS_BACKEND=exasol receipts init` then `receipts doctor` | the header says **Exasol** and **Python UDF in the database**; `doctor` ends with `All good.` after the reserved-word, UDF and 9 `AGENT_READER` checks |

## Known limits and what is not claimed

* All data is synthetic except the NYC taxi backtest.
* A x10 unit change on 2% to 10% of one gateway is held without a proven cause (12 of the 24 held-out cases). It is not published, but a person has to look.
* The real-data backtest has not been re-run since the unit tail check was added (not enough free disk on the laptop).
* The Exasol MCP server, Claude Desktop and Claude Code were not tested end to end; only the read-only database user was verified. The Dockerfile was not built.
* Six fault classes have detectors; anything else is held as UNEXPLAINED if it leaves the normal range, and published if it does not.
* One metric and one pipeline; the backtest connects real data through an adapter, not configuration.
* Nothing beyond 400,000 orders a day or 17.3 million payment rows; timings on one laptop only.
* `run.command` and `run.sh` were tested only under Git Bash on Windows, not on a real Mac or Linux machine.
* The Slack alert (`SLACK_WEBHOOK_URL`) was tested only for failing safely: an unreachable webhook does not stop the alert file or the watcher. No message was posted to a real Slack workspace.
* Full list: [`docs/EVAL_CARD.md`](docs/EVAL_CARD.md).

## Files that matter

| File | What it is |
|---|---|
| [`README.md`](README.md) | Overview, results, quick start, architecture |
| [`NOVELTY.md`](NOVELTY.md) | What is new and what is not |
| [`docs/EVAL_CARD.md`](docs/EVAL_CARD.md) | What was tested, results, holes, what is not claimed |
| [`docs/RUN_GUIDE.md`](docs/RUN_GUIDE.md) | Running on the stand-in and on Exasol, troubleshooting |
| [`receipts/gate.py`](receipts/gate.py) | The three layers and the evidence gate |
| [`receipts/undo.py`](receipts/undo.py) | Sandbox rebuild and history check |
| [`receipts/detectors.py`](receipts/detectors.py) | The six detectors, including the unit tail check |
| [`receipts/udf/clock_drift.py`](receipts/udf/clock_drift.py) | The Python UDF that runs inside Exasol |
| [`samples/exasol/`](samples/exasol/) | Every committed report from Exasol |
