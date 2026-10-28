"""Cold and warm timings of the IST case on the DuckDB stand-in, per gate step; writes samples/standin_bench.json.

Cold: a new process opens a freshly built stand-in database and runs the gate once (3 times).
Warm: one process runs the gate 3 more times on the same database after a first run.

    python scripts/bench_standin.py
"""

from __future__ import annotations

import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ONE = """
import json, sys, time
from receipts.db import DuckDBBackend
from receipts.gate import run
from receipts.load import ingest
from receipts.model import INCOMING_DAY
be = DuckDBBackend(sys.argv[1]); out = []
for i in range(int(sys.argv[2])):
    ingest(be, INCOMING_DAY, "ist_utc"); c = run(be, INCOMING_DAY, write_back=False)
    out.append({"total_ms": c["total_ms"], "verdict": c["verdict"], "steps": {s["step"]: s["ms"] for s in c["timings"]}})
print(json.dumps(out))
"""


def build(path: Path, data: Path) -> None:
    from receipts.datagen import GenConfig, generate
    from receipts.db import DuckDBBackend
    from receipts.load import init_database
    from receipts.model import INCOMING_DAY
    generate(data, GenConfig(seed=7, orders_per_day=20000, incoming_day=INCOMING_DAY))
    be = DuckDBBackend(str(path))
    init_database(be, data, log=lambda *a: None)
    be.close()


def runs(db: Path, n: int) -> list[dict]:
    r = subprocess.run([sys.executable, "-c", ONE, str(db), str(n)], cwd=ROOT, capture_output=True, text=True,
                       env=os.environ | {"PYTHONIOENCODING": "utf-8"})
    return json.loads(r.stdout.strip().splitlines()[-1])


def summary(xs: list[dict]) -> dict:
    steps = {k: [x["steps"][k] for x in xs] for k in xs[0]["steps"]}
    f = lambda v: {"median": round(statistics.median(v), 1), "min": round(min(v), 1), "max": round(max(v), 1)}
    return {"total_ms": f([x["total_ms"] for x in xs]), "steps": {k: f(v) for k, v in steps.items()},
            "verdicts": sorted({x["verdict"] for x in xs})}


def main() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="receipts_bench_"))
    cold = []
    for i in range(3):
        db = tmp / f"cold{i}.duckdb"
        build(db, tmp / f"data{i}")
        cold += runs(db, 1)
    warm_all = runs(tmp / "cold0.duckdb", 4)
    rep = {"generated_at": time.strftime("%Y-%m-%d %H:%M:%S"), "backend": "duckdb stand-in", "case": "ist_utc",
           "orders_per_day": 20000, "cold": summary(cold), "warm": summary(warm_all[1:]), "raw": {"cold": cold,
           "warm": warm_all}}
    out = ROOT / "samples" / "standin_bench.json"
    out.write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps({k: rep[k] for k in ("cold", "warm")}, indent=1))


if __name__ == "__main__":
    main()
