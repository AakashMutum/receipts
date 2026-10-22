"""Command line: receipts <command>. Run `receipts --help`."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

from .config import ROOT, settings


def _be():
    from .db import connect
    return connect()


def cmd_generate(a):
    from .datagen import GenConfig, generate
    m = generate(settings().data_dir, GenConfig(seed=a.seed, orders_per_day=a.orders_per_day))
    print(json.dumps(m["rows"], indent=2))


def _day(s: str) -> date:
    try:
        return date.fromisoformat(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM-DD, got {s!r}")


def _manifest() -> dict | None:
    f = settings().data_dir / "manifest.json"
    return json.loads(f.read_text()) if f.exists() else None


def _build(day: date, seed: int, orders_per_day: int, fresh: bool) -> None:
    """Generate data for `day` if needed (fresh, missing, or for another day), then build the database."""
    from .datagen import GenConfig, generate
    from .load import init_database
    cfg = settings()
    m = _manifest()
    if fresh or m is None or m["incoming_day"] != day.isoformat():
        print(f"generating data for {day} ({orders_per_day:,} orders a day, seed {seed})")
        generate(cfg.data_dir, GenConfig(seed=seed, orders_per_day=orders_per_day, incoming_day=day))
    if cfg.backend == "duckdb":
        Path(cfg.duckdb_path).unlink(missing_ok=True)
    be = _be()
    print(f"backend: {be.name}{' (local stand-in)' if be.is_standin else ''}")
    meta = init_database(be, cfg.data_dir)
    be.close()
    print(f"ready in {meta['seconds']}s. incoming batch day {meta['incoming_day']}. udf: {meta['udf']['detail']}")


def cmd_init(a):
    from .model import default_incoming_day
    _build(a.day or default_incoming_day(), a.seed, a.orders_per_day, a.fresh)


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


def cmd_variants(a):
    """Run the held-out fault variants on fresh data and write samples/variants_report.md."""
    import tempfile
    import time

    from . import gate
    from .datagen import GenConfig, generate
    from .db import DuckDBBackend
    from .load import ingest, init_database
    from .variants import VARIANTS, classify

    rows = []
    t0 = time.perf_counter()
    for seed in a.seeds:
        tmp = Path(tempfile.mkdtemp(prefix=f"receipts_var_{seed}_"))
        cfg = GenConfig(seed=seed, orders_per_day=a.orders_per_day)
        generate(tmp, cfg)
        be = DuckDBBackend(":memory:") if a.backend == "duckdb" else _be()
        init_database(be, tmp, log=lambda *x: None)
        day = cfg.incoming_day
        ingest(be, day, "healthy")
        truth = be.scalar(f"SELECT REVENUE_INR FROM PIPE.DAILY_REVENUE WHERE TXN_DAY = {be.dialect.day(day)}")
        for sc in VARIANTS:
            ingest(be, day, sc)
            c = gate.run(be, day, {"id": sc.id, "title": sc.title}, write_back=False)
            outcome, err = classify(sc, c, truth)
            rows.append((seed, sc, outcome, err, c))
            print(f"seed {seed} {sc.id:18s} {outcome:6s} error {err:+8.1f}%  {c['verdict']:13s} {','.join(c['confirmed']) or '-'}")
        be.close()
    from collections import Counter
    n = Counter(r[2] for r in rows)
    lines = ["# Held-out fault variants", "",
             f"{len(VARIANTS)} variants x {len(a.seeds)} seeds, {a.orders_per_day:,} orders a day, backend {a.backend}. "
             "Written after the detectors were fixed. See `receipts/variants.py`.", "",
             f"caught {n['caught']}, held {n['held']}, small (published, under 4% error) {n['small']}, "
             f"**published a wrong number {n['WRONG']}** of {len(rows)} runs.", "",
             "| Variant | Real error | Outcome | Verdict | Causes named |", "|---|---|---|---|---|"]
    for sc in VARIANTS:
        mine = [r for r in rows if r[1].id == sc.id]
        outs = "/".join(sorted({r[2] for r in mine}))
        err = f"{min(r[3] for r in mine):+.1f}% to {max(r[3] for r in mine):+.1f}%" if len(mine) > 1 else f"{mine[0][3]:+.1f}%"
        causes = "; ".join(sorted({",".join(r[4]['confirmed']) or "none" for r in mine}))
        lines.append(f"| {sc.title} | {err} | {outs} | {mine[0][4]['verdict']} | {causes} |")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "variants_report.md").write_text("\n".join(lines) + "\n")
    print(f"\ncaught {n['caught']}, held {n['held']}, small {n['small']}, WRONG {n['WRONG']} "
          f"in {time.perf_counter() - t0:.0f}s. Report: {out / 'variants_report.md'}")
    return 1 if n["WRONG"] else 0


def cmd_doctor(a):
    """Check the environment, and on Exasol check identifiers against reserved words."""
    from .doctor import run_doctor
    return run_doctor()


def _ensure_day(day: date) -> None:
    """Build the database for `day` unless it already holds that day."""
    from .load import incoming_day
    current = be = None
    try:
        be = _be()
        current = incoming_day(be)
    except Exception:  # database not built yet
        pass
    finally:
        if be is not None:
            be.close()  # DuckDB keeps a file lock, and the rebuild below may need to delete the file
    if current != day:
        print(f"database holds {current or 'no data'}, building it for {day}")
        conf = (_manifest() or {}).get("config", {})
        _build(day, conf.get("seed", 7), conf.get("orders_per_day", 20000), fresh=False)


def _open_browser_when_up(url: str, timeout: float = 120) -> None:
    """Wait in the background until the server answers, then open the page once."""
    import threading
    import time
    import urllib.request
    import webbrowser

    def wait_and_open():
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            try:
                with urllib.request.urlopen(url + "api/overview", timeout=2):
                    webbrowser.open(url)
                    return
            except Exception:
                time.sleep(0.5)
        print(f"The server did not answer within {timeout:.0f}s. Open {url} yourself.")

    threading.Thread(target=wait_and_open, daemon=True).start()


def _serve(a, browser: bool) -> None:
    import uvicorn

    from .model import default_incoming_day
    _ensure_day(a.day or default_incoming_day())
    url = f"http://{a.host}:{a.port}/"
    print(f"Receipts command center on {url}  (press Ctrl+C to stop)")
    if browser:
        _open_browser_when_up(url)
    if a.watch:
        import threading

        from . import api
        w = _watcher(a, connect=api.be, lock=api._lock, base_url=url)
        threading.Thread(target=w.run_forever, args=(a.interval,), daemon=True, name="receipts-watch").start()
    uvicorn.run("receipts.api:app", host=a.host, port=a.port, log_level="warning")


def _watcher(a, connect, lock=None, base_url: str = "http://127.0.0.1:8000/"):
    from .watch import Watcher
    cfg = settings()
    inbox = Path(a.inbox) if a.inbox else cfg.inbox_dir
    inbox.mkdir(parents=True, exist_ok=True)
    return Watcher(connect, lock=lock, alerts_dir=cfg.alerts_dir, inbox_dir=inbox, base_url=base_url,
                   slack_url=cfg.slack_url, log=lambda m: print(m, flush=True))


def cmd_watch(a):
    """Process new batches without the web server: once with --once, otherwise every --interval seconds."""
    be = _be()
    w = _watcher(a, connect=lambda: be)
    if a.once:
        cases = w.check_once()
        if not cases:
            print("watch: no new batch")
        return 0
    w.run_forever(a.interval)


def cmd_serve(a):
    _serve(a, browser=False)


def cmd_demo(a):
    """Build the database if needed, start the command center and open it in the browser."""
    _serve(a, browser=not (a.no_browser or os.environ.get("RECEIPTS_NO_BROWSER") == "1"))


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
    i.add_argument("--day", type=_day, help="incoming batch day, YYYY-MM-DD (default: yesterday in India). "
                                             "Use 2026-10-20 to reproduce the screenshots")
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
    vr = sub.add_parser("variants", help="held-out fault variants, scored against the clean value")
    vr.add_argument("--seeds", type=int, nargs="+", default=[11, 22])
    vr.add_argument("--orders-per-day", type=int, default=8000)
    vr.add_argument("--backend", choices=["duckdb", "exasol"], default="duckdb")
    vr.add_argument("--out", default=str(ROOT / "samples"))
    vr.set_defaults(fn=cmd_variants)
    dct = sub.add_parser("doctor", help="check the setup")
    dct.set_defaults(fn=cmd_doctor)
    sv = sub.add_parser("serve", help="start the command center")
    sv.add_argument("--host", default="127.0.0.1")
    sv.add_argument("--port", type=int, default=8000)
    sv.add_argument("--day", type=_day, help="incoming batch day, YYYY-MM-DD (default: yesterday in India). "
                                              "Rebuilds the database first if it holds another day")
    sv.set_defaults(fn=cmd_serve)
    dm = sub.add_parser("demo", help="build the database if needed, start the command center, open the browser")
    dm.add_argument("--host", default="127.0.0.1")
    dm.add_argument("--port", type=int, default=8000)
    dm.add_argument("--day", type=_day, help="incoming batch day, YYYY-MM-DD (default: yesterday in India)")
    dm.add_argument("--no-browser", action="store_true", help="do not open a browser window")
    dm.set_defaults(fn=cmd_demo)
    for sp in (sv, dm):
        sp.add_argument("--watch", action="store_true", help="also watch for new batches and raise alerts")
    wt = sub.add_parser("watch", help="judge new batches and raise alerts, without the web server")
    wt.add_argument("--once", action="store_true", help="process any new batch once and exit")
    for sp in (sv, dm, wt):
        sp.add_argument("--interval", type=float, default=60, help="seconds between checks (default 60)")
        sp.add_argument("--inbox", help="folder to read batch files from (default inbox/, or RECEIPTS_INBOX)")
    wt.set_defaults(fn=cmd_watch)
    a = p.parse_args(argv)
    try:
        rc = a.fn(a)
    except KeyboardInterrupt:
        rc = 130
    except Exception as e:
        if type(e).__name__ != "ExaConnectionFailedError":
            raise
        cfg = settings()
        print(f"\nCould not connect to Exasol at {cfg.exa_dsn}. Is the database running?\n"
              "Check with `exasol status`, start it with `exasol start`, then try again.", file=sys.stderr)
        rc = 2
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
