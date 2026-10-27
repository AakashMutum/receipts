"""Run the newest checks on a live Exasol and write samples/exasol/live_checks.md.

Needs Exasol running and the demo data built (`receipts init --fresh` with RECEIPTS_BACKEND=exasol). It lands the
IST case, reads MART.FINANCE_DAILY from a second session (so the audit log has a reader to find), runs the gate
with write-back and records: the blast radius, the audit-log readers, the DOWNSTREAM_* columns of
PUB.METRIC_TRUST, the RECEIPTS.METRIC_HISTORY snapshot, `receipts connect --check`, the two other metrics through
the gate, and /badge.svg after the hold and after approval.

    python scripts/live_checks.py
"""

from __future__ import annotations

import io
import json
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from receipts import badge, gate  # noqa: E402
from receipts.cli import main as cli  # noqa: E402
from receipts.db import ExasolBackend, connect  # noqa: E402
from receipts.config import settings  # noqa: E402
from receipts.load import incoming_day, ingest  # noqa: E402
from receipts.metrics import check, load  # noqa: E402


def run_cli(args: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            cli(args)
    except SystemExit as e:
        return int(e.code or 0), buf.getvalue()
    return 0, buf.getvalue()


def main() -> int:
    be = connect()
    assert isinstance(be, ExasolBackend), "set RECEIPTS_BACKEND=exasol and start Exasol first"
    out, ok_all = [], True

    def item(name, ok, detail):
        nonlocal ok_all
        ok_all &= bool(ok)
        out.append(f"| {name} | {'pass' if ok else 'FAIL'} | {detail} |")

    ver = be.scalar("SELECT PARAM_VALUE FROM SYS.EXA_METADATA WHERE PARAM_NAME = 'databaseProductVersion'")
    day = incoming_day(be)
    t0 = time.perf_counter()
    ingest(be, day, "ist_utc")
    other = ExasolBackend(settings())  # a second session, like a BI tool reading the report view
    other.query("SELECT COUNT(*) AS N FROM MART.FINANCE_DAILY")
    other.close()
    time.sleep(5)  # the audit log records a statement shortly after its session ends
    case = gate.run(be, day, {"id": "ist_utc"})
    b = case["blast_radius"]
    item("Verdict, IST case", case["verdict"] == "PROVEN_FAULT" and case["confirmed"] == ["clock_shift"],
         f"{case['verdict']}, {', '.join(case['confirmed'])}")
    item("Blast radius from SYS.EXA_ALL_VIEWS", b["count"] == 4,
         f"{b['count']} exposed: {', '.join(b['exposed'])}; protected: {', '.join(b['protected'])}; "
         f"{b['views_read']} views read")
    r = b["reads"]
    readers = r.get("readers") or []
    item("Audit log: read during the bad window", r.get("available") and readers,
         f"{r.get('note')}; " + ("; ".join(f"{x.get('user_name')} ({x.get('read_count')} reads)" for x in readers)
                                 if readers else "no readers found"))
    row = be.query(f"SELECT DOWNSTREAM_COUNT, DOWNSTREAM_OBJECTS FROM PUB.METRIC_TRUST WHERE TXN_DAY = {be.dialect.day(day)}")[0]
    item("PUB.METRIC_TRUST DOWNSTREAM_COUNT and DOWNSTREAM_OBJECTS", int(row["downstream_count"]) == b["count"],
         f"{int(row['downstream_count'])}: {row['downstream_objects']}")
    hist = be.query("SELECT METRIC_NAME, COUNT(*) AS N FROM RECEIPTS.METRIC_HISTORY GROUP BY METRIC_NAME ORDER BY 1")
    item("RECEIPTS.METRIC_HISTORY snapshot", len(hist) == 2 and all(h["n"] >= 35 for h in hist),
         ", ".join(f"{h['metric_name']} {h['n']} days" for h in hist))
    res = check(be, load())
    bad = [m for ok, m in res if not ok]
    item("receipts connect --check (SYS.EXA_ALL_COLUMNS)", not bad, f"{len(res)} checks, {len(bad)} problems" +
         (": " + "; ".join(bad) if bad else ""))
    for m in load():
        if m.publish:
            continue
        c = gate.run(be, day, {"id": "ist_utc"}, write_back=False, metric=m)
        item(f"{m.name} through the gate (PIPE.DAILY_ORDERS)", c["verdict"] in ("PROVEN_FAULT", "NO_INCIDENT"),
             f"{c['verdict']}, {c['trust_status']}, {', '.join(c['confirmed']) or 'no cause'}, "
             f"change {c['values']['change_pct']:+.1%}")
    got = badge.latest(be)
    item("Badge after the hold", got["status"] == "HELD", f"{got['status']}, last trusted {got['last_trusted']}")
    gate.approve(be, case["case_id"], "live check")
    got = badge.latest(be)
    item("Badge after approval", got["status"] == "CORRECTED", f"{got['status']}, last trusted {got['last_trusted']}")
    secs = time.perf_counter() - t0
    md = ["# Live checks on Exasol", "",
          f"Exasol {ver}, demo data, batch day {day}. Generated {time.strftime('%Y-%m-%d %H:%M:%S')} in {secs:.0f} s. "
          "Reproduce: `receipts init --fresh` then `python scripts/live_checks.py` with `RECEIPTS_BACKEND=exasol`.", "",
          "| Check | Result | Detail |", "|---|---|---|"] + out + [""]
    path = ROOT / "samples" / "exasol" / "live_checks.md"
    path.write_text("\n".join(md), encoding="utf-8")
    (path.with_suffix(".json")).write_text(json.dumps({"rows": out, "blast_radius": b}, indent=2, default=str),
                                           encoding="utf-8")
    print("\n".join(md))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
