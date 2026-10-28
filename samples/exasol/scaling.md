# Scaling the gate

The IST written as UTC case (`ist_utc`) on Exasol 2026.2.0-nano.3, at increasing order volumes. For each size: `receipts init --fresh --orders-per-day N` (seed 7, 42 days of history plus the incoming day), then one gate run with write-back. Client times are measured by Receipts around each statement; the "measured by Exasol" columns are what Exasol recorded itself in EXA_STATISTICS.EXA_SQL_LAST_DAY.

Reproduce: `receipts scale --backend exasol --sizes 20000 100000 200000 400000`. Total time 9 minutes.

| Orders a day | Payment rows | Load and build | Gate end to end | Inside the database (client) | Measured by Exasol | CUBE step | CUBE, measured by Exasol | Peak temp memory | Rows in the CUBE | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 20,000 | 863,336 | 11 s | 4.5 s | 3.6 s | 4.0 s | 0.7 s | 0.5 s | 65 MiB | 296,484 | PROVEN_FAULT clock_shift |
| 100,000 | 4,323,746 | 26 s | 7.2 s | 6.4 s | 6.6 s | 1.2 s | 1.0 s | 157 MiB | 1,480,308 | PROVEN_FAULT clock_shift |
| 200,000 | 8,636,296 | 46 s | 9.0 s | 8.3 s | 8.5 s | 1.6 s | 1.4 s | 218 MiB | 2,948,860 | PROVEN_FAULT clock_shift |
| 400,000 | 17,346,085 | 92 s | 15.8 s | 14.8 s | 15.1 s | 2.7 s | 2.5 s | 344 MiB | 5,950,587 | PROVEN_FAULT clock_shift |

How to read it:

* Each gate run is the first one after a fresh load, which is slower than a repeat run on the same data (earlier on this laptop at 20,000 orders a day: 7.8 s for the first run, 4.2 s for a repeat).
* The client "inside the database" column sums the statements up to the verdict. The Exasol column also includes the write-back step and the automatic commit after each statement, so it is a little larger.
* Peak temp memory is the largest TEMP_DB_RAM_PEAK Exasol recorded for any statement of the run.

Largest size measured: **400,000 orders a day, 17,346,085 payment rows**. Nothing larger is claimed.

Every size reached the right verdict and cause.
