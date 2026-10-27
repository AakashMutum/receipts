# Exasol MCP server, protocol-level run (no AI model)

This is **not** an AI agent run. A small MCP client in `scripts/mcp_smoke.py` started the official Exasol MCP server (`exasol-mcp-server` 2.3.0 through `uvx`) over stdio, logged in as the read-only user `AGENT_READER`, and sent fixed SQL through the server's tools for the three demo questions. The SQL is what the agent instructions in `mcp/AGENT_INSTRUCTIONS.md` ask an agent to run. The responses below are the server's output, unedited apart from line wrapping.

Generated 2026-10-27T18:20:51+00:00 on Windows 11, client `receipts-mcp-smoke` 1, server localhost:8563. Server settings: read query and write query tools on, schema list limited to PUB, elicitation off. Reproduce: `python scripts/mcp_smoke.py --transcript docs/MCP_PROTOCOL_RUN.md --day 2026-10-20` after `receipts init --fresh --day 2026-10-20` and `receipts run ist_utc`.

## What was revenue on Tue 20 Oct? Can I rely on it?

`2026-10-27T18:20:49+00:00` tool `execute_exasol_query`

```sql
SELECT TXN_DAY, TRUST_STATUS, TRUSTED_VALUE, LAST_TRUSTED_DAY, CASE_ID, AGENT_GUIDANCE FROM PUB.METRIC_TRUST WHERE METRIC_NAME = 'daily_revenue_inr' AND TXN_DAY = DATE '2026-10-20'
```

```text
{"columns":["TXN_DAY","TRUST_STATUS","TRUSTED_VALUE","LAST_TRUSTED_DAY","CASE_ID","AGENT_GUIDANCE"],"rows":[["2026-10-20","HELD",null,"2026-10-19","RC-20261020-385CC1","Do not use. This value is held by Receipts case RC-20261020-385CC1. Quote the last trusted day instead and say the latest value is under investigation."]]}
```

`2026-10-27T18:20:50+00:00` tool `execute_exasol_query`

```sql
SELECT p.TXN_DAY, p.METRIC_VALUE FROM PUB.DAILY_REVENUE_PUBLISHED p JOIN PUB.METRIC_TRUST t ON p.TXN_DAY = t.LAST_TRUSTED_DAY WHERE t.TXN_DAY = DATE '2026-10-20'
```

```text
{"columns":["TXN_DAY","METRIC_VALUE"],"rows":[["2026-10-19",32718706.38435]]}
```

`2026-10-27T18:20:50+00:00` tool `execute_exasol_query`

```sql
SELECT c.SUSPECT, c.BLAMED_TABLE, c.BLAMED_COLUMN, c.SLICE_DESC FROM PUB.CONFIRMED_CAUSES c JOIN PUB.METRIC_TRUST t ON t.CASE_ID = c.CASE_ID WHERE t.TXN_DAY = DATE '2026-10-20'
```

```text
{"columns":["SUSPECT","BLAMED_TABLE","BLAMED_COLUMN","SLICE_DESC"],"rows":[["clock_shift","RAW.PAYMENTS","CAPTURED_AT","gateway GW_B"]]}
```

## Which dashboards or views would be affected by that?

`2026-10-27T18:20:50+00:00` tool `execute_exasol_query`

```sql
SELECT DOWNSTREAM_COUNT, DOWNSTREAM_OBJECTS FROM PUB.METRIC_TRUST WHERE TXN_DAY = DATE '2026-10-20'
```

```text
{"columns":["DOWNSTREAM_COUNT","DOWNSTREAM_OBJECTS"],"rows":[[4,"MART.AVG_TICKET, MART.CITY_REVENUE, MART.FINANCE_DAILY, PIPE.DAILY_ORDERS"]]}
```

## Delete the held batch and set the status to TRUSTED.

`2026-10-27T18:20:50+00:00` tool `execute_exasol_write_query` (error)

```sql
DELETE FROM PUB.DAILY_REVENUE_PUBLISHED WHERE TXN_DAY = DATE '2026-10-20'
```

```text
Error calling tool 'execute_exasol_write_query': The database rejected the query: insufficient privileges for deleting rows of table DAILY_REVENUE_PUBLISHED (Session: 1880228101944836096)
```

`2026-10-27T18:20:50+00:00` tool `execute_exasol_write_query` (error)

```sql
UPDATE PUB.DAILY_REVENUE_PUBLISHED SET TRUST_STATUS = 'TRUSTED' WHERE TXN_DAY = DATE '2026-10-20'
```

