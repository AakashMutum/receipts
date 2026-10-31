# Audit-log match

Every statement Receipts sent in 3 full runs, each a new session that lands the batch again, matched against `EXA_DBA_AUDIT_SQL` on Exasol 2026.2.0-nano.3. Batch day 2026-10-28, the IST case. Reproduce: `receipts audit-match --runs 3` (needs Exasol with the demo data).

Matched means the same text, ignoring whitespace and a trailing semicolon; different means a statement at the same place whose text differs after the first 60 characters; missing means nothing in the audit log. Extra statements are in the audit log for the same session but not in the client's statement log.

## Gate session: landing, detectors, CUBE, lineage, undo tests, write-back

| Run | Case | Verdict | Seconds | Issued | Matched | Different | Missing | Extra in the audit log |
|---|---|---|---|---|---|---|---|---|
| 1 | RC-20261028-4681AD | PROVEN_FAULT | 26.3 | 57 | 57 | 0 | 0 | 83 |
| 2 | RC-20261028-E7D10D | PROVEN_FAULT | 22.9 | 57 | 57 | 0 | 0 | 83 |
| 3 | RC-20261028-136961 | PROVEN_FAULT | 20.9 | 57 | 57 | 0 | 0 | 83 |

Extra statements in the audit log, by kind, the same in every run: FLUSH STATISTICS 2, commit (other) 70, session id read 1, statistics or audit read 1, timing marker (SELECT CURRENT_STATEMENT) 9.

## Agent reads through the Exasol MCP server as AGENT_READER

| Run | Issued | Matched | Different | Missing | Extra in the audit log |
|---|---|---|---|---|---|
| 1 | 3 | 3 | 0 | 0 | 4 |
| 2 | 3 | 3 | 0 | 0 | 4 |
| 3 | 3 | 3 | 0 | 0 | 4 |

Extra statements in the audit log, by kind, the same in every run: commit (other) 3, rollback (other) 1.

## Why there are extra statements

None of the extras is a query Receipts or the agent sent that the client log hid. `COMMIT /* AUTO */` and `ROLLBACK /* AUTO */` are Exasol's own autocommit records. The timing markers (`SELECT CURRENT_STATEMENT`), a `FLUSH STATISTICS` and the `EXA_STATISTICS` read are the timing code reading Exasol's measurements; the session id read and the other `FLUSH STATISTICS` are audit-match itself. They go straight to the connection, outside the statement log, so that measuring does not change what is measured.

## Re-run on 2026-10-31

Three more full runs, each in a new session, after the 2023 and 2024 backtests and a fresh `receipts init`, at the commit that fixes a weekday with no trading history. Batch day 2026-10-30, the IST case, same command. Every statement matched again; the extras are of the same kinds and counts as above. A first attempt minutes before also matched 57 of 57 gate statements in all three runs, but the MCP server did not start (`uvx` was not on that shell's PATH), so it had no agent reads; it was run again with `uvx` on the PATH, and the three runs below are complete.

### Gate session: landing, detectors, CUBE, lineage, undo tests, write-back

| Run | Case | Verdict | Seconds | Issued | Matched | Different | Missing | Extra in the audit log |
|---|---|---|---|---|---|---|---|---|
| 1 | RC-20261030-F23FE9 | PROVEN_FAULT | 24.4 | 57 | 57 | 0 | 0 | 83 |
| 2 | RC-20261030-BDD85D | PROVEN_FAULT | 21.2 | 57 | 57 | 0 | 0 | 83 |
| 3 | RC-20261030-5629C4 | PROVEN_FAULT | 20.7 | 57 | 57 | 0 | 0 | 83 |

Extra statements in the audit log, by kind, the same in every run: FLUSH STATISTICS 2, commit (other) 70, session id read 1, statistics or audit read 1, timing marker (SELECT CURRENT_STATEMENT) 9.

### Agent reads through the Exasol MCP server as AGENT_READER

| Run | Issued | Matched | Different | Missing | Extra in the audit log |
|---|---|---|---|---|---|
| 1 | 3 | 3 | 0 | 0 | 4 |
| 2 | 3 | 3 | 0 | 0 | 4 |
| 3 | 3 | 3 | 0 | 0 | 4 |

Extra statements in the audit log, by kind, the same in every run: commit (other) 3, rollback (other) 1.
