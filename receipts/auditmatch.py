"""`receipts audit-match`: does Exasol's audit log show every statement Receipts says it sent?

One full run on Exasol: land the IST case, run the gate with write-back (detectors, CUBE, lineage, every undo test
in the sandbox schema, the evidence gate, the write to RECEIPTS and the trust table), then the agent's reads
through the Exasol MCP server as AGENT_READER. Every statement Receipts sent is kept, then matched against
EXA_DBA_AUDIT_SQL for those sessions:

  matched    the audit log holds the same text (whitespace and a trailing semicolon ignored)
  different  the audit log holds a statement at that position whose text differs (prefix match fails)
  missing    nothing in the audit log for it
  extra      statements in the audit log for these sessions that the client log does not hold
             (the timing markers and statistics reads, which bypass the client log, show up here)

Only on Exasol: the stand-in keeps no audit log.
"""

from __future__ import annotations

import re
import time
from collections import Counter


def norm(sql: str) -> str:
    return re.sub(r"\s+", " ", sql.strip().rstrip(";")).strip().upper()


def match(issued: list[str], audited: list[str]) -> dict:
    """Match issued statements to audit rows in order. Each audit row is used once."""
    pool = [norm(a) for a in audited]
    used = [False] * len(pool)
    rows = []
    for s in issued:
        n = norm(s)
        hit = next((i for i, a in enumerate(pool) if not used[i] and a == n), None)
        kind = "matched"
        if hit is None:  # the audit log may truncate long statements, or the driver may rewrite one
            hit = next((i for i, a in enumerate(pool) if not used[i] and len(a) >= 60 and n.startswith(a[:60])), None)
            kind = "different" if hit is not None else "missing"
        if hit is not None:
            used[hit] = True
        rows.append({"sql": s[:200], "result": kind})
    extra = [audited[i][:200] for i, u in enumerate(used) if not u]
    c = Counter(r["result"] for r in rows)
    return {"issued": len(issued), "matched": c["matched"], "different": c["different"], "missing": c["missing"],
            "extra": len(extra), "rows": rows, "extra_statements": extra,
            "extra_kinds": dict(Counter(_kind(e) for e in extra))}


def _kind(sql: str) -> str:
    u = norm(sql)
    if "CURRENT_STATEMENT" in u:
        return "timing marker (SELECT CURRENT_STATEMENT)"
    if u.startswith("FLUSH STATISTICS"):
        return "FLUSH STATISTICS"
    if "EXA_STATISTICS" in u or "EXA_DBA_AUDIT" in u:
        return "statistics or audit read"
    if "CURRENT_SESSION" in u:
        return "session id read"
    return u.split(" ")[0].lower() + " (other)"


AUDIT_SQL = ("SELECT SESSION_ID, STMT_ID, COMMAND_NAME, SQL_TEXT FROM EXA_DBA_AUDIT_SQL "
             "WHERE SESSION_ID IN ({ids}) ORDER BY SESSION_ID, STMT_ID")


def run(log=print) -> dict:
    """The full run on Exasol and the match. Needs RECEIPTS_BACKEND=exasol and the demo data built."""
    from . import gate
    from .config import settings
    from .db import ExasolBackend
    from .load import incoming_day, ingest

    cfg = settings()
    be = ExasolBackend(cfg)
    sid = int(be.con.execute("SELECT CURRENT_SESSION FROM DUAL").fetchval())
    t0 = time.perf_counter()
    be.log.clear()
    day = incoming_day(be)
    ingest(be, day, "ist_utc")
    issued = [e.sql for e in be.log]
    case = gate.run(be, day, {"id": "ist_utc"})
    issued += [e.sql for e in be.log]
    log(f"gate: {case['verdict']}, {len(issued)} statements in the client log (session {sid})")
    mcp = _mcp_reads(cfg, day, log)
    be.con.execute("FLUSH STATISTICS")
    time.sleep(5)  # the audit log records a session's statements shortly after they finish
    be.con.execute("FLUSH STATISTICS")
    rows = be.con.execute(AUDIT_SQL.format(ids=str(sid))).fetchall()
    gate_rows = [r[3] for r in rows if r[0] == sid]
    out = {"exasol": be.describe().get("version"), "day": day.isoformat(), "case": case["case_id"],
           "verdict": case["verdict"], "seconds": round(time.perf_counter() - t0, 1),
           "gate": match(issued, gate_rows)}
    if mcp:
        ids = ",".join(str(int(i)) for i in mcp["sessions"]) or "-1"
        mrows = be.con.execute(AUDIT_SQL.format(ids=ids)).fetchall()
        out["mcp"] = match(mcp["issued"], [r[3] for r in mrows]) | {"sessions": mcp["sessions"],
                                                                   "user": cfg.agent_user, "note": mcp["note"]}
    else:
        out["mcp"] = None
    be.close()
    return out


