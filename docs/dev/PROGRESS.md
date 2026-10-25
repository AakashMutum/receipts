> Working note for contributors, not part of the user documentation.

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

## Phase 4: Red team (2026-10-24)

* `receipts redteam [--backend exasol|duckdb] [--seeds N ...] [--orders-per-day N]` (receipts/redteam.py). Per
  class the share goes 100, 50, 25, 10, 5, 2 percent; past the first miss it keeps going while the missed
  fault still moves the number by 4% or more (first version stopped at the first miss and would have hidden
  the hole below). Unit errors also on GW_A, GW_B, GW_C at 100%. Then 9 up+down pairs at their floors.
* Exasol (seed 11, 20,000 orders a day, 7 min): floors unit_scale on GW_C 100%, duplicate_key 2%,
  key_fanout 2%, stale_feed binary (caught), clock_shift on GW_B 100%, orphan_code 5%. Below the floor:
  unit 50/25/10/5% held UNEXPLAINED (+230% to +20%), clock 50/25% held, orphan 2% published -0.70% (small).
  Pairs: 8 of 9 caught; duplicate_key 2% + orphan_code 5% held as PROVEN_FAULT naming orphan_code only.
  DuckDB (seed 11, 8,000 orders a day): the same floors and the same outcomes at every step.
* **HOLE, on both backends:** a unit change (x100) on 2% of GW_C's payments was published as a verified
  REAL_CHANGE, +6.47% off (Exasol; +5.72% on DuckDB). A live attack from the Red team tab on the demo data
  (seed 7) gave NO_INCIDENT, +8.56% off. Cause: the unit check compares medians, which a 2% change does not
  move, and the real-change test accepts a move with flat volume when the ticket ratio is within 6%.
* Proposed fixes, NOT applied (would need judge-check, the eval, variants and the backtest re-run):
  (a) a tail check in the unit detector: the share of today's amounts per gateway above 20x the baseline
  median, against its baseline share; (b) accept REAL_CHANGE only when volume carries most of the move,
  e.g. |ticket ratio - 1| <= max(0.02, 0.5 x |value ratio - 1|). (b) must be checked against the festival
  control and the two real changes in the taxi backtest before anyone relies on it.
* Red team tab: floor chart from samples/exasol/redteam_report.json (bars in red where a hole was found)
  and "Run one attack" (runs the gate without write-back, then removes the planted batch; refuses with 409
  if tonight is already judged, so it cannot touch a published number). Lab-only, 403 otherwise.
* Tests: tests/test_redteam.py (outcomes, the search keeps looking below the floor, one real attack restores
  RAW and PUB, report shows holes), red team endpoints in tests/test_lab.py.

## Phase 5: A real agent through the Exasol MCP server (2026-10-24)

* `receipts init` on Exasol creates (or re-passwords) `AGENT_READER` and grants CREATE SESSION and SELECT ON
  SCHEMA PUB, again on every init because PUB is recreated. Password from RECEIPTS_AGENT_PASSWORD (default in
  mcp/mcp_client_config.example.json). New view PUB.CONFIRMED_CAUSES (confirmed evidence only); the
  deterministic trust-checking agent now reads only PUB (asserted in tests/test_api.py).
* Verified on Exasol 2026.2.0-nano.3 (`receipts doctor`, `scripts/mcp_smoke.py`, tests/test_exasol_live.py):
  reads PUB.METRIC_TRUST (43 rows) and PUB.CONFIRMED_CAUSES; refused with "insufficient privileges" on
  RAW.PAYMENTS, PIPE.DAILY_REVENUE, RECEIPTS.CASES, DELETE/UPDATE/INSERT on PUB and CREATE SCHEMA. With the IST
  case held it sees HELD, no trusted value, the guidance, and the proven cause clock_shift (gateway GW_B).
* A probe script of mine first printed the writes as allowed; that was a bug in the probe (it never sent
  them). Re-run correctly, Exasol refused every one, and PUB was unchanged (42 rows). The doctor now only
  accepts an "insufficient privileges" error as a refusal.
* docs/MCP_DEMO.md: Claude Desktop config and `claude mcp add` command (from the Exasol MCP server docs:
  EXA_DSN/EXA_USER/EXA_PASSWORD, EXA_SSL_CERT_VALIDATION, EXA_MCP_SETTINGS with enable_read_query and a PUB
  schema filter), the prompts and the expected behaviour.
* NOT tested: the MCP server itself (uv is not installed here, so the smoke test skips that part), Claude
  Desktop, Claude Code, and any live model answer.

## Phase 6: Documentation and open-source polish (2026-10-24)

* docs/tour.gif (0.29 MB, 16 frames, 800x500), recorded on Exasol with scripts/capture_tour.py: batch lands
  and is published, Break the pipeline, the live timeline, HELD, receipt, approve, the agent. No image library:
  Chromium decodes and scales the screenshots, numpy writes the GIF. Checked by decoding it in Chromium.
* Dockerfile and .dockerignore for the stand-in demo in lab mode. NOT built: Docker Desktop was not running,
  and Podman is busy hosting Exasol on the same small VM.
* docs/EVAL_CARD.md (scope, data, results, holes, what is not claimed), docs/starter_issues.md, now docs/dev/starter_issues.md (6 issues;
  `gh` is not installed, so none were opened on GitHub).
* README restructured: pitch, results table, tour GIF and the two modes, how Exasol is used (with the
  Exasol-measured timings), quick start for Windows, macOS and Linux (plus Docker), real-data backtest, red
  team (with the hole), scaling, agent demo, limits, architecture and diagrams. Test count 112 (2 live-only).
* `receipts run` and `receipts sample` now refuse (exit 3) unless the loaded data is the synthetic data, as
  they plant faults too (lab rule).

