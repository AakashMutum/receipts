"""Scored evaluation against ground truth.

For each seed we generate a fresh dataset, then run every scenario through the
gate. Ground truth comes from faults.py, which the engine never reads.

Three systems are scored on the same runs:
  threshold alert   the usual monitor: hold when the number leaves its band
  detectors only    hold when any detector fires, blame whatever fired
  Receipts          detectors, then the undo test and the evidence gate

The detectors-only row is the ablation: it shows what the undo test adds.
"""

from __future__ import annotations

import json
import tempfile
import time
from datetime import date
from pathlib import Path

from .datagen import GenConfig, generate
from .db import DuckDBBackend, connect
from .faults import SCENARIOS
from .gate import run as run_gate
from .load import ingest, init_database

HOLD = {"PROVEN_FAULT", "UNEXPLAINED"}


def _score(runs: list[dict], system: str) -> dict:
    tp = fp = fn = 0
    verdict_ok = hold_ok = 0
    for r in runs:
        pred, exp = set(r[system]["causes"]), set(r["expected_causes"])
        tp += len(pred & exp)
        fp += len(pred - exp)
        fn += len(exp - pred)
        should_hold = r["expected_verdict"] in HOLD
        hold_ok += int(r[system]["held"] == should_hold)
        verdict_ok += int(r[system].get("verdict", "") == r["expected_verdict"])
    n = len(runs)
    prec = tp / (tp + fp) if tp + fp else 1.0
    rec = tp / (tp + fn) if tp + fn else 1.0
    return {"runs": n, "cause_precision": round(prec, 3), "cause_recall": round(rec, 3),
            "hold_decision_accuracy": round(hold_ok / n, 3), "verdict_accuracy": round(verdict_ok / n, 3),
            "false_causes": fp, "missed_causes": fn}


