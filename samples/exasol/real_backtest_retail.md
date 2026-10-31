# Real-data backtest: UCI Online Retail II with ECB rates

Dataset: **UCI Online Retail II (CC BY 4.0) with ECB euro reference rates**, from the UCI Machine Learning Repository and the European Central Bank, no login needed.

* https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip
* https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip

Captured invoices from 2009-12-01 to 2011-12-08: 40,032. The metric is the daily invoice total in rupees by UK invoice date. The first 35 days (2009-12-01 to 2010-01-04) are published as trusted history by assumption; the gate then judges 703 days, 2010-01-05 to 2011-12-08, one night at a time, on Exasol 2026.2.0-nano.3 (Python UDF: in-database). No threshold was changed for this data. How invoices map onto the pipeline tables is described in `scripts/backtest_retail.py`.

Reproduce: `python scripts/backtest_retail.py --backend exasol` (needs the two source files in the data folder, see the script; runs in about 26 minutes).

## Sources, licences and what was changed

* **UCI Online Retail II**, Chen, D. (2012), UCI Machine Learning Repository, https://doi.org/10.24432/C5CG6D. The dataset page states: "This dataset is licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license." All transactions of a UK-based online retailer, 1 Dec 2009 to 9 Dec 2011, prices in pounds sterling.
* **Euro foreign exchange reference rates**, source: European Central Bank (ecb.europa.eu, eurofxref-hist.zip). The ECB page states: "The reference rates are published for information purposes only." Its disclaimer and copyright page sets the terms of reuse.
* **These are UK retail sales converted to rupees for the test. They are not Indian transaction data.**
* Changes made: invoice lines summed to invoice totals; GBP converted to INR with the ECB cross rate (INR per EUR divided by GBP per EUR); a rate for every calendar day, with the last published rate carried forward over weekends and TARGET closing days; cancellations (`C` invoices), bad-debt adjustments (`A`) and totals of zero or less not counted as revenue; the 22,523 rows that appear in both workbook sheets (1 to 9 December 2010) kept once; 9 December 2011 not judged because the file ends at 12:50 that day. The mapping onto the pipeline tables is in [`scripts/backtest_retail.py`](../../scripts/backtest_retail.py).

Files used (not committed):

| File | Bytes | SHA-256 | Source |
|---|---|---|---|
| online_retail_ii.zip | 45,622,418 | `572e36277c2390fbfde10664750731e0a86f55e33470d91919085f0408e67bfb` | https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip |
| eurofxref-hist.zip | 642,255 | `73db21584dd46cebf5cd6df75ebb6de7afcdeebff52f54d5046ca8e459c0fbb3` | https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip |

## Detectors that do not apply

* `clock_shift`: the detector looks for one gateway's times written in UTC instead of IST; the shop records UK local time and has no gateways, so a planted shift would test the adapter, not a real failure.
* `key_fanout`: the merchant table is made by the adapter (one row per country), not a real reference table.
* `orphan_code`: the category codes are made by the adapter (GOODS and SERVICE), not a real code list.

## In short

* Real days held: **64 of 703**. Of these, 13 had no captured invoice at all (change -100%), and 50 were more than 40% above the expected value. A wholesale shop's daily total swings far more than the synthetic data: the median normal range here is wide (see below), and the gate still holds a day it cannot explain.
* Planted faults caught with the right cause: **5 of 9**. Missed, by name: 2010-04-14 Payment file F05 loaded twice (NO_INCIDENT, PUBLISHED, real error +11.5%); 2010-10-13 UK prices in pence (x100) (UNEXPLAINED, held, real error +6870.1%); 2010-11-10 Payment file F05 loaded twice (UNEXPLAINED, held, real error +3.2%); 2011-06-15 Payment file F05 loaded twice (NO_INCIDENT, PUBLISHED, real error +3.1%).
* Saturdays: the shop never trades on Saturdays, so the Saturday weekday index is 0. The first run on the stand-in stopped on 2010-01-24 with a division by zero in the weekday baseline. The fix (a weekday whose index is 0 expects 0, and anything else on it is held as UNEXPLAINED) is its own commit, and the run was started again from the first day. The second start stopped on 2010-02-06 in this report's row helper (the band as a percent of an expected 0); the band of such a day is reported as 0%, and the run was started again from the first day. Every number below is from the complete run.

## Every held real day

* 2010-01-26 Tue: UNEXPLAINED, change +55.3%, fired unit_scale:REJECTED
* 2010-02-25 Thu: UNEXPLAINED, change +86.4%, fired nothing
* 2010-03-19 Fri: UNEXPLAINED, change +115.0%, fired nothing
* 2010-03-23 Tue: UNEXPLAINED, change +118.2%, fired nothing
* 2010-03-29 Mon: UNEXPLAINED, change +104.1%, fired nothing
* 2010-03-30 Tue: UNEXPLAINED, change +59.5%, fired nothing
* 2010-04-02 Fri: UNEXPLAINED, change -100.0%, fired nothing
* 2010-04-04 Sun: UNEXPLAINED, change -100.0%, fired nothing
* 2010-04-05 Mon: UNEXPLAINED, change -100.0%, fired nothing
* 2010-04-19 Mon: UNEXPLAINED, change +68.3%, fired nothing
* 2010-05-31 Mon: UNEXPLAINED, change -100.0%, fired nothing
* 2010-06-07 Mon: UNEXPLAINED, change +115.1%, fired nothing
* 2010-06-08 Tue: UNEXPLAINED, change +130.5%, fired nothing
* 2010-06-17 Thu: UNEXPLAINED, change +102.7%, fired nothing
* 2010-06-28 Mon: UNEXPLAINED, change +103.8%, fired nothing
* 2010-07-15 Thu: UNEXPLAINED, change +142.7%, fired nothing
* 2010-08-01 Sun: UNEXPLAINED, change +124.4%, fired nothing
* 2010-08-18 Wed: UNEXPLAINED, change +62.5%, fired nothing
* 2010-08-30 Mon: UNEXPLAINED, change -100.0%, fired nothing
* 2010-09-21 Tue: UNEXPLAINED, change +116.7%, fired nothing
* 2010-09-24 Fri: UNEXPLAINED, change +107.8%, fired nothing
* 2010-09-27 Mon: UNEXPLAINED, change +256.2%, fired nothing
* 2010-10-03 Sun: UNEXPLAINED, change +117.5%, fired nothing
* 2010-10-05 Tue: UNEXPLAINED, change +155.9%, fired nothing
* 2010-10-08 Fri: UNEXPLAINED, change +107.3%, fired nothing
* 2010-10-13 Wed: UNEXPLAINED, change +87.4%, fired nothing
* 2010-10-14 Thu: UNEXPLAINED, change +108.2%, fired nothing
* 2010-10-15 Fri: UNEXPLAINED, change +111.1%, fired nothing
* 2010-11-04 Thu: UNEXPLAINED, change +103.7%, fired nothing
* 2010-11-08 Mon: UNEXPLAINED, change +151.4%, fired nothing
* 2010-11-10 Wed: UNEXPLAINED, change +108.7%, fired nothing
* 2010-11-11 Thu: UNEXPLAINED, change +53.2%, fired nothing
* 2010-11-15 Mon: UNEXPLAINED, change +227.2%, fired nothing
* 2010-11-24 Wed: UNEXPLAINED, change +43.2%, fired nothing
* 2010-11-25 Thu: UNEXPLAINED, change +84.7%, fired nothing
* 2010-12-22 Wed: UNEXPLAINED, change -87.0%, fired nothing
* 2010-12-24 Fri: UNEXPLAINED, change -100.0%, fired nothing
* 2011-01-11 Tue: UNEXPLAINED, change +506.4%, fired nothing
* 2011-01-18 Tue: UNEXPLAINED, change +378.7%, fired nothing
* 2011-03-20 Sun: UNEXPLAINED, change +183.0%, fired nothing
* 2011-03-29 Tue: UNEXPLAINED, change +148.9%, fired nothing
* 2011-04-17 Sun: UNEXPLAINED, change +69.7%, fired nothing
* 2011-04-18 Mon: UNEXPLAINED, change +130.4%, fired nothing
* 2011-04-22 Fri: UNEXPLAINED, change -100.0%, fired nothing
* 2011-04-24 Sun: UNEXPLAINED, change -100.0%, fired nothing
* 2011-04-25 Mon: UNEXPLAINED, change -100.0%, fired nothing
* 2011-04-29 Fri: UNEXPLAINED, change -100.0%, fired nothing
* 2011-05-02 Mon: UNEXPLAINED, change -100.0%, fired nothing
* 2011-05-30 Mon: UNEXPLAINED, change -100.0%, fired nothing
* 2011-06-10 Fri: UNEXPLAINED, change +122.4%, fired nothing
* 2011-07-24 Sun: UNEXPLAINED, change +131.8%, fired nothing
* 2011-07-31 Sun: UNEXPLAINED, change +271.3%, fired nothing
* 2011-08-17 Wed: UNEXPLAINED, change +100.2%, fired nothing
* 2011-08-24 Wed: UNEXPLAINED, change +76.9%, fired nothing
* 2011-08-29 Mon: UNEXPLAINED, change -100.0%, fired nothing
* 2011-09-02 Fri: UNEXPLAINED, change +103.5%, fired nothing
* 2011-09-04 Sun: UNEXPLAINED, change +76.1%, fired nothing
* 2011-09-11 Sun: UNEXPLAINED, change +265.4%, fired nothing
* 2011-09-13 Tue: UNEXPLAINED, change +109.1%, fired nothing
* 2011-09-20 Tue: UNEXPLAINED, change +320.6%, fired nothing
* 2011-09-25 Sun: UNEXPLAINED, change +131.9%, fired nothing
* 2011-10-30 Sun: UNEXPLAINED, change +139.8%, fired nothing
* 2011-11-06 Sun: UNEXPLAINED, change +197.9%, fired nothing
* 2011-11-13 Sun: UNEXPLAINED, change +124.2%, fired nothing

## Real days, no faults planted

* Days judged: **703**
* Held: **64**
* Verdicts: NO_INCIDENT 638, REAL_CHANGE 1, UNEXPLAINED 64
* Days where the weekday-aware baseline was used: 535 of 703
* Normal range around the expected value: median plus or minus 83.2%, from 0.0% to 602.3%
* Real days called PROVEN_FAULT: **0**
* Detector firings on real days that the undo test ruled out: 1 (unit_scale on 2010-01-26 Tue)

Held days (no fault was planted, so each is either a false hold or a real change the volume check did not accept):

