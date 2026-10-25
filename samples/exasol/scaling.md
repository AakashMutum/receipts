# Scaling the gate

The IST written as UTC case (`ist_utc`) on Exasol 2026.2.0-nano.3, at increasing order volumes. For each size: `receipts init --fresh --orders-per-day N` (seed 7, 42 days of history plus the incoming day), then one gate run with write-back. Client times are measured by Receipts around each statement; the "measured by Exasol" columns are what Exasol recorded itself in EXA_STATISTICS.EXA_SQL_LAST_DAY.

Reproduce: `receipts scale --backend exasol --sizes 20000 100000 200000 400000`. Total time 17 minutes.

| Orders a day | Payment rows | Load and build | Gate end to end | Inside the database (client) | Measured by Exasol | CUBE step | CUBE, measured by Exasol | Peak temp memory | Rows in the CUBE | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 20,000 | 863,336 | 25 s | 9.1 s | 6.9 s | 7.6 s | 2.4 s | 1.9 s | 73 MiB | 296,484 | PROVEN_FAULT clock_shift |
| 100,000 | 4,323,746 | 40 s | 14.0 s | 12.1 s | 12.6 s | 2.9 s | 2.5 s | 168 MiB | 1,480,308 | PROVEN_FAULT clock_shift |
| 200,000 | 8,636,296 | 86 s | 18.4 s | 16.5 s | 16.9 s | 3.4 s | 3.0 s | 229 MiB | 2,948,860 | PROVEN_FAULT clock_shift |
| 400,000 | 17,346,085 | 215 s | 27.5 s | 26.0 s | 26.3 s | 5.9 s | 5.5 s | 353 MiB | 5,950,587 | PROVEN_FAULT clock_shift |

How to read it:

* Each gate run is the first one after a fresh load, which is slower than a repeat run on the same data (earlier on this laptop at 20,000 orders a day: 7.8 s for the first run, 4.2 s for a repeat).
* The client "inside the database" column sums the statements up to the verdict. The Exasol column also includes the write-back step and the automatic commit after each statement, so it is a little larger.
* Peak temp memory is the largest TEMP_DB_RAM_PEAK Exasol recorded for any statement of the run.

Largest size measured: **400,000 orders a day, 17,346,085 payment rows**. Nothing larger is claimed.

Every size reached the right verdict and cause.
