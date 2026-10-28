"""Cold and warm timings of the IST case on Exasol, per gate step; writes samples/exasol/bench.json.

The same method as scripts/bench_standin.py, so the two can be compared line by line:
Cold: `receipts init --fresh`, then a new process runs the gate once (3 times). This is a fresh load and a new
session, not a database restart.
Warm: one process runs the gate 3 more times on the same data after a first run.
Without write-back. Needs RECEIPTS_BACKEND=exasol and the EXA_* settings.

    python scripts/bench_exasol.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from bench_standin import summary  # noqa: E402

ONE = """
import json, sys
from receipts.config import settings
from receipts.db import connect
from receipts.gate import run
from receipts.load import incoming_day, ingest
be = connect(settings()); day = incoming_day(be); out = []
for i in range(int(sys.argv[1])):
    ingest(be, day, "ist_utc"); c = run(be, day, write_back=False)
    m = c.get("exasol_measured") or {}
    out.append({"total_ms": c["total_ms"], "verdict": c["verdict"], "steps": {s["step"]: s["ms"] for s in c["timings"]},
                "exasol_ms": m.get("db_ms"), "exasol_source": m.get("source"),
                "exasol_steps": {s["step"]: s["db_ms"] for s in m.get("steps", [])},
                "temp_ram_peak_mib": m.get("temp_ram_peak_mib")})
print(json.dumps(out))
"""


def runs(n: int) -> list[dict]:
    r = subprocess.run([sys.executable, "-c", ONE, str(n)], cwd=ROOT, capture_output=True, text=True,
                       env=os.environ | {"PYTHONIOENCODING": "utf-8"})
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def init_fresh() -> None:
    subprocess.run([sys.executable, "-m", "receipts.cli", "init", "--fresh"], cwd=ROOT, check=True,
                   capture_output=True, env=os.environ | {"PYTHONIOENCODING": "utf-8"})


def exasol_summary(xs: list[dict]) -> dict:
    import statistics
    f = lambda v: {"median": round(statistics.median(v), 1), "min": round(min(v), 1), "max": round(max(v), 1)}
    steps = {k: [x["exasol_steps"][k] for x in xs] for k in xs[0]["exasol_steps"]}
    return {"total_ms": f([x["exasol_ms"] for x in xs]), "steps": {k: f(v) for k, v in steps.items()},
            "temp_ram_peak_mib": f([x["temp_ram_peak_mib"] for x in xs]),
            "sources": sorted({x["exasol_source"] for x in xs})}


def main() -> None:
    if os.environ.get("RECEIPTS_BACKEND") != "exasol":
        raise SystemExit("set RECEIPTS_BACKEND=exasol and the EXA_* settings first")
    cold = []
    for i in range(3):
        init_fresh()
        cold += runs(1)
    warm_all = runs(4)
    rep = {"generated_at": time.strftime("%Y-%m-%d %H:%M:%S"), "backend": "exasol", "case": "ist_utc",
           "orders_per_day": 20000, "cold": summary(cold), "warm": summary(warm_all[1:]),
           "exasol_measured": {"cold": exasol_summary(cold), "warm": exasol_summary(warm_all[1:])},
           "raw": {"cold": cold, "warm": warm_all}}
    out = ROOT / "samples" / "exasol" / "bench.json"
    out.write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps({k: rep[k] for k in ("cold", "warm", "exasol_measured")}, indent=1))


if __name__ == "__main__":
    main()
