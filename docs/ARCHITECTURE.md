# Architecture

## Data flow

```
 LANDING (clean copies)            RAW (what the pipeline reads)          PIPE (views)
 ORDERS, PAYMENTS, MERCHANTS  ->   batch lands here, faults applied  ->   STG_PAYMENTS, STG_ORDERS,
 CATEGORY_MAP, FX_RATES            by SQL in faults.py                    DIM_MERCHANT, DIM_CATEGORY,
                                                                          FX_DAILY -> FCT_REVENUE
                                                                          -> DAILY_REVENUE
                                                                                 |
                                       the gate (gate.py) <-----------------------+
                                             |
            +--------------------------------+--------------------------------+
            |                                |                                |
   RECEIPTS.CASES, EVIDENCE,        PUB.DAILY_REVENUE_PUBLISHED      RECEIPTS_SBX (sandbox)
   STEP_TIMINGS, APPROVALS                   |                        rebuilt per undo test
                                    PUB.METRIC_TRUST  <- agents (MCP)
                                    PUB.DASHBOARD_REVENUE <- dashboards
```

Dashboards and agents read only `PUB`. Only the gate writes `PUB`. On Exasol, `receipts init` creates the user
`AGENT_READER` with `CREATE SESSION` and `SELECT ON SCHEMA PUB` and nothing else; the MCP server logs in as it
(see [`MCP_DEMO.md`](MCP_DEMO.md)). `PUB.CONFIRMED_CAUSES` exposes only the causes the undo test confirmed, so an
agent can say why a value is held without reading `RECEIPTS`.

## The gate, step by step

1. **Read the candidate and trusted history.** Today's value from `PIPE.DAILY_REVENUE`; the last 14 trusted values from `PUB`. Normal range = mean plus or minus the larger of 3 standard deviations or 4%.
2. **Detectors** on the raw incoming batch (`detectors.py`). Each returns evidence (blamed table and column, slice, metrics, the SQL it ran) and a correction (a `SELECT` over one source that removes the suspected fault).

   | Detector | Looks for | Correction used by the undo test |
   |---|---|---|
   | Unit change | median amount per gateway and currency jumps by about 10, 100 or 1000 | divide by the detected factor for that slice |
   | Duplicate rows | repeated payment IDs well above the usual retry rate | keep one row per ID, latest attempt |
   | Join fan-out | dimension keys with more than one row | keep the newest row per key |
   | Stale reference feed | a currency paid today with no rate for today | carry the last rate forward |
   | Clock shift (UDF) | a gateway's time-of-day profile that matches its baseline after a fixed shift | shift that gateway's timestamps back |
   | Unmapped codes | codes in today's orders missing from the mapping table | keep those orders, labelled unmapped |

3. **Lineage** (`lineage.py`). View text from `SYS.EXA_ALL_VIEWS`, parsed with sqlglot. Walks back from `DAILY_REVENUE.REVENUE_INR`, separating columns that feed the value from columns that decide which rows exist and which day they fall on.
4. **Decomposition** (`decompose.py`). One `GROUP BY CUBE` over six dimensions for today and the baseline window: 64 grouping sets, over 11,000 slices.
5. **Reconciliation.** Distinct captured payments in the raw batch against revenue rows, and volume against value. Used to accept a real change.
6. **Undo test** (`undo.py`) per suspect: build `RECEIPTS_SBX` with the corrected source, rebuild all pipeline views there, re-run 15 days. History check: unchanged, restored to published, or altered (rejected).
7. **Evidence gate.** Suspects passing the four rules are candidates. Search combinations, largest first, for the one that puts today back in range with history intact. Those are confirmed. The rest are ruled out with a reason.
8. **Verdict.**

   | Verdict | When | Published as |
   |---|---|---|
   | `NO_INCIDENT` | in range, no candidate | `TRUSTED` |
   | `REAL_CHANGE` | out of range, no candidate, volume moved with value and raw payments reconcile one to one | `REAL_CHANGE` |
   | `PROVEN_FAULT` | a set of confirmed causes brings it back | `HELD` until a person approves, then `CORRECTED` |
   | `UNEXPLAINED` | anything else | `HELD` |

9. **Explain** (`explain.py`), then **write back** everything.

## Why these choices

* **Detectors on the raw batch, not on the metric.** A metric check sees only the net move. On the masked pair (two faults that partly cancel, net +4.0% to +7.9%) a threshold alert held 4 of 5 seeds without naming either cause and stayed silent on the fifth, where the net move (+4.0%) was inside the range; the detectors found both causes on all 5.
* **Undo instead of scoring.** A score says "probably". Undoing the fault and getting the clean number back is a demonstration, and it also yields the corrected value and the fix.
* **History as a check.** A correction that rewrites trusted history is not a fix for today's batch. The fan-out fix is the interesting case: it changes the candidate history back to exactly what was published, which is strong evidence on its own.
* **The LLM last.** It can be wrong without consequence because it only rewords a decision already made.

## Connecting your own metric

Metrics are listed in [`receipts.yaml`](../receipts.yaml): the daily view, its value and day columns, the raw tables, the amount, ID and time columns, and the weekday baseline option. `receipts connect --check` validates the file against the database, and the gate's band, baseline, lineage, undo test and blast radius follow it (see [`docs/RUN_GUIDE.md`](RUN_GUIDE.md#9-point-it-at-your-own-metric)). The detectors, the CUBE dimensions, the undo corrections and the fault scenarios still name the marketplace tables and columns directly, so a metric over a different raw layout gets the band and lineage but no cause from the detectors.

What a company would need to provide, and what each part maps to in the code:

| What to provide | Example | Used by |
|---|---|---|
| The view that holds the metric, one row per day | `PIPE.DAILY_REVENUE` (`TXN_DAY`, `REVENUE_INR`, `TXN_COUNT`) | the gate's candidate and baseline, `PUB.DAILY_REVENUE_PUBLISHED` |
| The chain of views from raw tables to that view | the six views in `pipeline.sql` | lineage from the catalog, and the undo test, which re-renders the chain in a sandbox schema with one source swapped |
| The raw tables feeding it, landed per batch | `RAW.ORDERS`, `RAW.PAYMENTS` with a `BATCH_DAY` column | the detectors and the watcher's "has a new batch landed" query |
| Which column is the amount | `PAYMENTS.AMOUNT` | unit check, CUBE, reconciliation |
| Which column is the record ID | `PAYMENTS.PAYMENT_ID` | duplicate check, reconciliation |
| Which column is the event timestamp, and its time zone | `PAYMENTS.CAPTURED_AT`, UTC | clock check (the in-database UDF), day boundary |
| The slicing dimensions | city, category, channel, gateway, currency, tier | the `GROUP BY CUBE` decomposition |
| Reference tables that can go stale or fan out | `MERCHANTS`, `CATEGORY_MAP`, `FX_RATES` | stale feed, join fan-out and new-code checks |

The real-data backtest ([`samples/real_backtest.md`](../samples/real_backtest.md)) shows what connecting a new source takes today: a thin adapter in [`receipts/backtest.py`](../receipts/backtest.py) maps NYC taxi trips onto these same tables (vendor as gateway, borough as city, rate code as category, and so on), and the unchanged engine runs on them. Turning that mapping into configuration, instead of an adapter per source, is the next step and is not done.
