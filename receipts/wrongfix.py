"""Wrong-fix control: the undo test is not circular.

For every planted fault the gate is shown corrections that are deliberately wrong: the right fix on the wrong
gateway, the right gateway with the wrong factor, the right fix applied to every day instead of tonight, or the
fix for a cause that was not planted. Each goes through the same sandbox undo and the same rules the gate uses
to confirm a cause:

  rule 3  undoing it moves today's number by at least 1.5%
  rule 4  history stays exactly as published (or comes back to it)
  gate    the corrected number lands inside the normal range

A wrong fix that passes all three would have been confirmed had a detector nominated it. Those are reported as
accepted, by name, however many there are.
"""

from __future__ import annotations

from datetime import date

from .db import Backend
from .detectors import PAY_COLS, Correction, _sel
from .faults import FAULT_CLASSES
from .gate import MATERIAL
from .undo import run_undo

GATEWAYS = ["GW_A", "GW_B", "GW_C"]
IST_MIN = 330


def _unit(D: str, gw: str, factor: float, today_only: bool = True) -> Correction:
    when = f"BATCH_DAY = {D} AND GATEWAY = '{gw}'" if today_only else f"GATEWAY = '{gw}'"
    case = f"CASE WHEN {when} THEN AMOUNT / {factor:g} ELSE AMOUNT END AS AMOUNT"
    return Correction("PAYMENTS", f"SELECT\n  {_sel(PAY_COLS, {'AMOUNT': case})}\nFROM {{{{ inp }}}}")


def _clock(be: Backend, D: str, gw: str) -> Correction:
    ts = be.dialect.add_minutes("CAPTURED_AT", -IST_MIN)
    case = f"CASE WHEN BATCH_DAY = {D} AND GATEWAY = '{gw}' THEN {ts} ELSE CAPTURED_AT END AS CAPTURED_AT"
    return Correction("PAYMENTS", f"SELECT\n  {_sel(PAY_COLS, {'CAPTURED_AT': case})}\nFROM {{{{ inp }}}}")


def _dedup(D: str) -> Correction:
    cols = ", ".join(PAY_COLS)
    return Correction("PAYMENTS", f"SELECT {cols} FROM {{{{ inp }}}} WHERE BATCH_DAY <> {D}\nUNION ALL\n"
                                  f"SELECT {cols} FROM (\n  SELECT i.*, ROW_NUMBER() OVER (PARTITION BY i.PAYMENT_ID "
                                  f"ORDER BY i.CAPTURED_AT DESC) AS RN\n  FROM {{{{ inp }}}} i WHERE i.BATCH_DAY = {D}\n) z "
                                  f"WHERE z.RN = 1")


def wrong_fixes(be: Backend, day: date, planted: dict[str, str | None]) -> list[tuple[str, str, Correction]]:
    """(kind, label, correction) for every wrong fix that applies to the planted faults.

    `planted` maps each planted fault class to its gateway (None when the class has no gateway).
    """
    D = be.dialect.day(day)
    out = []
    unit_gw = planted.get("unit_scale")
    clock_gw = planted.get("clock_shift")
    if "unit_scale" in planted:
        out.append(("wrong_factor", f"divide {unit_gw} by 10 instead of 100", _unit(D, unit_gw, 10)))
        out.append(("wrong_factor", f"divide {unit_gw} by 1000 instead of 100", _unit(D, unit_gw, 1000)))
        out.append(("every_day", f"divide {unit_gw} by 100 on every day, not only tonight", _unit(D, unit_gw, 100, False)))
    for gw in GATEWAYS:
        if gw != unit_gw:
            kind = "wrong_gateway" if "unit_scale" in planted else "different_cause"
            out.append((kind, f"unit fix (divide by 100) on {gw}", _unit(D, gw, 100)))
        if gw != clock_gw:
            kind = "wrong_gateway" if "clock_shift" in planted else "different_cause"
            out.append((kind, f"clock fix (shift back 5.5 hours) on {gw}", _clock(be, D, gw)))
    if "duplicate_key" not in planted:
        out.append(("different_cause", "remove duplicate payments in tonight's batch", _dedup(D)))
    return out


def judge(u: dict, A: float, low: float, high: float) -> dict:
    move = (u["value"] - A) / A if A else 0.0
    r3 = abs(move) >= MATERIAL
    r4 = u["history_check"] in ("UNCHANGED", "RESTORED")
    in_range = low <= u["value"] <= high
    why = ("would be confirmed: moves the number, keeps history and lands in range" if r3 and r4 and in_range else
           "history would change" if not r4 else
           f"moves today's number only {move:+.2%}" if not r3 else
           "the corrected number is still outside the normal range")
    return {"move_pct": round(move * 100, 2), "history": u["history_check"], "in_range": in_range,
            "accepted": r3 and r4 and in_range, "why": why}


def control(be: Backend, day: date, case: dict, planted: dict[str, str | None]) -> list[dict]:
    """Run every wrong fix for this case through the sandbox and the gate's rules."""
    v = case["values"]
    cand = {date.fromisoformat(d): x for d, x in case["series"]["candidate"].items()}
    pub = {date.fromisoformat(d): x for d, x in case["series"]["published"].items()}
    out = []
    for kind, label, corr in wrong_fixes(be, day, planted):
        u = run_undo(be, day, [corr], cand, pub)
        out.append({"kind": kind, "fix": label, "verdict": case["verdict"], "confirmed": case["confirmed"]}
                   | judge(u, v["candidate"], v["band_low"], v["band_high"]))
    return out


