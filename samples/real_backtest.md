# Real-data backtest

Dataset: **NYC TLC Trip Record Data, yellow taxi trip records**, published by the NYC Taxi and Limousine Commission, no login needed.

* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-02.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-03.parquet
* https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv

Trips from 2024-01-01 to 2024-03-31: 9,554,757. The metric is the daily total of `total_amount` by pickup date. The first 35 days (2024-01-01 to 2024-02-04) are published as trusted history by assumption; the gate then judges 56 days, 2024-02-05 to 2024-03-31, one night at a time, on the DuckDB stand-in. No threshold was changed for this data. How trips map onto the pipeline tables is described in `receipts/backtest.py`.

Reproduce: `receipts backtest` (downloads about 150 MB once into `data/real/`, then runs in about 4 minutes).

## Real days, no faults planted

* Days judged: **56**
* Held: **0**
* Verdicts: NO_INCIDENT 54, REAL_CHANGE 2
* Days where the weekday-aware baseline was used: 56 of 56
* Normal range around the expected value: median plus or minus 21.7%, from 12.9% to 31.9%
* Real days called PROVEN_FAULT: **0**
* Detector firings on real days that the undo test ruled out: 5 (clock_shift on 2024-02-17 Sat, clock_shift on 2024-02-24 Sat, clock_shift on 2024-03-09 Sat, clock_shift on 2024-03-16 Sat, clock_shift on 2024-03-30 Sat)

Published as a verified real change: 2024-02-13 (-33.9%), 2024-02-27 (+26.0%).

## Planted faults on real days

| Day | Fault | Real error | Outside the normal range | Verdict | Causes named | Caught |
|---|---|---|---|---|---|---|
| 2024-02-14 Wed | CMT sends cents (x100) | +2341.2% | yes | PROVEN_FAULT | unit_scale | yes |
| 2024-02-21 Wed | Payment file F05 loaded twice | +8.3% | no | PROVEN_FAULT | duplicate_key | yes |
| 2024-03-06 Wed | CMT sends cents (x100) | +2370.6% | yes | PROVEN_FAULT | unit_scale | yes |
| 2024-03-12 Tue | Payment file F05 loaded twice | +8.3% | no | PROVEN_FAULT | duplicate_key | yes |
| 2024-03-23 Sat | CMT sends cents (x100) | +2110.8% | yes | PROVEN_FAULT | unit_scale | yes |
| 2024-03-30 Sat | Payment file F05 loaded twice | +8.2% | no | PROVEN_FAULT | duplicate_key | yes |

Caught with the right cause: **6 of 6**.

## All judged days

