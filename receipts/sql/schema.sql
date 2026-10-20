-- Receipts storage layout
--   LANDING   clean copies of every source, as delivered by upstream teams
--   RAW       what the pipeline actually reads (faults are injected here)
--   PIPE      the revenue pipeline, a chain of views
--   PUB       what dashboards and AI agents are allowed to read
--   RECEIPTS  cases, evidence and timings written back by the gate
{% for s in ['LANDING', 'RAW', 'PIPE', 'PUB', 'RECEIPTS'] %}
DROP SCHEMA IF EXISTS {{ s }} CASCADE;
CREATE SCHEMA {{ s }};
{% endfor %}

{% for name, cols in tables.items() %}
CREATE TABLE LANDING.{{ name }} (
{% for c, t in cols %}
  {{ c }} {{ t }}{{ "," if not loop.last }}
{% endfor %}
);
CREATE TABLE RAW.{{ name }} (
{% for c, t in cols %}
  {{ c }} {{ t }}{{ "," if not loop.last }}
{% endfor %}
);
{% endfor %}

{% for name, like in festival.items() %}
CREATE TABLE LANDING.{{ name }} (
{% for c, t in tables[like] %}
  {{ c }} {{ t }}{{ "," if not loop.last }}
{% endfor %}
);
{% endfor %}

CREATE TABLE PUB.DAILY_REVENUE_PUBLISHED (
  TXN_DAY DATE,
  METRIC_VALUE DOUBLE,
  CANDIDATE_VALUE DOUBLE,
  TRUST_STATUS VARCHAR(20),
  CASE_ID VARCHAR(40),
  PUBLISHED_AT TIMESTAMP
);

CREATE TABLE RECEIPTS.CASES (
  CASE_ID VARCHAR(40),
  METRIC_NAME VARCHAR(40),
  TXN_DAY DATE,
  OPENED_AT TIMESTAMP,
  VERDICT VARCHAR(20),
  CANDIDATE_VALUE DOUBLE,
  BASELINE_VALUE DOUBLE,
  CORRECTED_VALUE DOUBLE,
  SCENARIO VARCHAR(40),
  ELAPSED_MS DOUBLE,
  SUMMARY VARCHAR(2000),
  CASE_JSON VARCHAR(2000000)
);

CREATE TABLE RECEIPTS.EVIDENCE (
  CASE_ID VARCHAR(40),
  SUSPECT VARCHAR(30),
  DETECTOR_FIRED BOOLEAN,
  OUTCOME VARCHAR(12),
  BLAMED_TABLE VARCHAR(40),
  BLAMED_COLUMN VARCHAR(40),
  SLICE_DESC VARCHAR(200),
  UNDO_VALUE DOUBLE,
  EXPLAINED_PCT DOUBLE,
  HISTORY_CHECK VARCHAR(20),
  REASON VARCHAR(600)
);

CREATE TABLE RECEIPTS.STEP_TIMINGS (
  CASE_ID VARCHAR(40),
  STEP_NAME VARCHAR(40),
  ELAPSED_MS DOUBLE,
  ROWS_IN_SCOPE BIGINT
);

CREATE TABLE RECEIPTS.APPROVALS (
  CASE_ID VARCHAR(40),
  APPROVED_AT TIMESTAMP,
  APPROVED_VALUE DOUBLE,
  NOTE VARCHAR(400)
);
