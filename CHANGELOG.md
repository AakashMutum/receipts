# Changelog

## 1.0.2 (2026-10-29)

Everything since 1.0.0. Version 1.0.1 was never tagged; its changes are listed here. No threshold changed, and every
re-run gave the same verdicts and causes as the committed reports.

### Added

* `receipts audit-match`: lands the IST case, runs the gate with write-back and the agent's reads through the Exasol MCP server, then matches every statement against `EXA_DBA_AUDIT_SQL` (issued, matched, different, missing, extra). `--runs N` repeats it in new sessions and writes one table row per run. On live Exasol, three runs in new sessions: 57 of 57 gate statements and 3 of 3 agent reads matched in every run, none different or missing ([`docs/AUDIT_MATCH.md`](docs/AUDIT_MATCH.md)).
* [`docs/BENCHMARKS.md`](docs/BENCHMARKS.md): Exasol and the stand-in measured the same way on the same day with [`scripts/bench_exasol.py`](scripts/bench_exasol.py) and [`scripts/bench_standin.py`](scripts/bench_standin.py); IST case warm median 3.23 s on Exasol (2.16 s measured by Exasol) and 0.65 s on the stand-in.
* [`docs/WHY_EXASOL.md`](docs/WHY_EXASOL.md): what Exasol does here, measured, and the same-gate comparison with the stand-in on the real-data backtest and the 50-run evaluation.
* A code of conduct, linked from the contributing guide, and one sentence near the top of the README on what one bad feed touches (4 views read the bad number, 3 were protected).
* Property-based tests with Hypothesis (`tests/test_properties.py`): for 30 generated faults (class, share, gateway) and every scenario, the verdict and trust status stay in their fixed sets and match, a published number is inside the normal range unless published as a real change, a proven correction lands in the range and is never further from the clean value than the number it corrects, the same batch gives the same verdict twice, and a held number never reaches `PUB.METRIC_TRUST.TRUSTED_VALUE`.

### Changed

* Re-runs on Exasol on 29 Oct. The 50-run scored evaluation: 50 of 50, every verdict, cause and wrong-fix count the same; gate latency median 4,535 ms to 2,969 ms, max 13,204 ms to 5,546 ms. The red team (seed 11) and the wrong-fix control (5 seeds): the same floors, holes, combinations and 235 / 225 / 10 wrong fixes; only the timings changed.
* The scaling run, re-run after the unit tail check: the right verdict at every size; at 400,000 orders a day (17,346,085 payment rows) the gate took 15.8 s (was 27.5 s), 15.1 s measured by Exasol (was 26.3 s), CUBE 2.7 s (was 5.9 s), peak temporary memory 344 MiB (was 353 MiB).
* `samples/eval_report.md` was an Exasol run from 21 Oct; it is now the same evaluation on the DuckDB stand-in, which gives the same verdicts and causes on all 50 runs.
* The backtest reports and the festival case file were regenerated from their saved JSON and now say "real change, no fault found".
* The run guide: Windows commands in the quick start, and a troubleshooting entry for bulk loads that fail at once because Podman inherited a proxy.
* The pitch deck, with the 29 Oct numbers.

### Fixed

* `receipts audit-match` picked up `AGENT_READER` sessions from `receipts doctor` and from earlier runs; it now matches only this run's agent session. The incoming-day read is now in the client log.

## 1.0.0 (2026-10-28)

### Added

* **The gate.** When a daily metric moves, Receipts holds it, runs six detectors on the incoming batch (unit change, duplicate rows, join fan-out, stale FX feed, clock shift as a Python UDF inside Exasol, unmapped codes) and names a cause only after undoing it in a sandbox schema brings the number back into range with published history unchanged. Scored on 10 scenarios x 5 seeds on Exasol: 50 of 50 ([`samples/exasol/eval_report.md`](samples/exasol/eval_report.md)).
* **A trust flag for people and agents.** `PUB.METRIC_TRUST` says per day whether the number may be quoted and what to quote instead; `PUB.DASHBOARD_REVENUE` shows the last trusted value while a number is held.
* **Watch mode.** `receipts watch` and `receipts serve --watch` judge each newly landed batch and write alerts (`tests/test_watch.py`).
* **Lab mode and the red team.** Planting faults, Break the pipeline and `receipts redteam` run only in lab mode and only on the built-in synthetic data ([`samples/exasol/redteam_report.md`](samples/exasol/redteam_report.md)).
* **Who saw this number.** Each receipt lists the views that read the affected metric or column, from the view catalog, and `PUB.METRIC_TRUST` carries `DOWNSTREAM_COUNT` and `DOWNSTREAM_OBJECTS`; on Exasol the audit log names who read them ([`samples/exasol/live_checks.md`](samples/exasol/live_checks.md)).
* **Trust badge.** `GET /badge.svg` and `/badge/<metric>.svg`, read-only ([`docs/screenshots/12_badges.png`](docs/screenshots/12_badges.png)).
* **Configurable metrics.** `receipts.yaml` and `receipts connect --check`; paid orders per day and average basket ship as examples ([`samples/metrics_report.md`](samples/metrics_report.md)).
* **Wrong-fix control.** `receipts wrongfix` feeds the gate deliberately wrong corrections: 235 tried, 225 rejected, 10 accepted and listed ([`samples/exasol/wrongfix_report.md`](samples/exasol/wrongfix_report.md)).
* **Blind test kit.** `receipts blindtest` and [`docs/BLIND_TEST.md`](docs/BLIND_TEST.md); no blind test results are claimed.
* **A read-only user for AI agents.** `receipts init` creates `AGENT_READER` with `SELECT` on `PUB` only; a Claude Code session limited to the Exasol MCP tools answered through it ([`docs/MCP_REAL_RUN.md`](docs/MCP_REAL_RUN.md)), and the server was also run at protocol level ([`docs/MCP_PROTOCOL_RUN.md`](docs/MCP_PROTOCOL_RUN.md)).

### Fixed

* **The red team hole.** A x100 unit change on 2% of one gateway was published as a real change; the unit tail check closed it: unit floor 100% to 2%, holes 1 to 0 ([`before`](samples/exasol/redteam_report_before.md), [`after`](samples/exasol/redteam_report.md)).
* **History for unpublished metrics.** A merchant fan-out rewrote past days in the views and moved the baseline with it; `RECEIPTS.METRIC_HISTORY` now keeps a snapshot. Average basket published wrong 6 of 16 held-out faults before, 0 after ([`before`](samples/metrics_heldout_before.md), [`after`](samples/exasol/metrics_heldout_after.md)).
* **Audit-log reads on Exasol.** The window start is shifted from session time to the audit log's system time, statistics are flushed first, and the `READS` alias, a reserved word in Exasol, is now `READ_COUNT` ([`samples/exasol/live_checks.md`](samples/exasol/live_checks.md)).

### Known limits

See [Verified and not covered](README.md#verified-and-not-covered) in the README.