| Day | Revenue | Expected | Change | Verdict | Detectors that fired |
|---|---|---|---|---|---|
| 2010-01-26 Tue | $3.51M | $2.26M | +55.3% | UNEXPLAINED | unit_scale:REJECTED |
| 2010-02-25 Thu | $3.31M | $1.78M | +86.4% | UNEXPLAINED | - |
| 2010-03-19 Fri | $3.15M | $1.47M | +115.0% | UNEXPLAINED | - |
| 2010-03-23 Tue | $3.86M | $1.77M | +118.2% | UNEXPLAINED | - |
| 2010-03-29 Mon | $4.03M | $1.98M | +104.1% | UNEXPLAINED | - |
| 2010-03-30 Tue | $2.63M | $1.65M | +59.5% | UNEXPLAINED | - |
| 2010-04-02 Fri | $0.00M | $1.69M | -100.0% | UNEXPLAINED | - |
| 2010-04-04 Sun | $0.00M | $1.23M | -100.0% | UNEXPLAINED | - |
| 2010-04-05 Mon | $0.00M | $2.00M | -100.0% | UNEXPLAINED | - |
| 2010-04-19 Mon | $3.09M | $1.84M | +68.3% | UNEXPLAINED | - |
| 2010-05-31 Mon | $0.00M | $1.76M | -100.0% | UNEXPLAINED | - |
| 2010-06-07 Mon | $3.40M | $1.58M | +115.1% | UNEXPLAINED | - |
| 2010-06-08 Tue | $3.69M | $1.60M | +130.5% | UNEXPLAINED | - |
| 2010-06-17 Thu | $3.99M | $1.97M | +102.7% | UNEXPLAINED | - |
| 2010-06-28 Mon | $3.75M | $1.84M | +103.8% | UNEXPLAINED | - |
| 2010-07-15 Thu | $4.05M | $1.67M | +142.7% | UNEXPLAINED | - |
| 2010-08-01 Sun | $2.22M | $0.99M | +124.4% | UNEXPLAINED | - |
| 2010-08-18 Wed | $2.71M | $1.67M | +62.5% | UNEXPLAINED | - |
| 2010-08-30 Mon | $0.00M | $1.88M | -100.0% | UNEXPLAINED | - |
| 2010-09-21 Tue | $4.46M | $2.06M | +116.7% | UNEXPLAINED | - |
| 2010-09-24 Fri | $3.59M | $1.73M | +107.8% | UNEXPLAINED | - |
| 2010-09-27 Mon | $8.48M | $2.38M | +256.2% | UNEXPLAINED | - |
| 2010-10-03 Sun | $2.73M | $1.26M | +117.5% | UNEXPLAINED | - |
| 2010-10-05 Tue | $6.03M | $2.36M | +155.9% | UNEXPLAINED | - |
| 2010-10-08 Fri | $4.25M | $2.05M | +107.3% | UNEXPLAINED | - |
| 2010-10-13 Wed | $4.08M | $2.18M | +87.4% | UNEXPLAINED | - |
| 2010-10-14 Thu | $6.19M | $2.97M | +108.2% | UNEXPLAINED | - |
| 2010-10-15 Fri | $3.89M | $1.84M | +111.1% | UNEXPLAINED | - |
| 2010-11-04 Thu | $6.47M | $3.18M | +103.7% | UNEXPLAINED | - |
| 2010-11-08 Mon | $6.52M | $2.59M | +151.4% | UNEXPLAINED | - |
| 2010-11-10 Wed | $5.71M | $2.74M | +108.7% | UNEXPLAINED | - |
| 2010-11-11 Thu | $4.61M | $3.01M | +53.2% | UNEXPLAINED | - |
| 2010-11-15 Mon | $7.63M | $2.33M | +227.2% | UNEXPLAINED | - |
| 2010-11-24 Wed | $4.47M | $3.12M | +43.2% | UNEXPLAINED | - |
| 2010-11-25 Thu | $5.20M | $2.82M | +84.7% | UNEXPLAINED | - |
| 2010-12-22 Wed | $0.43M | $3.32M | -87.0% | UNEXPLAINED | - |
| 2010-12-24 Fri | $0.00M | $3.42M | -100.0% | UNEXPLAINED | - |
| 2011-01-11 Tue | $4.83M | $0.80M | +506.4% | UNEXPLAINED | - |
| 2011-01-18 Tue | $6.98M | $1.46M | +378.7% | UNEXPLAINED | - |
| 2011-03-20 Sun | $1.61M | $0.57M | +183.0% | UNEXPLAINED | - |
| 2011-03-29 Tue | $5.05M | $2.03M | +148.9% | UNEXPLAINED | - |
| 2011-04-17 Sun | $0.92M | $0.54M | +69.7% | UNEXPLAINED | - |
| 2011-04-18 Mon | $4.05M | $1.76M | +130.4% | UNEXPLAINED | - |
| 2011-04-22 Fri | $0.00M | $2.00M | -100.0% | UNEXPLAINED | - |
| 2011-04-24 Sun | $0.00M | $0.62M | -100.0% | UNEXPLAINED | - |
| 2011-04-25 Mon | $0.00M | $1.73M | -100.0% | UNEXPLAINED | - |
| 2011-04-29 Fri | $0.00M | $1.99M | -100.0% | UNEXPLAINED | - |
| 2011-05-02 Mon | $0.00M | $1.89M | -100.0% | UNEXPLAINED | - |
| 2011-05-30 Mon | $0.00M | $2.49M | -100.0% | UNEXPLAINED | - |
| 2011-06-10 Fri | $4.54M | $2.04M | +122.4% | UNEXPLAINED | - |
| 2011-07-24 Sun | $1.96M | $0.85M | +131.8% | UNEXPLAINED | - |
| 2011-07-31 Sun | $2.41M | $0.65M | +271.3% | UNEXPLAINED | - |
| 2011-08-17 Wed | $4.00M | $2.00M | +100.2% | UNEXPLAINED | - |
| 2011-08-24 Wed | $3.71M | $2.10M | +76.9% | UNEXPLAINED | - |
| 2011-08-29 Mon | $0.00M | $1.74M | -100.0% | UNEXPLAINED | - |
| 2011-09-02 Fri | $3.14M | $1.54M | +103.5% | UNEXPLAINED | - |
| 2011-09-04 Sun | $1.27M | $0.72M | +76.1% | UNEXPLAINED | - |
| 2011-09-11 Sun | $2.64M | $0.72M | +265.4% | UNEXPLAINED | - |
| 2011-09-13 Tue | $4.15M | $1.98M | +109.1% | UNEXPLAINED | - |
| 2011-09-20 Tue | $8.28M | $1.97M | +320.6% | UNEXPLAINED | - |
| 2011-09-25 Sun | $2.39M | $1.03M | +131.9% | UNEXPLAINED | - |
| 2011-10-30 Sun | $2.71M | $1.13M | +139.8% | UNEXPLAINED | - |
| 2011-11-06 Sun | $3.37M | $1.13M | +197.9% | UNEXPLAINED | - |
| 2011-11-13 Sun | $2.72M | $1.21M | +124.2% | UNEXPLAINED | - |

Published as a real change, no fault found: 2010-12-19 (-73.2%).

## Planted faults on real days

| Day | Fault | Real error | Outside the normal range | Verdict | Causes named | Caught |
|---|---|---|---|---|---|---|
| 2010-03-10 Wed | UK prices in pence (x100) | +9319.2% | yes | PROVEN_FAULT | unit_scale | yes |
| 2010-04-14 Wed | Payment file F05 loaded twice | +11.5% | no | NO_INCIDENT | none | NO |
| 2010-05-12 Wed | ECB GBP rate missing today | -98.5% | yes | PROVEN_FAULT | stale_feed | yes |
| 2010-10-13 Wed | UK prices in pence (x100) | +6870.1% | yes | UNEXPLAINED | none | held, cause not proven |
| 2010-11-10 Wed | Payment file F05 loaded twice | +3.2% | yes | UNEXPLAINED | none | held, cause not proven |
| 2011-01-12 Wed | ECB GBP rate missing today | -98.6% | no | PROVEN_FAULT | stale_feed | yes |
| 2011-05-11 Wed | UK prices in pence (x100) | +8506.3% | yes | PROVEN_FAULT | unit_scale | yes |
| 2011-06-15 Wed | Payment file F05 loaded twice | +3.1% | no | NO_INCIDENT | none | NO |
| 2011-07-13 Wed | ECB GBP rate missing today | -98.6% | no | PROVEN_FAULT | stale_feed | yes |

Caught with the right cause: **5 of 9**.

## Timings

Measured on Exasol 2026.2.0-nano.3 (Python UDF: in-database), from the client. Building the database (adapter, load, pipeline, UDF, warm-up history) took 5 s.

| Measure | Median | Max |
|---|---|---|
| Gate run, end to end (712 runs) | 1,329 ms | 3,353 ms |
| Of which inside the database (sum over statements) | 639 ms | 1,869 ms |
| SQL statements per gate run | 19 | |

## Compared with the run on the DuckDB stand-in

* Gate runs compared: 712 (same days, same planted faults)
* Same verdict and same causes: **712 of 712**
* Same detectors fired: 712 of 712
* Largest relative difference in the metric value between the two databases: 7.92e-16

## All judged days

