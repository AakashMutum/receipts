<p align="center">
  <img src="docs/banner.svg" alt="Receipts: hold the number, prove why, tell people and agents whether to trust it" width="100%">
</p>

# RECEIPTS: Proof for Every Number That Moves

## Overview

Receipts is a data-trust layer for a daily business metric. When revenue jumps or drops, it holds the number back, proves which upstream fault caused it by undoing that fault in a sandbox, and publishes a trust flag that dashboards and AI agents can read. The checks, the proof and the write-back all run inside Exasol.

Built for ExaThon India 2026, Track 4: The Work Behind the Work.

## Problem

A finance analyst at an Indian fintech marketplace can't tell whether a sudden change in daily revenue is real or a silent data bug, because the number passes through several tables and every check says green. If this worked, she'd know within minutes which upstream fault caused it, with proof, instead of guessing for two days.

The faults are boring and common:

* a gateway starts sending paise instead of rupees
* a payment file is loaded twice
* a dimension table quietly gains duplicate keys
* the FX feed misses a day
* a connector writes IST into a UTC column
* a new category code falls out of an inner join

None of them trips a null check or a row count check. They just make the number wrong.

## Solution

Three layers, in this order. The LLM never decides what is true.

1. **Gate (prevent).** Six detectors check tonight's raw batch before the dashboard sees it. A suspicious number is held, and the dashboard keeps showing the last trusted value.
2. **Investigate (prove).** Break the change down across every slice in one `GROUP BY CUBE`, read lineage from the database's own view definitions, then undo each suspect in a sandbox schema and re-run the metric. A cause is confirmed only if undoing it brings the number back into range and leaves published history untouched.
3. **Explain.** A plain-language summary and the exact fix as a diff. Template text by default. An LLM rewrites it only if a key is set, and only from aggregated evidence.

## Key Features

* **Prove by undoing.** A detector only nominates a suspect. The undo test rebuilds the pipeline with the fault removed and shows the number come back.
* **Two faults that cancel out.** The total looks normal, a threshold alert stays silent, and Receipts proves both faults.
* **Real changes are published.** On a festival surge the duplicate check fires on payment retries, undoing it changes nothing, so it is ruled out and the surge is published as a verified real change.
* **Agent-safe.** `PUB.METRIC_TRUST` tells an AI agent connected through the Exasol MCP server not to quote a held number, and gives the last trusted value.
* **Human in the loop.** A proven fault stays held until a person approves the corrected value. Approval is logged.
* **Works without a key.** The LLM explanation is optional. The whole system runs offline.
* **Command center.** One responsive page: the number, the receipt, where it moved, the undo chart, lineage, the fix diff, and a side-by-side agent comparison.

## Technology Stack

* Exasol Personal: SQL, `GROUP BY CUBE` with `GROUPING_ID`, Python 3 SET SCRIPT UDF, `SYS.EXA_ALL_VIEWS`, schemas, `IMPORT`
* Exasol MCP server for agent access
* Python 3.10+, pyexasol, sqlglot (lineage), Jinja2 (one SQL template per dialect), NumPy
* DuckDB as a local stand-in so anyone can reproduce results without installing a database
* FastAPI and Uvicorn
* Plain HTML, CSS and JavaScript for the UI, no build step
* Optional: Anthropic API for the explanation text

## How It Works

```
raw batch lands
      |
      v
 six detectors  ---->  nominate suspects, each with evidence and a correction
      |
      v
 GROUP BY CUBE  ---->  11,000+ slices, today vs the 14-day baseline
      |
      v
 lineage        ---->  does this column feed the metric? (from EXA_ALL_VIEWS)
      |
      v
 undo test      ---->  rebuild pipeline in RECEIPTS_SBX with one fault removed, re-run 15 days
      |
      v
 evidence gate  ---->  four rules, then the combination that puts the number back in range
      |
      v
 verdict        ---->  NO_INCIDENT | REAL_CHANGE | PROVEN_FAULT | UNEXPLAINED
      |
      v
 write back     ---->  RECEIPTS.*, PUB.DAILY_REVENUE_PUBLISHED, PUB.METRIC_TRUST
```

