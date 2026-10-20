"""HTTP API and static UI for the Receipts command center."""

from __future__ import annotations

import json
import threading
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import agent, explain, gate
from .config import ROOT, settings
from .db import Backend, connect, to_date
from .dialect import lit
from .faults import DEMO_ORDER, SCENARIOS
from .load import ingest, udf_status

WEB = ROOT / "web"
SAMPLES = ROOT / "samples"

app = FastAPI(title="Receipts", version="1.0.0")
_lock = threading.RLock()
_state: dict = {"be": None, "error": None}


def be() -> Backend:
    with _lock:
        if _state["be"] is None:
            try:
                b = connect()
                b.scalar("SELECT COUNT(*) FROM PUB.DAILY_REVENUE_PUBLISHED")
                _state["be"], _state["error"] = b, None
            except Exception as e:  # not initialised yet, or Exasol not reachable
                _state["error"] = str(e)
                raise HTTPException(503, f"Database not ready: {e}. Run `make init` first.")
        return _state["be"]


def _day(b: Backend) -> date:
    return to_date(b.scalar("SELECT MAX(BATCH_DAY) FROM LANDING.ORDERS"))


def _scenarios():
    return [{"id": s.id, "title": s.title, "story": s.story, "kind": s.kind} for s in (SCENARIOS[i] for i in DEMO_ORDER)]


def _board(b: Backend, day: date) -> dict:
    rows = b.query("SELECT TXN_DAY, SHOWN_VALUE, IS_HELD, TRUST_STATUS, CASE_ID FROM PUB.DASHBOARD_REVENUE ORDER BY TXN_DAY")
    pts = [{"day": to_date(r["txn_day"]).isoformat(), "value": r["shown_value"], "held": bool(r["is_held"]),
            "status": r["trust_status"], "case_id": r["case_id"]} for r in rows]
    cand = b.scalar(f"SELECT REVENUE_INR FROM PIPE.DAILY_REVENUE WHERE TXN_DAY = {b.dialect.day(day)}")
    return {"points": pts, "candidate_today": cand}


def _latest_case(b: Backend) -> dict | None:
    raw = b.scalar("SELECT CASE_JSON FROM RECEIPTS.CASES ORDER BY OPENED_AT DESC, CASE_ID DESC LIMIT 1")
    return json.loads(raw) if raw else None


def _eval_summary():
    f = SAMPLES / "eval_report.json"
    if not f.exists():
        return None
    rep = json.loads(f.read_text())
    rep.pop("runs_detail", None)
    return rep


class RunReq(BaseModel):
    scenario: str


class ApproveReq(BaseModel):
    note: str = ""


@app.get("/api/overview")
def overview():
    b = be()
    with _lock:
        day = _day(b)
        rows = b.scalar("SELECT COUNT(*) FROM RAW.PAYMENTS")
        return {"backend": b.describe() | udf_status(b), "incoming_day": day.isoformat(),
                "scenarios": _scenarios(), "board": _board(b, day), "case": _latest_case(b),
                "raw_payment_rows": rows, "eval": _eval_summary(), "llm": bool(settings().llm_key)}


@app.post("/api/run")
def run(req: RunReq):
    if req.scenario not in SCENARIOS:
        raise HTTPException(404, f"Unknown scenario {req.scenario}")
    b = be()
    with _lock:
        day = _day(b)
        sc = ingest(b, day, req.scenario)
        case = gate.run(b, day, {"id": sc.id, "title": sc.title, "story": sc.story, "kind": sc.kind})
        return {"case": case, "board": _board(b, day)}


@app.get("/api/case/{case_id}")
def get_case(case_id: str):
    b = be()
    with _lock:
        raw = b.scalar(f"SELECT CASE_JSON FROM RECEIPTS.CASES WHERE CASE_ID = {lit(case_id)}")
    if not raw:
        raise HTTPException(404, "No such case")
    return json.loads(raw)


@app.get("/api/cases")
def cases():
    b = be()
    with _lock:
        return b.query("SELECT CASE_ID, TXN_DAY, VERDICT, SCENARIO, CANDIDATE_VALUE, CORRECTED_VALUE, ELAPSED_MS, "
                       "OPENED_AT FROM RECEIPTS.CASES ORDER BY OPENED_AT DESC LIMIT 20")


@app.post("/api/case/{case_id}/approve")
def approve(case_id: str, req: ApproveReq):
    b = be()
    with _lock:
        try:
            case = gate.approve(b, case_id, req.note)
        except KeyError:
            raise HTTPException(404, "No such case")
        except ValueError as e:
            raise HTTPException(409, str(e))
        return {"case": case, "board": _board(b, _day(b))}


@app.post("/api/case/{case_id}/explain")
def explain_case(case_id: str):
    case = get_case(case_id)
    return explain.llm(case)


@app.get("/api/agent")
def ask_agent():
    b = be()
    with _lock:
        return agent.ask(b, _day(b))


@app.get("/api/trust")
def trust():
    b = be()
    with _lock:
        rows = b.query("SELECT METRIC_NAME, TXN_DAY, TRUST_STATUS, TRUSTED_VALUE, CASE_ID, AGENT_GUIDANCE "
                       "FROM PUB.METRIC_TRUST ORDER BY TXN_DAY DESC LIMIT 3")
    return rows


@app.get("/api/health")
def health():
    try:
        b = be()
        return {"ok": True, "backend": b.name}
    except HTTPException as e:
        return JSONResponse({"ok": False, "error": e.detail}, status_code=503)


app.mount("/static", StaticFiles(directory=str(WEB)), name="static")


@app.get("/")
def index():
    return FileResponse(str(WEB / "index.html"))
