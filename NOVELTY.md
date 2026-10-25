# What is new in Receipts, and what is not

**Claim:** Receipts does not stop at flagging that a number moved; it names a cause only after undoing that cause in a sandbox copy of the pipeline brings the number back into its normal range without changing published history, and until then it holds the number and tells people and agents not to trust it.

## What is new

* **Proof by undoing the cause.** Each suspect from a detector comes with a correction. Receipts rebuilds the whole pipeline in a sandbox schema with that one source corrected, re-runs the metric and checks the result. A detector that fires is only a suspect; on the festival control the duplicate check fires on payment retries, undoing it changes nothing, and the day is published as a real change. Code: [`receipts/undo.py`](receipts/undo.py), [`receipts/gate.py`](receipts/gate.py).
* **The four rules for confirming a cause.** The evidence names a specific column and slice; lineage says that column feeds this metric; undoing it moves today's number by at least 1.5%; history stays exactly as published, or comes back to exactly what was published. Without the undo test the scored evaluation names 5 wrong causes; with it, 0 ([`samples/exasol/eval_report.md`](samples/exasol/eval_report.md)).
* **Red team detection floors.** `receipts redteam` shrinks each fault until the gate stops proving it and reports the smallest share still proven, what happens below it, and any way to get a wrong number published. The first run found a hole, which was fixed and re-run with held-out cases frozen beforehand ([`samples/exasol/redteam_report_before.md`](samples/exasol/redteam_report_before.md), [`redteam_report.md`](samples/exasol/redteam_report.md)).
* **Lineage read from Exasol's own catalog.** Which source columns feed the metric is parsed from the view text in `SYS.EXA_ALL_VIEWS`, not from a separate lineage tool ([`receipts/lineage.py`](receipts/lineage.py)).
* **A trust flag for agents through a read-only user.** `PUB.METRIC_TRUST` says, per day, whether the number may be quoted and what to quote instead. The Exasol MCP server logs in as `AGENT_READER`, which can read `PUB` and nothing else ([`docs/MCP_DEMO.md`](docs/MCP_DEMO.md)). The MCP server itself was not tested end to end.

## What is not new

* **The detectors.** Unit changes, duplicate keys, join fan-out, stale feeds, clock shifts and unmapped codes are well-known data quality checks. Receipts uses them only to nominate suspects.
* **`GROUP BY CUBE`** and slice-based breakdowns of a metric change are standard SQL and standard analysis.
* **Statistical bands.** The normal range is a baseline with a weekday pattern and a band around it; nothing new there.
* **Vendor features.** Python UDFs, the statistics tables, users and grants, `IMPORT` and the MCP server are Exasol features; Receipts uses them as they are.

## How Receipts relates to existing tools

The comparison below is based on the vendors' public pages as read in October 2026. It is a summary of what those pages describe, not a test of the products. A blank or an omission is not proof that a feature is missing.

| Tool | What its public pages describe | How Receipts relates |
|---|---|---|
| Great Expectations | Declarative tests (expectations) on data, run in pipelines | Receipts also checks data, but its output is a hold-or-publish decision with a proven cause, not a pass or fail per test |
| Soda | Data quality checks written in a check language, with monitoring and alerts | Same relation as above: Receipts goes from "a check fired" to "undoing this fault restores the number" |
| Elementary | Data observability built around dbt: test results, anomaly monitors, lineage | Receipts reads lineage from the database catalog and acts on one metric's publication |
| Datafold | Data diffing, comparing tables or the results of a code change before deployment | The undo test is also a comparison, but of today's metric with one suspect corrected, at run time rather than at deploy time |
| Anomalo | Automated detection of anomalies in table data, with root-cause hints | Receipts treats a hint as a suspect and confirms it only through the undo test and the four rules |
| Monte Carlo | Data observability: monitoring, troubleshooting agents, root cause analysis and lineage | Receipts adds a gate that keeps the number off the dashboard until the cause is proven, and a trust flag that agents read |

Receipts is a narrow prototype: one metric, one pipeline, six fault classes. These tools cover many tables and sources; the comparison is about the idea, not about coverage.
