# Run guide

## 0. One click

Download or clone the repository, then:

| System | Stand-in demo, nothing else to install | On Exasol Personal (must already be running) |
|---|---|---|
| Windows | double-click `run.bat` | double-click `run-exasol.bat` |
| macOS | double-click `run.command` | double-click `run-exasol.command` (Apple Silicon only) |
| Linux | `./run.sh` | `./run-exasol.sh` (needs Podman) |

Every script finds Python 3.10 or newer (and says where to get it if missing), creates `.venv` the first time, installs Receipts only if it is not installed yet, then runs `receipts demo`: build the data if needed, start the command center, open the browser. The window stays open with a message if anything fails. Press Ctrl+C in it to stop.

The `run-exasol` scripts look for the launcher on `PATH`, then in `EXASOL_HOME`, then in your Downloads folder. If Exasol is not running they say "Exasol is not running. Run: exasol start" and stop; they never install Podman or Exasol. Then they run `receipts init`, `receipts doctor` and `receipts demo --watch` against it, so newly landed batches raise alerts (section 7). Exasol Personal runs locally on Windows (amd64), on Apple Silicon Macs and on Linux with Podman; Intel Macs are not supported.

On macOS, the first double-click on a downloaded `.command` file may be blocked as coming from an unidentified developer: right-click it and choose Open once. If the repository came as a ZIP and the file will not run, make it executable with `chmod +x run.command run-exasol.command run.sh run-exasol.sh`.

`receipts demo` takes the same options as `receipts serve` (`--day`, `--port`, `--watch`, `--lab`) plus `--no-browser`.

**Two modes.** Without `--lab` (normal mode) Receipts watches and proves but cannot change data: no scenario picker, no Break the pipeline panel, no Red team tab, and those API endpoints answer 403. With `--lab` or `RECEIPTS_LAB=1` (lab mode, for demos) they appear, and breaking the pipeline is still refused unless the loaded data is the built-in synthetic data. The one-click scripts above start in lab mode. Inbox batch files that plant a scenario (section 7) are lab-only too.

## 1. Without Exasol (anyone, two minutes)

Requires Python 3.10 or newer.

macOS and Linux:

```bash
git clone https://github.com/AakashMutum/receipts.git && cd receipts
python3 -m venv .venv && source .venv/bin/activate
make install
make judge-check
```

Windows (PowerShell; `make` is usually not installed, so run what it runs):

```powershell
git clone https://github.com/AakashMutum/receipts.git; cd receipts
py -m venv .venv; .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
receipts judge-check
```

If PowerShell refuses to run `Activate.ps1`, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or skip
activation and call `.venv\Scripts\receipts.exe` directly.

`judge-check` generates fresh data on two seeds, runs all ten scenarios, scores them against ground truth and prints PASS or FAIL for eight claims. It needs no API key and no network.

Then the command center:

```bash
make demo        # same as: receipts demo (builds if needed, serves, opens the browser)
```

On Windows run `receipts demo` directly.

Open http://127.0.0.1:8000. The header chip says **Local stand-in** so nobody mistakes it for Exasol.

The incoming batch day is yesterday in India (Asia/Kolkata), with 42 days of history generated before it. Every date on the page, the agent's question and the case IDs follow it. `receipts demo` (and the run scripts) rebuild the database when it holds another day, also when the day turns while it runs, and in lab mode land the IST written as UTC batch so the page opens on a held number. `receipts serve` never rebuilds; it says "The data is for <date>. Run receipts demo to refresh." To pin a day, pass it to both commands (the README screenshots use Fri 23 Oct 2026):

```bash
receipts init --day 2026-10-23
receipts serve --lab --day 2026-10-23     # or: make demo DAY=2026-10-23
```

`scripts/capture_screenshots.py` uses the day the server holds, so the screenshots show a current date. `receipts judge-check`, `receipts eval`, `receipts variants` and the tests always use 20 Oct 2026, so their results do not change with the calendar.

## 2. On Exasol Personal (the real target)

Exasol Personal runs locally on macOS (Apple Silicon), on Linux with Podman, and on Windows (amd64) with Podman.

