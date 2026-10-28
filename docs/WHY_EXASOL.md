# Why Exasol

What Receipts uses Exasol for, with the numbers measured for each, and where the DuckDB stand-in is enough. All
Exasol numbers are from Exasol Personal 2026.2.0-nano.3 on one laptop ([`BENCHMARKS.md`](BENCHMARKS.md) has the
machine).

| What | How Receipts uses it | Measured |
|---|---|---|
| `GROUP BY CUBE` with `GROUPING_ID` | One scan tests every combination of six dimensions for today and the baseline: 11,074 slices | 450 ms measured by Exasol for the IST case at 863,336 payment rows (warm median); 2.5 s over 5,950,587 rows at 400,000 orders a day ([`BENCHMARKS.md`](BENCHMARKS.md), [`scaling.md`](../samples/exasol/scaling.md)) |
| `PYTHON3 SET SCRIPT` UDF | `RECEIPTS.CLOCK_DRIFT` compares each gateway's half-hour profile with its baseline inside the database and finds the shift that lines it up | the six detectors, UDF included: 485 ms measured by Exasol (warm median); `receipts doctor` confirms the UDF runs in the database |
| `SYS.EXA_ALL_VIEWS` | Lineage backwards from the metric to the raw columns, and forwards to every view that reads the number (the blast radius) | 27 ms measured by Exasol (warm median); 16 view definitions read, 4 views that showed the bad number and 3 the gate protected ([`live_checks.md`](../samples/exasol/live_checks.md)) |
| `EXA_DBA_AUDIT_SQL` | Who read an exposed view while the number was wrong | found the second session that read `MART.FINANCE_DAILY` in the live check ([`live_checks.md`](../samples/exasol/live_checks.md)); every one of 57 gate statements and 3 agent reads found in it, none different or missing ([`AUDIT_MATCH.md`](AUDIT_MATCH.md)) |
| A sandbox schema | Each suspect is undone by rebuilding the pipeline views in `RECEIPTS_SBX` with one source corrected, then re-reading the metric and the published history | 884 ms measured by Exasol for the undo tests of the IST case (warm median) |
| `EXA_STATISTICS` | Each receipt shows the time and memory Exasol itself recorded per step | 2.16 s (warm median, without write-back) and 62.5 to 67.7 MiB peak temporary memory per IST run ([`BENCHMARKS.md`](BENCHMARKS.md)) |
| Users and grants, and the Exasol MCP server | `AGENT_READER` can read `PUB` and nothing else; an agent reaches it only through the Exasol MCP server | Exasol refused the agent's `UPDATE` with insufficient privileges ([`MCP_REAL_RUN.md`](MCP_REAL_RUN.md)); 9 grant checks in `receipts doctor` |

## The same gate on Exasol and on the stand-in

The real-data backtest ran the same 62 gate runs over 9,554,757 NYC taxi trips on both
([`samples/exasol/real_backtest.md`](../samples/exasol/real_backtest.md), [`samples/real_backtest.md`](../samples/real_backtest.md)):

| | Exasol | DuckDB stand-in |
|---|---|---|
| Same verdict and same causes | 62 of 62 | 62 of 62 |
| Largest relative difference in the daily value | 9.94e-09 | |
| Gate run, median | 6,469 ms | 3,728 ms |
| Gate run, max | 12,896 ms | 9,179 ms |

The 50-run scored evaluation (10 scenarios x 5 seeds, 20,000 orders a day) ran on both on 29 Oct
([`samples/exasol/eval_report.md`](../samples/exasol/eval_report.md), [`samples/eval_report.md`](../samples/eval_report.md)):

| | Exasol | DuckDB stand-in |
|---|---|---|
| Right verdict and causes | 50 of 50 | 50 of 50 |
| Wrong fixes tried, rejected, accepted | 235, 225, 10 | 235, 225, 10 |
| Gate run, median (with the wrong-fix control) | 2,969 ms | 754 ms |
| Whole evaluation | 580 s | 126 s |

The two agree on the verdict, the causes and the change on all 50 runs.

For the IST case at 20,000 orders a day, measured the same way on both on 29 Oct, the gate takes a median 3.2 s warm
on Exasol (2.2 s of it measured by Exasol) and 0.65 s on the stand-in, same verdict ([`BENCHMARKS.md`](BENCHMARKS.md)).

## Where the stand-in is fine

* Tests, CI on three operating systems, `receipts judge-check` and the lab demo run on the stand-in, and the
  verdicts match Exasol wherever both were run.
* On this laptop and at these sizes the stand-in is faster: it runs in the Python process, while Exasol runs in a
  container behind a network round trip for each statement. Nothing here claims Exasol is faster at this scale.

## What only Exasol gives Receipts

* The clock check as a UDF inside the database; the stand-in runs the same source through a local shim.
* Exasol's own record of each statement's time and memory (`EXA_STATISTICS`) and of who read what (`EXA_DBA_AUDIT_SQL`);
  the stand-in has neither, and the receipt says so.
* A real read-only database user for agents, enforced by the database and reached through the Exasol MCP server.
