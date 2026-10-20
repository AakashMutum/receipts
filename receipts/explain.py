"""Layer 3: explanation. Deterministic by default, an LLM only if a key is set.

The LLM never decides anything. It receives the finished case, already judged
by the evidence gate, reduced to aggregates (no raw rows, no customer data),
and is asked to restate it for a finance reader. If its text contradicts the
verdict we discard it and keep the template.
"""

from __future__ import annotations

import json

from .config import settings


def inr(v: float | None) -> str:
    if v is None:
        return "n/a"
    v = float(v)
    sign = "-" if v < 0 else ""
    v = abs(v)
    if v >= 1e7:
        return f"{sign}₹{v / 1e7:,.2f} crore"
    if v >= 1e5:
        return f"{sign}₹{v / 1e5:,.2f} lakh"
    return f"{sign}₹{v:,.0f}"


def template(case: dict) -> str:
    v = case["values"]
    day = case["day_label"]
    chg = v["change_pct"]
    confirmed = [s for s in case["suspects"] if s["outcome"] == "CONFIRMED"]
    rejected = [s for s in case["suspects"] if s["fired"] and s["outcome"] == "REJECTED"]
    verdict = case["verdict"]
    if verdict == "NO_INCIDENT":
        return (f"Revenue for {day} is {inr(v['candidate'])}, {chg:+.1%} against the last two weeks and inside the "
                f"normal range. All six checks on the incoming batch passed, so it was published.")
    if verdict == "REAL_CHANGE":
        rej = ""
        if rejected:
            rej = (" One check did raise a flag (" + ", ".join(s["title"].lower() for s in rejected) +
                   "), but undoing it did not move the number, so it was ruled out.")
        return (f"Revenue for {day} moved {chg:+.1%}, outside the normal range, and Receipts found no data fault behind "
                f"it. Transaction volume moved with the value and every raw payment reconciles to one revenue row."
                f"{rej} It was published as a verified real change.")
    if verdict == "PROVEN_FAULT":
        causes = "; ".join(f"{s['title'].lower()} in {s['blamed']['table']}.{s['blamed']['column']} ({s['slice_text']})"
                           for s in confirmed)
        masked = ""
        if not case["anomaly"]:
            masked = " The total looked normal because the faults cancel each other out, which a threshold alert would miss."
        return (f"Revenue for {day} came in at {inr(v['candidate'])} ({chg:+.1%}). Receipts held it. "
                f"Proven cause{'s' if len(confirmed) > 1 else ''}: {causes}. Undoing "
                f"{'them' if len(confirmed) > 1 else 'it'} in a sandbox brings revenue to {inr(v['corrected'])}, "
                f"inside the normal range, with history unchanged.{masked} The dashboard keeps showing "
                f"the last trusted value until a person approves the correction.")
    return (f"Revenue for {day} came in at {inr(v['candidate'])} ({chg:+.1%}) and does not reconcile with volume. "
            f"None of the six detectors produced a cause that survives the undo test, so Receipts will not guess. "
            f"The value is held and needs a person. The breakdown shows where to start looking: "
            f"{case.get('where_text') or 'see the breakdown'}.")


def llm(case: dict) -> dict:
    cfg = settings()
    if not cfg.llm_key:
        return {"source": "template", "text": template(case)}
    import httpx

    brief = {
        "metric": case["metric_label"], "day": case["day_label"], "verdict": case["verdict"],
        "values": case["values"], "anomaly": case["anomaly"],
        "suspects": [{k: s[k] for k in ("title", "outcome", "summary", "reason", "blamed", "slice_text")}
                     for s in case["suspects"] if s["fired"]],
        "top_movers": case["decomposition"]["top_single"][:4],
    }
    prompt = ("You explain data incidents to a finance analyst. The verdict below was decided by deterministic "
              "checks and is final. Restate it in at most four plain sentences: what happened to the number, why, "
              "and what she should do. Do not introduce causes that are not listed. No jargon.\n\n"
              + json.dumps(brief, default=str))
    try:
        r = httpx.post("https://api.anthropic.com/v1/messages", timeout=30,
                       headers={"x-api-key": cfg.llm_key, "anthropic-version": "2023-06-01",
                                "content-type": "application/json"},
                       json={"model": cfg.llm_model, "max_tokens": 300,
                             "messages": [{"role": "user", "content": prompt}]})
        r.raise_for_status()
        text = "".join(b.get("text", "") for b in r.json().get("content", []))
    except Exception as e:
        return {"source": "template", "text": template(case), "note": f"LLM unavailable: {e}"}
    # guardrail: the LLM may not bring up a check that never fired
    silent = {s["title"].lower() for s in case["suspects"] if not s["fired"]}
    if any(o in text.lower() for o in silent):
        return {"source": "template", "text": template(case), "note": "LLM text named an unproven cause; discarded."}
    return {"source": "llm", "model": cfg.llm_model, "text": text.strip()}