Windows: download the `exasol` launcher from https://downloads.exasol.com/exasol-personal, put it in a folder on your `PATH`, open a new PowerShell and run `exasol version`. If Podman is missing the launcher offers to install it with `winget` (administrator approval may be asked). Windows arm64 is not supported for local deployments. The PowerShell equivalents of the exports below are `$env:EXA_DSN = "localhost:8563"`, and so on. On Windows the simplest route is to double-click `run-exasol.bat` (section 0), which does all of this for you.

```bash
curl https://downloads.exasol.com/exasol-personal/installer.sh | sh   # macOS and Linux only: installs the `exasol` launcher
exasol install local                     # starts the database
exasol slc install python3 --auto-approve   # Python UDF support (restarts the database)
exasol info                              # shows host and port
```

Then point Receipts at it and build:

```bash
export EXA_DSN=localhost:8563            # from `exasol info`
export EXA_USER=sys EXA_PASSWORD=exasol  # Exasol Personal local defaults
make exasol-init
```

`exasol-init` runs `receipts init` and then `receipts doctor`, which checks:

* every SQL statement parses with the Exasol grammar
* the database is reachable and its version
* no identifier we use is a reserved word in `SYS.EXA_SQL_KEYWORDS`
* `RECEIPTS.CLOCK_DRIFT` runs inside the database (if not, it tells you to install the Python container)
* data is loaded

Start the command center against Exasol:

```bash
RECEIPTS_BACKEND=exasol make serve
```

The header now shows **Exasol** and **Python UDF in the database**. Every receipt shows how long each step took inside Exasol.

TLS: local deployments use a self-signed certificate, so certificate checks are off by default (`EXA_INSECURE=1`). Set `EXA_INSECURE=0` and use a DSN with a fingerprint for anything shared.

