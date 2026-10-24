"""How the gate behaves as the data grows: the IST case at increasing order volumes.

For each size we generate fresh synthetic data (the same seed, more orders a day), rebuild the
database with it, land the IST written as UTC batch and run the gate once. We record the rows
loaded, how long the load took, how long the gate took, and how long the GROUP BY CUBE step took.

The run stops at the first size that fails, or when the disk is nearly full, and claims nothing
beyond the largest size that completed. Generated files are deleted after each size.
"""

from __future__ import annotations

import shutil
import tempfile
import time
from dataclasses import replace
from pathlib import Path

from . import gate
from .config import settings
from .datagen import GenConfig, generate
from .db import DuckDBBackend, connect
from .load import ingest, init_database

SCENARIO = "ist_utc"
MIN_FREE_GB = 4.0


def _free_gb(path: Path) -> float:
    return shutil.disk_usage(path).free / 1e9


def _cube_ms(case: dict) -> float | None:
    return next((s["ms"] for s in case["timings"] if "GROUP BY CUBE" in s["step"]), None)


def one(be, n: int, seed: int, tmp: Path, log=print) -> dict:
    t = time.perf_counter()
    cfg = GenConfig(seed=seed, orders_per_day=n)
    m = generate(tmp, cfg)
    gen_s = time.perf_counter() - t
    log(f"  generated {m['rows']['PAYMENTS']:,} payment rows in {gen_s:.0f}s")
    t = time.perf_counter()
    init_database(be, tmp, log=lambda *a: None)
    load_s = time.perf_counter() - t
    log(f"  loaded and built in {load_s:.0f}s")
    day = cfg.incoming_day
    ingest(be, day, SCENARIO)
    c = gate.run(be, day, {"id": SCENARIO, "title": "IST written as UTC"}, write_back=True)
    return {"orders_per_day": n, "payment_rows": m["rows"]["PAYMENTS"], "order_rows": m["rows"]["ORDERS"],
            "generate_s": round(gen_s, 1), "load_s": round(load_s, 1), "gate_ms": c["total_ms"],
            "db_ms": c["db_ms"], "cube_ms": _cube_ms(c), "cube_rows": c["decomposition"]["rows_in_scope"],
            "slices": c["decomposition"]["hypotheses"], "statements": c["statements"],
            "verdict": c["verdict"], "confirmed": c["confirmed"],
            "right": c["verdict"] == "PROVEN_FAULT" and c["confirmed"] == ["clock_shift"],
            "exasol_ms": _exa(c), "exasol_cube_ms": _exa(c, "GROUP BY CUBE"),
            "exasol_peak_mib": (c.get("exasol_measured") or {}).get("temp_ram_peak_mib")}


def _exa(case: dict, step: str | None = None) -> float | None:
    """Milliseconds Exasol itself recorded, for the whole gate or for one step. None when not measured."""
    m = case.get("exasol_measured") or {}
    if not m.get("steps"):
        return None
    if step is None:
        return m["db_ms"]
    return next((s["db_ms"] for s in m["steps"] if step in s["step"]), None)


def run(sizes: list[int], backend: str = "exasol", seed: int = 7, log=print) -> dict:
    t0 = time.perf_counter()
    results, stopped = [], None
    be = DuckDBBackend(":memory:") if backend == "duckdb" else connect(replace(settings(), backend=backend))
    desc = be.describe()
    for n in sizes:
        free = _free_gb(Path(tempfile.gettempdir()))
        if free < MIN_FREE_GB:
            stopped = f"stopped before {n:,} orders a day: only {free:.1f} GB free on disk"
            log(stopped)
            break
        log(f"{n:,} orders a day")
        tmp = Path(tempfile.mkdtemp(prefix=f"receipts_scale_{n}_"))
        try:
            r = one(be, n, seed, tmp, log)
        except Exception as e:  # record the failure and stop; nothing larger is claimed
            stopped = f"failed at {n:,} orders a day: {type(e).__name__}: {str(e).strip().splitlines()[0][:200]}"
            log(stopped)
            break
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        results.append(r)
        log(f"  gate {r['gate_ms']:,.0f} ms (database {r['db_ms']:,.0f} ms), CUBE {r['cube_ms']:,.0f} ms over "
            f"{r['cube_rows']:,} rows, verdict {r['verdict']} {','.join(r['confirmed']) or '-'}")
    be.close()
    return {"backend": desc, "scenario": SCENARIO, "seed": seed, "sizes_requested": sizes, "results": results,
            "stopped": stopped, "seconds": round(time.perf_counter() - t0)}