| Day | Revenue | Expected | Change | Normal range | Weekday baseline | Verdict | Fired |
|---|---|---|---|---|---|---|---|
| 2010-01-05 Tue | $1.42M | $2.58M | -44.9% | +/-156.6% | no | NO_INCIDENT | - |
| 2010-01-06 Wed | $0.64M | $2.47M | -74.0% | +/-167.0% | no | NO_INCIDENT | - |
| 2010-01-07 Thu | $5.31M | $2.27M | +134.0% | +/-188.0% | no | NO_INCIDENT | - |
| 2010-01-08 Fri | $2.22M | $2.43M | -8.9% | +/-199.4% | no | NO_INCIDENT | - |
| 2010-01-09 Sat | $0.00M | $2.47M | -100.0% | +/-195.0% | no | NO_INCIDENT | - |
| 2010-01-10 Sun | $1.73M | $2.07M | -16.5% | +/-213.3% | no | NO_INCIDENT | - |
| 2010-01-11 Mon | $2.78M | $1.93M | +44.2% | +/-217.3% | no | NO_INCIDENT | - |
| 2010-01-12 Tue | $3.02M | $1.84M | +64.3% | +/-211.2% | no | NO_INCIDENT | - |
| 2010-01-13 Wed | $1.67M | $1.88M | -11.4% | +/-210.7% | no | NO_INCIDENT | - |
| 2010-01-14 Thu | $2.35M | $1.77M | +32.8% | +/-215.0% | no | NO_INCIDENT | - |
| 2010-01-15 Fri | $1.01M | $1.88M | -46.3% | +/-199.9% | no | NO_INCIDENT | - |
| 2010-01-16 Sat | $0.00M | $1.86M | -100.0% | +/-203.2% | no | NO_INCIDENT | - |
| 2010-01-17 Sun | $1.31M | $1.71M | -23.4% | +/-235.9% | no | NO_INCIDENT | - |
| 2010-01-18 Mon | $1.60M | $1.75M | -8.7% | +/-228.0% | no | NO_INCIDENT | - |
| 2010-01-19 Tue | $2.50M | $1.79M | +39.5% | +/-220.2% | no | NO_INCIDENT | - |
| 2010-01-20 Wed | $1.43M | $1.87M | -23.4% | +/-212.4% | no | NO_INCIDENT | - |
| 2010-01-21 Thu | $2.04M | $1.92M | +6.1% | +/-200.3% | no | NO_INCIDENT | - |
| 2010-01-22 Fri | $2.75M | $1.69M | +62.9% | +/-156.2% | no | NO_INCIDENT | - |
| 2010-01-23 Sat | $0.00M | $1.73M | -100.0% | +/-158.5% | no | NO_INCIDENT | - |
| 2010-01-24 Sun | $1.20M | $1.30M | -7.8% | +/-108.5% | yes | NO_INCIDENT | - |
| 2010-01-25 Mon | $1.72M | $1.65M | +3.9% | +/-105.6% | yes | NO_INCIDENT | - |
| 2010-01-26 Tue | $3.51M | $2.26M | +55.3% | +/-102.3% | yes | UNEXPLAINED | unit_scale:REJECTED |
| 2010-01-27 Wed | $2.16M | $1.14M | +89.6% | +/-104.4% | yes | NO_INCIDENT | - |
| 2010-01-28 Thu | $1.49M | $3.23M | -53.8% | +/-104.4% | yes | NO_INCIDENT | - |
| 2010-01-29 Fri | $2.11M | $1.54M | +37.4% | +/-155.5% | no | NO_INCIDENT | - |
| 2010-01-30 Sat | $0.00M | $1.52M | -100.0% | +/-154.2% | no | NO_INCIDENT | - |
| 2010-01-31 Sun | $1.39M | $1.41M | -1.5% | +/-109.1% | yes | NO_INCIDENT | - |
| 2010-02-01 Mon | $1.46M | $1.77M | -17.6% | +/-106.7% | yes | NO_INCIDENT | - |
| 2010-02-02 Tue | $1.60M | $2.31M | -30.8% | +/-105.6% | yes | NO_INCIDENT | - |
| 2010-02-03 Wed | $1.57M | $1.47M | +6.8% | +/-105.7% | yes | NO_INCIDENT | - |
| 2010-02-04 Thu | $1.66M | $2.80M | -40.6% | +/-103.4% | yes | NO_INCIDENT | - |
| 2010-02-05 Fri | $1.61M | $2.02M | -20.4% | +/-107.3% | yes | NO_INCIDENT | - |
| 2010-02-06 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-02-07 Sun | $1.25M | $1.41M | -11.1% | +/-106.4% | yes | NO_INCIDENT | - |
| 2010-02-08 Mon | $1.27M | $1.71M | -25.6% | +/-104.8% | yes | NO_INCIDENT | - |
| 2010-02-09 Tue | $1.43M | $2.13M | -32.8% | +/-102.7% | yes | NO_INCIDENT | - |
| 2010-02-10 Wed | $0.70M | $1.49M | -53.4% | +/-102.7% | yes | NO_INCIDENT | - |
| 2010-02-11 Thu | $1.10M | $2.57M | -57.3% | +/-101.9% | yes | NO_INCIDENT | - |
| 2010-02-12 Fri | $0.83M | $1.94M | -57.4% | +/-82.2% | yes | NO_INCIDENT | - |
| 2010-02-13 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-02-14 Sun | $1.30M | $1.38M | -5.6% | +/-90.3% | yes | NO_INCIDENT | - |
| 2010-02-15 Mon | $3.11M | $1.77M | +76.1% | +/-88.9% | yes | NO_INCIDENT | - |
| 2010-02-16 Tue | $2.26M | $2.14M | +5.9% | +/-92.2% | yes | NO_INCIDENT | - |
| 2010-02-17 Wed | $1.94M | $1.50M | +28.8% | +/-89.4% | yes | NO_INCIDENT | - |
| 2010-02-18 Thu | $2.58M | $1.73M | +49.4% | +/-89.9% | yes | NO_INCIDENT | - |
| 2010-02-19 Fri | $1.94M | $1.66M | +16.9% | +/-91.4% | yes | NO_INCIDENT | - |
| 2010-02-20 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-02-21 Sun | $0.82M | $1.29M | -36.7% | +/-85.7% | yes | NO_INCIDENT | - |
| 2010-02-22 Mon | $1.89M | $1.83M | +3.0% | +/-87.9% | yes | NO_INCIDENT | - |
| 2010-02-23 Tue | $1.62M | $1.95M | -16.9% | +/-86.9% | yes | NO_INCIDENT | - |
| 2010-02-24 Wed | $2.36M | $1.56M | +51.6% | +/-85.5% | yes | NO_INCIDENT | - |
| 2010-02-25 Thu | $3.31M | $1.78M | +86.4% | +/-86.4% | yes | UNEXPLAINED | - |
| 2010-02-26 Fri | $1.17M | $1.85M | -36.7% | +/-87.9% | yes | NO_INCIDENT | - |
| 2010-02-27 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-02-28 Sun | $1.19M | $1.19M | -0.6% | +/-86.1% | yes | NO_INCIDENT | - |
| 2010-03-01 Mon | $1.78M | $1.89M | -5.9% | +/-86.1% | yes | NO_INCIDENT | - |
| 2010-03-02 Tue | $1.81M | $1.73M | +5.0% | +/-85.9% | yes | NO_INCIDENT | - |
| 2010-03-03 Wed | $2.35M | $1.75M | +34.9% | +/-84.4% | yes | NO_INCIDENT | - |
| 2010-03-04 Thu | $2.24M | $1.71M | +31.0% | +/-85.1% | yes | NO_INCIDENT | - |
| 2010-03-05 Fri | $1.90M | $1.53M | +23.9% | +/-84.2% | yes | NO_INCIDENT | - |
| 2010-03-06 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-03-07 Sun | $1.37M | $1.19M | +15.3% | +/-82.9% | yes | NO_INCIDENT | - |
| 2010-03-08 Mon | $2.56M | $1.90M | +34.8% | +/-82.8% | yes | NO_INCIDENT | - |
| 2010-03-09 Tue | $1.50M | $1.75M | -13.9% | +/-80.7% | yes | NO_INCIDENT | - |
| 2010-03-10 Wed | $1.87M | $1.79M | +4.6% | +/-81.0% | yes | NO_INCIDENT | - |
| 2010-03-11 Thu | $1.69M | $1.90M | -11.1% | +/-79.9% | yes | NO_INCIDENT | - |
| 2010-03-12 Fri | $1.50M | $1.49M | +0.4% | +/-79.9% | yes | NO_INCIDENT | - |
| 2010-03-13 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-03-14 Sun | $0.62M | $1.19M | -47.5% | +/-80.0% | yes | NO_INCIDENT | - |
| 2010-03-15 Mon | $1.90M | $2.12M | -10.6% | +/-84.5% | yes | NO_INCIDENT | - |
| 2010-03-16 Tue | $1.66M | $1.73M | -4.0% | +/-80.8% | yes | NO_INCIDENT | - |
| 2010-03-17 Wed | $2.14M | $1.84M | +16.2% | +/-80.1% | yes | NO_INCIDENT | - |
| 2010-03-18 Thu | $2.86M | $1.90M | +50.3% | +/-69.8% | yes | NO_INCIDENT | - |
| 2010-03-19 Fri | $3.15M | $1.47M | +115.0% | +/-64.9% | yes | UNEXPLAINED | - |
| 2010-03-20 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-03-21 Sun | $1.44M | $1.06M | +35.7% | +/-59.0% | yes | NO_INCIDENT | - |
| 2010-03-22 Mon | $1.75M | $2.25M | -22.1% | +/-60.4% | yes | NO_INCIDENT | - |
| 2010-03-23 Tue | $3.86M | $1.77M | +118.2% | +/-56.4% | yes | UNEXPLAINED | - |
| 2010-03-24 Wed | $2.04M | $2.13M | -4.2% | +/-54.7% | yes | NO_INCIDENT | - |
| 2010-03-25 Thu | $2.65M | $2.34M | +13.1% | +/-54.4% | yes | NO_INCIDENT | - |
| 2010-03-26 Fri | $2.18M | $1.63M | +34.1% | +/-54.5% | yes | NO_INCIDENT | - |
| 2010-03-27 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-03-28 Sun | $1.51M | $1.09M | +39.1% | +/-56.3% | yes | NO_INCIDENT | - |
| 2010-03-29 Mon | $4.03M | $1.98M | +104.1% | +/-53.8% | yes | UNEXPLAINED | - |
| 2010-03-30 Tue | $2.63M | $1.65M | +59.5% | +/-54.6% | yes | UNEXPLAINED | - |
| 2010-03-31 Wed | $2.02M | $2.15M | -6.2% | +/-55.7% | yes | NO_INCIDENT | - |
| 2010-04-01 Thu | $2.10M | $2.36M | -11.1% | +/-55.4% | yes | NO_INCIDENT | - |
| 2010-04-02 Fri | $0.00M | $1.69M | -100.0% | +/-54.9% | yes | UNEXPLAINED | - |
| 2010-04-03 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-04-04 Sun | $0.00M | $1.23M | -100.0% | +/-51.3% | yes | UNEXPLAINED | - |
| 2010-04-05 Mon | $0.00M | $2.00M | -100.0% | +/-52.1% | yes | UNEXPLAINED | - |
| 2010-04-06 Tue | $1.31M | $1.66M | -20.7% | +/-52.4% | yes | NO_INCIDENT | - |
| 2010-04-07 Wed | $2.34M | $2.09M | +12.0% | +/-52.7% | yes | NO_INCIDENT | - |
| 2010-04-08 Thu | $3.22M | $2.31M | +39.6% | +/-52.6% | yes | NO_INCIDENT | - |
| 2010-04-09 Fri | $1.15M | $1.86M | -37.9% | +/-55.4% | yes | NO_INCIDENT | - |
| 2010-04-10 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-04-11 Sun | $1.36M | $1.24M | +9.8% | +/-60.2% | yes | NO_INCIDENT | - |
| 2010-04-12 Mon | $1.86M | $2.07M | -10.2% | +/-60.2% | yes | NO_INCIDENT | - |
| 2010-04-13 Tue | $1.79M | $1.49M | +19.8% | +/-57.4% | yes | NO_INCIDENT | - |
| 2010-04-14 Wed | $1.86M | $2.08M | -10.7% | +/-58.1% | yes | NO_INCIDENT | - |
| 2010-04-15 Thu | $2.03M | $2.50M | -18.8% | +/-58.2% | yes | NO_INCIDENT | - |
| 2010-04-16 Fri | $1.34M | $1.61M | -17.0% | +/-55.3% | yes | NO_INCIDENT | - |
| 2010-04-17 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-04-18 Sun | $1.65M | $1.23M | +33.7% | +/-56.5% | yes | NO_INCIDENT | - |
| 2010-04-19 Mon | $3.09M | $1.84M | +68.3% | +/-44.3% | yes | UNEXPLAINED | - |
| 2010-04-20 Tue | $2.00M | $1.42M | +40.6% | +/-188.4% | no | NO_INCIDENT | - |
| 2010-04-21 Wed | $2.02M | $1.56M | +29.1% | +/-155.4% | no | NO_INCIDENT | - |
| 2010-04-22 Thu | $2.98M | $1.62M | +84.5% | +/-151.4% | no | NO_INCIDENT | - |
| 2010-04-23 Fri | $1.14M | $1.66M | -31.2% | +/-157.3% | no | NO_INCIDENT | - |
| 2010-04-24 Sat | $0.00M | $1.51M | -100.0% | +/-151.3% | no | NO_INCIDENT | - |
| 2010-04-25 Sun | $1.15M | $1.43M | -19.9% | +/-179.1% | no | NO_INCIDENT | - |
| 2010-04-26 Mon | $2.49M | $1.51M | +64.5% | +/-151.4% | no | NO_INCIDENT | - |
| 2010-04-27 Tue | $3.16M | $1.59M | +98.4% | +/-150.9% | no | NO_INCIDENT | - |
| 2010-04-28 Wed | $2.21M | $1.69M | +31.2% | +/-159.6% | no | NO_INCIDENT | - |
| 2010-04-29 Thu | $2.23M | $1.72M | +30.2% | +/-158.5% | no | NO_INCIDENT | - |
| 2010-04-30 Fri | $1.99M | $1.74M | +14.0% | +/-157.7% | no | NO_INCIDENT | - |
| 2010-05-01 Sat | $0.00M | $1.74M | -100.0% | +/-157.8% | no | NO_INCIDENT | - |
| 2010-05-02 Sun | $0.84M | $1.64M | -48.9% | +/-185.4% | no | NO_INCIDENT | - |
| 2010-05-03 Mon | $0.00M | $1.70M | -100.0% | +/-165.4% | no | NO_INCIDENT | - |
| 2010-05-04 Tue | $1.54M | $2.07M | -25.5% | +/-98.8% | yes | NO_INCIDENT | - |
| 2010-05-05 Wed | $1.91M | $2.09M | -8.6% | +/-98.8% | yes | NO_INCIDENT | - |
| 2010-05-06 Thu | $3.74M | $2.51M | +48.9% | +/-98.9% | yes | NO_INCIDENT | - |
| 2010-05-07 Fri | $2.39M | $1.41M | +69.9% | +/-99.9% | yes | NO_INCIDENT | - |
| 2010-05-08 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-05-09 Sun | $1.55M | $1.25M | +23.9% | +/-102.1% | yes | NO_INCIDENT | - |
| 2010-05-10 Mon | $2.22M | $1.45M | +53.1% | +/-100.6% | yes | NO_INCIDENT | - |
| 2010-05-11 Tue | $1.93M | $1.96M | -1.8% | +/-95.9% | yes | NO_INCIDENT | - |
| 2010-05-12 Wed | $2.12M | $2.07M | +2.4% | +/-93.0% | yes | NO_INCIDENT | - |
| 2010-05-13 Thu | $2.73M | $2.84M | -3.8% | +/-92.7% | yes | NO_INCIDENT | - |
| 2010-05-14 Fri | $1.25M | $1.60M | -22.3% | +/-92.6% | yes | NO_INCIDENT | - |
| 2010-05-15 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-05-16 Sun | $1.22M | $1.31M | -6.8% | +/-92.0% | yes | NO_INCIDENT | - |
| 2010-05-17 Mon | $1.68M | $1.64M | +2.6% | +/-92.2% | yes | NO_INCIDENT | - |
| 2010-05-18 Tue | $1.91M | $2.08M | -8.0% | +/-93.1% | yes | NO_INCIDENT | - |
| 2010-05-19 Wed | $1.18M | $2.02M | -41.6% | +/-92.7% | yes | NO_INCIDENT | - |
| 2010-05-20 Thu | $1.72M | $2.74M | -37.2% | +/-95.5% | yes | NO_INCIDENT | - |
| 2010-05-21 Fri | $1.84M | $1.62M | +13.7% | +/-96.9% | yes | NO_INCIDENT | - |
| 2010-05-22 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-05-23 Sun | $1.72M | $1.28M | +34.2% | +/-95.6% | yes | NO_INCIDENT | - |
| 2010-05-24 Mon | $2.42M | $1.60M | +51.3% | +/-96.0% | yes | NO_INCIDENT | - |
| 2010-05-25 Tue | $1.54M | $2.11M | -27.0% | +/-93.0% | yes | NO_INCIDENT | - |
| 2010-05-26 Wed | $2.62M | $1.89M | +38.7% | +/-94.6% | yes | NO_INCIDENT | - |
| 2010-05-27 Thu | $2.10M | $2.68M | -21.6% | +/-96.0% | yes | NO_INCIDENT | - |
| 2010-05-28 Fri | $1.48M | $1.72M | -14.0% | +/-97.0% | yes | NO_INCIDENT | - |
| 2010-05-29 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-05-30 Sun | $0.73M | $1.29M | -43.5% | +/-95.1% | yes | NO_INCIDENT | - |
| 2010-05-31 Mon | $0.00M | $1.76M | -100.0% | +/-98.4% | yes | UNEXPLAINED | - |
| 2010-06-01 Tue | $1.08M | $2.02M | -46.4% | +/-101.2% | yes | NO_INCIDENT | - |
| 2010-06-02 Wed | $1.12M | $2.01M | -44.3% | +/-97.3% | yes | NO_INCIDENT | - |
| 2010-06-03 Thu | $2.03M | $2.51M | -19.0% | +/-100.9% | yes | NO_INCIDENT | - |
| 2010-06-04 Fri | $1.45M | $1.79M | -18.8% | +/-101.5% | yes | NO_INCIDENT | - |
| 2010-06-05 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-06-06 Sun | $1.75M | $1.21M | +45.0% | +/-102.1% | yes | NO_INCIDENT | - |
| 2010-06-07 Mon | $3.40M | $1.58M | +115.1% | +/-100.1% | yes | UNEXPLAINED | - |
| 2010-06-08 Tue | $3.69M | $1.60M | +130.5% | +/-77.0% | yes | UNEXPLAINED | - |
| 2010-06-09 Wed | $2.63M | $1.79M | +46.8% | +/-78.3% | yes | NO_INCIDENT | - |
| 2010-06-10 Thu | $1.26M | $2.47M | -48.9% | +/-80.1% | yes | NO_INCIDENT | - |
| 2010-06-11 Fri | $2.59M | $1.68M | +54.0% | +/-77.5% | yes | NO_INCIDENT | - |
| 2010-06-12 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-06-13 Sun | $1.48M | $1.39M | +6.3% | +/-79.5% | yes | NO_INCIDENT | - |
| 2010-06-14 Mon | $1.67M | $2.11M | -20.7% | +/-79.5% | yes | NO_INCIDENT | - |
| 2010-06-15 Tue | $2.09M | $1.61M | +29.7% | +/-80.2% | yes | NO_INCIDENT | - |
| 2010-06-16 Wed | $2.16M | $1.93M | +11.6% | +/-80.9% | yes | NO_INCIDENT | - |
| 2010-06-17 Thu | $3.99M | $1.97M | +102.7% | +/-80.9% | yes | UNEXPLAINED | - |
| 2010-06-18 Fri | $1.29M | $1.72M | -25.4% | +/-79.0% | yes | NO_INCIDENT | - |
| 2010-06-19 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-06-20 Sun | $0.62M | $1.38M | -54.9% | +/-78.7% | yes | NO_INCIDENT | - |
| 2010-06-21 Mon | $1.44M | $1.92M | -25.3% | +/-86.5% | yes | NO_INCIDENT | - |
| 2010-06-22 Tue | $1.00M | $1.66M | -39.4% | +/-87.6% | yes | NO_INCIDENT | - |
| 2010-06-23 Wed | $1.92M | $1.94M | -1.1% | +/-90.5% | yes | NO_INCIDENT | - |
| 2010-06-24 Thu | $1.86M | $1.78M | +4.6% | +/-85.8% | yes | NO_INCIDENT | - |
| 2010-06-25 Fri | $1.22M | $1.73M | -29.2% | +/-85.7% | yes | NO_INCIDENT | - |
| 2010-06-26 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-06-27 Sun | $1.30M | $1.26M | +3.2% | +/-88.2% | yes | NO_INCIDENT | - |
| 2010-06-28 Mon | $3.75M | $1.84M | +103.8% | +/-86.9% | yes | UNEXPLAINED | - |
| 2010-06-29 Tue | $2.46M | $1.29M | +90.6% | +/-154.5% | no | NO_INCIDENT | - |
| 2010-06-30 Wed | $2.42M | $1.36M | +77.9% | +/-160.9% | no | NO_INCIDENT | - |
| 2010-07-01 Thu | $2.12M | $1.41M | +50.0% | +/-164.7% | no | NO_INCIDENT | - |
| 2010-07-02 Fri | $1.20M | $1.41M | -15.0% | +/-164.9% | no | NO_INCIDENT | - |
| 2010-07-03 Sat | $0.00M | $1.35M | -100.0% | +/-167.3% | no | NO_INCIDENT | - |
| 2010-07-04 Sun | $0.75M | $1.25M | -40.5% | +/-197.8% | no | NO_INCIDENT | - |
| 2010-07-05 Mon | $2.33M | $1.31M | +78.1% | +/-175.8% | no | NO_INCIDENT | - |
| 2010-07-06 Tue | $1.67M | $1.66M | +0.6% | +/-91.5% | yes | NO_INCIDENT | - |
| 2010-07-07 Wed | $2.29M | $2.05M | +12.0% | +/-87.2% | yes | NO_INCIDENT | - |
| 2010-07-08 Thu | $1.44M | $1.82M | -20.7% | +/-81.7% | yes | NO_INCIDENT | - |
| 2010-07-09 Fri | $2.63M | $1.55M | +69.5% | +/-82.3% | yes | NO_INCIDENT | - |
| 2010-07-10 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-07-11 Sun | $0.55M | $1.18M | -53.1% | +/-85.0% | yes | NO_INCIDENT | - |
| 2010-07-12 Mon | $1.40M | $1.81M | -22.8% | +/-87.7% | yes | NO_INCIDENT | - |
| 2010-07-13 Tue | $1.49M | $1.81M | -17.6% | +/-87.2% | yes | NO_INCIDENT | - |
| 2010-07-14 Wed | $1.70M | $2.28M | -25.6% | +/-86.6% | yes | NO_INCIDENT | - |
| 2010-07-15 Thu | $4.05M | $1.67M | +142.7% | +/-87.0% | yes | UNEXPLAINED | - |
| 2010-07-16 Fri | $1.63M | $1.79M | -9.0% | +/-86.8% | yes | NO_INCIDENT | - |
| 2010-07-17 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-07-18 Sun | $1.09M | $0.94M | +16.3% | +/-84.2% | yes | NO_INCIDENT | - |
| 2010-07-19 Mon | $2.20M | $1.71M | +28.7% | +/-79.1% | yes | NO_INCIDENT | - |
| 2010-07-20 Tue | $1.78M | $1.74M | +2.4% | +/-79.6% | yes | NO_INCIDENT | - |
| 2010-07-21 Wed | $1.61M | $2.10M | -23.1% | +/-79.2% | yes | NO_INCIDENT | - |
| 2010-07-22 Thu | $1.93M | $1.81M | +6.8% | +/-80.3% | yes | NO_INCIDENT | - |
| 2010-07-23 Fri | $1.87M | $1.59M | +17.6% | +/-78.9% | yes | NO_INCIDENT | - |
| 2010-07-24 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-07-25 Sun | $1.26M | $0.86M | +45.9% | +/-76.7% | yes | NO_INCIDENT | - |
| 2010-07-26 Mon | $1.84M | $1.84M | -0.2% | +/-74.3% | yes | NO_INCIDENT | - |
| 2010-07-27 Tue | $2.07M | $1.68M | +23.0% | +/-72.6% | yes | NO_INCIDENT | - |
| 2010-07-28 Wed | $1.70M | $1.99M | -14.4% | +/-67.3% | yes | NO_INCIDENT | - |
| 2010-07-29 Thu | $2.79M | $1.84M | +51.9% | +/-67.8% | yes | NO_INCIDENT | - |
| 2010-07-30 Fri | $1.17M | $1.71M | -31.7% | +/-71.2% | yes | NO_INCIDENT | - |
| 2010-07-31 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-08-01 Sun | $2.22M | $0.99M | +124.4% | +/-71.8% | yes | UNEXPLAINED | - |
| 2010-08-02 Mon | $2.14M | $1.94M | +10.0% | +/-71.6% | yes | NO_INCIDENT | - |
| 2010-08-03 Tue | $1.98M | $1.89M | +4.7% | +/-70.3% | yes | NO_INCIDENT | - |
| 2010-08-04 Wed | $1.58M | $1.94M | -18.9% | +/-68.2% | yes | NO_INCIDENT | - |
| 2010-08-05 Thu | $1.80M | $2.07M | -13.1% | +/-67.1% | yes | NO_INCIDENT | - |
| 2010-08-06 Fri | $1.12M | $1.70M | -34.4% | +/-67.8% | yes | NO_INCIDENT | - |
| 2010-08-07 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-08-08 Sun | $1.04M | $0.91M | +13.4% | +/-68.9% | yes | NO_INCIDENT | - |
| 2010-08-09 Mon | $2.33M | $1.98M | +17.9% | +/-66.8% | yes | NO_INCIDENT | - |
| 2010-08-10 Tue | $2.61M | $1.80M | +45.4% | +/-66.8% | yes | NO_INCIDENT | - |
| 2010-08-11 Wed | $1.74M | $1.78M | -1.9% | +/-69.3% | yes | NO_INCIDENT | - |
| 2010-08-12 Thu | $2.12M | $1.99M | +6.6% | +/-66.9% | yes | NO_INCIDENT | - |
| 2010-08-13 Fri | $2.73M | $1.68M | +62.0% | +/-63.9% | yes | NO_INCIDENT | - |
| 2010-08-14 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-08-15 Sun | $1.63M | $0.99M | +65.2% | +/-65.2% | yes | NO_INCIDENT | - |
| 2010-08-16 Mon | $1.53M | $1.98M | -23.0% | +/-61.4% | yes | NO_INCIDENT | - |
| 2010-08-17 Tue | $2.21M | $1.99M | +11.4% | +/-60.5% | yes | NO_INCIDENT | - |
| 2010-08-18 Wed | $2.71M | $1.67M | +62.5% | +/-58.0% | yes | UNEXPLAINED | - |
| 2010-08-19 Thu | $2.40M | $2.16M | +10.9% | +/-59.1% | yes | NO_INCIDENT | - |
| 2010-08-20 Fri | $1.85M | $1.70M | +8.7% | +/-58.1% | yes | NO_INCIDENT | - |
| 2010-08-21 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-08-22 Sun | $1.65M | $1.26M | +31.3% | +/-57.4% | yes | NO_INCIDENT | - |
| 2010-08-23 Mon | $1.59M | $2.01M | -20.8% | +/-57.4% | yes | NO_INCIDENT | - |
| 2010-08-24 Tue | $1.98M | $2.13M | -6.9% | +/-58.3% | yes | NO_INCIDENT | - |
| 2010-08-25 Wed | $2.29M | $1.66M | +38.2% | +/-57.5% | yes | NO_INCIDENT | - |
| 2010-08-26 Thu | $2.57M | $2.21M | +16.5% | +/-59.8% | yes | NO_INCIDENT | - |
| 2010-08-27 Fri | $1.32M | $1.75M | -24.4% | +/-59.3% | yes | NO_INCIDENT | - |
| 2010-08-28 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-08-29 Sun | $1.05M | $1.39M | -24.4% | +/-62.4% | yes | NO_INCIDENT | - |
| 2010-08-30 Mon | $0.00M | $1.88M | -100.0% | +/-63.9% | yes | UNEXPLAINED | - |
| 2010-08-31 Tue | $2.60M | $2.17M | +19.8% | +/-65.0% | yes | NO_INCIDENT | - |
| 2010-09-01 Wed | $1.68M | $1.83M | -7.8% | +/-65.5% | yes | NO_INCIDENT | - |
| 2010-09-02 Thu | $2.63M | $2.34M | +12.3% | +/-65.5% | yes | NO_INCIDENT | - |
| 2010-09-03 Fri | $2.67M | $1.64M | +63.5% | +/-65.0% | yes | NO_INCIDENT | - |
| 2010-09-04 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-09-05 Sun | $0.89M | $1.34M | -33.7% | +/-62.7% | yes | NO_INCIDENT | - |
| 2010-09-06 Mon | $2.06M | $1.90M | +8.5% | +/-65.0% | yes | NO_INCIDENT | - |
| 2010-09-07 Tue | $1.97M | $2.28M | -13.4% | +/-64.8% | yes | NO_INCIDENT | - |
| 2010-09-08 Wed | $1.27M | $1.82M | -30.3% | +/-64.9% | yes | NO_INCIDENT | - |
| 2010-09-09 Thu | $1.85M | $2.30M | -19.9% | +/-66.8% | yes | NO_INCIDENT | - |
| 2010-09-10 Fri | $1.26M | $1.94M | -34.9% | +/-66.6% | yes | NO_INCIDENT | - |
| 2010-09-11 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-09-12 Sun | $1.13M | $1.25M | -10.0% | +/-64.8% | yes | NO_INCIDENT | - |
| 2010-09-13 Mon | $2.75M | $1.88M | +46.4% | +/-64.1% | yes | NO_INCIDENT | - |
| 2010-09-14 Tue | $1.52M | $2.28M | -33.3% | +/-66.9% | yes | NO_INCIDENT | - |
| 2010-09-15 Wed | $2.51M | $1.75M | +43.7% | +/-68.6% | yes | NO_INCIDENT | - |
| 2010-09-16 Thu | $2.91M | $2.31M | +25.9% | +/-70.5% | yes | NO_INCIDENT | - |
| 2010-09-17 Fri | $1.54M | $1.97M | -21.7% | +/-71.0% | yes | NO_INCIDENT | - |
| 2010-09-18 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-09-19 Sun | $1.65M | $1.27M | +30.3% | +/-69.3% | yes | NO_INCIDENT | - |
| 2010-09-20 Mon | $3.13M | $1.98M | +58.2% | +/-69.5% | yes | NO_INCIDENT | - |
| 2010-09-21 Tue | $4.46M | $2.06M | +116.7% | +/-69.7% | yes | UNEXPLAINED | - |
| 2010-09-22 Wed | $2.18M | $1.94M | +12.5% | +/-71.0% | yes | NO_INCIDENT | - |
| 2010-09-23 Thu | $2.59M | $2.47M | +4.9% | +/-69.7% | yes | NO_INCIDENT | - |
| 2010-09-24 Fri | $3.59M | $1.73M | +107.8% | +/-69.6% | yes | UNEXPLAINED | - |
| 2010-09-25 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-09-26 Sun | $1.56M | $1.27M | +22.2% | +/-71.1% | yes | NO_INCIDENT | - |
| 2010-09-27 Mon | $8.48M | $2.38M | +256.2% | +/-70.4% | yes | UNEXPLAINED | - |
| 2010-09-28 Tue | $3.33M | $2.02M | +64.8% | +/-67.6% | yes | NO_INCIDENT | - |
| 2010-09-29 Wed | $2.75M | $1.99M | +38.5% | +/-72.3% | yes | NO_INCIDENT | - |
| 2010-09-30 Thu | $3.68M | $2.51M | +46.6% | +/-74.2% | yes | NO_INCIDENT | - |
| 2010-10-01 Fri | $2.72M | $1.70M | +60.4% | +/-77.3% | yes | NO_INCIDENT | - |
| 2010-10-02 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-10-03 Sun | $2.73M | $1.26M | +117.5% | +/-76.3% | yes | UNEXPLAINED | - |
| 2010-10-04 Mon | $2.78M | $2.65M | +5.0% | +/-76.6% | yes | NO_INCIDENT | - |
| 2010-10-05 Tue | $6.03M | $2.36M | +155.9% | +/-75.1% | yes | UNEXPLAINED | - |
| 2010-10-06 Wed | $2.18M | $2.08M | +4.8% | +/-76.8% | yes | NO_INCIDENT | - |
| 2010-10-07 Thu | $3.85M | $2.73M | +40.8% | +/-75.1% | yes | NO_INCIDENT | - |
| 2010-10-08 Fri | $4.25M | $2.05M | +107.3% | +/-76.7% | yes | UNEXPLAINED | - |
| 2010-10-09 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-10-10 Sun | $1.63M | $1.31M | +25.0% | +/-77.0% | yes | NO_INCIDENT | - |
| 2010-10-11 Mon | $3.08M | $2.68M | +15.0% | +/-73.4% | yes | NO_INCIDENT | - |
| 2010-10-12 Tue | $3.54M | $2.27M | +55.5% | +/-71.5% | yes | NO_INCIDENT | - |
| 2010-10-13 Wed | $4.08M | $2.18M | +87.4% | +/-70.8% | yes | UNEXPLAINED | - |
| 2010-10-14 Thu | $6.19M | $2.97M | +108.2% | +/-65.9% | yes | UNEXPLAINED | - |
| 2010-10-15 Fri | $3.89M | $1.84M | +111.1% | +/-61.0% | yes | UNEXPLAINED | - |
| 2010-10-16 Sat | $0.00M | $2.22M | -100.0% | +/-180.1% | no | NO_INCIDENT | - |
| 2010-10-17 Sun | $2.36M | $2.22M | +6.3% | +/-180.1% | no | NO_INCIDENT | - |
| 2010-10-18 Mon | $2.93M | $2.28M | +28.6% | +/-173.9% | no | NO_INCIDENT | - |
| 2010-10-19 Tue | $3.50M | $2.25M | +55.5% | +/-173.6% | no | NO_INCIDENT | - |
| 2010-10-20 Wed | $3.20M | $2.30M | +39.0% | +/-174.0% | no | NO_INCIDENT | - |
| 2010-10-21 Thu | $2.74M | $2.27M | +20.6% | +/-172.7% | no | NO_INCIDENT | - |
| 2010-10-22 Fri | $2.88M | $2.27M | +26.9% | +/-172.7% | no | NO_INCIDENT | - |
| 2010-10-23 Sat | $0.00M | $2.48M | -100.0% | +/-139.4% | no | NO_INCIDENT | - |
| 2010-10-24 Sun | $2.02M | $2.28M | -11.3% | +/-172.6% | no | NO_INCIDENT | - |
| 2010-10-25 Mon | $2.06M | $2.27M | -9.2% | +/-173.6% | no | NO_INCIDENT | - |
| 2010-10-26 Tue | $3.26M | $2.14M | +52.3% | +/-173.5% | no | NO_INCIDENT | - |
| 2010-10-27 Wed | $2.32M | $2.37M | -2.0% | +/-140.7% | no | NO_INCIDENT | - |
| 2010-10-28 Thu | $2.44M | $2.42M | +1.0% | +/-135.6% | no | NO_INCIDENT | - |
| 2010-10-29 Fri | $3.35M | $2.38M | +41.0% | +/-136.2% | no | NO_INCIDENT | - |
| 2010-10-30 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-10-31 Sun | $2.15M | $1.89M | +13.5% | +/-42.6% | yes | NO_INCIDENT | - |
| 2010-11-01 Mon | $2.12M | $2.71M | -22.0% | +/-40.3% | yes | NO_INCIDENT | - |
| 2010-11-02 Tue | $3.20M | $3.41M | -5.9% | +/-41.7% | yes | NO_INCIDENT | - |
| 2010-11-03 Wed | $3.24M | $2.61M | +24.1% | +/-41.9% | yes | NO_INCIDENT | - |
| 2010-11-04 Thu | $6.47M | $3.18M | +103.7% | +/-43.4% | yes | UNEXPLAINED | - |
| 2010-11-05 Fri | $3.33M | $2.98M | +11.6% | +/-43.4% | yes | NO_INCIDENT | - |
| 2010-11-06 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-11-07 Sun | $2.29M | $2.04M | +12.0% | +/-42.9% | yes | NO_INCIDENT | - |
| 2010-11-08 Mon | $6.52M | $2.59M | +151.4% | +/-42.4% | yes | UNEXPLAINED | - |
| 2010-11-09 Tue | $4.76M | $3.37M | +41.1% | +/-43.2% | yes | NO_INCIDENT | - |
| 2010-11-10 Wed | $5.71M | $2.74M | +108.7% | +/-47.1% | yes | UNEXPLAINED | - |
| 2010-11-11 Thu | $4.61M | $3.01M | +53.2% | +/-45.4% | yes | UNEXPLAINED | - |
| 2010-11-12 Fri | $3.66M | $2.47M | +48.3% | +/-149.6% | no | NO_INCIDENT | - |
| 2010-11-13 Sat | $0.00M | $2.58M | -100.0% | +/-146.6% | no | NO_INCIDENT | - |
| 2010-11-14 Sun | $2.12M | $2.35M | -9.8% | +/-179.7% | no | NO_INCIDENT | - |
| 2010-11-15 Mon | $7.63M | $2.33M | +227.2% | +/-181.0% | no | UNEXPLAINED | - |
| 2010-11-16 Tue | $5.30M | $2.33M | +127.1% | +/-181.0% | no | NO_INCIDENT | - |
| 2010-11-17 Wed | $3.73M | $2.54M | +46.9% | +/-189.5% | no | NO_INCIDENT | - |
| 2010-11-18 Thu | $3.26M | $2.56M | +27.3% | +/-189.4% | no | NO_INCIDENT | - |
| 2010-11-19 Fri | $3.48M | $3.30M | +5.4% | +/-43.6% | yes | NO_INCIDENT | - |
| 2010-11-20 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-11-21 Sun | $2.35M | $2.19M | +7.5% | +/-42.8% | yes | NO_INCIDENT | - |
| 2010-11-22 Mon | $3.14M | $2.37M | +32.6% | +/-42.8% | yes | NO_INCIDENT | - |
| 2010-11-23 Tue | $4.25M | $4.00M | +6.1% | +/-44.4% | yes | NO_INCIDENT | - |
| 2010-11-24 Wed | $4.47M | $3.12M | +43.2% | +/-43.0% | yes | UNEXPLAINED | - |
| 2010-11-25 Thu | $5.20M | $2.82M | +84.7% | +/-44.0% | yes | UNEXPLAINED | - |
| 2010-11-26 Fri | $2.91M | $2.74M | +6.4% | +/-182.8% | no | NO_INCIDENT | - |
| 2010-11-27 Sat | $0.00M | $2.95M | -100.0% | +/-151.3% | no | NO_INCIDENT | - |
| 2010-11-28 Sun | $1.98M | $2.78M | -28.8% | +/-179.4% | no | NO_INCIDENT | - |
| 2010-11-29 Mon | $5.67M | $2.58M | +119.5% | +/-183.4% | no | NO_INCIDENT | - |
| 2010-11-30 Tue | $4.28M | $2.73M | +56.9% | +/-192.8% | no | NO_INCIDENT | - |
| 2010-12-01 Wed | $4.18M | $3.03M | +37.7% | +/-160.1% | no | NO_INCIDENT | - |
| 2010-12-02 Thu | $3.37M | $3.18M | +5.9% | +/-153.0% | no | NO_INCIDENT | - |
| 2010-12-03 Fri | $3.31M | $3.04M | +8.7% | +/-149.4% | no | NO_INCIDENT | - |
| 2010-12-04 Sat | $0.00M | $3.01M | -100.0% | +/-149.9% | no | NO_INCIDENT | - |
| 2010-12-05 Sun | $2.24M | $2.78M | -19.5% | +/-182.4% | no | NO_INCIDENT | - |
| 2010-12-06 Mon | $3.86M | $2.69M | +43.5% | +/-187.7% | no | NO_INCIDENT | - |
| 2010-12-07 Tue | $7.02M | $2.97M | +136.5% | +/-154.6% | no | NO_INCIDENT | - |
| 2010-12-08 Wed | $3.23M | $3.30M | -2.2% | +/-166.9% | no | NO_INCIDENT | - |
| 2010-12-09 Thu | $3.82M | $3.31M | +15.6% | +/-166.6% | no | NO_INCIDENT | - |
| 2010-12-10 Fri | $4.22M | $3.34M | +26.3% | +/-42.5% | yes | NO_INCIDENT | - |
| 2010-12-11 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-12-12 Sun | $1.23M | $2.20M | -43.8% | +/-44.6% | yes | NO_INCIDENT | - |
| 2010-12-13 Mon | $2.70M | $4.22M | -36.1% | +/-51.6% | yes | NO_INCIDENT | - |
| 2010-12-14 Tue | $3.22M | $5.12M | -37.2% | +/-55.9% | yes | NO_INCIDENT | - |
| 2010-12-15 Wed | $2.16M | $3.71M | -41.7% | +/-60.7% | yes | NO_INCIDENT | - |
| 2010-12-16 Thu | $3.50M | $3.49M | +0.3% | +/-64.3% | yes | NO_INCIDENT | - |
| 2010-12-17 Fri | $3.21M | $3.51M | -8.8% | +/-63.1% | yes | NO_INCIDENT | - |
| 2010-12-18 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-12-19 Sun | $0.53M | $1.98M | -73.2% | +/-63.3% | yes | REAL_CHANGE | - |
| 2010-12-20 Mon | $1.89M | $3.84M | -50.8% | +/-78.7% | yes | NO_INCIDENT | - |
| 2010-12-21 Tue | $3.31M | $4.81M | -31.2% | +/-84.0% | yes | NO_INCIDENT | - |
| 2010-12-22 Wed | $0.43M | $3.32M | -87.0% | +/-86.5% | yes | UNEXPLAINED | - |
| 2010-12-23 Thu | $0.84M | $3.49M | -75.9% | +/-88.0% | yes | NO_INCIDENT | - |
| 2010-12-24 Fri | $0.00M | $3.42M | -100.0% | +/-99.8% | yes | UNEXPLAINED | - |
| 2010-12-25 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2010-12-26 Sun | $0.00M | $1.67M | -100.0% | +/-101.7% | yes | NO_INCIDENT | - |
| 2010-12-27 Mon | $0.00M | $3.45M | -100.0% | +/-126.6% | yes | NO_INCIDENT | - |
| 2010-12-28 Tue | $0.00M | $4.41M | -100.0% | +/-146.6% | yes | NO_INCIDENT | - |
| 2010-12-29 Wed | $0.00M | $3.19M | -100.0% | +/-163.4% | yes | NO_INCIDENT | - |
| 2010-12-30 Thu | $0.00M | $1.33M | -100.0% | +/-319.5% | no | NO_INCIDENT | - |
| 2010-12-31 Fri | $0.00M | $1.10M | -100.0% | +/-368.5% | no | NO_INCIDENT | - |
| 2011-01-01 Sat | $0.00M | $0.95M | -100.0% | +/-426.5% | no | NO_INCIDENT | - |
| 2011-01-02 Sun | $0.00M | $0.70M | -100.0% | +/-500.0% | no | NO_INCIDENT | - |
| 2011-01-03 Mon | $0.00M | $0.47M | -100.0% | +/-602.3% | no | NO_INCIDENT | - |
| 2011-01-04 Tue | $1.13M | $0.47M | +140.3% | +/-602.3% | no | NO_INCIDENT | - |
| 2011-01-05 Wed | $2.31M | $0.51M | +350.7% | +/-561.1% | no | NO_INCIDENT | - |
| 2011-01-06 Thu | $2.83M | $0.54M | +423.2% | +/-556.6% | no | NO_INCIDENT | - |
| 2011-01-07 Fri | $2.03M | $0.51M | +299.1% | +/-540.7% | no | NO_INCIDENT | - |
| 2011-01-08 Sat | $0.00M | $0.59M | -100.0% | +/-503.0% | no | NO_INCIDENT | - |
| 2011-01-09 Sun | $1.11M | $0.59M | +87.1% | +/-503.0% | no | NO_INCIDENT | - |
| 2011-01-10 Mon | $1.74M | $0.67M | +158.3% | +/-440.9% | no | NO_INCIDENT | - |
| 2011-01-11 Tue | $4.83M | $0.80M | +506.4% | +/-378.5% | no | UNEXPLAINED | - |
| 2011-01-12 Wed | $1.74M | $0.80M | +118.3% | +/-378.5% | no | NO_INCIDENT | - |
| 2011-01-13 Thu | $1.47M | $0.92M | +59.9% | +/-327.9% | no | NO_INCIDENT | - |
| 2011-01-14 Fri | $3.43M | $1.02M | +234.3% | +/-286.9% | no | NO_INCIDENT | - |
| 2011-01-15 Sat | $0.00M | $1.27M | -100.0% | +/-262.9% | no | NO_INCIDENT | - |
| 2011-01-16 Sun | $0.52M | $1.27M | -58.9% | +/-262.9% | no | NO_INCIDENT | - |
| 2011-01-17 Mon | $2.13M | $1.31M | +62.7% | +/-247.4% | no | NO_INCIDENT | - |
| 2011-01-18 Tue | $6.98M | $1.46M | +378.7% | +/-212.2% | no | UNEXPLAINED | - |
| 2011-01-19 Wed | $1.89M | $1.46M | +29.3% | +/-212.2% | no | NO_INCIDENT | - |
| 2011-01-20 Thu | $1.55M | $1.59M | -2.8% | +/-179.3% | no | NO_INCIDENT | - |
| 2011-01-21 Fri | $2.37M | $1.62M | +46.2% | +/-174.4% | no | NO_INCIDENT | - |
| 2011-01-22 Sat | $0.00M | $1.63M | -100.0% | +/-174.6% | no | NO_INCIDENT | - |
| 2011-01-23 Sun | $0.76M | $1.43M | -47.0% | +/-204.2% | no | NO_INCIDENT | - |
| 2011-01-24 Mon | $1.87M | $1.34M | +40.1% | +/-217.9% | no | NO_INCIDENT | - |
| 2011-01-25 Tue | $2.10M | $1.47M | +43.1% | +/-184.5% | no | NO_INCIDENT | - |
| 2011-01-26 Wed | $1.44M | $1.54M | -6.3% | +/-177.5% | no | NO_INCIDENT | - |
| 2011-01-27 Thu | $1.73M | $1.52M | +13.7% | +/-179.7% | no | NO_INCIDENT | - |
| 2011-01-28 Fri | $1.46M | $1.52M | -3.5% | +/-179.7% | no | NO_INCIDENT | - |
| 2011-01-29 Sat | $0.00M | $1.52M | -100.0% | +/-179.8% | no | NO_INCIDENT | - |
| 2011-01-30 Sun | $0.48M | $1.27M | -62.1% | +/-193.1% | no | NO_INCIDENT | - |
| 2011-01-31 Mon | $1.73M | $1.31M | +32.0% | +/-177.6% | no | NO_INCIDENT | - |
| 2011-02-01 Tue | $2.14M | $1.39M | +53.7% | +/-161.2% | no | NO_INCIDENT | - |
| 2011-02-02 Wed | $1.57M | $1.39M | +12.3% | +/-161.3% | no | NO_INCIDENT | - |
| 2011-02-03 Thu | $1.73M | $1.52M | +14.4% | +/-152.8% | yes | NO_INCIDENT | - |
| 2011-02-04 Fri | $1.85M | $1.86M | -0.7% | +/-137.1% | yes | NO_INCIDENT | - |
| 2011-02-05 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-02-06 Sun | $0.25M | $0.57M | -55.8% | +/-119.6% | yes | NO_INCIDENT | - |
| 2011-02-07 Mon | $1.90M | $1.49M | +27.6% | +/-106.5% | yes | NO_INCIDENT | - |
| 2011-02-08 Tue | $1.52M | $1.79M | -14.8% | +/-85.2% | yes | NO_INCIDENT | - |
| 2011-02-09 Wed | $1.22M | $1.79M | -31.8% | +/-82.5% | yes | NO_INCIDENT | - |
| 2011-02-10 Thu | $1.09M | $1.86M | -41.3% | +/-81.9% | yes | NO_INCIDENT | - |
| 2011-02-11 Fri | $1.67M | $2.23M | -25.0% | +/-77.1% | yes | NO_INCIDENT | - |
| 2011-02-12 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-02-13 Sun | $0.42M | $0.62M | -33.2% | +/-78.8% | yes | NO_INCIDENT | - |
| 2011-02-14 Mon | $1.94M | $1.87M | +3.8% | +/-67.5% | yes | NO_INCIDENT | - |
| 2011-02-15 Tue | $2.93M | $1.92M | +52.3% | +/-67.3% | yes | NO_INCIDENT | - |
| 2011-02-16 Wed | $1.82M | $1.57M | +16.1% | +/-69.5% | yes | NO_INCIDENT | - |
| 2011-02-17 Thu | $1.93M | $1.51M | +27.3% | +/-69.7% | yes | NO_INCIDENT | - |
| 2011-02-18 Fri | $1.19M | $2.16M | -44.8% | +/-70.5% | yes | NO_INCIDENT | - |
| 2011-02-19 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-02-20 Sun | $0.71M | $0.49M | +45.2% | +/-64.6% | yes | NO_INCIDENT | - |
| 2011-02-21 Mon | $2.66M | $1.91M | +38.7% | +/-66.2% | yes | NO_INCIDENT | - |
| 2011-02-22 Tue | $2.38M | $2.17M | +9.3% | +/-68.7% | yes | NO_INCIDENT | - |
| 2011-02-23 Wed | $1.97M | $1.59M | +24.1% | +/-67.5% | yes | NO_INCIDENT | - |
| 2011-02-24 Thu | $1.68M | $1.61M | +4.5% | +/-68.0% | yes | NO_INCIDENT | - |
| 2011-02-25 Fri | $1.50M | $1.71M | -12.1% | +/-67.8% | yes | NO_INCIDENT | - |
| 2011-02-26 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-02-27 Sun | $0.69M | $0.52M | +32.8% | +/-64.0% | yes | NO_INCIDENT | - |
| 2011-02-28 Mon | $1.60M | $2.02M | -20.9% | +/-62.4% | yes | NO_INCIDENT | - |
| 2011-03-01 Tue | $1.93M | $2.21M | -12.9% | +/-63.4% | yes | NO_INCIDENT | - |
| 2011-03-02 Wed | $1.37M | $1.60M | -14.7% | +/-63.9% | yes | NO_INCIDENT | - |
| 2011-03-03 Thu | $2.67M | $1.63M | +63.5% | +/-64.2% | yes | NO_INCIDENT | - |
| 2011-03-04 Fri | $1.43M | $1.53M | -7.0% | +/-69.6% | yes | NO_INCIDENT | - |
| 2011-03-05 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-03-06 Sun | $0.73M | $0.51M | +43.3% | +/-69.7% | yes | NO_INCIDENT | - |
| 2011-03-07 Mon | $2.38M | $1.97M | +20.8% | +/-70.0% | yes | NO_INCIDENT | - |
| 2011-03-08 Tue | $1.83M | $2.18M | -16.2% | +/-69.7% | yes | NO_INCIDENT | - |
| 2011-03-09 Wed | $1.61M | $1.59M | +1.2% | +/-70.5% | yes | NO_INCIDENT | - |
| 2011-03-10 Thu | $1.90M | $1.82M | +4.6% | +/-70.5% | yes | NO_INCIDENT | - |
| 2011-03-11 Fri | $1.84M | $1.53M | +20.7% | +/-70.1% | yes | NO_INCIDENT | - |
| 2011-03-12 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-03-13 Sun | $0.30M | $0.56M | -46.5% | +/-70.1% | yes | NO_INCIDENT | - |
| 2011-03-14 Mon | $1.89M | $2.10M | -9.9% | +/-67.9% | yes | NO_INCIDENT | - |
| 2011-03-15 Tue | $1.70M | $2.12M | -19.6% | +/-67.9% | yes | NO_INCIDENT | - |
| 2011-03-16 Wed | $1.59M | $1.60M | -0.3% | +/-66.9% | yes | NO_INCIDENT | - |
| 2011-03-17 Thu | $2.91M | $1.85M | +56.9% | +/-65.2% | yes | NO_INCIDENT | - |
| 2011-03-18 Fri | $2.05M | $1.53M | +34.4% | +/-61.9% | yes | NO_INCIDENT | - |
| 2011-03-19 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-03-20 Sun | $1.61M | $0.57M | +183.0% | +/-63.8% | yes | UNEXPLAINED | - |
| 2011-03-21 Mon | $1.23M | $2.09M | -41.4% | +/-61.5% | yes | NO_INCIDENT | - |
| 2011-03-22 Tue | $2.32M | $2.15M | +7.8% | +/-66.1% | yes | NO_INCIDENT | - |
| 2011-03-23 Wed | $1.76M | $1.67M | +5.0% | +/-63.0% | yes | NO_INCIDENT | - |
| 2011-03-24 Thu | $2.65M | $2.22M | +19.7% | +/-62.9% | yes | NO_INCIDENT | - |
| 2011-03-25 Fri | $2.26M | $1.60M | +40.7% | +/-62.2% | yes | NO_INCIDENT | - |
| 2011-03-26 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-03-27 Sun | $0.66M | $0.61M | +9.1% | +/-61.4% | yes | NO_INCIDENT | - |
| 2011-03-28 Mon | $1.66M | $1.95M | -14.8% | +/-61.2% | yes | NO_INCIDENT | - |
| 2011-03-29 Tue | $5.05M | $2.03M | +148.9% | +/-58.2% | yes | UNEXPLAINED | - |
| 2011-03-30 Wed | $2.29M | $1.66M | +37.9% | +/-58.3% | yes | NO_INCIDENT | - |
| 2011-03-31 Thu | $2.46M | $2.36M | +4.2% | +/-60.7% | yes | NO_INCIDENT | - |
| 2011-04-01 Fri | $1.83M | $1.82M | +1.0% | +/-57.5% | yes | NO_INCIDENT | - |
| 2011-04-02 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-04-03 Sun | $0.50M | $0.60M | -17.0% | +/-56.3% | yes | NO_INCIDENT | - |
| 2011-04-04 Mon | $2.40M | $1.75M | +37.0% | +/-57.2% | yes | NO_INCIDENT | - |
| 2011-04-05 Tue | $2.17M | $1.94M | +11.8% | +/-58.3% | yes | NO_INCIDENT | - |
| 2011-04-06 Wed | $1.25M | $1.72M | -27.4% | +/-58.4% | yes | NO_INCIDENT | - |
| 2011-04-07 Thu | $1.33M | $2.52M | -47.0% | +/-59.4% | yes | NO_INCIDENT | - |
| 2011-04-08 Fri | $1.82M | $1.88M | -3.2% | +/-65.2% | yes | NO_INCIDENT | - |
| 2011-04-09 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-04-10 Sun | $0.71M | $0.55M | +30.3% | +/-63.5% | yes | NO_INCIDENT | - |
| 2011-04-11 Mon | $1.62M | $1.91M | -15.1% | +/-63.1% | yes | NO_INCIDENT | - |
| 2011-04-12 Tue | $1.85M | $2.01M | -7.8% | +/-62.3% | yes | NO_INCIDENT | - |
| 2011-04-13 Wed | $1.77M | $1.70M | +4.5% | +/-62.2% | yes | NO_INCIDENT | - |
| 2011-04-14 Thu | $2.63M | $2.25M | +16.8% | +/-62.0% | yes | NO_INCIDENT | - |
| 2011-04-15 Fri | $2.05M | $1.96M | +4.7% | +/-60.6% | yes | NO_INCIDENT | - |
| 2011-04-16 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-04-17 Sun | $0.92M | $0.54M | +69.7% | +/-60.5% | yes | UNEXPLAINED | - |
| 2011-04-18 Mon | $4.05M | $1.76M | +130.4% | +/-53.2% | yes | UNEXPLAINED | - |
| 2011-04-19 Tue | $1.76M | $2.01M | -12.3% | +/-54.3% | yes | NO_INCIDENT | - |
| 2011-04-20 Wed | $2.08M | $1.73M | +20.1% | +/-54.0% | yes | NO_INCIDENT | - |
| 2011-04-21 Thu | $2.39M | $2.40M | -0.1% | +/-53.9% | yes | NO_INCIDENT | - |
| 2011-04-22 Fri | $0.00M | $2.00M | -100.0% | +/-52.7% | yes | UNEXPLAINED | - |
| 2011-04-23 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-04-24 Sun | $0.00M | $0.62M | -100.0% | +/-53.8% | yes | UNEXPLAINED | - |
| 2011-04-25 Mon | $0.00M | $1.73M | -100.0% | +/-53.8% | yes | UNEXPLAINED | - |
| 2011-04-26 Tue | $2.28M | $2.03M | +12.4% | +/-50.1% | yes | NO_INCIDENT | - |
| 2011-04-27 Wed | $1.91M | $1.83M | +4.3% | +/-49.9% | yes | NO_INCIDENT | - |
| 2011-04-28 Thu | $1.66M | $2.29M | -27.5% | +/-49.6% | yes | NO_INCIDENT | - |
| 2011-04-29 Fri | $0.00M | $1.99M | -100.0% | +/-51.9% | yes | UNEXPLAINED | - |
| 2011-04-30 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-05-01 Sun | $0.51M | $0.62M | -17.8% | +/-52.2% | yes | NO_INCIDENT | - |
| 2011-05-02 Mon | $0.00M | $1.89M | -100.0% | +/-53.0% | yes | UNEXPLAINED | - |
| 2011-05-03 Tue | $2.58M | $1.49M | +73.0% | +/-182.1% | no | NO_INCIDENT | - |
| 2011-05-04 Wed | $2.03M | $1.55M | +31.0% | +/-183.6% | no | NO_INCIDENT | - |
| 2011-05-05 Thu | $2.15M | $1.56M | +37.6% | +/-182.7% | no | NO_INCIDENT | - |
| 2011-05-06 Fri | $2.65M | $1.53M | +73.5% | +/-180.8% | no | NO_INCIDENT | - |
| 2011-05-07 Sat | $0.00M | $1.57M | -100.0% | +/-182.8% | no | NO_INCIDENT | - |
| 2011-05-08 Sun | $1.39M | $1.57M | -11.8% | +/-182.8% | no | NO_INCIDENT | - |
| 2011-05-09 Mon | $2.04M | $1.55M | +32.2% | +/-185.9% | no | NO_INCIDENT | - |
| 2011-05-10 Tue | $3.50M | $1.54M | +126.8% | +/-186.0% | no | NO_INCIDENT | - |
| 2011-05-11 Wed | $2.48M | $1.62M | +53.0% | +/-196.7% | no | NO_INCIDENT | - |
| 2011-05-12 Thu | $4.53M | $1.80M | +151.8% | +/-163.7% | no | NO_INCIDENT | - |
| 2011-05-13 Fri | $2.24M | $1.96M | +14.5% | +/-184.6% | no | NO_INCIDENT | - |
| 2011-05-14 Sat | $0.00M | $1.98M | -100.0% | +/-182.7% | no | NO_INCIDENT | - |
| 2011-05-15 Sun | $0.72M | $1.87M | -61.2% | +/-210.9% | no | NO_INCIDENT | - |
| 2011-05-16 Mon | $2.90M | $1.92M | +51.4% | +/-195.5% | no | NO_INCIDENT | - |
| 2011-05-17 Tue | $4.04M | $2.09M | +93.5% | +/-173.7% | no | NO_INCIDENT | - |
| 2011-05-18 Wed | $2.51M | $2.19M | +14.5% | +/-178.7% | no | NO_INCIDENT | - |
| 2011-05-19 Thu | $2.59M | $2.23M | +16.4% | +/-176.1% | no | NO_INCIDENT | - |
| 2011-05-20 Fri | $1.95M | $2.26M | -13.5% | +/-174.1% | no | NO_INCIDENT | - |
| 2011-05-21 Sat | $0.00M | $2.21M | -100.0% | +/-177.7% | no | NO_INCIDENT | - |
| 2011-05-22 Sun | $1.77M | $2.21M | -19.8% | +/-177.7% | no | NO_INCIDENT | - |
| 2011-05-23 Mon | $2.53M | $2.24M | +13.2% | +/-173.7% | no | NO_INCIDENT | - |
| 2011-05-24 Tue | $2.75M | $2.83M | -3.0% | +/-87.3% | yes | NO_INCIDENT | - |
| 2011-05-25 Wed | $1.80M | $2.20M | -18.5% | +/-83.1% | yes | NO_INCIDENT | - |
| 2011-05-26 Thu | $2.48M | $2.67M | -7.2% | +/-83.8% | yes | NO_INCIDENT | - |
| 2011-05-27 Fri | $2.11M | $2.28M | -7.4% | +/-83.5% | yes | NO_INCIDENT | - |
| 2011-05-28 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-05-29 Sun | $0.55M | $1.10M | -50.0% | +/-82.0% | yes | NO_INCIDENT | - |
| 2011-05-30 Mon | $0.00M | $2.49M | -100.0% | +/-89.2% | yes | UNEXPLAINED | - |
| 2011-05-31 Tue | $1.69M | $3.03M | -44.3% | +/-89.2% | yes | NO_INCIDENT | - |
| 2011-06-01 Wed | $1.52M | $2.14M | -29.2% | +/-92.1% | yes | NO_INCIDENT | - |
| 2011-06-02 Thu | $2.41M | $2.68M | -10.2% | +/-93.5% | yes | NO_INCIDENT | - |
| 2011-06-03 Fri | $1.24M | $2.24M | -44.8% | +/-89.8% | yes | NO_INCIDENT | - |
| 2011-06-04 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-06-05 Sun | $1.88M | $0.99M | +89.7% | +/-91.9% | yes | NO_INCIDENT | - |
| 2011-06-06 Mon | $1.31M | $2.49M | -47.6% | +/-85.0% | yes | NO_INCIDENT | - |
| 2011-06-07 Tue | $2.78M | $2.91M | -4.4% | +/-87.8% | yes | NO_INCIDENT | - |
| 2011-06-08 Wed | $3.16M | $2.07M | +53.1% | +/-87.4% | yes | NO_INCIDENT | - |
| 2011-06-09 Thu | $3.41M | $2.83M | +20.4% | +/-90.0% | yes | NO_INCIDENT | - |
| 2011-06-10 Fri | $4.54M | $2.04M | +122.4% | +/-87.9% | yes | UNEXPLAINED | - |
| 2011-06-11 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-06-12 Sun | $0.91M | $1.26M | -27.6% | +/-87.9% | yes | NO_INCIDENT | - |
| 2011-06-13 Mon | $1.64M | $2.20M | -25.2% | +/-91.4% | yes | NO_INCIDENT | - |
| 2011-06-14 Tue | $2.97M | $2.95M | +0.6% | +/-92.9% | yes | NO_INCIDENT | - |
| 2011-06-15 Wed | $3.57M | $2.29M | +55.7% | +/-92.6% | yes | NO_INCIDENT | - |
| 2011-06-16 Thu | $2.50M | $3.08M | -18.9% | +/-95.4% | yes | NO_INCIDENT | - |
| 2011-06-17 Fri | $1.53M | $1.89M | -19.0% | +/-91.1% | yes | NO_INCIDENT | - |
| 2011-06-18 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-06-19 Sun | $1.63M | $1.17M | +39.6% | +/-91.0% | yes | NO_INCIDENT | - |
| 2011-06-20 Mon | $2.73M | $2.09M | +30.5% | +/-84.5% | yes | NO_INCIDENT | - |
| 2011-06-21 Tue | $1.80M | $2.85M | -36.7% | +/-83.6% | yes | NO_INCIDENT | - |
| 2011-06-22 Wed | $1.58M | $2.51M | -37.1% | +/-81.8% | yes | NO_INCIDENT | - |
| 2011-06-23 Thu | $1.81M | $2.68M | -32.3% | +/-85.8% | yes | NO_INCIDENT | - |
| 2011-06-24 Fri | $1.41M | $1.71M | -17.7% | +/-87.9% | yes | NO_INCIDENT | - |
| 2011-06-25 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-06-26 Sun | $0.51M | $1.35M | -62.1% | +/-88.1% | yes | NO_INCIDENT | - |
| 2011-06-27 Mon | $1.22M | $2.05M | -40.4% | +/-97.7% | yes | NO_INCIDENT | - |
| 2011-06-28 Tue | $2.56M | $2.40M | +6.6% | +/-100.2% | yes | NO_INCIDENT | - |
| 2011-06-29 Wed | $1.59M | $2.33M | -31.7% | +/-100.0% | yes | NO_INCIDENT | - |
| 2011-06-30 Thu | $3.20M | $2.52M | +27.1% | +/-101.2% | yes | NO_INCIDENT | - |
| 2011-07-01 Fri | $0.98M | $1.57M | -37.9% | +/-101.6% | yes | NO_INCIDENT | - |
| 2011-07-02 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-07-03 Sun | $0.43M | $1.10M | -60.7% | +/-100.5% | yes | NO_INCIDENT | - |
| 2011-07-04 Mon | $3.19M | $1.73M | +84.9% | +/-103.3% | yes | NO_INCIDENT | - |
| 2011-07-05 Tue | $2.91M | $2.36M | +23.4% | +/-105.9% | yes | NO_INCIDENT | - |
| 2011-07-06 Wed | $1.87M | $2.28M | -17.9% | +/-104.3% | yes | NO_INCIDENT | - |
| 2011-07-07 Thu | $2.30M | $2.67M | -13.7% | +/-102.4% | yes | NO_INCIDENT | - |
| 2011-07-08 Fri | $1.92M | $1.29M | +48.9% | +/-102.6% | yes | NO_INCIDENT | - |
| 2011-07-09 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-07-10 Sun | $0.42M | $1.07M | -60.4% | +/-104.2% | yes | NO_INCIDENT | - |
| 2011-07-11 Mon | $1.60M | $2.02M | -20.5% | +/-107.8% | yes | NO_INCIDENT | - |
| 2011-07-12 Tue | $1.86M | $2.61M | -28.6% | +/-106.0% | yes | NO_INCIDENT | - |
| 2011-07-13 Wed | $1.61M | $2.36M | -31.7% | +/-107.2% | yes | NO_INCIDENT | - |
| 2011-07-14 Thu | $2.41M | $2.65M | -8.9% | +/-108.2% | yes | NO_INCIDENT | - |
| 2011-07-15 Fri | $1.06M | $1.46M | -26.9% | +/-107.0% | yes | NO_INCIDENT | - |
| 2011-07-16 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-07-17 Sun | $1.23M | $0.78M | +58.0% | +/-106.5% | yes | NO_INCIDENT | - |
| 2011-07-18 Mon | $2.78M | $2.08M | +33.9% | +/-106.2% | yes | NO_INCIDENT | - |
| 2011-07-19 Tue | $3.60M | $2.42M | +48.7% | +/-104.6% | yes | NO_INCIDENT | - |
| 2011-07-20 Wed | $2.39M | $2.04M | +16.9% | +/-106.5% | yes | NO_INCIDENT | - |
| 2011-07-21 Thu | $2.36M | $2.45M | -3.4% | +/-98.3% | yes | NO_INCIDENT | - |
| 2011-07-22 Fri | $1.46M | $1.38M | +5.6% | +/-98.3% | yes | NO_INCIDENT | - |
| 2011-07-23 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-07-24 Sun | $1.96M | $0.85M | +131.8% | +/-98.3% | yes | UNEXPLAINED | - |
| 2011-07-25 Mon | $1.95M | $2.31M | -15.7% | +/-89.7% | yes | NO_INCIDENT | - |
| 2011-07-26 Tue | $1.57M | $2.55M | -38.4% | +/-90.5% | yes | NO_INCIDENT | - |
| 2011-07-27 Wed | $1.85M | $1.81M | +2.1% | +/-91.8% | yes | NO_INCIDENT | - |
| 2011-07-28 Thu | $4.05M | $2.42M | +67.4% | +/-91.3% | yes | NO_INCIDENT | - |
| 2011-07-29 Fri | $1.35M | $1.36M | -0.7% | +/-93.1% | yes | NO_INCIDENT | - |
| 2011-07-30 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-07-31 Sun | $2.41M | $0.65M | +271.3% | +/-93.2% | yes | UNEXPLAINED | - |
| 2011-08-01 Mon | $1.55M | $2.15M | -28.1% | +/-91.5% | yes | NO_INCIDENT | - |
| 2011-08-02 Tue | $1.91M | $2.50M | -23.5% | +/-89.0% | yes | NO_INCIDENT | - |
| 2011-08-03 Wed | $2.04M | $1.86M | +9.7% | +/-90.7% | yes | NO_INCIDENT | - |
| 2011-08-04 Thu | $4.76M | $2.87M | +66.2% | +/-90.1% | yes | NO_INCIDENT | - |
| 2011-08-05 Fri | $1.57M | $1.35M | +16.0% | +/-94.4% | yes | NO_INCIDENT | - |
| 2011-08-06 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-08-07 Sun | $0.55M | $0.70M | -20.7% | +/-92.2% | yes | NO_INCIDENT | - |
| 2011-08-08 Mon | $1.72M | $2.21M | -22.3% | +/-88.7% | yes | NO_INCIDENT | - |
| 2011-08-09 Tue | $2.04M | $2.37M | -13.7% | +/-85.7% | yes | NO_INCIDENT | - |
| 2011-08-10 Wed | $2.12M | $1.95M | +8.5% | +/-86.0% | yes | NO_INCIDENT | - |
| 2011-08-11 Thu | $5.31M | $3.18M | +67.0% | +/-86.0% | yes | NO_INCIDENT | - |
| 2011-08-12 Fri | $1.56M | $1.47M | +6.0% | +/-85.7% | yes | NO_INCIDENT | - |
| 2011-08-13 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-08-14 Sun | $0.42M | $0.74M | -42.8% | +/-83.9% | yes | NO_INCIDENT | - |
| 2011-08-15 Mon | $1.28M | $1.92M | -33.6% | +/-84.0% | yes | NO_INCIDENT | - |
| 2011-08-16 Tue | $1.43M | $2.20M | -35.0% | +/-86.0% | yes | NO_INCIDENT | - |
| 2011-08-17 Wed | $4.00M | $2.00M | +100.2% | +/-88.7% | yes | UNEXPLAINED | - |
| 2011-08-18 Thu | $4.09M | $3.78M | +8.1% | +/-89.3% | yes | NO_INCIDENT | - |
| 2011-08-19 Fri | $1.31M | $1.40M | -6.3% | +/-85.2% | yes | NO_INCIDENT | - |
| 2011-08-20 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-08-21 Sun | $1.10M | $0.74M | +49.9% | +/-84.0% | yes | NO_INCIDENT | - |
| 2011-08-22 Mon | $2.23M | $1.85M | +20.5% | +/-80.8% | yes | NO_INCIDENT | - |
| 2011-08-23 Tue | $1.96M | $2.11M | -7.2% | +/-76.4% | yes | NO_INCIDENT | - |
| 2011-08-24 Wed | $3.71M | $2.10M | +76.9% | +/-62.3% | yes | UNEXPLAINED | - |
| 2011-08-25 Thu | $1.80M | $4.11M | -56.3% | +/-62.8% | yes | NO_INCIDENT | - |
| 2011-08-26 Fri | $1.92M | $1.45M | +32.6% | +/-67.0% | yes | NO_INCIDENT | - |
| 2011-08-27 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-08-28 Sun | $0.81M | $0.69M | +17.1% | +/-68.9% | yes | NO_INCIDENT | - |
| 2011-08-29 Mon | $0.00M | $1.74M | -100.0% | +/-67.0% | yes | UNEXPLAINED | - |
| 2011-08-30 Tue | $2.39M | $1.78M | +34.2% | +/-68.1% | yes | NO_INCIDENT | - |
| 2011-08-31 Wed | $1.91M | $2.00M | -4.7% | +/-69.0% | yes | NO_INCIDENT | - |
| 2011-09-01 Thu | $2.79M | $4.00M | -30.2% | +/-68.9% | yes | NO_INCIDENT | - |
| 2011-09-02 Fri | $3.14M | $1.54M | +103.5% | +/-72.4% | yes | UNEXPLAINED | - |
| 2011-09-03 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-09-04 Sun | $1.27M | $0.72M | +76.1% | +/-73.2% | yes | UNEXPLAINED | - |
| 2011-09-05 Mon | $2.76M | $1.69M | +62.9% | +/-73.2% | yes | NO_INCIDENT | - |
| 2011-09-06 Tue | $2.10M | $1.95M | +7.6% | +/-76.6% | yes | NO_INCIDENT | - |
| 2011-09-07 Wed | $2.54M | $2.02M | +25.6% | +/-76.5% | yes | NO_INCIDENT | - |
| 2011-09-08 Thu | $2.01M | $3.75M | -46.3% | +/-77.4% | yes | NO_INCIDENT | - |
| 2011-09-09 Fri | $2.23M | $1.59M | +40.4% | +/-83.4% | yes | NO_INCIDENT | - |
| 2011-09-10 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-09-11 Sun | $2.64M | $0.72M | +265.4% | +/-85.2% | yes | UNEXPLAINED | - |
| 2011-09-12 Mon | $2.23M | $2.00M | +11.6% | +/-84.0% | yes | NO_INCIDENT | - |
| 2011-09-13 Tue | $4.15M | $1.98M | +109.1% | +/-82.7% | yes | UNEXPLAINED | - |
| 2011-09-14 Wed | $1.78M | $2.19M | -18.9% | +/-84.5% | yes | NO_INCIDENT | - |
| 2011-09-15 Thu | $5.88M | $3.20M | +83.8% | +/-85.3% | yes | NO_INCIDENT | - |
| 2011-09-16 Fri | $2.07M | $1.76M | +17.6% | +/-89.4% | yes | NO_INCIDENT | - |
| 2011-09-17 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-09-18 Sun | $1.17M | $0.78M | +50.9% | +/-89.0% | yes | NO_INCIDENT | - |
| 2011-09-19 Mon | $3.70M | $2.12M | +74.2% | +/-81.7% | yes | NO_INCIDENT | - |
| 2011-09-20 Tue | $8.28M | $1.97M | +320.6% | +/-80.3% | yes | UNEXPLAINED | - |
| 2011-09-21 Wed | $3.67M | $2.07M | +76.7% | +/-79.4% | yes | NO_INCIDENT | - |
| 2011-09-22 Thu | $4.53M | $3.31M | +36.8% | +/-84.6% | yes | NO_INCIDENT | - |
| 2011-09-23 Fri | $3.09M | $1.88M | +63.9% | +/-85.0% | yes | NO_INCIDENT | - |
| 2011-09-24 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-09-25 Sun | $2.39M | $1.03M | +131.9% | +/-85.4% | yes | UNEXPLAINED | - |
| 2011-09-26 Mon | $2.25M | $2.31M | -2.6% | +/-218.8% | no | NO_INCIDENT | - |
| 2011-09-27 Tue | $2.78M | $2.33M | +19.5% | +/-217.0% | no | NO_INCIDENT | - |
| 2011-09-28 Wed | $3.34M | $2.37M | +40.9% | +/-213.8% | no | NO_INCIDENT | - |
| 2011-09-29 Thu | $3.55M | $2.61M | +36.3% | +/-180.5% | no | NO_INCIDENT | - |
| 2011-09-30 Fri | $3.38M | $2.70M | +25.3% | +/-175.8% | no | NO_INCIDENT | - |
| 2011-10-01 Sat | $0.00M | $2.82M | -100.0% | +/-167.2% | no | NO_INCIDENT | - |
| 2011-10-02 Sun | $0.89M | $2.40M | -62.9% | +/-185.0% | no | NO_INCIDENT | - |
| 2011-10-03 Mon | $5.06M | $2.31M | +118.9% | +/-198.1% | no | NO_INCIDENT | - |
| 2011-10-04 Tue | $3.71M | $2.67M | +38.9% | +/-172.3% | no | NO_INCIDENT | - |
| 2011-10-05 Wed | $5.77M | $2.85M | +102.0% | +/-157.4% | no | NO_INCIDENT | - |
| 2011-10-06 Thu | $4.75M | $3.00M | +58.3% | +/-166.5% | no | NO_INCIDENT | - |
| 2011-10-07 Fri | $4.11M | $3.08M | +33.4% | +/-167.5% | no | NO_INCIDENT | - |
| 2011-10-08 Sat | $0.00M | $3.05M | -100.0% | +/-167.0% | no | NO_INCIDENT | - |
| 2011-10-09 Sun | $0.96M | $2.83M | -66.2% | +/-198.3% | no | NO_INCIDENT | - |
| 2011-10-10 Mon | $3.70M | $3.20M | +15.5% | +/-90.2% | yes | NO_INCIDENT | - |
| 2011-10-11 Tue | $4.05M | $2.86M | +41.6% | +/-88.8% | yes | NO_INCIDENT | - |
| 2011-10-12 Wed | $2.48M | $3.42M | -27.5% | +/-87.0% | yes | NO_INCIDENT | - |
| 2011-10-13 Thu | $2.88M | $4.15M | -30.4% | +/-87.4% | yes | NO_INCIDENT | - |
| 2011-10-14 Fri | $2.81M | $2.98M | -5.5% | +/-83.2% | yes | NO_INCIDENT | - |
| 2011-10-15 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-10-16 Sun | $1.70M | $1.01M | +69.2% | +/-81.4% | yes | NO_INCIDENT | - |
| 2011-10-17 Mon | $4.02M | $3.39M | +18.6% | +/-84.9% | yes | NO_INCIDENT | - |
| 2011-10-18 Tue | $3.52M | $3.52M | +0.1% | +/-80.9% | yes | NO_INCIDENT | - |
| 2011-10-19 Wed | $3.31M | $3.40M | -2.8% | +/-79.4% | yes | NO_INCIDENT | - |
| 2011-10-20 Thu | $4.80M | $4.32M | +11.2% | +/-71.9% | yes | NO_INCIDENT | - |
| 2011-10-21 Fri | $5.03M | $3.09M | +62.6% | +/-69.4% | yes | NO_INCIDENT | - |
| 2011-10-22 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-10-23 Sun | $0.98M | $1.18M | -16.8% | +/-69.4% | yes | NO_INCIDENT | - |
| 2011-10-24 Mon | $3.87M | $3.75M | +3.4% | +/-70.5% | yes | NO_INCIDENT | - |
| 2011-10-25 Tue | $3.27M | $3.52M | -7.0% | +/-70.4% | yes | NO_INCIDENT | - |
| 2011-10-26 Wed | $3.01M | $3.71M | -18.9% | +/-69.3% | yes | NO_INCIDENT | - |
| 2011-10-27 Thu | $4.54M | $4.10M | +10.7% | +/-70.7% | yes | NO_INCIDENT | - |
| 2011-10-28 Fri | $3.19M | $3.68M | -13.5% | +/-70.7% | yes | NO_INCIDENT | - |
| 2011-10-29 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-10-30 Sun | $2.71M | $1.13M | +139.8% | +/-70.5% | yes | UNEXPLAINED | - |
| 2011-10-31 Mon | $4.48M | $3.78M | +18.5% | +/-70.5% | yes | NO_INCIDENT | - |
| 2011-11-01 Tue | $2.29M | $3.47M | -34.0% | +/-65.6% | yes | NO_INCIDENT | - |
| 2011-11-02 Wed | $3.62M | $3.58M | +1.0% | +/-67.5% | yes | NO_INCIDENT | - |
| 2011-11-03 Thu | $5.01M | $4.11M | +21.9% | +/-67.0% | yes | NO_INCIDENT | - |
| 2011-11-04 Fri | $4.95M | $3.70M | +33.5% | +/-66.6% | yes | NO_INCIDENT | - |
| 2011-11-05 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-11-06 Sun | $3.37M | $1.13M | +197.9% | +/-67.2% | yes | UNEXPLAINED | - |
| 2011-11-07 Mon | $6.77M | $4.22M | +60.2% | +/-66.0% | yes | NO_INCIDENT | - |
| 2011-11-08 Tue | $4.59M | $3.37M | +36.2% | +/-71.6% | yes | NO_INCIDENT | - |
| 2011-11-09 Wed | $5.30M | $3.64M | +45.7% | +/-73.4% | yes | NO_INCIDENT | - |
| 2011-11-10 Thu | $5.67M | $4.40M | +28.9% | +/-70.7% | yes | NO_INCIDENT | - |
| 2011-11-11 Fri | $4.41M | $4.02M | +9.9% | +/-71.9% | yes | NO_INCIDENT | - |
| 2011-11-12 Sat | $0.00M | $0.00M | +0.0% | +/-0.0% | yes | NO_INCIDENT | - |
| 2011-11-13 Sun | $2.72M | $1.21M | +124.2% | +/-71.9% | yes | UNEXPLAINED | - |
| 2011-11-14 Mon | $9.19M | $3.59M | +156.0% | +/-178.9% | no | NO_INCIDENT | - |
| 2011-11-15 Tue | $4.89M | $4.02M | +21.6% | +/-192.2% | no | NO_INCIDENT | - |
| 2011-11-16 Wed | $5.28M | $4.37M | +21.0% | +/-159.7% | no | NO_INCIDENT | - |
| 2011-11-17 Thu | $4.91M | $4.43M | +11.0% | +/-158.4% | no | NO_INCIDENT | - |
| 2011-11-18 Fri | $4.16M | $4.61M | -9.8% | +/-147.1% | no | NO_INCIDENT | - |
| 2011-11-19 Sat | $0.00M | $4.65M | -100.0% | +/-145.1% | no | NO_INCIDENT | - |
| 2011-11-20 Sun | $2.84M | $4.29M | -33.8% | +/-177.7% | no | NO_INCIDENT | - |
| 2011-11-21 Mon | $4.08M | $4.14M | -1.6% | +/-185.5% | no | NO_INCIDENT | - |
| 2011-11-22 Tue | $5.25M | $4.43M | +18.3% | +/-155.1% | no | NO_INCIDENT | - |
| 2011-11-23 Wed | $6.54M | $4.33M | +51.2% | +/-153.5% | no | NO_INCIDENT | - |
| 2011-11-24 Thu | $4.12M | $4.47M | -7.7% | +/-153.6% | no | NO_INCIDENT | - |
| 2011-11-25 Fri | $4.10M | $4.38M | -6.3% | +/-155.8% | no | NO_INCIDENT | - |
| 2011-11-26 Sat | $0.00M | $4.27M | -100.0% | +/-158.0% | no | NO_INCIDENT | - |
| 2011-11-27 Sun | $1.66M | $3.95M | -57.9% | +/-189.7% | no | NO_INCIDENT | - |
| 2011-11-28 Mon | $4.63M | $4.07M | +13.6% | +/-172.7% | no | NO_INCIDENT | - |
| 2011-11-29 Tue | $5.90M | $3.75M | +57.5% | +/-150.7% | no | NO_INCIDENT | - |
| 2011-11-30 Wed | $4.93M | $3.82M | +28.9% | +/-152.7% | no | NO_INCIDENT | - |
| 2011-12-01 Thu | $4.21M | $3.79M | +11.0% | +/-152.3% | no | NO_INCIDENT | - |
| 2011-12-02 Fri | $4.63M | $3.74M | +23.6% | +/-152.7% | no | NO_INCIDENT | - |
| 2011-12-03 Sat | $0.00M | $3.78M | -100.0% | +/-152.2% | no | NO_INCIDENT | - |
| 2011-12-04 Sun | $1.98M | $3.78M | -47.7% | +/-152.2% | no | NO_INCIDENT | - |
| 2011-12-05 Mon | $7.13M | $5.83M | +22.4% | +/-65.3% | yes | NO_INCIDENT | - |
| 2011-12-06 Tue | $4.55M | $4.58M | -0.7% | +/-62.1% | yes | NO_INCIDENT | - |
| 2011-12-07 Wed | $6.09M | $5.13M | +18.6% | +/-53.5% | yes | NO_INCIDENT | - |
| 2011-12-08 Thu | $6.71M | $4.78M | +40.2% | +/-50.1% | yes | NO_INCIDENT | - |
