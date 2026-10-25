# Evaluation card

One page on what Receipts was tested on, what came out, and what is not claimed. Every number links to an
unedited report in `samples/`. Platform: Exasol Personal 2026.2.0-nano.3 on a Windows 11 laptop (Intel
Core 5, Podman on WSL2, about 7.7 GiB visible to the VM), unless a line says the DuckDB stand-in.

## Scope

* **One metric:** daily revenue, built by a chain of six views from raw payments, orders and three reference
  tables. **Six fault classes** with a detector each: unit change, duplicate rows, join fan-out, stale FX
  feed, clock shift (a Python UDF inside Exasol) and unmapped codes.
* **The decision:** hold or publish tonight's number, and name the cause only if undoing it in a sandbox puts
  the number back in range with published history unchanged. Verdicts: NO_INCIDENT, REAL_CHANGE (published),
  PROVEN_FAULT, UNEXPLAINED (held).
* No thresholds were changed for any test on this page. One detector was extended after the red team found a
  hole (the unit tail check, below); every test except the real-data backtest was re-run after it.

## Data

| Data | What it is |
|---|---|
| Synthetic marketplace | Seeded generator: 8 cities, 6 categories, 4 gateways, a USD slice with daily FX, evening-heavy shopping in IST, background payment retries; 42 days of history plus the incoming day. Faults are SQL in `receipts/faults.py`, which the engine never imports |
| NYC TLC yellow taxi trips | Public, Jan to Mar 2024, 9,554,757 trips, mapped onto the same tables by an adapter (`receipts/backtest.py`) |

## Results

| Test | Result | Report |
|---|---|---|
| Scored evaluation, 10 scenarios x 5 seeds, 20,000 orders a day | 50 of 50; cause precision and recall 100%, 0 wrong causes. Ablation without the undo test: 5 wrong causes. Threshold alert: 0% of causes, misses the masked pair. Corrected values within 0.017% of the clean value | [`samples/exasol/eval_report.md`](../samples/exasol/eval_report.md) |
| Held-out variants, 17, written after the detectors were fixed | caught 15, held 1, published under 4% off 1, published wrong 0 (before the tail check: caught 13, held 3) | [`samples/exasol/variants_report.md`](../samples/exasol/variants_report.md) |
| Real data, 56 days judged (before the tail check; not re-run) | 0 held, 54 NO_INCIDENT, 2 verified REAL_CHANGE; 6 of 6 planted faults caught; 62 of 62 runs agree with the DuckDB run | [`samples/exasol/real_backtest.md`](../samples/exasol/real_backtest.md) |
| Red team, seed 11, 20,000 orders a day | Floors: unit 2%, duplicates 2%, fan-out 2%, new codes 5%, clock faults 100%, stale FX caught. 0 holes (1 before the tail check). 8 of 9 opposite-direction pairs caught, 1 held with one cause |
| Held-out partial unit changes, 24, frozen before the tail check | before: caught 0, held 24; after: caught 12 (all x1000), held 12 (all x10); published 0 both times | [`samples/exasol/heldout_unit_after.md`](../samples/exasol/heldout_unit_after.md) | [`samples/exasol/redteam_report.md`](../samples/exasol/redteam_report.md) |
| Scaling, IST case (24 Oct, before the unit tail check) | Right verdict at 20k, 100k, 200k and 400k orders a day; at 400k (17,346,085 payment rows) the gate takes 27.5 s, 26.3 s measured by Exasol, peak temporary memory 353 MiB | [`samples/exasol/scaling.md`](../samples/exasol/scaling.md) |
| Live demo, click to HELD | median 8.4 s over 5 runs (6.8 to 20.5 s) | [`samples/exasol/timings.md`](../samples/exasol/timings.md) |
| IST case, `receipts run ist_utc`, one session on an idle laptop | median 5.6 s end to end over 4 repeats, 4.6 s measured by Exasol, 63 to 69 MiB peak temporary memory | [`samples/exasol/timings.md`](../samples/exasol/timings.md) |
| Read-only agent user | reads PUB; refused on RAW, PIPE, RECEIPTS, insert, update, delete, create schema | [`docs/MCP_DEMO.md`](MCP_DEMO.md) |

## The unit-change hole: before and after the tail check

The red team found that a x100 unit change on 2% of one small gateway's payments was published (REAL_CHANGE on
seed 11, +6.47%): the unit check compared medians, which 2% of rows do not move. A tail check was
added: per gateway and currency, today's count of amounts above 20 times the
baseline median against the baseline share (Poisson test, false-alarm budget 1e-6 per slice and night). A stricter
real-change test was also proposed; it was not needed and is not applied. The held-out cases were committed before
the fix was written and were not used to tune it.

| Test on Exasol | Before | After |
|---|---|---|
| Red team, seed 11 | unit floor 100%, 1 hole | unit floor 2%, 0 holes |
| Held-out partial unit changes, 24 | caught 0, held 24, published 0 | caught 12, held 12, published 0 |
| Variants, 17 | caught 13, held 3, small 1, wrong 0 | caught 15, held 1, small 1, wrong 0 |
| Scored evaluation, 50 runs | 50 of 50 | 50 of 50, same precision, recall and ablation numbers, festival control published as REAL_CHANGE on all 5 seeds |
| Real-data backtest | 0 held, REAL_CHANGE on 13 Feb and 27 Feb, 6 of 6 | not re-run: not enough free disk |

Reports: `samples/exasol/*_before.md` and the files without the suffix. The DuckDB stand-in gives the same
held-out counts and the same red team floors.

## Known limits and holes

* **Not closed:** a x10 unit change on 2% to 10% of a gateway is held without a proven cause (12 of 24 held-out
  cases): those amounts mostly stay below the 20x cut. Held, not published, but a person has to look.
* The real-data backtest was not re-run after the tail check, so whether the festival-like real changes there
  (13 Feb, 27 Feb) still publish with it is checked only on synthetic data (the festival control, 5 seeds).
* Partial clock shifts (25% to 50%) are held without a proven cause. Safe, but a person has to investigate.
* A fault without a detector is held as UNEXPLAINED when it leaves the normal range, and published when it
  does not. On real taxi data the normal range is about plus or minus 22%.
* No holiday calendar; a verified real change becomes part of the baseline.
* One metric and one pipeline; the backtest connects real data through an adapter, not configuration.
* Red team and scaling ran on one seed and one laptop. The eval ran on 5 seeds.
* `run.command` and `run.sh` were tested only under Git Bash on Windows, not on a real Mac or Linux machine.
* The Slack alert was tested only for failing safely (an unreachable webhook does not stop the watcher); no
  message was posted to a real Slack workspace.

## What is not claimed

* Anything beyond 400,000 orders a day or 17.3 million payment rows.
* That the six detectors cover the faults of a real company's pipeline.
* That the Exasol MCP server, Claude Desktop or Claude Code were tested end to end: `uv` was not installed on
  the build machine, so only the read-only database user was verified.
* Timings on any other machine. Each scaling run is the first after a fresh load, which is slower than a repeat.
* That the Dockerfile builds: Docker was not running on the build machine.