## Phase 7: Final checks and screenshots (2026-10-24)

* `pytest -q`: 110 passed, 2 skipped (the live-Exasol tests); `RECEIPTS_LIVE_EXASOL=1 pytest -q
  tests/test_exasol_live.py` on Exasol: 2 passed. `receipts judge-check`: all 8 checks pass, 20/20 runs.
* `receipts doctor` on Exasol: all checks ok, including the 9 AGENT_READER checks.
* `receipts init --fresh` on Exasol (15.2 s), then all screenshots retaken on Exasol with
  scripts/capture_screenshots.py for batch day Fri 23 Oct 2026: 01 to 06 as before, 07_timings replaced by
  10_measured_by_exasol, new 08_break_it (click to HELD 7.39 s in that capture) and 09_redteam.
* Docs re-read for stale numbers, links (all relative links resolve) and em dashes (none). Updated the run
  guide, demo script, security notes and architecture for lab mode and the agent user.
* Left on Exasol: fresh demo data (`receipts init --fresh` at the end), no server running.
* Open: the unit-change hole (fixes proposed above, not applied); the MCP server, Claude clients and Docker
  build are untested here; GitHub issues not created (no `gh`). Nothing merged into main.

## Small fixes: day rollover, first view, empty timings (2026-10-24)

* `receipts demo` and the run scripts rebuild when the data is not for yesterday in India (no --day), also at midnight while running; `serve` only shows "The data is for <date>. Run receipts demo to refresh." (API `stale`).
* In lab mode `demo` lands the IST written as UTC batch after a rebuild, so the page opens on a held number; normal mode waits and says "Run receipts demo, or load a batch". "Where the time went" says "No run yet" until a run exists.
* Tests: tests/test_stale_day.py (stand-in). Phase 8 work (unit tail check, held-out reruns) is in the working tree, not committed, and paused as asked.

## Phase 8: Close the unit-change hole (2026-10-26)

* Held-out partial unit errors (`receipts heldout`, 24 cases: x10 and x1000, GW_A and GW_B, 2/5/10%, seeds 21
  and 22) were committed before the fix (cf597ca) and not changed after.
* Fix (a) applied in `receipts/detectors.py` (`_unit_tail`): per gateway and currency, today's rows above 20x
  the baseline median against the baseline share, Poisson test with a 1e-6 false-alarm budget per slice and
  night (lambda floored at 0.5); the factor (10, 100, 1000) is fitted from the baseline's upper tail and the
  correction divides only the rows above the cut. Tests: `tests/test_unit_tail.py`. Fix (b) was not needed: no
  re-run published a wrong number, so it is not applied.
* Re-run on Exasol, in order, one job at a time: judge-check 8 of 8 (20/20); held-out before 0 caught / 24 held,
  after 12 caught (all x1000) / 12 held (all x10), 0 published either time; red team seed 11 unit floor 100% ->
  2%, holes 1 -> 0, pairs 8 of 9 as before; variants caught 13 -> 15, held 3 -> 1, wrong 0; eval 50 of 50,
  identical precision, recall and ablation figures, festival REAL_CHANGE on all 5 seeds, gate median 3,410 ms.
  DuckDB copies (held-out, red team, variants with 2 seeds: caught 26 -> 30) agree.
* **Not closed:** x10 on 2 to 10% of a gateway is held without a cause (amounts stay below the 20x cut). The cut
  was not lowered after seeing the held-out results.
* **Not re-run: the real-data backtest.** It was stopped while exporting its CSVs at 556 MB free disk on C:;
  deleting the regenerable files in the project freed 0.13 GB (2.3 GB free, 6 GB wanted). So whether 13 Feb and
  27 Feb still publish as REAL_CHANGE with the tail check is not verified; the docs say so.

## Phase 9: One set of timings on an idle laptop (2026-10-26)

* Waited until 30 s of CPU samples averaged 11.5% (max 19.7%), then one job at a time on Exasol: `init --fresh`
  15.9 s; `receipts run ist_utc` x5, all PROVEN_FAULT clock_shift: first run 6.6 s end to end (5.4 s by Exasol),
  repeats median 5.6 s (4.2 to 5.7 s), 4.6 s by Exasol, 27 client statements, 37 in EXA_STATISTICS, peak temp
  memory 63 to 69 MiB; click to HELD (`scripts/measure_break.py --runs 5`, port 8765) median 8.4 s, runs 9.4,
  8.4, 8.4, 6.8 and 20.5 s (the slow run kept). Report: `samples/exasol/timings.md` and `.json`.
* README, RUN_GUIDE, EVAL_CARD and DEMO_SCRIPT now quote this set. Slower than the 24 Oct figures (4.2 s, 7.3 s);
  the tail check adds a query and the laptop was not otherwise controlled, so no step-by-step comparison is made.
  Scaling, the backtest timings and screenshot 10 are from 24 Oct and are labelled so.
* Found: `receipts run` crashes with a charmap UnicodeEncodeError on Windows when stdout is redirected to a file
  (cp1252); the gate finished and the case was written, but `--json` was not. Worked around with
  PYTHONIOENCODING=utf-8; not fixed.
* Left on Exasol: demo data from `init --fresh` (batch day 2026-10-25) after the timing runs; no server running.

## Housekeeping and judge docs (2026-10-26)

* Moved PROGRESS.md, DEMO_SCRIPT.md and starter_issues.md into docs/dev/ with a working-note line; links updated (relative-link check: 0 broken).
* Added JUDGES.md (criteria to evidence, Exasol features, metrics copied from samples/, verify commands, limits) and NOVELTY.md; README opens with a Start here note.
* `pytest -q`: 124 passed, 2 skipped (live Exasol). No Exasol runs or evals in this step.
