"""Command line: receipts <command>. Run `receipts --help`."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import ROOT, settings


def _be():
    from .db import connect
    return connect()


def cmd_generate(a):
    from .datagen import GenConfig, generate
    m = generate(settings().data_dir, GenConfig(seed=a.seed, orders_per_day=a.orders_per_day))
    print(json.dumps(m["rows"], indent=2))


def cmd_init(a):
    from .datagen import GenConfig, generate
    from .load import init_database
    cfg = settings()
    if a.fresh or not (cfg.data_dir / "manifest.json").exists():
        print(f"generating data ({a.orders_per_day:,} orders a day, seed {a.seed})")
        generate(cfg.data_dir, GenConfig(seed=a.seed, orders_per_day=a.orders_per_day))
    if cfg.backend == "duckdb":
        Path(cfg.duckdb_path).unlink(missing_ok=True)
    be = _be()
    print(f"backend: {be.name}{' (local stand-in)' if be.is_standin else ''}")
    meta = init_database(be, cfg.data_dir)
    print(f"ready in {meta['seconds']}s. incoming batch day {meta['incoming_day']}. udf: {meta['udf']['detail']}")


def _print_case(c):
    v = c["values"]
    print(f"\n{c['case_id']}  {c['day_label']}  verdict {c['verdict']}  status {c['trust_status']}")
    print(f"  candidate {v['candidate']:,.0f}  baseline {v['baseline']:,.0f}  change {v['change_pct']:+.1%}"
          + (f"  corrected {v['corrected']:,.0f}" if v["corrected"] else ""))
    for s in c["suspects"]:
        if s["fired"]:
            print(f"  [{s['outcome']:9s}] {s['title']}: {s['summary']}")
            if s["reason"]:
                print(f"              {s['reason']}")
    print(f"  {c['explanation']['text']}")
    print(f"  {c['decomposition']['hypotheses']:,} slices tested over {c['decomposition']['rows_in_scope']:,} rows; "
          f"total {c['total_ms']:.0f} ms, {c['statements']} SQL statements")


def cmd_run(a):
    from . import gate
    from .faults import SCENARIOS
    from .load import incoming_day, ingest
    be = _be()
    day = incoming_day(be)
    sc = ingest(be, day, a.scenario)
    c = gate.run(be, day, {"id": sc.id, "title": sc.title, "story": sc.story, "kind": sc.kind})
    _print_case(c)
    if a.json:
        Path(a.json).write_text(json.dumps(c, indent=2, default=str))
    ok = c["verdict"] == SCENARIOS[a.scenario].expected_verdict
    return 0 if ok else 1


def cmd_eval(a):
    from .evaluate import evaluate, save, to_markdown
    seeds = (11, 22, 33) if a.quick else (11, 22, 33, 44, 55)
    opd = 3000 if a.quick else 20000
    rep = evaluate(seeds=seeds, orders_per_day=a.orders_per_day or opd, backend=a.backend)
    out = Path(a.out)
    if a.quick:
        out.mkdir(parents=True, exist_ok=True)
        (out / "eval_quick.json").write_text(json.dumps(rep, indent=2, default=str))
        (out / "eval_quick.md").write_text(to_markdown(rep))
    else:
        save(rep, out)
    print("\n" + to_markdown(rep).split("## Per scenario")[0])
    return 0


def cmd_judge_check(a):
    """No API key, no Exasol needed. Builds, evaluates and asserts the headline claims."""
    from .evaluate import evaluate
    print("Receipts judge check: fresh synthetic data, every scenario, scored against ground truth.\n")
    rep = evaluate(seeds=(11, 22), orders_per_day=12000, backend="duckdb")
    s = rep["systems"]
    checks = [
        ("Every faulty batch held, every good batch published", s["receipts"]["hold_decision_accuracy"] == 1.0),
        ("No wrong cause named (precision 100%)", s["receipts"]["cause_precision"] == 1.0),
        ("Every planted cause found (recall 100%)", s["receipts"]["cause_recall"] == 1.0),
        ("Healthy control: no incident invented",
         all(r["receipts"]["verdict"] == "NO_INCIDENT" for r in rep["runs_detail"] if r["scenario"] == "healthy")),
        ("Real festival surge published as a verified real change",
         all(r["receipts"]["verdict"] == "REAL_CHANGE" for r in rep["runs_detail"] if r["scenario"] == "festival")),
        ("Unknown fault held without guessing a cause",
         all(r["receipts"]["verdict"] == "UNEXPLAINED" and not r["receipts"]["causes"]
             for r in rep["runs_detail"] if r["scenario"] == "unknown_discount")),
        ("Ablation: without the undo test a wrong cause gets named", s["detectors_only"]["false_causes"] > 0),
        ("Corrected values within 0.1% of the true clean value", (rep["corrected_value_error_pct"]["max"] or 0) < 0.1),
    ]
    print()
    for name, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    passed = all(ok for _, ok in checks)
    print(f"\n{'ALL CHECKS PASSED' if passed else 'SOME CHECKS FAILED'} ({rep['passed']}/{rep['runs']} runs, "
          f"{rep['seconds']}s)")
    return 0 if passed else 1


def cmd_sample(a):
    """Run the demo scenarios and save the unedited case files."""
    from . import gate
    from .faults import DEMO_ORDER, SCENARIOS
    from .load import incoming_day, ingest
    be = _be()
    day = incoming_day(be)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for sid in DEMO_ORDER:
        sc = ingest(be, day, sid)
        c = gate.run(be, day, {"id": sc.id, "title": sc.title, "story": sc.story, "kind": sc.kind})
        (out / f"{sid}.json").write_text(json.dumps(c, indent=2, default=str))
        print(f"{sid:17s} {c['verdict']:13s} {', '.join(c['confirmed']) or '-'}  {c['total_ms']:.0f} ms")
    ingest(be, day, "healthy")
    gate.run(be, day, {"id": "healthy", "title": "Healthy day"})


def cmd_export_sql(a):
    """Render every statement for Exasol into sql/exasol so it can be read and run by hand."""
    from datetime import date
    from .decompose import sql_for
    from .dialect import Dialect
    from .faults import SCENARIOS
    from .load import PROD_SRC
    from .model import FESTIVAL_TABLES, INCOMING_DAY, SOURCE_TABLES
    from .udf import clock_drift_ddl
    d = Dialect("exasol")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "01_schema.sql").write_text(d.render("schema.sql", tables=SOURCE_TABLES, festival=FESTIVAL_TABLES))
    (out / "02_pipeline.sql").write_text(d.render("pipeline.sql", schema="PIPE", src=PROD_SRC))
    (out / "03_pub.sql").write_text(d.render("pub.sql"))
    (out / "04_udf_clock_drift.sql").write_text(clock_drift_ddl() + "\n/\n")

    class _B:  # minimal stand-in so the decomposition renderer can be reused
        dialect = d
        render_string = staticmethod(d.render_string)
    (out / "05_decomposition_cube.sql").write_text(sql_for(_B, INCOMING_DAY) + ";\n")
    faults = []
    for s in SCENARIOS.values():
        for stmt in s.inject:
            faults.append(f"-- {s.id}: {s.title}\n{d.render_string(stmt, incoming=INCOMING_DAY)};\n")
    (out / "06_fault_injection.sql").write_text("\n".join(faults))
    print(f"wrote Exasol SQL to {out}")


def cmd_doctor(a):
    """Check the environment, and on Exasol check identifiers against reserved words."""
    from .doctor import run_doctor
    return run_doctor()


def cmd_serve(a):
    import uvicorn
    print(f"Receipts command center on http://{a.host}:{a.port}")
    uvicorn.run("receipts.api:app", host=a.host, port=a.port, log_level="warning")


def main(argv=None):
    p = argparse.ArgumentParser(prog="receipts", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate", help="write synthetic CSVs")
    g.add_argument("--seed", type=int, default=7)
    g.add_argument("--orders-per-day", type=int, default=20000)
    g.set_defaults(fn=cmd_generate)
    i = sub.add_parser("init", help="generate data if needed and build the database")
    i.add_argument("--seed", type=int, default=7)
    i.add_argument("--orders-per-day", type=int, default=20000)
    i.add_argument("--fresh", action="store_true", help="regenerate data even if it exists")
    i.set_defaults(fn=cmd_init)
    r = sub.add_parser("run", help="ingest a scenario's batch and run the gate")
    r.add_argument("scenario")
    r.add_argument("--json")
    r.set_defaults(fn=cmd_run)
    e = sub.add_parser("eval", help="scored evaluation against ground truth")
    e.add_argument("--quick", action="store_true")
    e.add_argument("--orders-per-day", type=int)
    e.add_argument("--backend", choices=("duckdb", "exasol"), default="duckdb",
                   help="exasol rebuilds the database at EXA_DSN once per seed")
    e.add_argument("--out", default=str(ROOT / "samples"))
    e.set_defaults(fn=cmd_eval)
    j = sub.add_parser("judge-check", help="reproduce the headline claims, no key or Exasol needed")
    j.set_defaults(fn=cmd_judge_check)
    s = sub.add_parser("sample", help="save unedited case files for every demo scenario")
    s.add_argument("--out", default=str(ROOT / "samples" / "cases"))
    s.set_defaults(fn=cmd_sample)
    x = sub.add_parser("export-sql", help="render all Exasol SQL to files")
    x.add_argument("--out", default=str(ROOT / "sql" / "exasol"))
    x.set_defaults(fn=cmd_export_sql)
    dct = sub.add_parser("doctor", help="check the setup")
    dct.set_defaults(fn=cmd_doctor)
    sv = sub.add_parser("serve", help="start the command center")
    sv.add_argument("--host", default="127.0.0.1")
    sv.add_argument("--port", type=int, default=8000)
    sv.set_defaults(fn=cmd_serve)
    a = p.parse_args(argv)
    rc = a.fn(a)
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
