# Timings on Exasol, one session

Measured on 2026-10-26 on one Windows 11 laptop, Intel Core 5, Podman on WSL2 (about 7.7 GiB visible to the VM), Exasol 2026.2.0-nano.3, one job at a time, after the unit tail check. 30 s of CPU samples just before: average 11.5%, max 19.7% (a browser was open, no other job running). Demo data, 20,000 orders a day (863,336 payment rows). Raw numbers: [`timings.json`](timings.json).

| What | Result |
|---|---|
| `receipts init --fresh` | 15.9 s |
| `receipts run ist_utc`, first run after the fresh load | 6.6 s end to end, 5.4 s measured by Exasol |
| `receipts run ist_utc`, 4 repeats | median 5.6 s end to end (4.2 to 5.7 s), median 4.6 s measured by Exasol |
| Statements per IST run | 27 sent by the client, 37 in Exasol's statistics |
| Peak temporary memory per IST run | 62.8 to 68.8 MiB |
| Click Break the pipeline to HELD (`scripts/measure_break.py --runs 5`) | median 8.4 s; runs 9.4, 8.4, 8.4, 6.8, 20.5 s |
| Gate latency in the 50-run eval (same day, just before) | median 3.4 s, max 11.7 s |

Every IST run gave PROVEN_FAULT with clock_shift.

## Where the time went, IST case, median of the 4 repeats

| Step | End to end | Measured by Exasol |
|---|---|---|
| Read candidate and trusted history | 166 ms | 139 ms |
| Run six detectors on the incoming batch | 890 ms | 816 ms |
| Read lineage from view definitions | 46 ms | 15 ms |
| Test 11,074 slices in one GROUP BY CUBE | 1,306 ms | 918 ms |
| Reconcile raw payments to revenue rows | 466 ms | 440 ms |
| Undo each suspect in a sandbox schema | 1,420 ms | 1,258 ms |
| Write receipts back to the database | 825 ms | 718 ms |

## Notes

* Slower than the numbers first published on 24 Oct (IST case 4.2 s end to end, click to HELD 7.3 s). Since then the unit detector runs one more query (the tail check); the machine was idle but not otherwise controlled, so the two sets are not compared step by step. The docs now use this set.
* The fifth click-to-HELD run took 20.5 s, the others 6.8 to 9.4 s. It was neither repeated nor dropped; the median is reported.
* Not re-measured: scaling (20k to 400k orders a day) and the real-data backtest. Both need more free disk than the laptop had; their timings are from 24 Oct, before the tail check.
