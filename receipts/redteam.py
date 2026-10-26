"""Red team: find where Receipts breaks.

Run it on the built-in synthetic data or a sandbox copy, never on live production tables: every
attack writes a planted fault into RAW.

For each of the six fault classes an attacker shrinks the fault, step by step. Past the first step
the gate no longer proves it keeps going, because a smaller fault could still be published as a
wrong number, and stops early once a missed fault moves the number by less than 4 percent (it can no
longer cause a wrong publish). The share of rows affected goes 100, 50, 25, 10, 5, 2 percent; unit errors are
also tried on each gateway, from the largest to the smallest. Every step records:

  verdict          what the gate decided
  right cause      the planted class, and only it, was confirmed
  wrong published  the number was published although it is more than 4 percent off the clean value
  held, no cause   the number was held, but nothing was proven

The detection floor of a class is the smallest share that was still proven with the right cause.
Then pairs of faults that push revenue in opposite directions are planted together at their floors,
to see whether two faults that cancel can slip through.

Nothing is tuned here. The detectors and the gate run exactly as in production; a bad result is a
finding, written into the report as a hole.
"""

from __future__ import annotations

import tempfile
import time
from dataclasses import replace
from datetime import date
from pathlib import Path

from . import gate, wrongfix
from .config import settings
from .datagen import GenConfig, generate
from .db import Backend, DuckDBBackend, connect
from .faults import FAULT_CLASSES, Scenario, fault_sql
from .load import ingest, init_database, reset_raw

SHARES = [1.0, 0.5, 0.25, 0.10, 0.05, 0.02]
WRONG_PCT = 4.0
UP = ["unit_scale", "duplicate_key", "key_fanout"]      # faults that push revenue up
DOWN = ["clock_shift", "orphan_code", "stale_feed"]     # faults that push it down

OUTCOMES = {
    "caught": "proven, right cause",
    "held": "held, nothing proven",
    "held_partial": "held, part of the cause proven",
    "wrong_cause": "a cause that was not planted was named",
    "small": "published, under 4% off",
    "WRONG": "published a number more than 4% off",
}
HOLES = {"wrong_cause", "WRONG"}


def classify(case: dict, expected: set[str], truth: float) -> dict:
    err = (case["values"]["candidate"] - truth) / truth * 100 if truth else 0.0
    confirmed = set(case["confirmed"])
    held = case["trust_status"] == "HELD"
    if case["verdict"] == "PROVEN_FAULT" and confirmed == expected:
        out = "caught"
    elif confirmed - expected:
        out = "wrong_cause"
    elif held:
        out = "held_partial" if confirmed else "held"
    else:
        out = "small" if abs(err) < WRONG_PCT else "WRONG"
    return {"outcome": out, "verdict": case["verdict"], "trust": case["trust_status"],
            "confirmed": sorted(confirmed), "right_cause": confirmed == expected,
            "wrong_published": not held and abs(err) >= WRONG_PCT, "held_no_cause": held and not confirmed,
            "error_pct": round(err, 2), "ms": case["total_ms"]}


def attack(be: Backend, day: date, kinds: list[tuple[str, float, str | None]], truth: float,
           control: bool = False) -> dict:
    """Plant one or more faults into tonight's RAW batch, run the gate without write-back, restore RAW."""
    sql = [s for k, sh, gw in kinds for s in fault_sql(k, sh, gw)]
    sc = Scenario("redteam", " + ".join(k for k, _, _ in kinds), "", "PROVEN_FAULT",
                  frozenset(k for k, _, _ in kinds), sql, kind="redteam")
    planted = {k: (gw or FAULT_CLASSES[k][3]) for k, _, gw in kinds} if control else None
    r = attack_sql(be, day, sc, truth, planted)
    r["faults"] = [{"fault": k, "share": sh, "gateway": gw or FAULT_CLASSES[k][3]} for k, sh, gw in kinds]
    return r