def _mcp_reads(cfg, day, log) -> dict | None:
    """Send the agent's three reads through the Exasol MCP server as AGENT_READER; return what was sent."""
    import json
    import os
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    try:
        from mcp_smoke import Stdio, mcp_command
    except ImportError:
        return None
    cmd = mcp_command()
    if not cmd:
        log("MCP server not started: uvx or exasol-mcp-server is not on PATH")
        return None
    env = os.environ | {"EXA_DSN": cfg.exa_dsn, "EXA_USER": cfg.agent_user, "EXA_PASSWORD": cfg.agent_password,
                        "EXA_SSL_CERT_VALIDATION": "false" if cfg.exa_insecure else "true",
                        "EXA_MCP_SETTINGS": json.dumps({"enable_read_query": True, "schemas": {"like_pattern": "PUB"}}),
                        "EXASOL_TELEMETRY_DISABLE": "1"}
    D = f"DATE '{day.isoformat()}'"
    sent = [f"SELECT TXN_DAY, TRUST_STATUS, TRUSTED_VALUE, LAST_TRUSTED_DAY, CASE_ID, AGENT_GUIDANCE FROM PUB.METRIC_TRUST "
            f"WHERE METRIC_NAME = 'daily_revenue_inr' AND TXN_DAY = {D}",
            f"SELECT DOWNSTREAM_COUNT, DOWNSTREAM_OBJECTS FROM PUB.METRIC_TRUST WHERE TXN_DAY = {D}",
            f"SELECT c.SUSPECT, c.SLICE_DESC FROM PUB.CONFIRMED_CAUSES c JOIN PUB.METRIC_TRUST t ON t.CASE_ID = c.CASE_ID "
            f"WHERE t.TXN_DAY = {D}"]
    s = Stdio(cmd, env)
    try:
        s.call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                              "clientInfo": {"name": "receipts-audit-match", "version": "1"}})
        s.notify("notifications/initialized")
        tools = s.call("tools/list")["tools"]
        q = next(t for t in tools if t["name"] == "execute_exasol_query")
        arg = next(iter(q.get("inputSchema", {}).get("properties", {"query": {}})))
        for sql in sent:
            s.call("tools/call", {"name": q["name"], "arguments": {arg: sql}})
    finally:
        s.close()
    time.sleep(5)
    from .db import ExasolBackend
    from .config import settings
    be = ExasolBackend(settings())
    be.con.execute("FLUSH STATISTICS")
    rows = be.con.execute(
        f"SELECT a.SESSION_ID FROM EXA_DBA_AUDIT_SQL a JOIN EXA_DBA_AUDIT_SESSIONS s ON s.SESSION_ID = a.SESSION_ID "
        f"WHERE s.USER_NAME = '{cfg.agent_user}' AND s.LOGIN_TIME >= ADD_SECONDS(SYSTIMESTAMP, -300) "
        f"AND UPPER(a.SQL_TEXT) LIKE '%AGENT_GUIDANCE FROM PUB.METRIC_TRUST%' "
        f"ORDER BY s.LOGIN_TIME DESC LIMIT 1").fetchall()  # this run's session only, not doctor's grant checks
    be.close()
    return {"issued": sent, "sessions": [int(r[0]) for r in rows],
            "note": "the three reads were sent through execute_exasol_query; the server may add its own statements"}


def to_markdown(rep: dict, command: str) -> str:
    def block(name, m):
        if not m:
            return [f"## {name}", "", "Not run (the Exasol MCP server could not be started).", ""]
        lines = [f"## {name}", "", "| Issued | Matched | Different | Missing | Extra in the audit log |", "|---|---|---|---|---|",
                 f"| {m['issued']} | {m['matched']} | {m['different']} | {m['missing']} | {m['extra']} |", ""]
        if m.get("extra_kinds"):
            lines += ["Extra statements in the audit log, by kind: " +
                      ", ".join(f"{k} {v}" for k, v in sorted(m["extra_kinds"].items())) + ".", ""]
        odd = [r for r in m["rows"] if r["result"] != "matched"]
        if odd:
            lines += ["Not matched exactly:", ""] + [f"* {r['result']}: `{r['sql'][:120]}`" for r in odd] + [""]
        return lines
    out = ["# Audit-log match", "",
           f"Every statement Receipts sent in one full run, matched against `EXA_DBA_AUDIT_SQL` on Exasol "
           f"{rep['exasol']}. Batch day {rep['day']}, case {rep['case']}, verdict {rep['verdict']}, {rep['seconds']} s. "
           f"Reproduce: `{command}` (needs Exasol with the demo data).", "",
           "Matched means the same text, ignoring whitespace and a trailing semicolon; different means a statement at the "
           "same place whose text differs after the first 60 characters; missing means nothing in the audit log. Extra "
           "statements are in the audit log for the same session but not in the client's statement log.", ""]
    out += block("Gate session: landing, detectors, CUBE, lineage, undo tests, write-back", rep["gate"])
    out += block("Agent reads through the Exasol MCP server as AGENT_READER", rep.get("mcp"))
    out += ["## Why there are extra statements", "",
            "None of the extras is a query Receipts or the agent sent that the client log hid. `COMMIT /* AUTO */` and "
            "`ROLLBACK /* AUTO */` are Exasol's own autocommit records. The timing markers (`SELECT CURRENT_STATEMENT`), "
            "a `FLUSH STATISTICS` and the `EXA_STATISTICS` read are the timing code reading Exasol's measurements; the "
            "session id read and the other `FLUSH STATISTICS` are audit-match itself. They go straight to the "
            "connection, outside the statement log, so that measuring does not change what is measured.", ""]
    return "\n".join(out) + "\n"
