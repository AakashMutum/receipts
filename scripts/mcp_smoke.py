"""Prove the agent's read-only path into Exasol works, without Claude or any other AI client.

1. Log in to Exasol as the read-only agent user (AGENT_READER, created by `receipts init`) and show it
   can read PUB.METRIC_TRUST and PUB.CONFIRMED_CAUSES, and cannot read RAW, PIPE or RECEIPTS or write
   anything.
2. Ask the agent's question as that user: the latest day's trust row and, when it is held, the proven
   cause from PUB.CONFIRMED_CAUSES.
3. If the Exasol MCP server can be started (`uvx` or `exasol-mcp-server` on PATH), start it with that
   user over stdio, list its tools, and ask its query tool for today's trust status, the same question
   an agent asks. Without `uv` this part is skipped and says so.

    python scripts/mcp_smoke.py           # uses EXA_DSN, RECEIPTS_AGENT_USER, RECEIPTS_AGENT_PASSWORD

Exits 1 if any check fails.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from receipts.config import settings  # noqa: E402
from receipts.doctor import agent_reader_checks  # noqa: E402

TRUST_SQL = ("SELECT TXN_DAY, TRUST_STATUS, TRUSTED_VALUE, LAST_TRUSTED_DAY, CASE_ID, AGENT_GUIDANCE "
             "FROM PUB.METRIC_TRUST ORDER BY TXN_DAY DESC LIMIT 1")


def agent_question(cfg) -> list[tuple[bool, str]]:
    """What an agent sees as AGENT_READER for the latest day: the trust row and, when held, the proven cause."""
    import ssl

    import pyexasol
    kw = {"websocket_sslopt": {"cert_reqs": ssl.CERT_NONE}} if cfg.exa_insecure else {}
    con = pyexasol.connect(dsn=cfg.exa_dsn, user=cfg.agent_user, password=cfg.agent_password, encryption=True, **kw)
    r = con.execute(TRUST_SQL).fetchone()
    if not r:
        return [(False, "PUB.METRIC_TRUST is empty")]
    day, status, trusted, last_day, case_id, guidance = r
    out = [(True, f"latest day {day}: {status}, trusted value {trusted}, last trusted day {last_day}. Guidance: {guidance}")]
    if status == "HELD":
        causes = con.execute(f"SELECT SUSPECT, SLICE_DESC FROM PUB.CONFIRMED_CAUSES WHERE CASE_ID = '{case_id}'").fetchall()
        out.append((trusted is None, "a held day has no trusted value to quote"))
        out.append((True, f"proven causes for {case_id}: " + ("; ".join(f"{a} ({b})" for a, b in causes) or "none yet")))
    con.close()
    return out


def mcp_command() -> list[str] | None:
    if shutil.which("exasol-mcp-server"):
        return ["exasol-mcp-server"]
    if shutil.which("uvx"):
        return ["uvx", "exasol-mcp-server@latest"]
    return None


class Stdio:
    """A minimal MCP client: JSON-RPC 2.0, one message per line, over the server's stdin and stdout."""

    def __init__(self, cmd: list[str], env: dict):
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                  env=env, text=True, encoding="utf-8")
        self.n = 0

    def call(self, method: str, params: dict | None = None) -> dict:
        self.n += 1
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params or {}}) + "\n")
        self.p.stdin.flush()
        while True:
            line = self.p.stdout.readline()
            if not line:
                raise RuntimeError("the MCP server closed its output")
            msg = json.loads(line)
            if msg.get("id") == self.n:
                if "error" in msg:
                    raise RuntimeError(msg["error"].get("message", msg["error"]))
                return msg["result"]

    def notify(self, method: str) -> None:
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": method}) + "\n")
        self.p.stdin.flush()

    def close(self) -> None:
        self.p.kill()


def mcp_checks(cfg) -> list[tuple[bool, str]]:
    cmd = mcp_command()
    if not cmd:
        return [(None, "Exasol MCP server not started: neither `uvx` nor `exasol-mcp-server` is on PATH "
                       "(install uv, see docs/MCP_DEMO.md). Only the database checks above ran.")]
    env = os.environ | {"EXA_DSN": cfg.exa_dsn, "EXA_USER": cfg.agent_user, "EXA_PASSWORD": cfg.agent_password,
                        "EXA_SSL_CERT_VALIDATION": "false" if cfg.exa_insecure else "true",
                        "EXA_MCP_SETTINGS": json.dumps({"enable_read_query": True, "schemas": {"like_pattern": "PUB"}}),
                        "EXASOL_TELEMETRY_DISABLE": "1"}
    s = Stdio(cmd, env)
    out = []
    try:
        s.call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                              "clientInfo": {"name": "receipts-mcp-smoke", "version": "1"}})
        s.notify("notifications/initialized")
        tools = s.call("tools/list")["tools"]
        out.append((True, f"MCP server answers with {len(tools)} tools: {', '.join(t['name'] for t in tools)}"))
        q = next((t for t in tools if "query" in t["name"] and "write" not in t["name"]), None)
        if not q:
            return out + [(False, "no read query tool listed (is enable_read_query on?)")]
        arg = next(iter(q.get("inputSchema", {}).get("properties", {"query": {}})))
        r = s.call("tools/call", {"name": q["name"], "arguments": {arg: TRUST_SQL}})
        text = " ".join(c.get("text", "") for c in r.get("content", []))
        out.append(("TRUST_STATUS" in text.upper() and not r.get("isError"),
                    f"{q['name']} as {cfg.agent_user}: {text[:300]}"))
        r = s.call("tools/call", {"name": q["name"], "arguments": {arg: "SELECT COUNT(*) FROM RAW.PAYMENTS"}})
        text = " ".join(c.get("text", "") for c in r.get("content", []))
        out.append((bool(r.get("isError")) or "privilege" in text.lower() or "not found" in text.lower(),
                    f"{q['name']} on RAW.PAYMENTS is refused: {text[:200]}"))
    except Exception as e:
        out.append((False, f"MCP server: {type(e).__name__}: {e}"))
    finally:
        s.close()
    return out


def main() -> int:
    cfg = settings()
    print(f"Agent path smoke test against {cfg.exa_dsn} as {cfg.agent_user}\n")
    ok = True
    for good, msg in agent_reader_checks(cfg) + agent_question(cfg) + mcp_checks(cfg):
        mark = "skip" if good is None else ("ok  " if good else "FAIL")
        ok &= good is not False
        print(f"  {mark}  {msg}")
    print("\n" + ("All checks passed." if ok else "Some checks failed."))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
