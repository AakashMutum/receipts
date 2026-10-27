"""`receipts connect`: check the metric config, judge tonight for every metric, or run every scenario per metric.

The scenario run is lab work on synthetic data: for each configured metric it lands each scenario, runs the same
gate (without write-back for metrics that are not published), and compares the metric's candidate value with its
clean value (the same night without the fault). A fault that does not move a metric is the right thing for that
metric to publish; a fault that moves it by 4% or more should be held.
"""

from __future__ import annotations

import tempfile
import time
from pathlib import Path

from .datagen import GenConfig, generate
from .db import DuckDBBackend
from .faults import SCENARIOS
from .gate import run as run_gate
from .load import ingest, init_database
from .metrics import Metric

WRONG_PCT = 4.0

# Held-out cases for the configured metrics, written and committed before the history-snapshot fix was run.
# (fault, share, gateway) on seeds 31 and 32; none of them was used while writing the fix.
HELDOUT = [("key_fanout", 0.05, None), ("key_fanout", 0.25, None), ("key_fanout", 1.0, None),
           ("orphan_code", 0.25, None), ("duplicate_key", 0.25, None), ("clock_shift", 1.0, "GW_A"),
           ("unit_scale", 0.10, "GW_B"), ("stale_feed", 1.0, None)]
HELDOUT_SEEDS = (31, 32)


def _value(be, m: Metric, day) -> float:
    return be.scalar(f"SELECT {m.value_column} FROM {m.view} WHERE {m.day_column} = {be.dialect.day(day)}") or 0.0


def outcome(held: bool, err_pct: float, festival: bool) -> str:
    moved = abs(err_pct) >= WRONG_PCT and not festival
    if held:
        return "held, right" if moved else "held, metric was fine"
    return "published WRONG" if moved else "published, right"


def _backend(backend: str):
    if backend == "duckdb":
        return DuckDBBackend(":memory:")
    from dataclasses import replace

    from .config import settings
    from .db import connect
    return connect(replace(settings(), backend=backend))


