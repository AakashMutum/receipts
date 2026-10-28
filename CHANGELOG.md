# Changelog

## 1.0.2 (2026-10-29)

### Added

* [`docs/AUDIT_MATCH.md`](docs/AUDIT_MATCH.md) and its JSON, from `receipts audit-match` on live Exasol: 57 of 57 gate statements and 3 of 3 agent reads through the Exasol MCP server matched, none different or missing.

### Fixed

* `receipts audit-match` picked up `AGENT_READER` sessions from `receipts doctor` and from earlier runs; it now matches only this run's agent session. The incoming-day read is now in the client log.

## 1.0.1 (2026-10-28)

No verdict, threshold or reported result changed.

### Added

* `receipts audit-match`: lands the IST case, runs the gate with write-back and the agent's reads through the Exasol MCP server, then matches every statement against `EXA_DBA_AUDIT_SQL` (issued, matched, different, missing, extra). Covered by tests; not yet run on live Exasol (see 1.0.2).
* [`docs/BENCHMARKS.md`](docs/BENCHMARKS.md) with cold and warm runs on the stand-in ([`scripts/bench_standin.py`](scripts/bench_standin.py)) next to the recorded Exasol timings, and [`docs/WHY_EXASOL.md`](docs/WHY_EXASOL.md) with what Exasol does here, measured.
* A code of conduct, and one sentence near the top of the README on what one bad feed touches (4 views read the bad number, 3 were protected).
* Windows steps in the run guide's "Without Exasol" section.

### Changed

* The backtest reports and the festival case file were regenerated from their saved JSON and now say "real change, no fault found".

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
