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
* No thresholds were changed for any test on this page.

## Data

| Data | What it is |
|---|---|
| Synthetic marketplace | Seeded generator: 8 cities, 6 categories, 4 gateways, a USD slice with daily FX, evening-heavy shopping in IST, background payment retries; 42 days of history plus the incoming day. Faults are SQL in `receipts/faults.py`, which the engine never imports |
| NYC TLC yellow taxi trips | Public, Jan to Mar 2024, 9,554,757 trips, mapped onto the same tables by an adapter (`receipts/backtest.py`) |

## Results

| Test | Result | Report |
|---|---|---|
| Scored evaluation, 10 scenarios x 5 seeds, 20,000 orders a day | 50 of 50; cause precision and recall 100%, 0 wrong causes. Ablation without the undo test: 5 wrong causes. Threshold alert: 0% of causes, misses the masked pair. Corrected values within 0.017% of the clean value | [`samples/exasol/eval_report.md`](../samples/exasol/eval_report.md) |
| Held-out variants, 17, written after the detectors were fixed | caught 13, held 3, published under 4% off 1, published wrong 0 | [`samples/exasol/variants_report.md`](../samples/exasol/variants_report.md) |
| Real data, 56 days judged | 0 held, 54 NO_INCIDENT, 2 verified REAL_CHANGE; 6 of 6 planted faults caught; 62 of 62 runs agree with the DuckDB run | [`samples/exasol/real_backtest.md`](../samples/exasol/real_backtest.md) |
| Red team, seed 11, 20,000 orders a day | Floors: duplicates 2%, fan-out 2%, new codes 5%, unit and clock faults 100%, stale FX caught. 1 hole (below). 8 of 9 opposite-direction pairs caught, 1 held with one cause | [`samples/exasol/redteam_report.md`](../samples/exasol/redteam_report.md) |
| Scaling, IST case | Right verdict at 20k, 100k, 200k and 400k orders a day; at 400k (17,346,085 payment rows) the gate takes 27.5 s, 26.3 s measured by Exasol, peak temporary memory 353 MiB | [`samples/exasol/scaling.md`](../samples/exasol/scaling.md) |
| Live demo, click to HELD | median 7.3 s over 5 runs (6.9 to 8.5 s) | [`docs/RUN_GUIDE.md`](RUN_GUIDE.md#8-break-the-pipeline-lab-mode) |
| Read-only agent user | reads PUB; refused on RAW, PIPE, RECEIPTS, insert, update, delete, create schema | [`docs/MCP_DEMO.md`](MCP_DEMO.md) |

## Known limits and holes

* **Hole:** a x100 unit change on 2% of one small gateway's payments is published (as REAL_CHANGE on seed 11,
  +6.47%; as NO_INCIDENT on the demo data, +8.56%). The median-based unit check does not move, and the
  real-change test tolerates a 6% ticket change with flat volume. Fixes are proposed in
  [`PROGRESS.md`](PROGRESS.md), not applied.
* Partial unit changes (5% to 50% of a gateway) and partial clock shifts (25% to 50%) are held without a
  proven cause. Safe, but a person has to investigate.
* A fault without a detector is held as UNEXPLAINED when it leaves the normal range, and published when it
  does not. On real taxi data the normal range is about plus or minus 22%.
* No holiday calendar; a verified real change becomes part of the baseline.
* One metric and one pipeline; the backtest connects real data through an adapter, not configuration.
* Red team and scaling ran on one seed and one laptop. The eval ran on 5 seeds.

## What is not claimed

* Anything beyond 400,000 orders a day or 17.3 million payment rows.
* That the six detectors cover the faults of a real company's pipeline.
* That the Exasol MCP server, Claude Desktop or Claude Code were tested end to end: `uv` was not installed on
  the build machine, so only the read-only database user was verified.
* Timings on any other machine. Each scaling run is the first after a fresh load, which is slower than a repeat.
* That the Dockerfile builds: Docker was not running on the build machine.