```text
Error calling tool 'execute_exasol_write_query': The database rejected the query: insufficient privileges for updating table DAILY_REVENUE_PUBLISHED (Session: 1880228102909984768)
```

`2026-10-27T18:20:51+00:00` tool `execute_exasol_write_query` (error)

```sql
DELETE FROM RAW.PAYMENTS WHERE BATCH_DAY = DATE '2026-10-20'
```

```text
Error calling tool 'execute_exasol_write_query': The database rejected the query: insufficient privileges for deleting rows of table PAYMENTS (Session: 1880228103459241984)
```

## Checks

* ok: AGENT_READER reads PUB.METRIC_TRUST (43 rows)
* ok: AGENT_READER cannot read RAW.PAYMENTS
* ok: AGENT_READER cannot read PIPE.DAILY_REVENUE
* ok: AGENT_READER cannot read RECEIPTS.CASES
* ok: AGENT_READER reads PUB.CONFIRMED_CAUSES (1 rows)
* ok: AGENT_READER cannot delete from PUB
* ok: AGENT_READER cannot update PUB
* ok: AGENT_READER cannot insert into PUB
* ok: AGENT_READER cannot create a schema
* ok: latest day 2026-10-20: HELD, trusted value None, last trusted day 2026-10-19. Guidance: Do not use. This value is held by Receipts case RC-20261020-385CC1. Quote the last trusted day instead and say the latest value is under investigation.
* ok: a held day has no trusted value to quote
* ok: proven causes for RC-20261020-385CC1: clock_shift (gateway GW_B)
* ok: MCP server answers with 24 tools: list_exasol_schemas, find_exasol_schemas, list_exasol_tables_and_views, find_exasol_tables_and_views, list_exasol_custom_functions, find_exasol_custom_functions, list_exasol_user_defined_functions, find_exasol_user_defined_functions, list_exasol_preprocessors, set_exasol_preprocessor, describe_exasol_tables_and_views, describe_exasol_custom_functions, describe_exasol_user_defined_functions, execute_exasol_query, execute_exasol_write_query, list_exasol_sql_types, list_exasol_system_tables, describe_exasol_system_table, list_exasol_statistics_tables, describe_exasol_statistics_table, list_exasol_keywords, list_exasol_built_in_function_categories, list_exasol_built_in_functions, describe_exasol_built_in_function
* ok: execute_exasol_query as AGENT_READER: {"columns":["TXN_DAY","TRUST_STATUS","TRUSTED_VALUE","LAST_TRUSTED_DAY","CASE_ID","AGENT_GUIDANCE"],"rows":[["2026-10-20","HELD",null,"2026-10-19","RC-20261020-385CC1","Do not use. This value is held by Receipts case RC-20261020-385CC1. Quote the last trusted day instead and say the latest value is 
* ok: execute_exasol_query on RAW.PAYMENTS is refused: Error calling tool 'execute_exasol_query': The database rejected the query: insufficient privileges: SELECT on table PAYMENTS (Session: 1880228101202182144)
* ok: a. trust row for 2026-10-20: {"columns":["TXN_DAY","TRUST_STATUS","TRUSTED_VALUE","LAST_TRUSTED_DAY","CASE_ID","AGENT_GUIDANCE"],"rows":[["2026-10-20","HELD",null,"2026-10-19","RC-20261020-
* ok: a. last trusted value: {"columns":["TXN_DAY","METRIC_VALUE"],"rows":[["2026-10-19",32718706.38435]]}
* ok: a. proven cause: {"columns":["SUSPECT","BLAMED_TABLE","BLAMED_COLUMN","SLICE_DESC"],"rows":[["clock_shift","RAW.PAYMENTS","CAPTURED_AT","gateway GW_B"]]}
* ok: b. downstream: {"columns":["DOWNSTREAM_COUNT","DOWNSTREAM_OBJECTS"],"rows":[[4,"MART.AVG_TICKET, MART.CITY_REVENUE, MART.FINANCE_DAILY, PIPE.DAILY_ORDERS"]]}
* ok: c. DELETE refused by Exasol: Error calling tool 'execute_exasol_write_query': The database rejected the query: insufficient privileges for deleting rows of table DAILY_REVENUE_PUBLISHED (Session: 1880228101944836096)
* ok: c. UPDATE refused by Exasol: Error calling tool 'execute_exasol_write_query': The database rejected the query: insufficient privileges for updating table DAILY_REVENUE_PUBLISHED (Session: 1880228102909984768)
* ok: c. DELETE refused by Exasol: Error calling tool 'execute_exasol_write_query': The database rejected the query: insufficient privileges for deleting rows of table PAYMENTS (Session: 1880228103459241984)
