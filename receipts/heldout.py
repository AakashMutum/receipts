"""Held-out partial unit errors, written before the fix for the red team's unit hole and frozen since.

The red team found that a x100 unit change on 2% of GW_C's payments was published. The fix must not be
tuned to that one case, so these cases differ on every axis the fix could overfit to: the factor (x10 and
x1000, not x100), the gateway (GW_A and GW_B, not GW_C), the share (2, 5 and 10 percent) and the data
(seeds 21 and 22, not 11 or 7). They were committed and run on the old code before the fix was written.

Run them on synthetic data or a sandbox copy only: each case writes a planted fault into RAW.
"""

from __future__ import annotations

import tempfile
import time
from dataclasses import replace
from pathlib import Path

from .config import settings
from .datagen import GenConfig, generate
from .db import DuckDBBackend, connect
from .faults import D, Scenario
from .load import init_database
from .redteam import HOLES, OUTCOMES, attack_sql, clean_value

FACTORS = [10, 1000]
GATEWAYS = ["GW_A", "GW_B"]
SHARES = [0.02, 0.05, 0.10]
SEEDS = [21, 22]


def case_sql(gw: str, factor: int, share: float) -> str:
    k = round(share * 1000)
    return (f"UPDATE RAW.PAYMENTS SET AMOUNT = AMOUNT * {factor} WHERE BATCH_DAY = {D} AND GATEWAY = '{gw}' "
            f"AND MOD(PAYMENT_ID, 1000) < {k}")


CASES = [(gw, f, sh) for gw in GATEWAYS for f in FACTORS for sh in SHARES]


def run(backend: str = "duckdb", seeds=SEEDS, orders_per_day: int = 20000, log=print) -> dict:
    t0 = time.perf_counter()
    rows = []
    desc = None
    for seed in seeds:
        tmp = Path(tempfile.mkdtemp(prefix=f"receipts_heldout_{seed}_"))
        cfg = GenConfig(seed=seed, orders_per_day=orders_per_day)
        generate(tmp, cfg)
        be = DuckDBBackend(":memory:") if backend == "duckdb" else connect(replace(settings(), backend=backend))
        init_database(be, tmp, log=lambda *a: None)
        desc = be.describe()
        day = cfg.incoming_day
        truth = clean_value(be, day)
        for gw, f, sh in CASES:
            sc = Scenario("heldout", f"x{f} on {sh:.0%} of {gw}", "", "PROVEN_FAULT", frozenset({"unit_scale"}),
                          [case_sql(gw, f, sh)], kind="heldout")
            r = attack_sql(be, day, sc, truth)
            r |= {"seed": seed, "gateway": gw, "factor": f, "share": sh}
            rows.append(r)
            log(f"seed {seed} {gw} x{f:<5d} {sh:>4.0%}  {r['outcome']:12s} {r['verdict']:13s} "
                f"{','.join(r['confirmed']) or '-':12s} error {r['error_pct']:+8.2f}%")
        be.close()
    n = {o: sum(r["outcome"] == o for r in rows) for o in OUTCOMES}
    return {"backend": desc, "seeds": list(seeds), "orders_per_day": orders_per_day, "runs": rows, "counts": n,
            "holes": sum(r["outcome"] in HOLES for r in rows), "seconds": round(time.perf_counter() - t0),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")}


def to_markdown(rep: dict, title: str, command: str) -> str:
    b = rep["backend"]
    where = (f"Exasol {b.get('version', '')}".strip() if b["backend"] == "exasol" and not b.get("standin")
             else "the DuckDB stand-in")
    c = rep["counts"]
    out = [f"# {title}", "",
           "Partial unit errors written before the fix and frozen: factors x10 and x1000, gateways GW_A and GW_B, "
           "2, 5 and 10 percent of the gateway's payments, seeds 21 and 22. Run on synthetic data only.", "",
           f"On {where}, {rep['orders_per_day']:,} orders a day. Generated {rep['generated_at']} in "
           f"{max(1, round(rep['seconds'] / 60))} minutes. Reproduce: `{command}`.", "",
           f"**{len(rep['runs'])} cases: caught {c['caught']}, held without a proven cause {c['held'] + c['held_partial']}, "
           f"published under 4% off {c['small']}, wrong cause named {c['wrong_cause']}, "
           f"published a number more than 4% off {c['WRONG']}.**", "",
           "| Seed | Gateway | Factor | Share | Outcome | Verdict | Causes named | Error |", "|---|---|---|---|---|---|---|---|"]
    for r in rep["runs"]:
        out.append(f"| {r['seed']} | {r['gateway']} | x{r['factor']} | {r['share']:.0%} | {r['outcome']} | {r['verdict']} | "
                   f"{', '.join(r['confirmed']) or 'none'} | {r['error_pct']:+.2f}% |")
    out += ["", "Outcomes: " + "; ".join(f"`{k}` {v}" for k, v in OUTCOMES.items()) + "."]
    return "\n".join(out) + "\n"
