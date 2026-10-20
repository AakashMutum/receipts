# Instructions for any AI agent reading business metrics from this database

Paste this into the agent's system prompt or project instructions. It works with
any agent that reaches Exasol through the official Exasol MCP server.

---

Before you quote any business metric, check whether it can be trusted.

1. Query `PUB.METRIC_TRUST` for the metric and day you are about to report:

   ```sql
   SELECT TRUST_STATUS, TRUSTED_VALUE, LAST_TRUSTED_DAY, CASE_ID, AGENT_GUIDANCE
   FROM PUB.METRIC_TRUST
   WHERE METRIC_NAME = 'daily_revenue_inr' AND TXN_DAY = DATE '2026-10-20';
   ```

2. If `TRUSTED_VALUE` is not null, report it. If `TRUST_STATUS` is `REAL_CHANGE`
   or `CORRECTED`, say so in one short clause.
3. If `TRUSTED_VALUE` is null, do not report the pipeline's number. Follow
   `AGENT_GUIDANCE`: say the value is held, name the case, and give the last
   trusted day's value from `PUB.DAILY_REVENUE_PUBLISHED`.
4. To explain why a value is held, read `RECEIPTS.EVIDENCE` for that `CASE_ID`
   where `OUTCOME = 'CONFIRMED'`. Never offer a cause that is not confirmed there.
5. Never read `PIPE.*` or `RAW.*` to answer a business question.
