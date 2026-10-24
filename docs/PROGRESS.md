# Progress log

Work on the `exasol-first-evidence` branch, one entry per phase, so a later session can continue from
here after the context is cleared. Exasol Personal 2026.2.0-nano.3 on a Windows 11 laptop (Intel Core 5,
Podman on WSL2, about 7.7 GiB visible to the VM) is the main platform; the DuckDB stand-in is for CI and
tests. Numbers are copied from the committed reports, not retyped from memory.

Rule added during the work: everything that can write bad data or attack the system is lab-only
(`serve --lab` / `demo --lab` / `RECEIPTS_LAB=1`, and on synthetic data only). See `receipts/lab.py`.

## Phase 1: Exasol-first evidence (2026-10-24)

* `receipts backtest --backend exasol` (new flag; also `--months`): the trip adapter still reads parquet in
  DuckDB, writes the mapped LANDING tables to CSV, IMPORTs them into Exasol, and everything else (pipeline,
  UDF, gate, write-back) runs in Exasol. Full range, no fallback: 9,554,757 trips, Jan to Mar 2024.
* Result on Exasol 2026.2.0-nano.3: 56 real days judged, 0 held (NO_INCIDENT 54, REAL_CHANGE 2: 13 Feb
  -33.9%, 27 Feb +26.0%), 6 of 6 planted faults caught with the right cause. Same thresholds as before.
* Against the DuckDB run: 62 of 62 gate runs with the same verdict and causes, same detectors fired on all
  62, largest relative difference in the daily value 6.45e-05. Two full Exasol runs gave identical verdicts.
* Exasol timings, client side: gate median 14.8 s, max 47.5 s per run (62 runs, RAW grows to 9.5M rows).
  Building the database took 150 s in run 1 and 450 s in run 2; run 2 overlapped about two minutes of local
  test runs on the same laptop, so 150 s is the clean figure. Report: `samples/exasol/real_backtest.md`.
* Lesson: the first run lost its results to a bug in the report code, so the JSON is now written first.
* `receipts scale --backend exasol` (new): IST case after `init --fresh --orders-per-day N`, one gate run
  each. All four sizes gave PROVEN_FAULT clock_shift. Gate end to end 9.1 s / 14.0 s / 18.4 s / 27.5 s at
  20k / 100k / 200k / 400k orders a day (863,336 to 17,346,085 payment rows); load and build 25 / 40 / 86 /
  215 s; CUBE 2.4 / 2.9 / 3.4 / 5.9 s over 296,484 to 5,950,587 rows; Exasol-measured gate time 7.6 / 12.6 /
  16.9 / 26.3 s, peak temp memory 73 / 168 / 229 / 353 MiB. Stopped at 400k on purpose: 8.7 GB free disk
  would not hold the 800k CSVs and the database growth. `samples/exasol/scaling.md` and `.json`.
  `receipts init --fresh` ran at the end (demo day 2026-10-23, 13.7 s, AGENT_READER created).
* Not tested: sizes above 400k; scaling on DuckDB (the command supports it, CI runs a tiny version).