def attack_sql(be: Backend, day: date, sc: Scenario, truth: float, planted: dict | None = None) -> dict:
    """Land tonight's batch with a scenario's fault SQL, run the gate without write-back, restore RAW."""
    ingest(be, day, sc)
    try:
        c = gate.run(be, day, {"id": sc.id, "title": sc.title}, write_back=False)
        wrong = wrongfix.control(be, day, c, planted) if planted else None
    finally:
        reset_raw(be, day)  # leave tonight unlanded, as the attack found it
    out = classify(c, set(sc.expected_causes), truth)
    if wrong is not None:
        out["wrong_fixes"] = wrong
    return out


def clean_value(be: Backend, day: date) -> float:
    ingest(be, day, "healthy")
    v = be.scalar(f"SELECT REVENUE_INR FROM PIPE.DAILY_REVENUE WHERE TXN_DAY = {be.dialect.day(day)}")
    reset_raw(be, day)
    return v


def ladder(be: Backend, day: date, kind: str, truth: float, gateway: str | None = None, log=print) -> dict:
    """Shrink one fault until the gate stops proving it. Returns every step and the floor."""
    shares = SHARES if FAULT_CLASSES[kind][1] else [1.0]  # a missing FX rate has no share to shrink
    steps, floor, missed = [], None, False
    for sh in shares:
        r = attack(be, day, [(kind, sh, gateway)], truth)
        steps.append(r)
        log(f"  {kind:14s} {gateway or FAULT_CLASSES[kind][3] or '':5s} {sh:>5.0%}  {r['outcome']:12s} "
            f"{r['verdict']:13s} error {r['error_pct']:+7.2f}%")
        missed |= r["outcome"] != "caught"
        if not missed:
            floor = sh
        # Below the floor keep shrinking while the fault is still big enough to publish a wrong number:
        # stopping at the first miss would hide a hole further down. Once a missed fault moves the
        # number by less than 4 percent, smaller shares can no longer cause a wrong publish, so stop.
        if missed and abs(r["error_pct"]) < WRONG_PCT:
            break
    return {"fault": kind, "gateway": gateway or FAULT_CLASSES[kind][3], "steps": steps, "floor": floor,
            "binary": not FAULT_CLASSES[kind][1], "holes": [s for s in steps if s["outcome"] in HOLES]}


def run(backend: str = "duckdb", seeds=(11,), orders_per_day: int = 8000, log=print) -> dict:
    t0 = time.perf_counter()
    per_seed = []
    for seed in seeds:
        tmp = Path(tempfile.mkdtemp(prefix=f"receipts_redteam_{seed}_"))
        cfg = GenConfig(seed=seed, orders_per_day=orders_per_day)
        generate(tmp, cfg)
        be = DuckDBBackend(":memory:") if backend == "duckdb" else connect(replace(settings(), backend=backend))
        init_database(be, tmp, log=lambda *a: None)
        desc = be.describe()
        day = cfg.incoming_day
        truth = clean_value(be, day)
        log(f"seed {seed}: clean value {truth:,.0f}")
        ladders = [ladder(be, day, k, truth, log=log) for k in FAULT_CLASSES]
        gws = FAULT_CLASSES["unit_scale"][2]
        scope = []
        for gw in gws:  # unit errors on each gateway, largest to smallest, all of its rows
            r = attack(be, day, [("unit_scale", 1.0, gw)], truth)
            r["gateway"] = gw
            scope.append(r)
            log(f"  unit_scale     {gw:5s}  100%  {r['outcome']:12s} {r['verdict']:13s} error {r['error_pct']:+7.2f}%")
        # wrong-fix control: each class at 100%, every deliberately wrong correction through the gate's rules
        controls = []
        for k in FAULT_CLASSES:
            r = attack(be, day, [(k, 1.0, None)], truth, control=True)
            controls.append({"fault": k, "verdict": r["verdict"], "wrong_fixes": r["wrong_fixes"]})
            log(f"  wrong fixes for {k:14s} tried {len(r['wrong_fixes'])}, "
                f"accepted {sum(w['accepted'] for w in r['wrong_fixes'])}")
        floors = {l["fault"]: l["floor"] for l in ladders}
        combos = []
        for up in UP:
            for down in DOWN:
                if floors[up] is None or floors[down] is None:
                    continue
                r = attack(be, day, [(up, floors[up], None), (down, floors[down], None)], truth)
                combos.append(r)
                log(f"  pair {up}@{floors[up]:.0%} + {down}@{floors[down]:.0%}: {r['outcome']} {r['verdict']} "
                    f"{','.join(r['confirmed']) or '-'} error {r['error_pct']:+.2f}%")
        be.close()
        per_seed.append({"seed": seed, "clean_value": truth, "ladders": ladders, "unit_gateways": scope,
                         "combos": combos, "wrong_fix_control": controls})
    return {"backend": desc, "seeds": list(seeds), "orders_per_day": orders_per_day, "shares": SHARES,
            "wrong_pct": WRONG_PCT, "runs": per_seed, "summary": summarise(per_seed),
            "seconds": round(time.perf_counter() - t0), "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")}


