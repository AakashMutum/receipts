"""HTTP API and static UI for the Receipts command center."""

from __future__ import annotations

import json
import re
import threading
import time
import uuid
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import agent, explain, gate, lab
from .config import ROOT, settings
from .db import Backend, connect, to_date
from .dialect import lit
from .faults import DEMO_ORDER, FAULT_CLASSES, SCENARIOS, fault_scenario
from .load import ingest, reset_raw, udf_status

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
                from .model import stale_message
                _state["error"] = str(e)
                raise HTTPException(503, f"{stale_message(None)} ({type(e).__name__})")
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


def _require_lab() -> None:
    if not lab.enabled():
        raise HTTPException(403, lab.OFF)


def _require_synthetic(b: Backend) -> None:
    ok, why = lab.synthetic_check(b)
    if not ok:
        raise HTTPException(409, f"Refused: {why}")


class RunReq(BaseModel):
    scenario: str


class BreakReq(BaseModel):
    fault: str
    share: float = 1.0
    gateway: str | None = None


class ApproveReq(BaseModel):
    note: str = ""


def _rebuild_if_stale(b: Backend) -> Backend:
    """In `receipts demo`, a new day (midnight in India) rebuilds the demo data for it, once, here."""
    import os

    from .model import expected_day
    if os.environ.get("RECEIPTS_AUTO_REBUILD") != "1" or _day(b) == expected_day():
        return b
    from .cli import _build, _manifest, preland_headline
    conf = (_manifest() or {}).get("config", {})
    b.close()
    _state["be"] = None
    _build(expected_day(), conf.get("seed", 7), conf.get("orders_per_day", 20000), fresh=False)
    if lab.enabled():
        preland_headline()
    return be()


def _stale(day: date) -> dict | None:
    from .model import expected_day, stale_message
    if day == expected_day():
        return None
    return {"data_day": day.isoformat(), "expected_day": expected_day().isoformat(), "message": stale_message(day)}


@app.get("/api/overview")
def overview():
    b = be()
    with _lock:
        b = _rebuild_if_stale(b)
        day = _day(b)
        rows = b.scalar("SELECT COUNT(*) FROM RAW.PAYMENTS")
        on = lab.enabled()
        return {"backend": b.describe() | udf_status(b), "incoming_day": day.isoformat(),
                "scenarios": _scenarios() if on else [], "board": _board(b, day), "case": _latest_case(b),
                "raw_payment_rows": rows, "eval": _eval_summary(), "llm": bool(settings().llm_key),
                "lab": on, "stale": _stale(day), "faults": [{"id": k, "title": v[0], "share_of": v[1], "gateways": v[2], "gateway": v[3]}
                                      for k, v in FAULT_CLASSES.items()] if on else []}


@app.post("/api/run")
def run(req: RunReq):
    """Land a scenario's batch, planted fault included, and run the gate. Lab only."""
    _require_lab()
    if req.scenario not in SCENARIOS:
        raise HTTPException(404, f"Unknown scenario {req.scenario}")
    b = be()
    with _lock:
        _require_synthetic(b)
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


@app.get("/api/alerts")
def alerts():
    """Holds raised by the watcher that nobody has approved or dismissed yet."""
    from .watch import open_alerts
    b = be()
    with _lock:
        return open_alerts(b, settings().alerts_dir)


@app.post("/api/alerts/{case_id}/dismiss")
def dismiss_alert(case_id: str):
    from .watch import dismiss
    if not dismiss(settings().alerts_dir, case_id):
        raise HTTPException(404, "No such alert")
    return {"dismissed": case_id}


# lab: break the pipeline, watch the gate step by step, reset ------------------------------------------
_jobs: dict[str, dict] = {}


def _break_job(job: dict, sc, t_click: float) -> None:
    b = be()
    try:
        with _lock:
            day = _day(b)
            t = time.perf_counter()
            ingest(b, day, sc)  # the clean incoming batch, then the fault on RAW; LANDING and history untouched
            job["steps"].append({"step": "Land the batch with the fault in RAW", "ms": round((time.perf_counter() - t) * 1000, 1)})
            case = gate.run(b, day, {"id": sc.id, "title": sc.title, "story": sc.story, "kind": sc.kind},
                            on_step=lambda st: job["steps"].append(dict(st)))
            job["board"] = _board(b, day)
        job["case"] = case
        job["server_ms"] = round((time.perf_counter() - t_click) * 1000, 1)
        job["status"] = "done"
    except Exception as e:  # shown on the page; the lab must never take the server down
        job["status"], job["error"] = "error", f"{type(e).__name__}: {e}"