Measured on Exasol Personal 2026.2.0-nano.3 (Windows 11, Podman on WSL2 with 6 CPUs and 7.7 GiB RAM visible to the VM, 20,000 orders a day): `receipts init --fresh` took 15.9 s, and `receipts run ist_utc` reaches `PROVEN_FAULT` in a median of 5.6 s end to end over 4 repeats (4.6 s inside the database by Exasol's statistics; 6.6 s on the first run after a fresh load). The slowest steps are the sandbox undo test (1.4 s) and the `GROUP BY CUBE` over 11,074 slices (1.3 s). All from one session on 26 Oct: [`samples/exasol/timings.md`](../samples/exasol/timings.md). The full evaluation on Exasol (`receipts eval --backend exasol --out samples/exasol`, 50 runs) passes 50 of 50 with a median gate latency of 3.4 s and takes about 9 minutes. `receipts variants --backend exasol --seeds 11 --out samples/exasol` takes about 2 minutes. Both rebuild the database once per seed, so run `receipts init --fresh` afterwards to get the demo data back.

Measured earlier (before the unit tail check), at 100,000 orders a day (`receipts init --fresh --orders-per-day 100000`, 4.2 million payment rows, about 40 s to load and 2.5 minutes including data generation) `ist_utc` takes 6.8 s and `masked_pair` 9.7 s on the same laptop.

If Exasol refuses connections after the computer has slept, the Podman machine has usually stopped. Run `podman machine start`, then `exasol start`, then `receipts doctor`.

Bigger data for timing claims: `receipts init --fresh --orders-per-day 200000` gives about 8.6 million payment rows.

## 3. The command line

```bash
receipts run ist_utc          # land a batch with a planted fault and run the gate
receipts run festival         # the real-change control
receipts run masked_pair      # two faults that partly cancel
receipts eval                 # full scored evaluation, 5 seeds, writes samples/eval_report.md
receipts eval --backend exasol  # the same evaluation on Exasol
receipts sample               # writes an unedited case file per scenario to samples/cases
receipts export-sql           # writes all Exasol SQL to sql/exasol for reading
receipts demo --watch         # command center plus the batch watcher and alerts (section 7)
receipts watch --once         # judge any newly landed batch once and exit
receipts backtest             # the gate over real NYC taxi data, writes samples/real_backtest.md
receipts backtest --backend exasol  # the same inside Exasol, writes samples/exasol/real_backtest.md
receipts scale                # the IST case at 20k to 400k orders a day on Exasol, writes samples/exasol/scaling.md
receipts redteam              # shrink each fault until the gate stops proving it (synthetic data only)
```

`receipts backtest` downloads about 150 MB of NYC TLC yellow taxi trip records (January to March 2024) once into `data/real/` with a progress line, then judges 56 real days one night at a time and plants six faults on real days. It runs on the local stand-in and takes a few minutes after the download. With `--backend exasol` the mapped trips are bulk loaded into Exasol (about 2.5 minutes for 9.5 million trips on the laptop above) and every gate run happens there, about 35 minutes in all.

`receipts scale` and `receipts redteam --backend exasol` rebuild the database at `EXA_DSN` with synthetic data (the red team plants faults into it) and run `receipts init --fresh` at the end to restore the demo data. Never point them at a database that holds anything else.

Scenarios: `healthy`, `festival`, `unit_paise`, `duplicate_load`, `join_fanout`, `stale_fx`, `ist_utc`, `new_code`, `masked_pair`, `unknown_discount`.

## 4. Connect a real AI agent (MCP)

Full steps for Claude Desktop and Claude Code, with the read-only `AGENT_READER` user that `receipts init` creates on Exasol, are in [`MCP_DEMO.md`](MCP_DEMO.md). In short:

1. Install `uv`, then add the Exasol MCP server to any MCP client (for example a desktop AI assistant) using [`mcp/mcp_client_config.example.json`](../mcp/mcp_client_config.example.json). It logs in as `AGENT_READER`, which can read `PUB` and nothing else. `python scripts/mcp_smoke.py` checks that path without any AI client.
2. Put [`mcp/AGENT_INSTRUCTIONS.md`](../mcp/AGENT_INSTRUCTIONS.md) into the agent's instructions.
3. Run `receipts run unit_paise`, then ask the agent for revenue on the incoming day (the date `receipts init` printed; yesterday unless you passed `--day`), for example "What was revenue on 20 October?" after `--day 2026-10-20`. With the instructions it reads `PUB.METRIC_TRUST`, sees the value is held, and quotes the last trusted day instead. Remove the instructions and ask again to see it quote the broken number.

The command center's "Ask an AI agent" panel shows the same contrast with two deterministic agents, so the demo does not depend on a live model.

## 5. Optional LLM explanation

```bash
export ANTHROPIC_API_KEY=...       # optional
export RECEIPTS_LLM_MODEL=claude-sonnet-5-5
```

A button appears on each receipt. The model receives only the aggregated case (values, verdict, suspects, top slices), never raw rows. If its text brings up a check that never fired, it is discarded and the template text stays. The verdict is never its decision.

## 6. Tests

```bash
make test
```

112 tests, 2 of which run only against a live Exasol (`RECEIPTS_LIVE_EXASOL=1 pytest -q tests/test_exasol_live.py`). `tests/test_scenarios.py` runs all ten scenarios twice: once on the DuckDB stand-in and once on the Exasol SQL path, where every statement is rendered for Exasol, parsed by sqlglot's Exasol grammar, translated and executed.

## 7. Watch for new batches and get alerts

`receipts serve --watch` (or `receipts demo --watch`) runs the command center and a light watcher in one process. Closing the window or pressing Ctrl+C stops both.

* Every 60 seconds (`--interval` to change it) the watcher runs one cheap query: is the newest day in RAW later than the newest published day? Only then does it run the gate. Between checks it sleeps; measured on a laptop it used 0.26% of one core with a 5 second interval and the page open.
* In lab mode it also reads an inbox folder (`inbox/` by default, `--inbox` or `RECEIPTS_INBOX` to change it). A file named after a scenario, such as `ist_utc.batch`, lands that scenario's batch on the next check and is moved to `inbox/processed/`. Other files are moved to `inbox/ignored/`.
* When the gate holds a batch (`PROVEN_FAULT` or `UNEXPLAINED`) it prints an `ALERT` line, writes `alerts/<case>.txt` and `alerts/<case>.json` (verdict, one-line cause, last trusted value, receipt link), and shows an orange **ALERTS** banner in the command center until the case is approved, a new batch replaces it, or someone clicks Dismiss.
* If `SLACK_WEBHOOK_URL` is set it also posts a short message to that Slack incoming webhook, with a 5 second timeout. If Slack is down the alert file is still written and the watcher keeps going.
* A published batch prints one quiet line. A failed check prints one line and the watcher tries again next time; it never stops the server.

Try it:

```bash
receipts demo --watch --lab --interval 5
```

Then, in a second terminal or in your file manager, drop a bad batch into the inbox:

```bash
touch inbox/ist_utc.batch          # Windows PowerShell: New-Item inbox\ist_utc.batch
```

Within a few seconds the console prints `ALERT RC-... held (PROVEN_FAULT). Proven cause: clock shift in RAW.PAYMENTS.CAPTURED_AT (gateway GW_B) ...`, `alerts/` holds the receipt, and the page shows the banner. Drop `inbox/healthy.batch` to land a clean batch: one quiet line, no alert.

Without the web server, `receipts watch --once` processes any new batch once and exits (handy in a scheduler); `receipts watch` keeps checking. On the DuckDB stand-in only one process can open the database file, so stop `receipts serve` before running `receipts watch` there; on Exasol both can run at once.

## 8. Break the pipeline (lab mode)

Start `receipts demo --lab --watch` (the run scripts do). Under the number, **Break the pipeline** lets you pick
one of the six fault classes, the share of rows it affects and, for unit and clock faults, the gateway. Pressing
the button plants that fault into tonight's RAW batch with the same SQL the scenarios use (LANDING and the
published history are never touched) and runs the gate. The page lists each step with its time as it finishes,
then shows the HELD banner, the receipt and the Approve button. **Reset** removes tonight's batch and its
published row, so the demo can run again.

