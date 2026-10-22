"""Watch for new batches and raise an alert when Receipts holds one.

Once a minute the watcher runs one cheap query: is the newest day in RAW later than the newest
published day? Landing a batch (a new night, or `ingest` re-landing today) leaves today without a
published row, so the answer is yes until the gate has run. Only then does it run the gate.

An optional inbox folder lets anyone land a batch without touching the database: a file named
after a scenario, for example `inbox/ist_utc.batch`, lands that scenario's batch on the next check.

A hold (PROVEN_FAULT or UNEXPLAINED) prints an alert line, writes alerts/<case>.txt and .json,
and posts to Slack when SLACK_WEBHOOK_URL is set. A published verdict prints one quiet line.
"""

from __future__ import annotations

import contextlib
import json
import shutil
import threading
from datetime import date
from pathlib import Path
from typing import Callable

from . import gate
from .db import Backend, to_date
from .detectors import DETECTOR_TITLES
from .dialect import lit
from .explain import inr
from .faults import SCENARIOS
from .load import incoming_day, ingest

HOLD = ("PROVEN_FAULT", "UNEXPLAINED")


def pending_day(be: Backend) -> date | None:
    """The day of a landed batch the gate has not judged yet, or None. One query."""
    r = be.query("SELECT (SELECT MAX(BATCH_DAY) FROM RAW.ORDERS) AS RAW_DAY, "
                 "(SELECT MAX(TXN_DAY) FROM PUB.DAILY_REVENUE_PUBLISHED) AS PUB_DAY" + be.dialect.from_dual())[0]
    raw_day = to_date(r["raw_day"]) if r["raw_day"] is not None else None
    pub_day = to_date(r["pub_day"]) if r["pub_day"] is not None else None
    if raw_day is None or (pub_day is not None and raw_day <= pub_day):
        return None
    return raw_day


def cause_line(case: dict) -> str:
    confirmed = [s for s in case["suspects"] if s["outcome"] == "CONFIRMED"]
    if not confirmed:
        return "No proven cause yet. A person needs to look."
    parts = []
    for s in confirmed:
        b = s.get("blamed") or {}
        where = f" in {b['table']}.{b['column']}" if b.get("table") else ""
        parts.append(f"{DETECTOR_TITLES.get(s['id'], s['title']).lower()}{where}"
                     + (f" ({s['slice_text']})" if s.get("slice_text") else ""))
    return "Proven cause: " + "; ".join(parts) + "."


def open_alerts(be: Backend, alerts_dir: Path) -> list[dict]:
    """Alerts whose case is still held: not approved, not re-landed, not dismissed."""
    out = []
    for f in sorted(Path(alerts_dir).glob("RC-*.json"), reverse=True):
        if f.with_suffix(".dismissed").exists():
            continue
        a = json.loads(f.read_text(encoding="utf-8"))
        status = be.scalar(f"SELECT TRUST_STATUS FROM PUB.DAILY_REVENUE_PUBLISHED WHERE CASE_ID = {lit(a['case_id'])}")
        if status == "HELD":
            out.append(a)
    return out


def dismiss(alerts_dir: Path, case_id: str) -> bool:
    f = Path(alerts_dir) / f"{case_id}.json"
    if not f.exists():
        return False
    f.with_suffix(".dismissed").write_text("dismissed\n", encoding="utf-8")
    return True