def summarise(per_seed: list[dict]) -> dict:
    """Per class: the worst floor over seeds (the largest share still needed), and every hole found."""
    out = {}
    for k in FAULT_CLASSES:
        ls = [l for s in per_seed for l in s["ladders"] if l["fault"] == k]
        floors = [l["floor"] for l in ls]
        first_miss = [st for l in ls for st in l["steps"] if st["outcome"] != "caught"]
        out[k] = {"title": FAULT_CLASSES[k][0], "binary": ls[0]["binary"],
                  "floor": None if None in floors else max(floors), "floors": floors,
                  "below_floor": sorted({m["outcome"] for m in first_miss}),
                  "holes": sum(len(l["holes"]) for l in ls)}
    combos = [c for s in per_seed for c in s["combos"]]
    gws = [g for s in per_seed for g in s["unit_gateways"]]
    holes = ([{"where": f"{l['fault']}{' on ' + l['gateway'] if l['gateway'] else ''} at "
                        f"{st['faults'][0]['share']:.0%} of {FAULT_CLASSES[l['fault']][1]} (seed {s['seed']})", **st}
              for s in per_seed for l in s["ladders"] for st in l["holes"]] +
             [{"where": "unit_scale on " + g["gateway"], **g} for g in gws if g["outcome"] in HOLES] +
             [{"where": " + ".join(f"{f['fault']} at {f['share']:.0%}" for f in c["faults"]), **c}
              for c in combos if c["outcome"] in HOLES])
    return {"classes": out, "combos": {o: sum(c["outcome"] == o for c in combos) for o in OUTCOMES},
            "combo_runs": len(combos), "holes": holes,
            "wrong_fix": wrongfix.summary([w for s in per_seed for c in s.get("wrong_fix_control", [])
                                           for w in c["wrong_fixes"]])}


def _pct(x) -> str:
    return "none" if x is None else f"{x:.0%}"