The four rules for confirming a cause:

1. The evidence names a specific column and slice.
2. That column feeds this metric, according to lineage parsed from the catalog.
3. Undoing it moves today's number by at least 1.5%.
4. History stays exactly as published, or comes back to exactly what was published.

How Exasol is used:

| Exasol feature | What Receipts does with it |
|---|---|
| `GROUP BY CUBE` with `GROUPING_ID` | Tests every combination of six dimensions for today and the baseline in one scan |
| `PYTHON3 SET SCRIPT` UDF | `RECEIPTS.CLOCK_DRIFT` compares each gateway's half-hour profile with its baseline and finds the shift that lines it up, per group, inside the database |
| `SYS.EXA_ALL_VIEWS` | Lineage from the view text Exasol already stores |
| Views and schemas | The undo test rebuilds the full pipeline in a sandbox schema with one source swapped |
| `IMPORT` via pyexasol | Bulk load of the synthetic landing data |
| `SYS.EXA_SQL_KEYWORDS` | `receipts doctor` checks every identifier against reserved words |
| Exasol MCP server | Agents read `PUB.METRIC_TRUST` before quoting a number |

The architecture in full is in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Project Structure

```
receipts/
├── receipts/            engine
│   ├── sql/             schema, pipeline views, published views (Jinja, rendered per dialect)
│   ├── udf/             clock_drift.py, the in-database Python UDF, deployed verbatim
│   ├── detectors.py     six detectors, each returning evidence and a correction
│   ├── decompose.py     GROUP BY CUBE over six dimensions
│   ├── lineage.py       lineage from the catalog's view text
│   ├── undo.py          sandbox rebuild and history check
│   ├── gate.py          the three layers, the evidence gate, write-back, approval
│   ├── agent.py         naive agent vs trust-checking agent
│   ├── evaluate.py      scored evaluation with baselines and ablation
│   ├── faults.py        planted faults and ground truth (the engine never imports it)
│   ├── datagen.py       seeded synthetic marketplace data
│   └── api.py           FastAPI endpoints for the command center
├── web/                 command center: index.html, app.css, app.js
├── tests/               35 tests, including every scenario on the Exasol SQL path
├── samples/             committed, unedited eval reports and case files
├── sql/exasol/          all rendered Exasol SQL, for reading
├── mcp/                 MCP server config and agent instructions
└── docs/                run guide, architecture, demo script, jury Q&A
```

## Building & Running

Requires Python 3.10 or newer. Works on Windows, macOS and Linux.

### 1. Try it with no database

Windows (PowerShell):

```powershell
git clone https://github.com/AakashMutum/receipts.git
cd receipts
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
receipts judge-check     # reproduces the results table below on fresh data
receipts init            # builds the local stand-in database
receipts serve           # opens on http://127.0.0.1:8000
```

macOS and Linux:

```bash
git clone https://github.com/AakashMutum/receipts.git && cd receipts
python3 -m venv .venv && source .venv/bin/activate
make install
make judge-check
make demo
```

The header chip on the page says **Local stand-in** so nobody mistakes it for Exasol.

### 2. Run it on Exasol Personal

