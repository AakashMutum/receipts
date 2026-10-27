# Live checks on Exasol

Exasol 2026.2.0-nano.3, demo data, batch day 2026-10-26. Generated 2026-10-27 21:41:44 in 20 s. Reproduce: `receipts init --fresh` then `python scripts/live_checks.py` with `RECEIPTS_BACKEND=exasol`.

| Check | Result | Detail |
|---|---|---|
| Verdict, IST case | pass | PROVEN_FAULT, clock_shift |
| Blast radius from SYS.EXA_ALL_VIEWS | pass | 4 exposed: MART.AVG_TICKET, MART.CITY_REVENUE, MART.FINANCE_DAILY, PIPE.DAILY_ORDERS; protected: MART.EXEC_SUMMARY, PUB.DASHBOARD_REVENUE, PUB.METRIC_TRUST; 16 views read |
| Audit log: read during the bad window | pass | from EXA_DBA_AUDIT_SQL since the previous publish; SYS (1 reads) |
| PUB.METRIC_TRUST DOWNSTREAM_COUNT and DOWNSTREAM_OBJECTS | pass | 4: MART.AVG_TICKET, MART.CITY_REVENUE, MART.FINANCE_DAILY, PIPE.DAILY_ORDERS |
| RECEIPTS.METRIC_HISTORY snapshot | pass | avg_basket_inr 42 days, daily_order_count 42 days |
| receipts connect --check (SYS.EXA_ALL_COLUMNS) | pass | 27 checks, 0 problems |
| daily_order_count through the gate (PIPE.DAILY_ORDERS) | pass | PROVEN_FAULT, HELD, clock_shift, change -19.1% |
| avg_basket_inr through the gate (PIPE.DAILY_ORDERS) | pass | NO_INCIDENT, TRUSTED, no cause, change -0.1% |
| Badge after the hold | pass | HELD, last trusted 2026-10-25 |
| Badge after approval | pass | CORRECTED, last trusted 2026-10-26 |
