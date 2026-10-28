# Benchmarks

Every number on this page comes from a committed, recorded run. The IST case (`ist_utc`: one gateway writes IST
timestamps as UTC) at 20,000 orders a day is the reference: 863,336 payment rows, 11,074 slices in the CUBE.

## Machine

| | |
|---|---|
| Laptop | Intel Core 5 120U (10 cores, 12 threads), 15.6 GiB RAM, Windows 11 Pro 10.0.26300 |
| Exasol | Exasol Personal 2026.2.0-nano.3 in Podman 5.8.3 on WSL2 (VM set to 6 CPUs; about 7.7 GiB visible to it) |
| Free RAM | 2.1 GiB free on the host when the stand-in runs below were recorded (28 Oct, other work open) |
| Stand-in | DuckDB, in the same Python process as Receipts |

## Exasol, IST case

Recorded on 26 Oct 2026 after the unit tail check, one session on an idle laptop
([`samples/exasol/timings.md`](../samples/exasol/timings.md)). "First run" is the first gate run after
`receipts init --fresh` (a fresh load, not a database restart); "repeats" are 4 more runs on the same data.

| | End to end | Measured by Exasol |
|---|---|---|
| First run after a fresh load | 6.6 s | 5.4 s |
| Repeats, median (range) | 5.6 s (4.2 to 5.7 s) | 4.6 s |
| Peak temporary memory per run | | 62.8 to 68.8 MiB |
| Statements per run | 27 sent by the client | 37 in Exasol's statistics |

Median per step over the 4 repeats:

| Step | End to end | Measured by Exasol |
|---|---|---|
| Read candidate and trusted history | 166 ms | 139 ms |
| Run six detectors (clock check is the Python UDF) | 890 ms | 816 ms |
| Read lineage from view definitions | 46 ms | 15 ms |
| Test 11,074 slices in one GROUP BY CUBE | 1,306 ms | 918 ms |
| Reconcile raw payments to revenue rows | 466 ms | 440 ms |
| Undo each suspect in a sandbox schema | 1,420 ms | 1,258 ms |
| Write receipts back to the database (cases, evidence, trust table) | 825 ms | 718 ms |

Click Break the pipeline to the HELD banner: median 8.4 s over 5 runs (6.8 to 20.5 s), same report.

## DuckDB stand-in, IST case

Recorded on 28 Oct 2026 with [`scripts/bench_standin.py`](../scripts/bench_standin.py)
([`samples/standin_bench.json`](../samples/standin_bench.json)). Cold: a new process on a freshly built database,
3 times. Warm: 3 repeats in one process after a first run. Without write-back.

| | Cold, median (range) | Warm, median (range) |
|---|---|---|
| Gate, end to end | 541 ms (537 to 546) | 547 ms (511 to 551) |
| Read candidate and trusted history | 46 ms | 43 ms |
| Run six detectors (the UDF source runs through a local shim) | 89 ms | 97 ms |
| Read lineage from view definitions | 46 ms | 22 ms |
| Test 11,074 slices in one GROUP BY CUBE | 191 ms | 189 ms |
| Reconcile raw payments to revenue rows | 105 ms | 98 ms |
| Undo each suspect in a sandbox schema | 62 ms | 70 ms |

All 6 runs gave PROVEN_FAULT, clock shift.

## Scaling on Exasol

Recorded on 24 Oct 2026, before the unit tail check ([`samples/exasol/scaling.md`](../samples/exasol/scaling.md)).
Each size is the first gate run after a fresh load.

| Orders a day | Payment rows | Gate end to end | Measured by Exasol | CUBE | Peak temp memory |
|---|---|---|---|---|---|
| 20,000 | 863,336 | 9.1 s | 7.6 s | 2.4 s | 73 MiB |
| 100,000 | 4,323,746 | 14.0 s | 12.6 s | 2.9 s | 168 MiB |
| 200,000 | 8,636,296 | 18.4 s | 16.9 s | 3.4 s | 229 MiB |
| 400,000 | 17,346,085 | 27.5 s | 26.3 s | 5.9 s | 353 MiB |

## Real data on Exasol

9,554,757 NYC taxi trips, 62 gate runs as RAW grows to 9.5 million rows, after the unit tail check: median 6.5 s,
max 12.9 s per gate run on Exasol; 3.7 s median on the stand-in for the same 62 runs, recorded on 26 Oct
([`samples/exasol/real_backtest.md`](../samples/exasol/real_backtest.md), [`samples/real_backtest.md`](../samples/real_backtest.md)).

## Not measured

* Cold runs after restarting the Exasol database, and a repeat of the scaling run after the unit tail check: both were
  planned for 28 Oct, but bulk loading into Exasol failed on the laptop that night, so neither was run.
* Anything above 400,000 orders a day, and any other machine.

## How to read it

On this laptop and at these sizes the stand-in is faster than Exasol for the gate: it runs inside the Python process,
while Exasol runs in a container behind a network round trip for each of about 30 statements. The stand-in exists so
tests, CI and the demo run anywhere; the numbers above do not show Exasol's own speed at scale.