def to_markdown(rep: dict, command: str) -> str:
    b, s = rep["backend"], rep["summary"]
    where = (f"Exasol {b.get('version', '')}".strip() if b["backend"] == "exasol" and not b.get("standin")
             else "the DuckDB stand-in")
    out = ["# Red team: where Receipts breaks", "",
           "**Run this on the built-in synthetic data or a sandbox copy, never on live production tables.** "
           "Every attack writes a planted fault into RAW.", "",
           f"On {where}, {rep['orders_per_day']:,} orders a day, seeds {', '.join(map(str, rep['seeds']))}. "
           f"Generated {rep['generated_at']} in {rep['seconds'] / 60:.0f} minutes. Reproduce: `{command}`.", "",
           "For each fault class an attacker shrinks the share of rows affected (100, 50, 25, 10, 5, 2 percent). "
           "After the first step the gate no longer proves, it keeps shrinking while the fault still moves the number by "
           f"{rep['wrong_pct']:.0f}% or more (a smaller one cannot be published as a wrong number), then stops. The detection floor "
           "is the smallest share proven with the right cause at every step down to it; with several seeds the worst seed "
           "counts. Nothing was tuned for this run.", "",
           "## Detection floor per fault class", "",
           "| Fault class | Detection floor | What happened below the floor | Holes |", "|---|---|---|---|"]
    for k, c in s["classes"].items():
        below = ", ".join(OUTCOMES[o] for o in c["below_floor"]) or ("not reached: proven at every step" if not c["binary"]
                                                                       else "binary fault, nothing to shrink")
        floor = _pct(c["floor"]) + (" (binary: one rate is missing or not)" if c["binary"] else "")
        out.append(f"| {c['title']} | {floor} | {below} | {c['holes']} |")
    out += ["", "## Every step", "", "| Seed | Fault | Gateway | Share | Outcome | Verdict | Causes named | Error |",
            "|---|---|---|---|---|---|---|---|"]
    for r in rep["runs"]:
        for l in r["ladders"]:
            for st in l["steps"]:
                f = st["faults"][0]
                out.append(f"| {r['seed']} | {l['fault']} | {f['gateway'] or '-'} | {f['share']:.0%} | {st['outcome']} | "
                           f"{st['verdict']} | {', '.join(st['confirmed']) or 'none'} | {st['error_pct']:+.2f}% |")
    out += ["", "## Unit errors by gateway (all of the gateway's rows)", "",
            "| Seed | Gateway | Outcome | Verdict | Error |", "|---|---|---|---|---|"]
    for r in rep["runs"]:
        for g in r["unit_gateways"]:
            out.append(f"| {r['seed']} | {g['gateway']} | {g['outcome']} | {g['verdict']} | {g['error_pct']:+.2f}% |")
    out += ["", "## Two faults that push in opposite directions, each at its floor", "",
            f"{s['combo_runs']} pairs: " + ", ".join(f"{OUTCOMES[o]} {n}" for o, n in s["combos"].items() if n) + ".", "",
            "| Seed | Faults | Outcome | Verdict | Causes named | Error |", "|---|---|---|---|---|---|"]
    for r in rep["runs"]:
        for c in r["combos"]:
            fs = " + ".join(f"{f['fault']} {f['share']:.0%}" for f in c["faults"])
            out.append(f"| {r['seed']} | {fs} | {c['outcome']} | {c['verdict']} | {', '.join(c['confirmed']) or 'none'} | "
                       f"{c['error_pct']:+.2f}% |")
    out += ["", "## Holes", ""]
    if s["holes"]:
        out.append("Each of these is a way to get past Receipts today. None is hidden.")
        out.append("")
        for h in s["holes"]:
            what = ("named a cause that was not planted (" + ", ".join(h["confirmed"]) + ")" if h["outcome"] == "wrong_cause"
                    else f"published a number {h['error_pct']:+.2f}% off as trusted")
            out.append(f"* **{h['where']}**: {what}, verdict {h['verdict']}.")
    else:
        out.append("No attack got a wrong number published or a wrong cause named. Below each floor the gate either held "
                   "the number with nothing proven (safe, a person looks) or published a number that was less than "
                   f"{rep['wrong_pct']:.0f}% off (inside the normal noise).")
    w = s.get("wrong_fix")
    if w:
        out += ["", "## Wrong-fix control", "",
                "Each fault class at 100%, then deliberately wrong corrections (wrong gateway, wrong factor, every day "
                "instead of tonight, or the fix for another cause) judged by the gate's own rules. Accepted means it "
                "moves today by at least 1.5%, keeps history and lands in range.", "",
                f"Tried {w['tried']}, rejected {w['rejected']}, accepted {w['accepted']}."]
        out += [f"* Accepted: {r['fix']} ({r['move_pct']:+.2f}%), gate verdict {r['verdict']}, confirmed "
                f"{', '.join(r['confirmed']) or 'none'}." for r in w["accepted_list"]]
    out += ["", "## What the outcomes mean", ""] + [f"* `{k}`: {v}" for k, v in OUTCOMES.items()]
    out.append("* Holes are `wrong_cause` and `WRONG`. Held is safe: the number is not shown and a person decides.")
    return "\n".join(out) + "\n"
