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

## Phase 2: Exasol reports its own timings (2026-10-24)

* Verified live on Exasol 2026.2.0-nano.3: `EXA_STATISTICS.EXA_SQL_LAST_DAY` (after `FLUSH STATISTICS`) has
  SESSION_ID, STMT_ID, COMMAND_NAME, DURATION (s), CPU, TEMP_DB_RAM_PEAK (MiB), ROW_COUNT and more.
  `EXA_DBA_AUDIT_SQL` has the same columns (auditing is on here) and is the fallback. `EXA_USER_PROFILE_LAST_DAY`
  is empty unless the session sets `PROFILE = 'ON'`, which the gate does not do (it would add overhead).
* How: `SELECT CURRENT_STATEMENT FROM DUAL` before the gate and after every step gives statement-id markers;
  after the run the statistics for the session between the markers are read and summed per step. Automatic
  COMMITs count as database time but not as statements. Stored with the case as `exasol_measured`.
* Shown in the receipt as "Measured by Exasol" and per step in "Where the time went". Unreadable statistics:
  labelled client-side timing. Stand-in: n/a. Tests: `tests/test_measured.py` (stand-in with a fake
  statistics source), `tests/test_exasol_live.py` (real Exasol, skipped unless RECEIPTS_LIVE_EXASOL=1; passed).
* IST case on the demo data, two runs: Exasol measured 4,289 ms and 3,091 ms in 25 statements (client 5,252
  and 3,849 ms end to end), CUBE 1,494 and 834 ms, peak temp memory 67.5 and 76.5 MiB. Reading the
  statistics (FLUSH included) takes another 0.7 to 0.9 s, outside the gate's total.
* The UI part of this phase is in the next commit, because it shares web/app.js with the lab panel.

## Phase 3: Break the pipeline, live, in lab mode (2026-10-24)

* Lab mode (`serve --lab`, `demo --lab`, `RECEIPTS_LAB=1`): without it the page has no scenario picker, no
  Break panel, no Reset, no Red team tab (removed server-side from index.html; /static/index.html is 404) and
  `/api/run`, `/api/lab/*` answer 403. With it, breaking or resetting is refused (409) unless LANDING matches
  `data/manifest.json` of the synthetic generator. Inbox scenario files are lab-only too. Run scripts pass --lab.
* `faults.fault_sql(kind, share, gateway)`: the six faults with a share-of-rows dial (MOD(id, 1000)) and a
  gateway for unit and clock faults; stale FX has no share (one rate is there or not).
* API: POST /api/lab/break starts the gate in a thread and GET /api/lab/job/{id} returns each step as it
  finishes (gate.run got an on_step callback); POST /api/lab/reset removes tonight's RAW batch and published
  row. The page polls every 250 ms and shows the timeline, then the HELD banner, receipt and Approve.
* Measured on Exasol with scripts/measure_break.py (headless Chromium, clock_shift on GW_B, 100%): click to
  HELD 7,254 / 8,483 / 7,166 / 6,890 / 7,566 ms, median 7,254 ms, 9 steps shown live. Port 8000 was taken by
  another app on this laptop, so the measurement ran on port 8765.
* Tests: tests/test_lab.py (403 without lab for every lab endpoint, panel absent, panel present with lab,
  break shows every step then HELD, approve, reset, refusal on non-synthetic data, the --lab flag) and the
  run-script check in tests/test_scripts.py. Not tested: the page in Safari/Firefox, only headless Chromium.
