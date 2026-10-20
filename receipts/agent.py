"""Two AI-agent answers to the same question, side by side.

Both agents answer "What was revenue on <day>?" by running SQL, the way an
agent connected through the Exasol MCP server would. The only difference is
the instruction in mcp/AGENT_INSTRUCTIONS.md: check PUB.METRIC_TRUST first.

These two agents are deterministic so the demo is reproducible. Pointing a real
LLM agent at the database through the MCP server gives the same contrast; see
docs/RUN_GUIDE.md.
"""

from __future__ import annotations

from datetime import date

from .db import Backend, to_date
from .detectors import DETECTOR_TITLES
from .explain import inr


def ask(be: Backend, day: date) -> dict:
    D = be.dialect.day(day)
    label = f"{day:%a %d %b}"
    question = f"What was our revenue on {label}?"

    naive_sql = f"SELECT REVENUE_INR FROM PIPE.DAILY_REVENUE WHERE TXN_DAY = {D}"
    v = be.scalar(naive_sql)
    naive = {"sql": naive_sql,
             "answer": f"Revenue on {label} was {inr(v)}." if v is not None else f"I found no revenue for {label}."}

    trust_sql = (f"SELECT TRUST_STATUS, TRUSTED_VALUE, CANDIDATE_VALUE, LAST_TRUSTED_DAY, CASE_ID, AGENT_GUIDANCE "
                 f"FROM PUB.METRIC_TRUST WHERE TXN_DAY = {D}")
    rows = be.query(trust_sql)
    steps = [trust_sql]
    if not rows:
        answer = f"Revenue for {label} has not been published yet, so I will not quote a number."
        status = "MISSING"
    else:
        r = rows[0]
        status = r["trust_status"]
        if r["trusted_value"] is not None:
            note = {"REAL_CHANGE": " It moved a lot, and Receipts checked it: the change is real.",
                    "CORRECTED": " A data fault was found and the corrected value was approved by a person."}.get(status, "")
            answer = f"Revenue on {label} was {inr(r['trusted_value'])}.{note}"
        else:
            last = to_date(r["last_trusted_day"]) if r["last_trusted_day"] else None
            prev = None
            if last:
                q2 = f"SELECT METRIC_VALUE FROM PUB.DAILY_REVENUE_PUBLISHED WHERE TXN_DAY = {be.dialect.day(last)}"
                steps.append(q2)
                prev = be.scalar(q2)
            cause = be.query(f"SELECT SUSPECT, SLICE_DESC FROM RECEIPTS.EVIDENCE WHERE CASE_ID = '{r['case_id']}' "
                             f"AND OUTCOME = 'CONFIRMED'")
            why = ("The cause is proven: " + "; ".join(f"{DETECTOR_TITLES.get(c['suspect'], c['suspect']).lower()} ({c['slice_desc']})"
                                                      for c in cause) + ".") if cause else \
                "The cause is not proven yet and a person is looking at it."
            answer = (f"I can't give you a reliable number for {label}. The figure in the pipeline is held by data "
                      f"quality case {r['case_id']}. {why}"
                      + (f" The last trusted day, {last:%a %d %b}, was {inr(prev)}." if prev else ""))
    return {"question": question, "naive": naive,
            "trusted": {"sql": "\n".join(steps), "answer": answer, "status": status}}