def planted_of(kind_or_causes, case: dict, gateway: str | None = None) -> dict[str, str | None]:
    """Fault class -> gateway, from the scenario's planted causes and the gateway the gate found (or the default)."""
    kinds = [kind_or_causes] if isinstance(kind_or_causes, str) else list(kind_or_causes)
    found = {s["id"]: (s.get("slice") or {}).get("GATEWAY") for s in case["suspects"] if s["outcome"] == "CONFIRMED"}
    out = {}
    for k in kinds:
        gw_opts = FAULT_CLASSES.get(k, (None, None, None, None))[2]
        out[k] = (gateway or found.get(k) or FAULT_CLASSES[k][3]) if gw_opts else None
    return out


def summary(rows: list[dict]) -> dict:
    acc = [r for r in rows if r["accepted"]]
    by = {}
    for r in rows:
        k = by.setdefault(r["kind"], {"tried": 0, "rejected": 0, "accepted": 0})
        k["tried"] += 1
        k["accepted" if r["accepted"] else "rejected"] += 1
    return {"tried": len(rows), "rejected": len(rows) - len(acc), "accepted": len(acc), "by_kind": by,
            "accepted_list": acc}


def run(seeds=(11,), orders_per_day: int = 8000, backend: str = "duckdb", log=print) -> dict:
    """Every scenario with a planted fault, every wrong fix, on fresh synthetic data per seed."""
    import tempfile
    import time
    from dataclasses import replace
    from pathlib import Path

    from .config import settings
    from .datagen import GenConfig, generate
    from .db import DuckDBBackend, connect
    from .faults import SCENARIOS
    from .gate import run as run_gate
    from .load import ingest, init_database

    t0 = time.perf_counter()
    rows = []
    desc = None
    for seed in seeds:
        tmp = Path(tempfile.mkdtemp(prefix=f"receipts_wrongfix_{seed}_"))
        cfg = GenConfig(seed=seed, orders_per_day=orders_per_day)
        generate(tmp, cfg)
        be = DuckDBBackend(":memory:") if backend == "duckdb" else connect(replace(settings(), backend=backend))
        init_database(be, tmp, log=lambda *a: None)
        desc = be.describe()
        day = cfg.incoming_day
        for sc in SCENARIOS.values():
            if sc.expected_verdict != "PROVEN_FAULT":
                continue
            ingest(be, day, sc)
            c = run_gate(be, day, {"id": sc.id, "title": sc.title}, write_back=False)
            got = control(be, day, c, planted_of(sc.expected_causes, c))
            for r in got:
                rows.append({"seed": seed, "scenario": sc.id} | r)
            n_acc = sum(r["accepted"] for r in got)
            log(f"seed {seed} {sc.id:15s} verdict {c['verdict']:13s} wrong fixes {len(got)}, accepted {n_acc}")
        be.close()
    return {"backend": desc, "seeds": list(seeds), "orders_per_day": orders_per_day, "rows": rows,
            "summary": summary(rows), "seconds": round(time.perf_counter() - t0),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")}


def to_markdown(rep: dict, command: str) -> str:
    b, s = rep["backend"], rep["summary"]
    where = (f"Exasol {b.get('version', '')}".strip() if b["backend"] == "exasol" and not b.get("standin")
             else "the DuckDB stand-in")
    out = ["# Wrong-fix control", "",
           "Is the undo test circular? For every scenario with a planted fault, the gate's own rules are shown "
           "corrections that are deliberately wrong: the right fix on the wrong gateway, the wrong factor, the right "
           "fix applied to every day instead of tonight, or the fix for a cause that was not planted. A wrong fix is "
           "**accepted** if it moves today's number by at least 1.5%, keeps history as published and lands inside "
           "the normal range, which is what the gate needs to confirm a cause.", "",
           f"On {where}, {rep['orders_per_day']:,} orders a day, seeds {', '.join(map(str, rep['seeds']))}. "
           f"Generated {rep['generated_at']} in {rep['seconds']} s. Reproduce: `{command}`.", "",
           f"**Wrong fixes tried {s['tried']}, rejected {s['rejected']}, accepted {s['accepted']}.**", "",
           "| Kind of wrong fix | Tried | Rejected | Accepted |", "|---|---|---|---|"]
    for k, v in s["by_kind"].items():
        out.append(f"| {k.replace('_', ' ')} | {v['tried']} | {v['rejected']} | {v['accepted']} |")
    out += ["", "## Accepted wrong fixes", ""]
    if s["accepted_list"]:
        out.append("Each of these would have been confirmed if a detector had nominated it. In every one the gate's "
                   "own verdict did not use it (the confirmed causes are listed).")
        out.append("")
        for r in s["accepted_list"]:
            out.append(f"* seed {r['seed']}, {r['scenario']}: {r['fix']} moves today {r['move_pct']:+.2f}%, history "
                       f"{r['history'].lower()}, lands in range. Gate verdict {r['verdict']}, confirmed "
                       f"{', '.join(r['confirmed']) or 'none'}.")
    else:
        out.append("None.")
    out += ["", "## Every wrong fix", "", "| Seed | Scenario | Wrong fix | Move | History | In range | Result |",
            "|---|---|---|---|---|---|---|"]
    for r in rep["rows"]:
        out.append(f"| {r['seed']} | {r['scenario']} | {r['fix']} | {r['move_pct']:+.2f}% | {r['history'].lower()} | "
                   f"{'yes' if r['in_range'] else 'no'} | {'ACCEPTED' if r['accepted'] else 'rejected: ' + r['why']} |")
    return "\n".join(out) + "\n"
