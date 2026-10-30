"""The evaluation, the wrong-fix control and the red team over many seeds, one seed at a time.

The same functions, settings and scoring as `receipts eval`, `receipts wrongfix` and `receipts redteam`; only the
number of seeds is larger. Each finished seed is appended to a JSON lines file outside the repository, so a run that
stops keeps every finished seed, and a second start skips them. `--report` combines the seeds into one report.

    python scripts/evidence_seeds.py eval --backend exasol
    python scripts/evidence_seeds.py eval --backend duckdb
    python scripts/evidence_seeds.py eval --report        # samples/exasol/eval_extended.md and .json
    python scripts/evidence_seeds.py wrongfix --backend exasol
    python scripts/evidence_seeds.py redteam --backend exasol
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from receipts import evaluate, redteam, wrongfix  # noqa: E402

SEEDS = tuple(11 * k for k in range(1, 26))  # 11, 22, ..., 275: the five published seeds first, then 20 more
OPD = 20000
STORE = Path("D:/Hackathon/data/evidence") if sys.platform == "win32" else ROOT / "data" / "evidence"
OUT = ROOT / "samples" / "exasol"


def rows_file(mode: str, backend: str) -> Path:
    return STORE / f"{mode}_{backend}.jsonl"


def done(mode: str, backend: str) -> dict[int, dict]:
    f = rows_file(mode, backend)
    if not f.exists():
        return {}
    out = {}
    for line in f.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["seed"]] = r
    return out


def run(mode: str, backend: str, seeds, log) -> None:
    STORE.mkdir(parents=True, exist_ok=True)
    have = done(mode, backend)
    for s in seeds:
        if s in have:
            log(f"seed {s} already done")
            continue
        t = time.perf_counter()
        if mode == "eval":
            rep = evaluate.evaluate(seeds=(s,), orders_per_day=OPD, backend=backend, log=log)
            rec = {"seed": s, "runs": rep["runs_detail"]}
        elif mode == "wrongfix":
            rep = wrongfix.run(seeds=(s,), orders_per_day=OPD, backend=backend, log=log)
            rec = {"seed": s, "rows": rep["rows"], "backend": rep["backend"]}
        else:
            rep = redteam.run(backend=backend, seeds=(s,), orders_per_day=OPD, log=log)
            rec = {"seed": s, "run": rep["runs"][0], "backend": rep["backend"]}
        rec["seconds"] = round(time.perf_counter() - t, 1)
        with rows_file(mode, backend).open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, default=str) + "\n")
        log(f"seed {s} finished in {rec['seconds']:.0f} s")


def eval_report() -> None:
    exa, duck = done("eval", "exasol"), done("eval", "duckdb")
    seeds = [s for s in SEEDS if s in exa]
    runs = [r for s in seeds for r in exa[s]["runs"]]
    errs = [r["receipts"]["corrected_error_pct"] for r in runs if r["receipts"]["corrected_error_pct"] is not None]
    ms = sorted(r["ms"] for r in runs)
    rep = {"generated_at": time.strftime("%Y-%m-%d %H:%M:%S"), "backend": "exasol", "seeds": seeds,
           "orders_per_day": OPD, "history_days": 42, "scenarios": len(runs) // max(len(seeds), 1), "runs": len(runs),
           "passed": sum(r["pass"] for r in runs),
           "systems": {k: evaluate._score(runs, k) for k in ("receipts", "detectors_only", "threshold_alert")},
           "corrected_value_error_pct": {"max": max(errs) if errs else None,
                                         "mean": round(sum(errs) / len(errs), 3) if errs else None},
           "latency_ms": {"median": ms[len(ms) // 2], "max": ms[-1]},
           "seconds": round(sum(exa[s]["seconds"] for s in seeds), 1), "runs_detail": runs,
           "wrong_fix": wrongfix.summary([w for r in runs for w in r.get("wrong_fixes", [])])}
    key = lambda r: (r["seed"], r["scenario"])
    theirs = {key(r): r for s in duck for r in duck[s]["runs"]}
    shared = [r for r in runs if key(r) in theirs]
    differ = [r for r in shared if (r["receipts"]["verdict"], sorted(r["receipts"]["causes"])) !=
              (theirs[key(r)]["receipts"]["verdict"], sorted(theirs[key(r)]["receipts"]["causes"]))]
    rep["standin"] = {"seeds": sorted(duck), "compared": len(shared), "same_verdict_and_causes": len(shared) - len(differ),
                      "differ": [key(r) for r in differ],
                      "passed": sum(r["pass"] for s in duck for r in duck[s]["runs"]),
                      "runs": sum(len(duck[s]["runs"]) for s in duck),
                      "seconds": round(sum(duck[s]["seconds"] for s in duck), 1)}
    md = evaluate.to_markdown(rep).replace("# Receipts evaluation", "# Receipts evaluation, extended to 25 seeds", 1)
    fails = [r for r in runs if not r["pass"]]
    extra = ["## Extended run", "",
             f"Seeds {', '.join(map(str, seeds))}: the five seeds of [`eval_report.md`](eval_report.md) (11 to 55) "
             f"and {len(seeds) - 5} more, with the same generator settings ({OPD:,} orders a day, 42 days of history), "
             "the same scenarios and the same scoring. Each seed was run on its own and saved as it finished "
             f"([`scripts/evidence_seeds.py`](../../scripts/evidence_seeds.py)). Time on Exasol: {rep['seconds'] / 60:.0f} "
             "minutes in all.", "",
             "Runs that did not pass: " + (", ".join(f"{r['scenario']} seed {r['seed']} (verdict {r['receipts']['verdict']},"
                                                    f" causes {','.join(r['receipts']['causes']) or 'none'})" for r in fails)
                                         if fails else "none."), "",
             "## The same runs on the DuckDB stand-in", "",
             f"* Seeds run on the stand-in: {len(duck)} of {len(seeds)}; runs passed there: "
             f"{rep['standin']['passed']} of {rep['standin']['runs']}.",
             f"* Runs compared one by one: {len(shared)}; same verdict and same causes: "
             f"**{len(shared) - len(differ)} of {len(shared)}**.",
             "* Runs that differ: " + (", ".join(f"{sc} seed {sd}" for sd, sc in rep["standin"]["differ"]) or "none."),
             "* The stand-in seeds ran on 30 October at version 1.0.0; the Exasol seeds ran on 31 October after the fix "
             "for a weekday with no trading history. That fix changes no number here: the five seeds of "
             "`eval_report.md`, run again before and after it on both backends, gave the published numbers each time.",
             ""]
    i = md.index("## Per scenario") if "## Per scenario" in md else len(md)
    md = md[:i] + "\n".join(extra) + "\n" + md[i:]
    (OUT / "eval_extended.json").write_text(json.dumps(rep, indent=2, default=str), encoding="utf-8")
    (OUT / "eval_extended.md").write_text(md, encoding="utf-8")
    print(f"eval: {rep['passed']} of {rep['runs']} on Exasol; stand-in agrees on {len(shared) - len(differ)} of {len(shared)}")


def wrongfix_report() -> None:
    exa = done("wrongfix", "exasol")
    seeds = [s for s in SEEDS if s in exa]
    rows = [r for s in seeds for r in exa[s]["rows"]]
    rep = {"backend": exa[seeds[0]]["backend"], "seeds": seeds, "orders_per_day": OPD, "rows": rows,
           "summary": wrongfix.summary(rows), "seconds": round(sum(exa[s]["seconds"] for s in seeds)),
           "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    md = wrongfix.to_markdown(rep, "python scripts/evidence_seeds.py wrongfix --backend exasol")
    acc = [r for r in rows if r["accepted"]]
    md += "\n".join(["", "## Every accepted wrong fix, by seed", "",
                     "| Seed | Scenario | Kind | Wrong fix | Move | History | Verdict of the run |", "|---|---|---|---|---|---|---|"] +
                    [f"| {r['seed']} | {r['scenario']} | {r['kind']} | {r['fix']} | {r['move_pct']:+.2f}% | {r['history']} | "
                     f"{r['verdict']} |" for r in acc] + [""])
    (OUT / "wrongfix_extended.json").write_text(json.dumps(rep, indent=2, default=str), encoding="utf-8")
    (OUT / "wrongfix_extended.md").write_text(md, encoding="utf-8")
    s = rep["summary"]
    print(f"wrongfix: {s['tried']} tried, {s['rejected']} rejected, {s['accepted']} accepted")


def redteam_report() -> None:
    exa = done("redteam", "exasol")
    seeds = [s for s in SEEDS if s in exa]
    per_seed = [exa[s]["run"] for s in seeds]
    rep = {"backend": exa[seeds[0]]["backend"], "seeds": seeds, "orders_per_day": OPD, "shares": redteam.SHARES,
           "wrong_pct": redteam.WRONG_PCT, "runs": per_seed, "summary": redteam.summarise(per_seed),
           "seconds": round(sum(exa[s]["seconds"] for s in seeds)), "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    md = redteam.to_markdown(rep, "python scripts/evidence_seeds.py redteam --backend exasol")
    lines = ["", "## Every hole and every miss, by seed", "",
             "A hole is a wrong number published or a wrong cause named. A miss below the floor is listed too.", "",
             "| Seed | Where | Outcome | Verdict | Causes | Error |", "|---|---|---|---|---|---|"]
    n = 0
    for s in per_seed:
        steps = [(f"{l['fault']}{' on ' + l['gateway'] if l['gateway'] else ''} at {st['faults'][0]['share']:.0%}", st)
                 for l in s["ladders"] for st in l["steps"] if st["outcome"] != "caught"]
        steps += [(f"unit_scale on {g['gateway']} at 100%", g) for g in s["unit_gateways"] if g["outcome"] != "caught"]
        steps += [(" + ".join(f"{f['fault']} at {f['share']:.0%}" for f in c["faults"]), c)
                  for c in s["combos"] if c["outcome"] != "caught"]
        for where, st in steps:
            n += 1
            lines.append(f"| {s['seed']} | {where} | {st['outcome']}{' (HOLE)' if st['outcome'] in redteam.HOLES else ''} | "
                         f"{st['verdict']} | {','.join(st['confirmed']) or '-'} | {st['error_pct']:+.2f}% |")
    if not n:
        lines.append("| - | none | | | | |")
    md += "\n".join(lines) + "\n"
    (OUT / "redteam_extended.json").write_text(json.dumps(rep, indent=2, default=str), encoding="utf-8")
    (OUT / "redteam_extended.md").write_text(md, encoding="utf-8")
    print(f"redteam: {len(rep['summary']['holes'])} holes over {len(seeds)} seeds")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["eval", "wrongfix", "redteam"])
    ap.add_argument("--backend", default="exasol", choices=["exasol", "duckdb"])
    ap.add_argument("--seeds", type=int, nargs="+", default=list(SEEDS))
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if a.report:
        {"eval": eval_report, "wrongfix": wrongfix_report, "redteam": redteam_report}[a.mode]()
        return
    run(a.mode, a.backend, a.seeds, log=lambda m: print(f"{time.strftime('%H:%M:%S')} {m}", flush=True))


if __name__ == "__main__":
    main()
