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

`receipts demo` takes the same options as `receipts serve` (`--day`, `--port`) plus `--no-browser`.

## 1. Without Exasol (anyone, two minutes)

Requires Python 3.10 or newer.

```bash
git clone https://github.com/AakashMutum/receipts.git && cd receipts
python3 -m venv .venv && source .venv/bin/activate
make install
make judge-check
```

`judge-check` generates fresh data on two seeds, runs all ten scenarios, scores them against ground truth and prints PASS or FAIL for eight claims. It needs no API key and no network.

Then the command center:

```bash
make demo        # same as: receipts demo (builds if needed, serves, opens the browser)
```

Open http://127.0.0.1:8000. The header chip says **Local stand-in** so nobody mistakes it for Exasol.

The incoming batch day is yesterday in India (Asia/Kolkata), with 42 days of history generated before it. Every date on the page, the agent's question and the case IDs follow it. `receipts serve` rebuilds the database first if it holds another day. To reproduce the screenshots, pin the day on both commands:

```bash
receipts init --day 2026-10-20
receipts serve --day 2026-10-20     # or: make demo DAY=2026-10-20
```

`receipts judge-check`, `receipts eval`, `receipts variants` and the tests always use 20 Oct 2026, so their results do not change with the calendar.

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

Measured on Exasol Personal 2026.2.0-nano.3 (Windows 11, Podman on WSL2 with 6 CPUs and 7.7 GiB RAM visible to the VM, 20,000 orders a day): `receipts init` loads in 12 to 18 s, and `receipts run ist_utc` reaches `PROVEN_FAULT` in 4.2 s end to end (3.2 s inside the database, 26 statements; the first run after a fresh load takes about 8 s). The slowest steps are the `GROUP BY CUBE` over 11,074 slices (1.1 s) and the sandbox undo test (1.0 s). The full evaluation on Exasol (`receipts eval --backend exasol --out samples/exasol`, 50 runs) passes 50 of 50 with a median gate latency of 3.4 s and takes about 9 minutes. `receipts variants --backend exasol --seeds 11 --out samples/exasol` takes about 2 minutes. Both rebuild the database once per seed, so run `receipts init --fresh` afterwards to get the demo data back.

At 100,000 orders a day (`receipts init --fresh --orders-per-day 100000`, 4.2 million payment rows, about 40 s to load and 2.5 minutes including data generation) `ist_utc` takes 6.8 s and `masked_pair` 9.7 s on the same laptop.

If Exasol refuses connections after the computer has slept, the Podman machine has usually stopped. Run `podman machine start`, then `exasol start`, then `receipts doctor`.

Bigger data for timing claims: `receipts init --fresh --orders-per-day 200000` gives about 8.6 million payment rows.

## 3. The command line

```bash
receipts run ist_utc          # land a batch with a planted fault and run the gate
receipts run festival         # the real-change control
receipts run masked_pair      # two faults that cancel out
receipts eval                 # full scored evaluation, 5 seeds, writes samples/eval_report.md
receipts eval --backend exasol  # the same evaluation on Exasol
receipts sample               # writes an unedited case file per scenario to samples/cases
receipts export-sql           # writes all Exasol SQL to sql/exasol for reading
receipts demo --watch         # command center plus the batch watcher and alerts (section 7)
receipts watch --once         # judge any newly landed batch once and exit
receipts backtest             # the gate over real NYC taxi data, writes samples/real_backtest.md
```

`receipts backtest` downloads about 150 MB of NYC TLC yellow taxi trip records (January to March 2024) once into `data/real/` with a progress line, then judges 56 real days one night at a time and plants six faults on real days. It runs on the local stand-in and takes a few minutes after the download.

Scenarios: `healthy`, `festival`, `unit_paise`, `duplicate_load`, `join_fanout`, `stale_fx`, `ist_utc`, `new_code`, `masked_pair`, `unknown_discount`.

## 4. Connect a real AI agent (MCP)

1. Install `uv`, then add the Exasol MCP server to any MCP client (for example a desktop AI assistant) using [`mcp/mcp_client_config.example.json`](../mcp/mcp_client_config.example.json).
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

35 tests. `tests/test_scenarios.py` runs all ten scenarios twice: once on the DuckDB stand-in and once on the Exasol SQL path, where every statement is rendered for Exasol, parsed by sqlglot's Exasol grammar, translated and executed.

## 7. Watch for new batches and get alerts

`receipts serve --watch` (or `receipts demo --watch`) runs the command center and a light watcher in one process. Closing the window or pressing Ctrl+C stops both.

* Every 60 seconds (`--interval` to change it) the watcher runs one cheap query: is the newest day in RAW later than the newest published day? Only then does it run the gate. Between checks it sleeps; measured on a laptop it used 0.26% of one core with a 5 second interval and the page open.
* It also reads an inbox folder (`inbox/` by default, `--inbox` or `RECEIPTS_INBOX` to change it). A file named after a scenario, such as `ist_utc.batch`, lands that scenario's batch on the next check and is moved to `inbox/processed/`. Other files are moved to `inbox/ignored/`.
* When the gate holds a batch (`PROVEN_FAULT` or `UNEXPLAINED`) it prints an `ALERT` line, writes `alerts/<case>.txt` and `alerts/<case>.json` (verdict, one-line cause, last trusted value, receipt link), and shows an orange **ALERTS** banner in the command center until the case is approved, a new batch replaces it, or someone clicks Dismiss.
* If `SLACK_WEBHOOK_URL` is set it also posts a short message to that Slack incoming webhook, with a 5 second timeout. If Slack is down the alert file is still written and the watcher keeps going.
* A published batch prints one quiet line. A failed check prints one line and the watcher tries again next time; it never stops the server.

Try it:

```bash
receipts demo --watch --interval 5
```

Then, in a second terminal or in your file manager, drop a bad batch into the inbox:

```bash
touch inbox/ist_utc.batch          # Windows PowerShell: New-Item inbox\ist_utc.batch
```

Within a few seconds the console prints `ALERT RC-... held (PROVEN_FAULT). Proven cause: clock shift in RAW.PAYMENTS.CAPTURED_AT (gateway GW_B) ...`, `alerts/` holds the receipt, and the page shows the banner. Drop `inbox/healthy.batch` to land a clean batch: one quiet line, no alert.

Without the web server, `receipts watch --once` processes any new batch once and exits (handy in a scheduler); `receipts watch` keeps checking. On the DuckDB stand-in only one process can open the database file, so stop `receipts serve` before running `receipts watch` there; on Exasol both can run at once.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Command center says "Database not ready" | Run `make init` (or `make exasol-init`) first |
| `receipts doctor` says the UDF is unavailable | `exasol slc install python3`, then `make exasol-init` again. Until then the clock check runs the same UDF source on the client and the receipt says so |
| DuckDB "could not set lock" | Stop the running `receipts serve` before running CLI commands against the same stand-in file |
| Fonts look plain | The page loads Archivo and IBM Plex Mono from Google Fonts and falls back to system fonts offline |
