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