@app.post("/api/lab/break")
def lab_break(req: BreakReq):
    """Plant one fault class into tonight's RAW batch and run the gate in the background. Lab only."""
    _require_lab()
    t_click = time.perf_counter()
    if req.fault not in FAULT_CLASSES:
        raise HTTPException(404, f"Unknown fault {req.fault}")
    if not 0 < req.share <= 1:
        raise HTTPException(422, "share must be above 0 and at most 1")
    try:
        sc = fault_scenario(req.fault, req.share, req.gateway)
    except ValueError as e:
        raise HTTPException(422, str(e))
    b = be()
    with _lock:
        _require_synthetic(b)
        if any(j["status"] == "running" for j in _jobs.values()):
            raise HTTPException(409, "A gate run is already in progress.")
        job = {"id": uuid.uuid4().hex[:8], "status": "running", "fault": req.fault, "title": sc.title, "steps": []}
        _jobs.clear()
        _jobs[job["id"]] = job
    threading.Thread(target=_break_job, args=(job, sc, t_click), daemon=True).start()
    return {"job": job["id"], "title": sc.title}


@app.get("/api/lab/job/{job_id}")
def lab_job(job_id: str):
    _require_lab()
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(404, "No such job")
    return job


@app.post("/api/lab/reset")
def lab_reset():
    """Remove tonight's landed batch and its published row, so the demo can run again. Lab only."""
    _require_lab()
    b = be()
    with _lock:
        _require_synthetic(b)
        day = _day(b)
        reset_raw(b, day)
        return {"board": _board(b, day), "incoming_day": day.isoformat()}


# lab: red team --------------------------------------------------------------------------------------------
def _redteam_file() -> Path | None:
    for f in (SAMPLES / "exasol" / "redteam_report.json", SAMPLES / "redteam_report.json"):
        if f.exists():
            return f
    return None


@app.get("/api/lab/redteam")
def lab_redteam():
    """The saved red team report: detection floor per fault class, and every hole. Lab only."""
    _require_lab()
    f = _redteam_file()
    if not f:
        raise HTTPException(404, "No red team report yet. Run `receipts redteam`.")
    rep = json.loads(f.read_text(encoding="utf-8"))
    return {"file": f.relative_to(ROOT).as_posix(), "backend": rep["backend"], "orders_per_day": rep["orders_per_day"],
            "seeds": rep["seeds"], "generated_at": rep["generated_at"], "summary": rep["summary"]}


@app.post("/api/lab/redteam/attack")
def lab_attack(req: BreakReq):
    """Run one attack live: plant the fault, run the gate without write-back, restore RAW. Lab only."""
    from .redteam import OUTCOMES, attack, clean_value
    _require_lab()
    if req.fault not in FAULT_CLASSES:
        raise HTTPException(404, f"Unknown fault {req.fault}")
    if not 0 < req.share <= 1:
        raise HTTPException(422, "share must be above 0 and at most 1")
    b = be()
    with _lock:
        _require_synthetic(b)
        day = _day(b)
        if _board(b, day)["points"] and _board(b, day)["points"][-1]["day"] == day.isoformat():
            raise HTTPException(409, "Tonight's batch is already judged. Press Reset first, so the attack cannot "
                                     "touch a published number.")
        try:
            r = attack(b, day, [(req.fault, req.share, req.gateway)], clean_value(b, day))
        except ValueError as e:
            raise HTTPException(422, str(e))
        r["meaning"] = OUTCOMES[r["outcome"]]
        return r


@app.get("/api/health")
def health():
    try:
        b = be()
        return {"ok": True, "backend": b.name}
    except HTTPException as e:
        return JSONResponse({"ok": False, "error": e.detail}, status_code=503)


@app.get("/static/index.html")
def raw_page():
    """The page is served at / only, so the lab-only parts cannot be reached around the mode check."""
    raise HTTPException(404, "Not found")


app.mount("/static", StaticFiles(directory=str(WEB)), name="static")


LAB_BLOCK = re.compile(r"<!-- lab -->.*?<!-- /lab -->", re.S)
NORMAL_BLOCK = re.compile(r"<!-- normal -->(.*?)<!-- /normal -->", re.S)


def page(lab_on: bool) -> str:
    """index.html with the lab-only parts removed, or the normal-mode note removed, depending on the mode."""
    html = (WEB / "index.html").read_text(encoding="utf-8")
    if lab_on:
        return NORMAL_BLOCK.sub("", html)
    return LAB_BLOCK.sub("", NORMAL_BLOCK.sub(lambda m: m.group(1), html))


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(page(lab.enabled()))