def evaluate(seeds=(11, 22, 33), orders_per_day=3000, history_days=42, backend: str = "duckdb", log=print) -> dict:
    t_all = time.perf_counter()
    runs = []
    for seed in seeds:
        tmp = Path(tempfile.mkdtemp(prefix=f"receipts_eval_{seed}_"))
        cfg = GenConfig(seed=seed, orders_per_day=orders_per_day, history_days=history_days)
        generate(tmp, cfg)
        be = DuckDBBackend(":memory:") if backend == "duckdb" else connect()
        init_database(be, tmp, log=lambda *a: None)
        day = cfg.incoming_day
        truth = {}
        for sid in ("healthy", "festival"):
            ingest(be, day, sid)
            truth[sid] = be.scalar(f"SELECT REVENUE_INR FROM PIPE.DAILY_REVENUE WHERE TXN_DAY = {be.dialect.day(day)}")
        for sc in SCENARIOS.values():
            ingest(be, day, sc)
            c = run_gate(be, day, {"id": sc.id, "title": sc.title}, write_back=False)
            true_value = truth["festival"] if sc.festival else truth["healthy"]
            fired = [s["id"] for s in c["suspects"] if s["fired"]]
            corrected = c["values"]["corrected"]
            run = {
                "seed": seed, "scenario": sc.id, "kind": sc.kind,
                "expected_verdict": sc.expected_verdict, "expected_causes": sorted(sc.expected_causes),
                "change_pct": round(c["values"]["change_pct"], 4),
                "receipts": {"verdict": c["verdict"], "causes": c["confirmed"], "held": c["trust_status"] == "HELD",
                             "corrected_error_pct": round(abs(corrected - true_value) / true_value * 100, 3)
                             if corrected is not None else None},
                "detectors_only": {"causes": fired, "held": bool(fired),
                                   "verdict": "PROVEN_FAULT" if fired else ("NO_INCIDENT" if not c["anomaly"] else "")},
                "threshold_alert": {"causes": [], "held": c["anomaly"],
                                    "verdict": "UNEXPLAINED" if c["anomaly"] else "NO_INCIDENT"},
                "ms": c["total_ms"],
            }
            ok = (run["receipts"]["verdict"] == sc.expected_verdict and
                  set(run["receipts"]["causes"]) == set(sc.expected_causes))
            run["pass"] = ok
            runs.append(run)
            log(f"seed {seed} {sc.id:17s} {'PASS' if ok else 'FAIL'}  verdict {c['verdict']:13s} "
                f"causes {','.join(c['confirmed']) or '-':28s} {c['total_ms']:.0f} ms")
        be.close()
    errs = [r["receipts"]["corrected_error_pct"] for r in runs if r["receipts"]["corrected_error_pct"] is not None]
    ms = sorted(r["ms"] for r in runs)
    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "backend": backend,
        "seeds": list(seeds), "orders_per_day": orders_per_day, "history_days": history_days,
        "scenarios": len(SCENARIOS), "runs": len(runs), "passed": sum(r["pass"] for r in runs),
        "systems": {
            "receipts": _score(runs, "receipts"),
            "detectors_only": _score(runs, "detectors_only"),
            "threshold_alert": _score(runs, "threshold_alert"),
        },
        "corrected_value_error_pct": {"max": max(errs) if errs else None,
                                      "mean": round(sum(errs) / len(errs), 3) if errs else None},
        "latency_ms": {"median": ms[len(ms) // 2], "max": ms[-1]},
        "seconds": round(time.perf_counter() - t_all, 1),
        "runs_detail": runs,
    }
    return report


def to_markdown(rep: dict) -> str:
    s = rep["systems"]
    rows = [("Receipts", s["receipts"]), ("Detectors only (ablation, no undo test)", s["detectors_only"]),
            ("Threshold alert (typical monitor)", s["threshold_alert"])]
    out = [f"# Receipts evaluation", "",
           f"{rep['runs']} runs: {rep['scenarios']} scenarios x {len(rep['seeds'])} seeds "
           f"({rep['orders_per_day']:,} orders a day, {rep['history_days']} days of history, backend {rep['backend']}). "
           f"Generated {rep['generated_at']}.", "",
           f"**Receipts passed {rep['passed']} of {rep['runs']} runs** (right verdict and exactly the right causes).", "",
           "| System | Hold decision right | Cause precision | Cause recall | Wrong causes named | Causes missed |",
           "|---|---|---|---|---|---|"]
    for name, m in rows:
        out.append(f"| {name} | {m['hold_decision_accuracy']:.0%} | {m['cause_precision']:.0%} | "
                   f"{m['cause_recall']:.0%} | {m['false_causes']} | {m['missed_causes']} |")
    e = rep["corrected_value_error_pct"]
    out += ["", f"Corrected value after the proven fix, against the true clean value: mean error {e['mean']}%, "
                f"max {e['max']}%.",
            f"Gate latency per run: median {rep['latency_ms']['median']:.0f} ms, max {rep['latency_ms']['max']:.0f} ms.",
            "", "## Per scenario", "", "| Scenario | Seed | Change | Expected | Receipts verdict | Causes | Pass |",
            "|---|---|---|---|---|---|---|"]
    for r in rep["runs_detail"]:
        out.append(f"| {r['scenario']} | {r['seed']} | {r['change_pct']:+.1%} | {r['expected_verdict']} | "
                   f"{r['receipts']['verdict']} | {', '.join(r['receipts']['causes']) or '-'} | "
                   f"{'yes' if r['pass'] else 'NO'} |")
    out += ["", "## What the rows mean", "",
            "* **Hold decision right**: faulty batches held, healthy and genuinely changed batches published.",
            "* **Detectors only** is the ablation. It names every check that fired. On the festival day the retry "
            "burst trips the duplicate check, so it blames a fault that is not there. The undo test removes it.",
            "* **Threshold alert** never names a cause, holds the real festival surge, and misses the masked pair "
            "because the total looks normal.",
            "* The unknown fault has no detector by design. The right answer is UNEXPLAINED (held, no cause named), "
            "and that is what is scored.", ""]
    return "\n".join(out)


def save(rep: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "eval_report.json").write_text(json.dumps(rep, indent=2, default=str))
    (out_dir / "eval_report.md").write_text(to_markdown(rep))