Measured on Exasol Personal 2026.2.0-nano.3 on the laptop described in section 2, with
`python scripts/measure_break.py --runs 5` (a headless browser that clicks the button): IST written as UTC on
GW_B, click to HELD banner in a median of 8.4 s (6.8 to 20.5 s over 5 runs, one slow run at 20.5 s), on 26 Oct after the unit tail check. Port 8000 was taken on this laptop, so it ran on 8765.

The **Red team** tab next to it shows the detection floor per fault class from the saved red team report and
runs one attack live (`receipts redteam` writes the report; see the README). Run it on the built-in synthetic
data or a sandbox copy, never on live production tables.

## 9. Point it at your own metric

Metrics are listed in `receipts.yaml` in the project folder. Each entry names the daily view, its value and day
columns, the raw tables the batch lands in, the amount, ID and time columns of the main raw table, and whether to
use a weekday baseline (`auto`, `on` or `off`). Adding a metric is an edit to that file, not to the code. The
sample file ships three metrics over the same pipeline: daily revenue (the one published to PUB), paid orders per
day and the average basket.

```bash
receipts connect --check
```

checks every metric against the database: the view and raw tables exist, the columns exist, the value column is a
number, the day and time columns are dates or timestamps, and the amount is a number. Each problem is printed in one
plain line, for example `the value column NOPE is not in PIPE.DAILY_ORDERS. It has: AVG_BASKET_INR, ORDER_COUNT,
TXN_DAY.` `receipts connect` with no flag judges tonight's batch for every metric without write-back, and
`receipts connect --scenarios` runs every synthetic scenario for every metric and writes
[`samples/metrics_report.md`](../samples/metrics_report.md).

What a config change covers: the metric's own band and weekday baseline, lineage from the catalog to that metric,
the undo test re-reading that metric in the sandbox, and the blast radius. What it does not cover: the six detectors
are written for the payments layout of the sample pipeline, so a metric over a different raw layout gets the band
and lineage but no detector would nominate a cause there; the slice breakdown runs on revenue; and only
`daily_revenue_inr` is written to `PUB.METRIC_TRUST`, the other metrics are judged and reported.

## 10. Trust badge

With `receipts serve` running (normal or lab mode), `http://127.0.0.1:8000/badge.svg` is a small SVG: the metric
name, today's trust status and the last trusted day, read from `PUB.METRIC_TRUST`. No values, no raw data, and it
is never cached. `/badge/<metric>.svg` selects a metric by name; an unknown name returns 404 with a grey badge.

```markdown
![Revenue trust](http://127.0.0.1:8000/badge.svg)
```

```html
<img src="http://127.0.0.1:8000/badge/daily_revenue_inr.svg" alt="Revenue trust">
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| Command center says "Database not ready" | Run `make init` (or `make exasol-init`) first |
| `receipts doctor` says the UDF is unavailable | `exasol slc install python3`, then `make exasol-init` again. Until then the clock check runs the same UDF source on the client and the receipt says so |
| DuckDB "could not set lock" | Stop the running `receipts serve` before running CLI commands against the same stand-in file |
| Fonts look plain | The page loads Archivo and IBM Plex Mono from Google Fonts and falls back to system fonts offline |