| Day | Revenue | Expected | Change | Normal range | Weekday baseline | Verdict | Fired |
|---|---|---|---|---|---|---|---|
| 2024-02-05 Mon | $2.44M | $2.33M | +4.6% | +/-17.6% | yes | NO_INCIDENT | - |
| 2024-02-06 Tue | $2.73M | $2.54M | +7.6% | +/-17.5% | yes | NO_INCIDENT | - |
| 2024-02-07 Wed | $2.86M | $2.70M | +5.8% | +/-16.8% | yes | NO_INCIDENT | - |
| 2024-02-08 Thu | $3.16M | $2.96M | +7.0% | +/-15.5% | yes | NO_INCIDENT | - |
| 2024-02-09 Fri | $3.02M | $2.76M | +9.4% | +/-15.5% | yes | NO_INCIDENT | - |
| 2024-02-10 Sat | $2.80M | $2.65M | +5.9% | +/-16.0% | yes | NO_INCIDENT | - |
| 2024-02-11 Sun | $2.61M | $2.32M | +12.6% | +/-15.7% | yes | NO_INCIDENT | - |
| 2024-02-12 Mon | $2.55M | $2.33M | +9.8% | +/-12.9% | yes | NO_INCIDENT | - |
| 2024-02-13 Tue | $1.73M | $2.62M | -33.9% | +/-13.3% | yes | REAL_CHANGE | - |
| 2024-02-14 Wed | $3.21M | $2.80M | +15.0% | +/-21.2% | yes | NO_INCIDENT | - |
| 2024-02-15 Thu | $3.29M | $3.02M | +8.7% | +/-21.4% | yes | NO_INCIDENT | - |
| 2024-02-16 Fri | $2.93M | $2.81M | +4.4% | +/-21.6% | yes | NO_INCIDENT | - |
| 2024-02-17 Sat | $2.63M | $2.72M | -3.2% | +/-21.7% | yes | NO_INCIDENT | clock_shift:REJECTED |
| 2024-02-18 Sun | $2.47M | $2.45M | +0.9% | +/-21.7% | yes | NO_INCIDENT | - |
| 2024-02-19 Mon | $2.22M | $2.39M | -6.9% | +/-21.7% | yes | NO_INCIDENT | - |
| 2024-02-20 Tue | $2.71M | $2.49M | +8.6% | +/-21.6% | yes | NO_INCIDENT | - |
| 2024-02-21 Wed | $2.79M | $2.92M | -4.7% | +/-21.7% | yes | NO_INCIDENT | - |
| 2024-02-22 Thu | $3.18M | $3.09M | +2.8% | +/-21.8% | yes | NO_INCIDENT | - |
| 2024-02-23 Fri | $2.79M | $2.82M | -1.0% | +/-21.7% | yes | NO_INCIDENT | - |
| 2024-02-24 Sat | $2.94M | $2.70M | +8.8% | +/-20.8% | yes | NO_INCIDENT | clock_shift:REJECTED |
| 2024-02-25 Sun | $2.62M | $2.45M | +7.1% | +/-21.1% | yes | NO_INCIDENT | - |
| 2024-02-26 Mon | $2.56M | $2.39M | +7.0% | +/-20.9% | yes | NO_INCIDENT | - |
| 2024-02-27 Tue | $3.15M | $2.50M | +26.0% | +/-21.1% | yes | REAL_CHANGE | - |
| 2024-02-28 Wed | $3.10M | $2.88M | +7.5% | +/-23.6% | yes | NO_INCIDENT | - |
| 2024-02-29 Thu | $3.58M | $3.13M | +14.1% | +/-23.7% | yes | NO_INCIDENT | - |
| 2024-03-01 Fri | $3.18M | $2.88M | +10.5% | +/-24.3% | yes | NO_INCIDENT | - |
| 2024-03-02 Sat | $3.07M | $2.76M | +11.2% | +/-24.7% | yes | NO_INCIDENT | - |
| 2024-03-03 Sun | $2.73M | $2.52M | +8.5% | +/-25.2% | yes | NO_INCIDENT | - |
| 2024-03-04 Mon | $2.68M | $2.43M | +10.5% | +/-25.4% | yes | NO_INCIDENT | - |
| 2024-03-05 Tue | $3.06M | $2.60M | +17.9% | +/-25.7% | yes | NO_INCIDENT | - |
| 2024-03-06 Wed | $3.58M | $2.93M | +22.0% | +/-26.5% | yes | NO_INCIDENT | - |
| 2024-03-07 Thu | $3.38M | $3.24M | +4.2% | +/-27.5% | yes | NO_INCIDENT | - |
| 2024-03-08 Fri | $3.27M | $2.94M | +11.1% | +/-27.1% | yes | NO_INCIDENT | - |
| 2024-03-09 Sat | $3.47M | $2.83M | +22.5% | +/-27.3% | yes | NO_INCIDENT | clock_shift:REJECTED |
| 2024-03-10 Sun | $2.90M | $2.57M | +12.9% | +/-28.6% | yes | NO_INCIDENT | - |
| 2024-03-11 Mon | $2.81M | $2.49M | +12.6% | +/-28.8% | yes | NO_INCIDENT | - |
| 2024-03-12 Tue | $3.16M | $2.68M | +18.1% | +/-29.2% | yes | NO_INCIDENT | - |
| 2024-03-13 Wed | $3.35M | $3.11M | +7.8% | +/-29.9% | yes | NO_INCIDENT | - |
| 2024-03-14 Thu | $3.87M | $3.32M | +16.7% | +/-29.6% | yes | NO_INCIDENT | - |
| 2024-03-15 Fri | $3.55M | $3.04M | +16.9% | +/-30.2% | yes | NO_INCIDENT | - |
| 2024-03-16 Sat | $3.44M | $2.98M | +15.3% | +/-31.0% | yes | NO_INCIDENT | clock_shift:REJECTED |
| 2024-03-17 Sun | $3.02M | $2.67M | +13.1% | +/-31.3% | yes | NO_INCIDENT | - |
| 2024-03-18 Mon | $2.80M | $2.57M | +9.0% | +/-31.7% | yes | NO_INCIDENT | - |
| 2024-03-19 Tue | $3.09M | $2.76M | +11.9% | +/-31.9% | yes | NO_INCIDENT | - |
| 2024-03-20 Wed | $3.29M | $3.20M | +2.7% | +/-23.8% | yes | NO_INCIDENT | - |
| 2024-03-21 Thu | $3.61M | $3.46M | +4.5% | +/-23.8% | yes | NO_INCIDENT | - |
| 2024-03-22 Fri | $3.24M | $3.15M | +2.9% | +/-23.6% | yes | NO_INCIDENT | - |
| 2024-03-23 Sat | $3.06M | $3.11M | -1.7% | +/-23.3% | yes | NO_INCIDENT | - |
| 2024-03-24 Sun | $2.92M | $2.75M | +6.3% | +/-21.6% | yes | NO_INCIDENT | - |
| 2024-03-25 Mon | $2.72M | $2.61M | +4.2% | +/-20.9% | yes | NO_INCIDENT | - |
| 2024-03-26 Tue | $3.11M | $3.03M | +2.5% | +/-19.0% | yes | NO_INCIDENT | - |
| 2024-03-27 Wed | $3.37M | $3.22M | +4.6% | +/-18.0% | yes | NO_INCIDENT | - |
| 2024-03-28 Thu | $3.76M | $3.52M | +6.8% | +/-16.3% | yes | NO_INCIDENT | - |
| 2024-03-29 Fri | $3.24M | $3.21M | +1.1% | +/-15.3% | yes | NO_INCIDENT | - |
| 2024-03-30 Sat | $2.87M | $3.19M | -10.3% | +/-13.5% | yes | NO_INCIDENT | clock_shift:REJECTED |
| 2024-03-31 Sun | $2.73M | $2.84M | -3.7% | +/-13.9% | yes | NO_INCIDENT | - |
