"""Lab mode: everything that can write bad data or attack the system.

Planting a scenario's fault, the "Break the pipeline" panel, its Reset and the red team are lab-only.
Lab mode is off unless `receipts serve --lab` (or `demo --lab`) or RECEIPTS_LAB=1 turns it on.
Without it the command center watches batches, proves causes and lets a person approve a proven
correction, and nothing else: the lab endpoints answer 403.

Even in lab mode, breaking the pipeline is refused unless the database holds the built-in
synthetic data, so a lab switch left on can never plant faults into someone's real tables.
"""

from __future__ import annotations

import json
from pathlib import Path

from .config import settings
from .db import Backend

OFF = ("Lab mode is off. Breaking the pipeline and the red team only run with `receipts serve --lab` "
       "(or RECEIPTS_LAB=1), on the built-in synthetic data.")


def enabled() -> bool:
    return settings().lab


def synthetic_check(be: Backend, data_dir: Path | None = None) -> tuple[bool, str]:
    """Is the loaded data the built-in synthetic data? Compares the database with data/manifest.json."""
    f = (data_dir or settings().data_dir) / "manifest.json"
    if not f.exists():
        return False, f"No {f.name} in {f.parent}: this does not look like the built-in synthetic data."
    try:
        m = json.loads(f.read_text(encoding="utf-8"))
        seed, rows = m["config"]["seed"], m["rows"]
    except (ValueError, KeyError, TypeError):
        return False, f"{f} is not a manifest written by the synthetic data generator."
    try:
        n_pay = be.scalar("SELECT COUNT(*) FROM LANDING.PAYMENTS")
        n_ord = be.scalar("SELECT COUNT(*) FROM LANDING.ORDERS")
        gws = {r["gateway"] for r in be.query("SELECT DISTINCT GATEWAY FROM LANDING.PAYMENTS")}
    except Exception as e:
        return False, f"Could not read LANDING: {e}"
    if (n_pay, n_ord) != (rows.get("PAYMENTS"), rows.get("ORDERS")):
        return False, (f"The database holds {n_pay:,} payment and {n_ord:,} order rows, but the synthetic manifest "
                       f"(seed {seed}) has {rows.get('PAYMENTS', 0):,} and {rows.get('ORDERS', 0):,}. "
                       "Run `receipts init` to load the synthetic data first.")
    if not gws <= {"GW_A", "GW_B", "GW_C", "GW_INTL"}:
        return False, "The payment gateways are not the synthetic ones."
    return True, f"Synthetic data, seed {seed}, {n_pay:,} payment rows."