class Watcher:
    def __init__(self, connect: Callable[[], Backend], lock=None, alerts_dir: Path | str = "alerts",
                 inbox_dir: Path | str | None = None, base_url: str = "http://127.0.0.1:8000/",
                 slack_url: str | None = None, log=print):
        self.connect = connect
        self.lock = lock or contextlib.nullcontext()
        self.alerts_dir = Path(alerts_dir)
        self.inbox_dir = Path(inbox_dir) if inbox_dir else None
        self.base_url = base_url
        self.slack_url = slack_url
        self.log = log

    # one check ------------------------------------------------------------------------------------
    def check_once(self) -> list[dict]:
        """Land at most one inbox batch, then judge a pending batch if there is one."""
        with self.lock:
            be = self.connect()
            landed = self._take_inbox(be)
            day = pending_day(be)
            if day is None:
                return []
            case = gate.run(be, day, landed or {"id": "batch", "title": "Nightly batch"})
        self._report(case)
        return [case]

    def _take_inbox(self, be: Backend) -> dict | None:
        if not self.inbox_dir or not self.inbox_dir.is_dir():
            return None
        files = sorted((f for f in self.inbox_dir.iterdir() if f.is_file()), key=lambda f: f.stat().st_mtime)
        if not files:
            return None
        f = files[0]
        sid = f.stem.lower()
        done = self.inbox_dir / ("processed" if sid in SCENARIOS else "ignored")
        done.mkdir(exist_ok=True)
        shutil.move(str(f), str(done / f.name))
        if sid not in SCENARIOS:
            self.log(f"watch: ignored inbox file {f.name}. Name it after a scenario, for example ist_utc.batch")
            return None
        sc = ingest(be, incoming_day(be), sid)
        self.log(f"watch: landed batch {f.name} ({sc.title})")
        return {"id": sc.id, "title": sc.title, "story": sc.story, "kind": sc.kind}

    # reporting --------------------------------------------------------------------------------------
    def _report(self, case: dict) -> None:
        if case["verdict"] not in HOLD:
            self.log(f"watch: {case['day_label']} published ({case['verdict']}), case {case['case_id']}")
            return
        v = case["values"]
        last_day = v.get("last_trusted_day")
        alert = {
            "case_id": case["case_id"], "day": case["day"], "day_label": case["day_label"],
            "verdict": case["verdict"], "cause": cause_line(case),
            "candidate_value": v["candidate"], "last_trusted_value": v.get("last_trusted_value"),
            "last_trusted_day": last_day, "link": f"{self.base_url}?case={case['case_id']}",
            "opened_at": case.get("opened_at"),
        }
        last = (f"{inr(alert['last_trusted_value'])} on {date.fromisoformat(last_day):%a %d %b}"
                if last_day and alert["last_trusted_value"] is not None else "none yet")
        text = (f"Receipts held revenue for {case['day_label']} ({case['verdict']}).\n"
                f"{alert['cause']}\n"
                f"Pipeline value: {inr(v['candidate'])}. Last trusted value: {last}.\n"
                f"Receipt: {alert['link']}\n")
        self.alerts_dir.mkdir(parents=True, exist_ok=True)
        (self.alerts_dir / f"{case['case_id']}.txt").write_text(text, encoding="utf-8")
        (self.alerts_dir / f"{case['case_id']}.json").write_text(json.dumps(alert, indent=2, default=str),
                                                                  encoding="utf-8")
        self.log(f"ALERT {case['case_id']} {case['day_label']} held ({case['verdict']}). {alert['cause']} "
                 f"Last trusted: {last}. {alert['link']}")
        self._slack(text)

    def _slack(self, text: str) -> None:
        if not self.slack_url:
            return
        try:
            import httpx
            r = httpx.post(self.slack_url, json={"text": text}, timeout=5)
            r.raise_for_status()
        except Exception as e:  # Slack being down must never stop the watcher
            self.log(f"watch: could not post to Slack ({type(e).__name__}). The alert file was still written.")

    # the loop ---------------------------------------------------------------------------------------
    def tick(self) -> bool:
        """One check that never raises. Returns False if the check failed."""
        try:
            self.check_once()
            return True
        except Exception as e:
            self.log(f"watch: check failed, will try again: {type(e).__name__}: {e}")
            return False

    def run_forever(self, interval: float = 60, stop: threading.Event | None = None) -> None:
        stop = stop or threading.Event()
        inbox = f", inbox {self.inbox_dir}" if self.inbox_dir else ""
        self.log(f"watch: checking for new batches every {interval:g}s{inbox}")
        while True:
            self.tick()
            if stop.wait(interval):  # sleeps without using the CPU
                return
