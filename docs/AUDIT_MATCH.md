# Audit-log match

Every statement Receipts sent in one full run, matched against `EXA_DBA_AUDIT_SQL` on Exasol 2026.2.0-nano.3. Batch day 2026-10-28, case RC-20261028-A0990F, verdict PROVEN_FAULT, 22.9 s. Reproduce: `receipts audit-match` (needs Exasol with the demo data).

Matched means the same text, ignoring whitespace and a trailing semicolon; different means a statement at the same place whose text differs after the first 60 characters; missing means nothing in the audit log. Extra statements are in the audit log for the same session but not in the client's statement log.

## Gate session: landing, detectors, CUBE, lineage, undo tests, write-back

| Issued | Matched | Different | Missing | Extra in the audit log |
|---|---|---|---|---|
| 57 | 57 | 0 | 0 | 83 |

Extra statements in the audit log, by kind: FLUSH STATISTICS 2, commit (other) 70, session id read 1, statistics or audit read 1, timing marker (SELECT CURRENT_STATEMENT) 9.

## Agent reads through the Exasol MCP server as AGENT_READER

| Issued | Matched | Different | Missing | Extra in the audit log |
|---|---|---|---|---|
| 3 | 3 | 0 | 0 | 4 |

Extra statements in the audit log, by kind: commit (other) 3, rollback (other) 1.

## Why there are extra statements

None of the extras is a query Receipts or the agent sent that the client log hid. `COMMIT /* AUTO */` and `ROLLBACK /* AUTO */` are Exasol's own autocommit records. The timing markers (`SELECT CURRENT_STATEMENT`), a `FLUSH STATISTICS` and the `EXA_STATISTICS` read are the timing code reading Exasol's measurements; the session id read and the other `FLUSH STATISTICS` are audit-match itself. They go straight to the connection, outside the statement log, so that measuring does not change what is measured.