def scenarios(metrics: list[Metric], seeds=(11,), orders_per_day: int = 8000, log=print,
              backend: str = "duckdb") -> dict:
    t0 = time.perf_counter()
    rows = []
    for seed in seeds:
        tmp = Path(tempfile.mkdtemp(prefix=f"receipts_connect_{seed}_"))
        cfg = GenConfig(seed=seed, orders_per_day=orders_per_day)
        generate(tmp, cfg)
        be = _backend(backend)
        desc = be.describe()
        init_database(be, tmp, log=lambda *a: None)
        day = cfg.incoming_day
        clean = {}
        for sid in ("healthy", "festival"):
            ingest(be, day, sid)
            clean[sid] = {m.name: _value(be, m, day) for m in metrics}
        for sc in SCENARIOS.values():
            ingest(be, day, sc)
            for m in metrics:
                c = run_gate(be, day, {"id": sc.id, "title": sc.title}, write_back=False, metric=m)
                truth = clean["festival" if sc.festival else "healthy"][m.name]
                err = (c["values"]["candidate"] - truth) / truth * 100 if truth else 0.0
                held = c["trust_status"] == "HELD"
                rows.append({"seed": seed, "metric": m.name, "scenario": sc.id, "verdict": c["verdict"],
                             "confirmed": c["confirmed"], "error_pct": round(err, 2), "held": held,
                             "outcome": outcome(held, err, sc.festival)})
                log(f"seed {seed} {m.name:18s} {sc.id:17s} {c['verdict']:13s} error {err:+7.2f}%  {rows[-1]['outcome']}")
        be.close()
    by = {}
    for r in rows:
        k = by.setdefault(r["metric"], {})
        k[r["outcome"]] = k.get(r["outcome"], 0) + 1
    return {"backend": desc, "seeds": list(seeds), "orders_per_day": orders_per_day, "rows": rows, "summary": by,
            "metrics": [m.name for m in metrics], "seconds": round(time.perf_counter() - t0),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")}


def _where(rep: dict) -> str:
    b = rep.get("backend") or {"backend": "duckdb", "standin": True}
    return (f"Exasol {b.get('version', '')}".strip() if b["backend"] == "exasol" and not b.get("standin")
            else "the DuckDB stand-in")


def to_markdown(rep: dict, command: str, title: str = "Configured metrics through the same gate") -> str:
    out = [f"# {title}", "",
           f"Metrics from `receipts.yaml`: {', '.join(rep['metrics'])}. On {_where(rep)}, synthetic data, "
           f"{rep['orders_per_day']:,} orders a day, seeds {', '.join(map(str, rep['seeds']))}. Generated "
           f"{rep['generated_at']} in {rep['seconds']} s. Reproduce: `{command}`.", "",
           "Each scenario is landed once and judged for every metric. The error is the metric's candidate value "
           "against the same night without the fault. A fault that does not move a metric should be published for "
           f"that metric; a move of {WRONG_PCT:.0f}% or more should be held. Metrics other than revenue are judged "
           "without write-back. The six detectors and the slice breakdown are the revenue pipeline's own, so the "
           "causes they name are about the shared raw tables.", "",
           "| Metric | Held, right | Published, right | Held, metric was fine | Published WRONG |", "|---|---|---|---|---|"]
    for name, s in rep["summary"].items():
        out.append(f"| {name} | {s.get('held, right', 0)} | {s.get('published, right', 0)} | "
                   f"{s.get('held, metric was fine', 0)} | {s.get('published WRONG', 0)} |")
    out += ["", "## Every run", "", "| Seed | Metric | Scenario | Error | Verdict | Causes | Outcome |",
            "|---|---|---|---|---|---|---|"]
    for r in rep["rows"]:
        out.append(f"| {r['seed']} | {r['metric']} | {r['scenario']} | {r['error_pct']:+.2f}% | {r['verdict']} | "
                   f"{', '.join(r['confirmed']) or '-'} | {r['outcome']} |")
    return "\n".join(out) + "\n"


def heldout(metrics: list[Metric], orders_per_day: int = 8000, log=print, backend: str = "duckdb") -> dict:
    """The frozen HELDOUT cases for every metric that is not published (the published one has its own tests)."""
    from .faults import fault_scenario
    t0 = time.perf_counter()
    ms = [m for m in metrics if not m.publish]
    rows = []
    for seed in HELDOUT_SEEDS:
        tmp = Path(tempfile.mkdtemp(prefix=f"receipts_mheld_{seed}_"))
        cfg = GenConfig(seed=seed, orders_per_day=orders_per_day)
        generate(tmp, cfg)
        be = _backend(backend)
        desc = be.describe()
        init_database(be, tmp, log=lambda *a: None)
        day = cfg.incoming_day
        ingest(be, day, "healthy")
        clean = {m.name: _value(be, m, day) for m in ms}
        for kind, share, gw in HELDOUT:
            sc = fault_scenario(kind, share, gw)
            ingest(be, day, sc)
            for m in ms:
                c = run_gate(be, day, {"id": sc.id, "title": sc.title}, write_back=False, metric=m)
                err = (c["values"]["candidate"] - clean[m.name]) / clean[m.name] * 100 if clean[m.name] else 0.0
                held = c["trust_status"] == "HELD"
                rows.append({"seed": seed, "metric": m.name, "scenario": sc.title, "verdict": c["verdict"],
                             "confirmed": c["confirmed"], "error_pct": round(err, 2), "held": held,
                             "outcome": outcome(held, err, False)})
                log(f"seed {seed} {m.name:18s} {sc.title:55s} {c['verdict']:13s} error {err:+7.2f}%  "
                    f"{rows[-1]['outcome']}")
        be.close()
    by = {}
    for r in rows:
        k = by.setdefault(r["metric"], {})
        k[r["outcome"]] = k.get(r["outcome"], 0) + 1
    return {"backend": desc, "seeds": list(HELDOUT_SEEDS), "orders_per_day": orders_per_day, "rows": rows, "summary": by,
            "metrics": [m.name for m in ms], "seconds": round(time.perf_counter() - t0),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")}