def to_markdown(rep: dict) -> str:
    b = rep["backend"]
    where = (f"Exasol {b.get('version', '')}".strip() if b["backend"] == "exasol" and not b.get("standin")
             else "the DuckDB stand-in")
    res = rep["results"]
    out = ["# Scaling the gate", "",
           f"The IST written as UTC case (`{rep['scenario']}`) on {where}, at increasing order volumes. For each size: "
           f"`receipts init --fresh --orders-per-day N` (seed {rep['seed']}, 42 days of history plus the incoming day), "
           "then one gate run with write-back. Client times are measured by Receipts around each statement; the "
           "\"measured by Exasol\" columns are what Exasol recorded itself in EXA_STATISTICS.EXA_SQL_LAST_DAY.", "",
           f"Reproduce: `receipts scale --backend {b['backend'] if not b.get('standin') else 'duckdb'} --sizes "
           f"{' '.join(str(s) for s in rep['sizes_requested'])}`. Total time {rep['seconds'] / 60:.0f} minutes.", "",
           "| Orders a day | Payment rows | Load and build | Gate end to end | Inside the database (client) | "
           "Measured by Exasol | CUBE step | CUBE, measured by Exasol | Peak temp memory | Rows in the CUBE | Verdict |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]

    def sec(v):
        return "n/a" if v is None else f"{v / 1000:,.1f} s"
    for r in res:
        peak = "n/a" if r.get("exasol_peak_mib") is None else f"{r['exasol_peak_mib']:,.0f} MiB"
        out.append(f"| {r['orders_per_day']:,} | {r['payment_rows']:,} | {r['load_s']:,.0f} s | {sec(r['gate_ms'])} | "
                   f"{sec(r['db_ms'])} | {sec(r.get('exasol_ms'))} | {sec(r['cube_ms'])} | {sec(r.get('exasol_cube_ms'))} | "
                   f"{peak} | {r['cube_rows']:,} | "
                   f"{r['verdict']} {', '.join(r['confirmed'])}{'' if r['right'] else ' (WRONG)'} |")
    out += ["", "How to read it:", "",
            "* Each gate run is the first one after a fresh load, which is slower than a repeat run on the same data "
            "(earlier on this laptop at 20,000 orders a day: 7.8 s for the first run, 4.2 s for a repeat).",
            "* The client \"inside the database\" column sums the statements up to the verdict. The Exasol column also "
            "includes the write-back step and the automatic commit after each statement, so it is a little larger.",
            "* Peak temp memory is the largest TEMP_DB_RAM_PEAK Exasol recorded for any statement of the run.", ""]
    if res:
        big = res[-1]
        out.append(f"Largest size measured: **{big['orders_per_day']:,} orders a day, {big['payment_rows']:,} payment "
                   f"rows**. Nothing larger is claimed.")
    if rep["stopped"]:
        out.append(f"\nThe run stopped: {rep['stopped']}.")
    wrong = [r for r in res if not r["right"]]
    out.append("\n" + ("Every size reached the right verdict and cause." if not wrong else
                       "Wrong verdict or cause at: " + ", ".join(f"{r['orders_per_day']:,}" for r in wrong) + "."))
    return "\n".join(out) + "\n"