1. **Install the launcher.**
   * Windows 10 or later (amd64): download the `exasol` launcher from the [Exasol download portal](https://downloads.exasol.com/exasol-personal), put it in a folder on your `PATH`, then open a new PowerShell and run `exasol version`. The launcher offers to install Podman through `winget` if it is missing, which may ask for administrator approval.
   * macOS and Linux: `curl https://downloads.exasol.com/exasol-personal/installer.sh | sh`
2. **Start the database.** `exasol install local`
3. **Enable Python UDFs.** `exasol slc install python3` (restarts the database)
4. **Read the connection details.** `exasol info`. Local defaults are user `sys`, password `exasol`.
5. **Point Receipts at it and build.**

   PowerShell:

   ```powershell
   $env:RECEIPTS_BACKEND = "exasol"
   $env:EXA_DSN = "localhost:8563"
   $env:EXA_USER = "sys"
   $env:EXA_PASSWORD = "exasol"
   receipts init
   receipts doctor
   receipts serve
   ```

   macOS and Linux:

   ```bash
   export EXA_DSN=localhost:8563 EXA_USER=sys EXA_PASSWORD=exasol
   make exasol-init
   RECEIPTS_BACKEND=exasol make serve
   ```

`receipts doctor` checks that every statement parses with the Exasol grammar, that the database is reachable, that no identifier is a reserved word, and that the UDF runs inside the database. The header chip now reads **Exasol** and every receipt shows how long each step took in the database.

### 3. Try the scenarios

```
receipts run ist_utc          IST written as UTC
receipts run unit_paise       a gateway sends paise
receipts run festival         the real-change control
receipts run masked_pair      two faults that cancel out
receipts eval                 full scored evaluation, writes samples/eval_report.md
receipts eval --backend exasol  the same evaluation on Exasol (rebuilds the database once per seed)
```

Others: `healthy`, `duplicate_load`, `join_fanout`, `stale_fx`, `new_code`, `unknown_discount`.

### 4. Connect an AI agent (optional)

Add the Exasol MCP server using [`mcp/claude_desktop_config.example.json`](mcp/claude_desktop_config.example.json) and paste [`mcp/AGENT_INSTRUCTIONS.md`](mcp/AGENT_INSTRUCTIONS.md) into the agent's instructions. Full steps, an optional LLM explanation key, and troubleshooting are in [`docs/RUN_GUIDE.md`](docs/RUN_GUIDE.md).

### Running Tests

```
pytest -q
```

## Results

Scored against ground truth on Exasol Personal, on freshly generated data: 10 scenarios on each of 5 seeds, 20,000 orders a day (`receipts eval --backend exasol`). Full report: [`samples/eval_report.md`](samples/eval_report.md).

| System | Right call to hold or publish | Cause precision | Cause recall | Wrong causes named |
|---|---|---|---|---|
| **Receipts** | **100%** | **100%** | **100%** | **0** |
| Detectors without the undo test (ablation) | 80% | 89% | 100% | 5 |
| Threshold alert (a typical monitor) | 88% | n/a | 0% | 0 |

* 50 of 50 runs: right verdict and exactly the right causes.
* Corrected values land within 0.017% of the true clean value.
* Without the undo test, the festival retry burst gets blamed as a duplicate load every time.
* The threshold alert never names a cause and misses the masked pair because the total looks normal.
* The tenth scenario has no detector on purpose. Receipts holds it as `UNEXPLAINED` and names no cause, which is scored as correct.
* Gate latency on Exasol, from batch landing to written receipt: median 3.4 s per run. 45 of 50 runs finished within 7 s; five took 7 to 27 s, spread over different seeds and scenarios, which we put down to the local container on a laptop rather than to the query plan.
* The same 50 runs with the current code (weekday baseline included) are in [`samples/exasol/eval_report.md`](samples/exasol/eval_report.md): 50 of 50 again.

### Exasol timings for one incident

`receipts run ist_utc` on Exasol Personal 2026.2.0-nano.3 (Windows 11 laptop, Podman on WSL2 with 6 CPUs and 7.7 GiB RAM visible to the VM, 20,000 orders a day, about 844,000 payment rows). Verdict `PROVEN_FAULT`, cause `clock_shift`, 26 SQL statements, 4.2 s end to end, 3.2 s of it inside the database. The first run right after a fresh load is slower (7.8 s).

| Step | Time |
|---|---|
| Read candidate and five weeks of trusted history | 192 ms |
| Run six detectors on the incoming batch (clock check is a Python UDF inside Exasol) | 692 ms |
| Read lineage from view definitions (`EXA_ALL_VIEWS`) | 44 ms |
| Test 11,074 slices over 296,484 rows in one `GROUP BY CUBE` | 1,091 ms |
| Reconcile raw payments to revenue rows | 354 ms |
| Undo each suspect in a sandbox schema | 997 ms |
| Write receipts back to the database | 761 ms |

Loading the full dataset with `receipts init` takes 12 to 18 s.

At five times the volume (`receipts init --fresh --orders-per-day 100000`, 4.2 million payment rows, loaded in 40 s) on the same laptop, both cases still reach the right verdict. `ist_utc` takes 6.8 s (5.9 s in the database, CUBE over 1.48 million rows in 1.9 s) and `masked_pair` 9.7 s (8.6 s in the database, two suspects undone). Nothing larger has been measured.

At a smaller sample (3,000 orders a day) Receipts passes 29 of 30. It misses the no-detector fault on one seed, because daily noise there is wider than the fault. See [`samples/eval_quick.md`](samples/eval_quick.md).

## Beyond the scripted scenarios

The ten scenarios were used to build and tune the detectors, so a perfect score on them shows the system is consistent, not that it generalises. To test that, `receipts variants` runs 17 held-out variants: other gateways, other factors, partial row coverage, other file counts, and two faults at once. Each run is judged against the clean value, so the question is how a miss fails, not whether the score is 100%. Full table: [`samples/variants_report.md`](samples/variants_report.md).

* **Result: 26 caught, 6 held for a person, 2 published as harmless, 0 published wrong** (17 variants on 2 seeds, 34 runs). Nothing that was wrong by more than 4% was published as trusted.
* **On Exasol** (`receipts variants --backend exasol --seeds 11`): caught 13, held 3, small 1, wrong 0, the same outcome for every variant as the stand-in on that seed. Table: [`samples/exasol/variants_report.md`](samples/exasol/variants_report.md).
* **Known gaps, all held for a person with no cause named:** a unit change on only part of a gateway's rows (the median does not move), and a clock shift of 12 hours.
* **One variant is published on purpose:** a one-hour clock shift on one gateway moves revenue by 1.5%, inside normal noise.
* Writing the variants found a real bug. The unit check only recognised a factor of about 100, while the README claimed 10, 100 and 1000. It now accepts any power of ten up to 1000.

Weekly pattern: real revenue has weekday and weekend levels. With five weeks of trusted history the gate learns each weekday's index when (and only when) a one-way ANOVA says the pattern is real, and compares today with what that weekday should look like. On data with a weekly pattern of up to 16% above average, the gate gave 63 of 63 correct verdicts across all seven weekdays. With the old flat 14-day baseline the same data gave 56 of 63: no false alarms, but the wider range let an undetected fault of about 9% through unnoticed on every weekday.

## Technical Notes

**What is real and what is synthetic.** All data is synthetic: a fictional marketplace with 8 cities, 6 categories, 4 payment gateways, a USD slice with a daily FX feed, evening-heavy shopping in IST, and background payment retries, generated from a seed. The faults are planted as SQL statements in `receipts/faults.py`. Every query, the CUBE decomposition, the UDF, lineage parsing, the undo tests, the write-back, the timings and the evaluation numbers are real.

**About the local stand-in.** DuckDB is not a second implementation. The same SQL templates render both spellings and the UDF source file is identical in both paths. The tests also run every scenario through an Exasol SQL path: each statement is rendered for Exasol, parsed with sqlglot's Exasol grammar, translated and executed, and must reach the same verdicts.

**Limitations.**

* It only proves fault classes it has a detector for. Six today. Anything else becomes `UNEXPLAINED`: held, no cause guessed, a person decides.
* The baseline is the mean and spread of the last 14 trusted days, with no weekly or festival calendar.
* One metric, one pipeline. Lineage parsing handles joins, filters, group by and simple expressions, not deeply nested SQL or stored procedures.
* Corrections are hotfixes. The real fix is upstream, and Receipts records the evidence for that conversation.
* Access control is a convention on Exasol Personal because it is single-user. On Enterprise it is a role grant.
* Exasol itself is not started in CI, so the Exasol path is verified by hand on Exasol Personal 2026.2.0-nano.3 and by the stand-in tests.

## License

MIT. See [LICENSE](LICENSE).
