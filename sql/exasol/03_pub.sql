-- What people and agents read. Dashboards never read PIPE directly.

CREATE OR REPLACE VIEW PUB.METRIC_TRUST AS
SELECT
  'daily_revenue_inr' AS METRIC_NAME,
  p.TXN_DAY,
  p.TRUST_STATUS,
  CASE WHEN p.TRUST_STATUS IN ('TRUSTED', 'REAL_CHANGE', 'CORRECTED') THEN p.METRIC_VALUE END AS TRUSTED_VALUE,
  p.CANDIDATE_VALUE,
  l.LAST_TRUSTED_DAY,
  p.CASE_ID,
  CASE
    WHEN p.TRUST_STATUS = 'TRUSTED' THEN 'Safe to use.'
    WHEN p.TRUST_STATUS = 'REAL_CHANGE' THEN 'Safe to use. The change was investigated and no data fault was found.'
    WHEN p.TRUST_STATUS = 'CORRECTED' THEN 'Safe to use. A proven fault was corrected and approved by a person.'
    ELSE 'Do not use. This value is held by Receipts case ' || p.CASE_ID || '. Quote the last trusted day instead and say the latest value is under investigation.'
  END AS AGENT_GUIDANCE,
  p.PUBLISHED_AT,
  -- blast radius: views that read the pipeline directly, so they showed the candidate value
  COALESCE(c.DOWNSTREAM_COUNT, 0) AS DOWNSTREAM_COUNT,
  c.DOWNSTREAM_OBJECTS
FROM PUB.DAILY_REVENUE_PUBLISHED p
LEFT JOIN RECEIPTS.CASES c ON c.CASE_ID = p.CASE_ID
JOIN (
  -- Exasol rejects a correlated subquery with "<", so the latest trusted earlier day comes from a join.
  SELECT a.TXN_DAY, MAX(b.TXN_DAY) AS LAST_TRUSTED_DAY
  FROM PUB.DAILY_REVENUE_PUBLISHED a
  LEFT JOIN PUB.DAILY_REVENUE_PUBLISHED b
    ON b.TXN_DAY < a.TXN_DAY AND b.TRUST_STATUS IN ('TRUSTED', 'REAL_CHANGE', 'CORRECTED')
  GROUP BY a.TXN_DAY
) l ON l.TXN_DAY = p.TXN_DAY;

CREATE OR REPLACE VIEW PUB.DASHBOARD_REVENUE AS
SELECT
  t.TXN_DAY,
  COALESCE(t.TRUSTED_VALUE, l.METRIC_VALUE) AS SHOWN_VALUE,
  CASE WHEN t.TRUSTED_VALUE IS NULL THEN TRUE ELSE FALSE END AS IS_HELD,
  t.TRUST_STATUS,
  t.CASE_ID
FROM PUB.METRIC_TRUST t
LEFT JOIN PUB.DAILY_REVENUE_PUBLISHED l ON l.TXN_DAY = t.LAST_TRUSTED_DAY;

-- Why a value is held, without exposing RECEIPTS itself: only causes the undo test confirmed.
CREATE OR REPLACE VIEW PUB.CONFIRMED_CAUSES AS
SELECT
  e.CASE_ID,
  e.SUSPECT,
  e.BLAMED_TABLE,
  e.BLAMED_COLUMN,
  e.SLICE_DESC,
  e.REASON
FROM RECEIPTS.EVIDENCE e
WHERE e.OUTCOME = 'CONFIRMED';
-- Reports built on top of the pipeline, the way analysts and BI tools add them over time.
-- Receipts does not need them; they are here so the blast radius has real readers to find.
-- Two read the pipeline directly and so show tonight's number before the gate decides;
-- one reads PUB and so shows only what the gate published; one does not depend on revenue.

CREATE OR REPLACE VIEW MART.FINANCE_DAILY AS
SELECT
  d.TXN_DAY,
  d.REVENUE_INR,
  d.TXN_COUNT
FROM PIPE.DAILY_REVENUE d;

CREATE OR REPLACE VIEW MART.AVG_TICKET AS
SELECT
  f.TXN_DAY,
  f.REVENUE_INR / NULLIF(f.TXN_COUNT, 0) AS AVG_TICKET_INR
FROM MART.FINANCE_DAILY f;

CREATE OR REPLACE VIEW MART.CITY_REVENUE AS
SELECT
  r.TXN_DAY,
  r.CITY,
  SUM(r.REVENUE_INR) AS REVENUE_INR
FROM PIPE.FCT_REVENUE r
GROUP BY r.TXN_DAY, r.CITY;

CREATE OR REPLACE VIEW MART.EXEC_SUMMARY AS
SELECT
  b.TXN_DAY,
  b.SHOWN_VALUE,
  b.IS_HELD
FROM PUB.DASHBOARD_REVENUE b;

CREATE OR REPLACE VIEW MART.CATEGORY_LIST AS
SELECT
  c.CATEGORY_CODE,
  c.CATEGORY_NAME
FROM PIPE.DIM_CATEGORY c;