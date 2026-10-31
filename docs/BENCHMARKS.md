# Benchmarks

Every number on this page comes from a committed, recorded run. The IST case (`ist_utc`: one gateway writes IST
timestamps as UTC) at 20,000 orders a day is the reference: 863,336 payment rows, 11,074 slices in the CUBE.

## Machine

| | |
|---|---|
| Laptop | Intel Core 5 120U (10 cores, 12 threads), 15.6 GiB RAM, Windows 11 Pro 10.0.26300 |
| Exasol | Exasol Personal 2026.2.0-nano.3 in Podman 5.8.3 on WSL2 (VM set to 6 CPUs; about 7.7 GiB visible to it) |
| Free RAM | 0.9 GiB free on the host on 29 Oct, with the Exasol VM running during every run below |
| Stand-in | DuckDB, in the same Python process as Receipts |

## The IST case on Exasol and on the stand-in

Recorded on 29 Oct 2026, one job at a time, with the same method on both: [`scripts/bench_exasol.py`](../scripts/bench_exasol.py)
([`samples/exasol/bench.json`](../samples/exasol/bench.json)) and [`scripts/bench_standin.py`](../scripts/bench_standin.py)
([`samples/standin_bench.json`](../samples/standin_bench.json)). Cold: a freshly built database (`receipts init --fresh`
on Exasol) and a new process that runs the gate once, 3 times. This is a fresh load and a new session, not a database
restart. Warm: 3 repeats in one process after a first run. Without write-back. All 14 runs, the first warm runs included, gave PROVEN_FAULT.

| Gate only, IST case, without write-back, end to end | Cold, median (range) | Warm, median (range) |
|---|---|---|
| Exasol | 3.38 s (3.17 to 4.15) | 3.23 s (3.12 to 3.27) |
| Exasol, measured by Exasol | 2.28 s (2.03 to 2.74) | 2.16 s (2.12 to 2.18) |
| DuckDB stand-in | 0.68 s (0.66 to 0.73) | 0.65 s (0.63 to 0.68) |

Peak temporary memory on Exasol: 62.5 to 67.7 MiB per run.

Median per step, warm:

| Step | Exasol, end to end | Measured by Exasol | Stand-in |
|---|---|---|---|
| Read candidate and trusted history | 98 ms | 81 ms | 50 ms |
| Run six detectors (on Exasol the clock check is the Python UDF; on the stand-in the same source runs through a local shim) | 536 ms | 485 ms | 114 ms |
| Read lineage from view definitions | 56 ms | 27 ms | 26 ms |
| Test 11,074 slices in one GROUP BY CUBE | 669 ms | 450 ms | 233 ms |
| Reconcile raw payments to revenue rows | 235 ms | 222 ms | 131 ms |
| Undo each suspect in a sandbox schema | 981 ms | 884 ms | 86 ms |

Earlier recordings of the same case, with write-back: 5.6 s median end to end and 4.6 s measured by Exasol on 26 Oct
([`samples/exasol/timings.md`](../samples/exasol/timings.md)), and 0.54 s cold and 0.55 s warm on the stand-in on 28 Oct
(without write-back). In the live UI, from clicking Break the pipeline until the HELD banner shows (landing the fault, the gate with write-back and the page's polling): median 8.4 s over 5 runs (6.8 to 20.5 s), 26 Oct, same report.

## Scaling on Exasol

Recorded on 29 Oct 2026, after the unit tail check ([`samples/exasol/scaling.md`](../samples/exasol/scaling.md)).
Each size is the first gate run after a fresh load, with write-back. Every size gave the right verdict and cause.

| Orders a day | Payment rows | Gate end to end | Measured by Exasol | CUBE | Peak temp memory |
|---|---|---|---|---|---|
| 20,000 | 863,336 | 4.5 s | 4.0 s | 0.7 s | 65 MiB |
| 100,000 | 4,323,746 | 7.2 s | 6.6 s | 1.2 s | 157 MiB |
| 200,000 | 8,636,296 | 9.0 s | 8.5 s | 1.6 s | 218 MiB |
| 400,000 | 17,346,085 | 15.8 s | 15.1 s | 2.7 s | 344 MiB |

The first recording, on 24 Oct before the tail check, took 9.1 / 14.0 / 18.4 / 27.5 s end to end on the same laptop.
The tail check adds statements (33 per run instead of 26), so the later run does more work; why it was faster was not
measured (other load on the laptop was not recorded on 24 Oct).

## Real data on Exasol

9,554,757 NYC taxi trips, 62 gate runs as RAW grows to 9.5 million rows, after the unit tail check: median 6.5 s,
max 12.9 s per gate run on Exasol; 3.7 s median on the stand-in for the same 62 runs, recorded on 26 Oct
([`samples/exasol/real_backtest.md`](../samples/exasol/real_backtest.md), [`samples/real_backtest.md`](../samples/real_backtest.md)).

## Not measured

* Cold runs right after restarting the Exasol database. A restart has to be done from a normal PowerShell window,
  not from the tool that ran these benchmarks, so it was not part of this run.
* Anything above 400,000 orders a day, and any other machine.

## How to read it

On this laptop and at these sizes the stand-in is faster than Exasol for the gate: it runs inside the Python process,
while Exasol runs in a container behind a network round trip for each of about 30 statements; the largest gap is the undo step, which rebuilds the pipeline views in a sandbox schema. The stand-in exists so
tests, CI and the demo run anywhere; the numbers above do not show Exasol's own speed at scale.
