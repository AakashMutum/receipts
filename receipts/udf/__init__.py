"""In-database UDFs and a local shim that runs the same source in the stand-in.

In Exasol the UDF runs inside the database. In the DuckDB stand-in there is no
Python UDF runtime for SET scripts, so `run_set_script_locally` feeds the rows
of each group through the identical `run(ctx)` function. The source file is the
same in both paths, which is what keeps the stand-in honest.
"""

from __future__ import annotations

from pathlib import Path

UDF_DIR = Path(__file__).resolve().parent

CLOCK_DRIFT_DDL = """CREATE OR REPLACE PYTHON3 SET SCRIPT RECEIPTS.CLOCK_DRIFT(
  slice_key VARCHAR(40), is_today BOOLEAN, bin_idx INTEGER, cnt DOUBLE)
EMITS (slice_key VARCHAR(40), n_today DOUBLE, tvd DOUBLE, best_shift_bins INTEGER, tvd_after_shift DOUBLE) AS
"""

CLOCK_DRIFT_OUT = ["slice_key", "n_today", "tvd", "best_shift_bins", "tvd_after_shift"]


def clock_drift_source() -> str:
    return (UDF_DIR / "clock_drift.py").read_text()


def clock_drift_ddl() -> str:
    return CLOCK_DRIFT_DDL + clock_drift_source()


class _Ctx:
    def __init__(self, rows: list[dict], out: list, out_cols: list[str]):
        self._rows, self._i, self._out, self._cols = rows, 0, out, out_cols

    def __getattr__(self, name):
        return self._rows[self._i][name]

    def next(self) -> bool:
        self._i += 1
        return self._i < len(self._rows)

    def reset(self) -> None:
        self._i = 0

    def size(self) -> int:
        return len(self._rows)

    def emit(self, *values) -> None:
        self._out.append(dict(zip(self._cols, values)))


def run_set_script_locally(source: str, rows: list[dict], group_key: str, out_cols: list[str]) -> list[dict]:
    ns: dict = {}
    exec(compile(source, "udf", "exec"), ns)
    groups: dict = {}
    for r in rows:
        groups.setdefault(r[group_key], []).append(r)
    out: list[dict] = []
    for _, g in groups.items():
        ns["run"](_Ctx(g, out, out_cols))
    return out
