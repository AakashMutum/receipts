# Run guide

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
make demo        # same as: receipts init && receipts serve
```

Open http://127.0.0.1:8000. The header chip says **Local stand-in** so nobody mistakes it for Exasol.

## 2. On Exasol Personal (the real target)

Exasol Personal runs locally on macOS (Apple Silicon), on Linux with Podman, and on Windows (amd64) with Podman.

Windows: download the `exasol` launcher from https://downloads.exasol.com/exasol-personal, put it in a folder on your `PATH`, open a new PowerShell and run `exasol version`. If Podman is missing the launcher offers to install it with `winget` (administrator approval may be asked). Windows arm64 is not supported for local deployments. The PowerShell equivalents of the exports below are `$env:EXA_DSN = "localhost:8563"`, and so on; `make` is not needed, run the `receipts` commands directly.

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
```

Scenarios: `healthy`, `festival`, `unit_paise`, `duplicate_load`, `join_fanout`, `stale_fx`, `ist_utc`, `new_code`, `masked_pair`, `unknown_discount`.

## 4. Connect a real AI agent (MCP)

1. Install `uv`, then add the Exasol MCP server to Claude Desktop (or any MCP client) using [`mcp/claude_desktop_config.example.json`](../mcp/claude_desktop_config.example.json).
2. Put [`mcp/AGENT_INSTRUCTIONS.md`](../mcp/AGENT_INSTRUCTIONS.md) into the agent's instructions.
3. Run `receipts run unit_paise`, then ask the agent "What was revenue on 20 October?". With the instructions it reads `PUB.METRIC_TRUST`, sees the value is held, and quotes the last trusted day instead. Remove the instructions and ask again to see it quote the broken number.

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

## Troubleshooting

| Symptom | Fix |
|---|---|
| Command center says "Database not ready" | Run `make init` (or `make exasol-init`) first |
| `receipts doctor` says the UDF is unavailable | `exasol slc install python3`, then `make exasol-init` again. Until then the clock check runs the same UDF source on the client and the receipt says so |
| DuckDB "could not set lock" | Stop the running `receipts serve` before running CLI commands against the same stand-in file |
| Fonts look plain | The page loads Archivo and IBM Plex Mono from Google Fonts and falls back to system fonts offline |
