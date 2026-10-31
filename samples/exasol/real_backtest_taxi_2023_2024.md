# Real-data backtest, 2023 and 2024 in monthly chunks

Dataset: **NYC TLC Trip Record Data, yellow taxi trip records**, published by the NYC Taxi and Limousine Commission, no login needed.

* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-02.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-03.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-04.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-05.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-06.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-07.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-08.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-09.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-10.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-11.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-12.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-02.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-03.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-04.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-05.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-06.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-07.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-08.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-09.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-10.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-11.parquet
* https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-12.parquet
* https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv

Trips from 2023-02-01 to 2024-12-31: 76,412,486. The metric is the daily total of `total_amount` by pickup date. The first 35 days (2023-01-01 to 2023-02-04) are published as trusted history by assumption; the gate then judges 696 days, 2023-02-05 to 2024-12-31, one night at a time, on Exasol 2026.2.0-nano.3 (Python UDF: in-database). No threshold was changed for this data. How trips map onto the pipeline tables is described in `receipts/backtest.py`.

Reproduce: `python scripts/backtest_taxi_chunks.py --backend exasol` (downloads about 50 to 80 MB per month into `D:/Hackathon/data/taxi`).

## Two years in monthly chunks, in short

* Range judged: **2023-02-05 to 2024-12-31**, 696 real days in 23 monthly chunks (2023-02 to 2024-12). January 2023 and the first 4 days of February 2023 are the warm-up, published as trusted by assumption; after that every day is judged against the history the gate itself published, carried forward from chunk to chunk.
* Trips in the judged months: 76,412,486.
* Gate runs: 742 (696 real days, 46 with a planted fault).
* Real days held: **8** (2023-09-05 UNEXPLAINED, 2023-10-31 UNEXPLAINED, 2023-11-23 UNEXPLAINED, 2023-11-24 UNEXPLAINED, 2023-11-25 UNEXPLAINED, 2023-12-24 UNEXPLAINED, 2024-11-05 UNEXPLAINED, 2024-11-28 UNEXPLAINED).
* Real days published as a real change, no fault found: 34.
* Planted faults caught with the right cause: **45 of 46** (misses: 2023-05-16 Payment file F05 loaded twice UNEXPLAINED -).
* Gate run, end to end: median 3,381 ms, max 5,219 ms. Total time on Exasol including the monthly loads: 1.1 hours.
* Cross-check on the DuckDB stand-in, the 10% sample fixed before the run (every day whose ordinal is a multiple of ten, with any fault planted on it): see the comparison below. Over every gate run both backends judged: same verdict and causes in **742 of 742**.
* Planted faults, fixed before the run: in every judged month, CMT sends cents (x100) on the second Wednesday and file F05 is loaded twice on the third Tuesday.
* Each chunk holds its month and the month before; a trip from a monthly file whose pickup date falls outside those two months is not loaded.

### Source and terms

Trip files and the zone lookup from the NYC Taxi and Limousine Commission (TLC Trip Record Data, https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page). The TLC page states: "The trip data was not created by the TLC, and TLC makes no representations as to the accuracy of these data." The NYC Open Data FAQ (https://www.nyc.gov/opendata/get-started/FAQs) states: "Open Data belongs to all New Yorkers. There are no restrictions on the use of Open Data." Downloaded files, outside the repository (see also [`docs/DATA_MANIFEST.md`](../../docs/DATA_MANIFEST.md)):

| File | Bytes | SHA-256 |
|---|---|---|
| taxi_zone_lookup.csv | 12,331 | `1a99e105092230f8620f301edcca7f80d3080642ff404d28ed957d3fa222c8ed` |
| yellow_tripdata_2023-01.parquet | 47,673,370 | `32df6f67578fa86c484a6b5ef23a5281992ff085521082340b0f9e5889e9a572` |
| yellow_tripdata_2023-02.parquet | 47,748,012 | `4809e6aaac64f05a62d16a25d55713be1537ad64fc261e895eaf2d2120fe750a` |
| yellow_tripdata_2023-03.parquet | 56,127,762 | `e7d44943111b007bf0e7084863511886e0db29f862f9a96239383a1f86c6c26e` |
| yellow_tripdata_2023-04.parquet | 54,222,699 | `95c01c53c865e06489179bdecce3a59603697a1557c4d5d183c20ae13a144dc6` |
| yellow_tripdata_2023-05.parquet | 58,654,627 | `9bd7d1c557bb9d0413619ba296b4828b884852a70bd07f2230b83f080d9a8591` |
| yellow_tripdata_2023-06.parquet | 54,999,465 | `3e60e29b5df45683948b68acbfb503aa459d14162c610622585c6580fdbfc73a` |
| yellow_tripdata_2023-07.parquet | 48,361,828 | `98504ae351d920e9e0b61241f5707f90ee1588cfb199c378459234b5035805ab` |
| yellow_tripdata_2023-08.parquet | 48,152,353 | `84ce36a2f84fa14c12fd976c79a7d4f30c871f1782b08ca7c27bb76ab946e66b` |
| yellow_tripdata_2023-09.parquet | 47,895,515 | `091bf156bea5bb10bd217f5f12375f966f8789349af45d5ee4153e3e1e077a87` |
| yellow_tripdata_2023-10.parquet | 59,009,059 | `dc5f069476d350df802ed8120f3b39ec321c34cfa905381e87f608c78ca0c645` |
| yellow_tripdata_2023-11.parquet | 56,094,653 | `af203de0e73a92d640121f02a34326f25037d62380fc406237c87c2a4231ae58` |
| yellow_tripdata_2023-12.parquet | 56,804,275 | `ab4f4db11cb31484747f62eb507c13fcfaff290aaf59c13e6465dea0b1166b9c` |
| yellow_tripdata_2024-01.parquet | 49,961,641 | `c4d59da7bbc8abaeeeb1727947ee93d9891a71acb42854bd80db1571b2030510` |
| yellow_tripdata_2024-02.parquet | 50,349,284 | `c76c43c18c6c6664080dd920baab4928988d5786a6b65980792ca7cd796f9f20` |
| yellow_tripdata_2024-03.parquet | 60,078,280 | `2d4cdc8fb96726cdd3803b13b02d2e61e71d45720aff0ebc693a8bdd1f249823` |
| yellow_tripdata_2024-04.parquet | 59,133,625 | `ce37f736c7cf9e92164c850ef2b502a8f7bb590fc1804b6edbcb80293da01b89` |
| yellow_tripdata_2024-05.parquet | 62,553,128 | `1974230be2b5a3ea92e47b5eb77f32dbf1de896d81ad8df4ab6faba52749ad23` |
| yellow_tripdata_2024-06.parquet | 59,859,922 | `677cf14c8347f745b583f012fbdba072334c6c4efa17bfd6a64369f2ba30329c` |
| yellow_tripdata_2024-07.parquet | 52,299,432 | `af12d6b04daeb78550799ae99933d495b27d715b6dbb0fad9bb750a4537d3070` |
| yellow_tripdata_2024-08.parquet | 51,067,350 | `7315643dd16bafc03e27d9903edbfd35404c2550a695d0da0a3e73852d940cfb` |
| yellow_tripdata_2024-09.parquet | 61,170,186 | `2f42e4a383a6635de803001462848d0aee2b47f6ce899126805d2d05361fb843` |
| yellow_tripdata_2024-10.parquet | 64,346,071 | `d19fe05aa0b259af24eb47051735293287f1e6dc263ba04030ec1ab4c6ec2650` |
| yellow_tripdata_2024-11.parquet | 60,658,709 | `5ef321876de5007a7c147a347389133fc94fd7ac28f82eb1d57d8f2cf05cfd3b` |
| yellow_tripdata_2024-12.parquet | 61,524,085 | `41ebf7db80bebde60c58e5143c14cdf38ad04a0f3e3ff44215b3e240d55f6c78` |

### Per month

| Month | Trips | Days | Held | Real change | Planted caught | Load s | Month s |
|---|---|---|---|---|---|---|---|
| 2023-02 | 2,913,910 | 24 | 0 | 0 | 2 of 2 | 26 | 138 |
| 2023-03 | 3,403,619 | 31 | 0 | 1 | 2 of 2 | 28 | 179 |
| 2023-04 | 3,288,240 | 30 | 0 | 3 | 2 of 2 | 29 | 173 |
| 2023-05 | 3,513,645 | 31 | 0 | 7 | 1 of 2 | 31 | 180 |
| 2023-06 | 3,307,218 | 30 | 0 | 0 | 2 of 2 | 31 | 176 |
| 2023-07 | 2,907,065 | 31 | 0 | 3 | 2 of 2 | 28 | 168 |
| 2023-08 | 2,824,181 | 31 | 0 | 0 | 2 of 2 | 26 | 168 |
| 2023-09 | 2,846,698 | 30 | 1 | 6 | 2 of 2 | 26 | 158 |
| 2023-10 | 3,522,240 | 31 | 1 | 0 | 2 of 2 | 28 | 176 |
| 2023-11 | 3,339,697 | 30 | 3 | 2 | 2 of 2 | 30 | 169 |
| 2023-12 | 3,376,527 | 31 | 1 | 2 | 2 of 2 | 30 | 185 |
| 2024-01 | 2,964,612 | 31 | 0 | 0 | 2 of 2 | 26 | 165 |
| 2024-02 | 3,007,514 | 29 | 0 | 2 | 2 of 2 | 25 | 158 |
| 2024-03 | 3,582,607 | 31 | 0 | 0 | 2 of 2 | 27 | 179 |
| 2024-04 | 3,514,282 | 30 | 0 | 1 | 2 of 2 | 29 | 171 |
| 2024-05 | 3,723,801 | 31 | 0 | 2 | 2 of 2 | 30 | 181 |
| 2024-06 | 3,539,155 | 30 | 0 | 0 | 2 of 2 | 30 | 170 |
| 2024-07 | 3,076,859 | 31 | 0 | 1 | 2 of 2 | 28 | 168 |
| 2024-08 | 2,979,161 | 31 | 0 | 1 | 2 of 2 | 26 | 164 |
| 2024-09 | 3,633,013 | 30 | 0 | 2 | 2 of 2 | 27 | 170 |
| 2024-10 | 3,833,746 | 31 | 0 | 0 | 2 of 2 | 31 | 182 |
| 2024-11 | 3,646,346 | 30 | 2 | 1 | 2 of 2 | 31 | 182 |
| 2024-12 | 3,668,350 | 31 | 0 | 0 | 2 of 2 | 30 | 182 |

## Real days, no faults planted

* Days judged: **696**
* Held: **8**
* Verdicts: NO_INCIDENT 654, REAL_CHANGE 34, UNEXPLAINED 8
* Days where the weekday-aware baseline was used: 442 of 696
* Normal range around the expected value: median plus or minus 21.7%, from 7.2% to 163.8%
* Real days called PROVEN_FAULT: **0**
* Detector firings on real days that the undo test ruled out: 17 (clock_shift on 2023-04-01 Sat, unit_scale on 2023-07-16 Sun, clock_shift on 2023-10-28 Sat, clock_shift on 2023-12-31 Sun, clock_shift on 2024-01-13 Sat, clock_shift on 2024-01-20 Sat, clock_shift on 2024-01-27 Sat, clock_shift on 2024-02-03 Sat, clock_shift on 2024-02-17 Sat, clock_shift on 2024-02-24 Sat, clock_shift on 2024-03-09 Sat, clock_shift on 2024-03-16 Sat, clock_shift on 2024-03-30 Sat, clock_shift on 2024-04-06 Sat, clock_shift on 2024-06-29 Sat, clock_shift on 2024-09-07 Sat, clock_shift on 2024-10-05 Sat)

Held days (no fault was planted, so each is either a false hold or a real change the volume check did not accept):

| Day | Revenue | Expected | Change | Verdict | Detectors that fired |
|---|---|---|---|---|---|
| 2023-09-05 Tue | $3.24M | $2.69M | +20.5% | UNEXPLAINED | - |
| 2023-10-31 Tue | $2.80M | $3.33M | -15.9% | UNEXPLAINED | - |
| 2023-11-23 Thu | $1.71M | $3.86M | -55.8% | UNEXPLAINED | - |
| 2023-11-24 Fri | $2.15M | $3.66M | -41.2% | UNEXPLAINED | - |
| 2023-11-25 Sat | $2.56M | $3.40M | -24.7% | UNEXPLAINED | - |
| 2023-12-24 Sun | $1.69M | $3.40M | -50.4% | UNEXPLAINED | - |
| 2024-11-05 Tue | $2.57M | $3.68M | -30.1% | UNEXPLAINED | - |
| 2024-11-28 Thu | $2.00M | $4.01M | -50.0% | UNEXPLAINED | - |

Published as a real change, no fault found: 2023-03-13 (+12.4%), 2023-04-06 (-10.2%), 2023-04-07 (-11.1%), 2023-04-08 (-14.1%), 2023-05-15 (+12.0%), 2023-05-16 (+12.9%), 2023-05-17 (+15.2%), 2023-05-26 (-15.7%), 2023-05-27 (-19.7%), 2023-05-28 (-21.0%), 2023-05-29 (-24.2%), 2023-07-02 (-31.2%), 2023-07-03 (-36.9%), 2023-07-04 (-47.1%), 2023-09-06 (+24.5%), 2023-09-07 (+31.8%), 2023-09-08 (+42.4%), 2023-09-09 (+33.0%), 2023-09-21 (-63.3%), 2023-09-22 (-95.7%), 2023-11-19 (-12.2%), 2023-11-22 (-26.6%), 2023-12-23 (-36.1%), 2023-12-25 (-60.9%), 2024-02-13 (-33.9%), 2024-02-27 (+26.0%), 2024-04-02 (+15.8%), 2024-05-14 (+22.0%), 2024-05-25 (-30.3%), 2024-07-02 (-28.6%), 2024-08-13 (-19.4%), 2024-09-05 (+25.7%), 2024-09-06 (+33.1%), 2024-11-29 (-39.9%).

## Planted faults on real days

| Day | Fault | Real error | Outside the normal range | Verdict | Causes named | Caught |
|---|---|---|---|---|---|---|
| 2023-02-08 Wed | CMT sends cents (x100) | +2616.7% | yes | PROVEN_FAULT | unit_scale | yes |
| 2023-02-21 Tue | Payment file F05 loaded twice | +8.4% | no | PROVEN_FAULT | duplicate_key | yes |
| 2023-03-08 Wed | CMT sends cents (x100) | +2670.7% | yes | PROVEN_FAULT | unit_scale | yes |
| 2023-03-21 Tue | Payment file F05 loaded twice | +8.3% | no | PROVEN_FAULT | duplicate_key | yes |
| 2023-04-12 Wed | CMT sends cents (x100) | +2631.1% | yes | PROVEN_FAULT | unit_scale | yes |
| 2023-04-18 Tue | Payment file F05 loaded twice | +8.2% | yes | PROVEN_FAULT | duplicate_key | yes |
| 2023-05-10 Wed | CMT sends cents (x100) | +2556.7% | yes | PROVEN_FAULT | unit_scale | yes |
| 2023-05-16 Tue | Payment file F05 loaded twice | +8.3% | yes | UNEXPLAINED | none | held, cause not proven |
| 2023-06-14 Wed | CMT sends cents (x100) | +2533.2% | yes | PROVEN_FAULT | unit_scale | yes |
| 2023-06-20 Tue | Payment file F05 loaded twice | +8.3% | no | PROVEN_FAULT | duplicate_key | yes |
| 2023-07-12 Wed | CMT sends cents (x100) | +2458.1% | yes | PROVEN_FAULT | unit_scale | yes |
| 2023-07-18 Tue | Payment file F05 loaded twice | +8.3% | no | PROVEN_FAULT | duplicate_key | yes |
| 2023-08-09 Wed | CMT sends cents (x100) | +2433.1% | yes | PROVEN_FAULT | unit_scale | yes |
| 2023-08-15 Tue | Payment file F05 loaded twice | +8.3% | no | PROVEN_FAULT | duplicate_key | yes |
| 2023-09-13 Wed | CMT sends cents (x100) | +2440.7% | yes | PROVEN_FAULT | unit_scale | yes |
| 2023-09-19 Tue | Payment file F05 loaded twice | +8.4% | no | PROVEN_FAULT | duplicate_key | yes |
| 2023-10-11 Wed | CMT sends cents (x100) | +2427.1% | yes | PROVEN_FAULT | unit_scale | yes |
| 2023-10-17 Tue | Payment file F05 loaded twice | +8.3% | no | PROVEN_FAULT | duplicate_key | yes |
| 2023-11-08 Wed | CMT sends cents (x100) | +2412.7% | yes | PROVEN_FAULT | unit_scale | yes |
| 2023-11-21 Tue | Payment file F05 loaded twice | +8.3% | no | PROVEN_FAULT | duplicate_key | yes |
| 2023-12-13 Wed | CMT sends cents (x100) | +2410.0% | yes | PROVEN_FAULT | unit_scale | yes |
| 2023-12-19 Tue | Payment file F05 loaded twice | +8.3% | no | PROVEN_FAULT | duplicate_key | yes |
| 2024-01-10 Wed | CMT sends cents (x100) | +2381.4% | yes | PROVEN_FAULT | unit_scale | yes |
| 2024-01-16 Tue | Payment file F05 loaded twice | +8.3% | no | PROVEN_FAULT | duplicate_key | yes |
| 2024-02-14 Wed | CMT sends cents (x100) | +2341.2% | yes | PROVEN_FAULT | unit_scale | yes |
| 2024-02-20 Tue | Payment file F05 loaded twice | +8.3% | no | PROVEN_FAULT | duplicate_key | yes |
| 2024-03-13 Wed | CMT sends cents (x100) | +2415.4% | yes | PROVEN_FAULT | unit_scale | yes |
| 2024-03-19 Tue | Payment file F05 loaded twice | +8.4% | no | PROVEN_FAULT | duplicate_key | yes |
| 2024-04-10 Wed | CMT sends cents (x100) | +2522.2% | yes | PROVEN_FAULT | unit_scale | yes |
| 2024-04-16 Tue | Payment file F05 loaded twice | +8.3% | no | PROVEN_FAULT | duplicate_key | yes |
| 2024-05-08 Wed | CMT sends cents (x100) | +2330.2% | yes | PROVEN_FAULT | unit_scale | yes |
| 2024-05-21 Tue | Payment file F05 loaded twice | +8.4% | no | PROVEN_FAULT | duplicate_key | yes |
| 2024-06-12 Wed | CMT sends cents (x100) | +2337.7% | yes | PROVEN_FAULT | unit_scale | yes |
| 2024-06-18 Tue | Payment file F05 loaded twice | +8.4% | no | PROVEN_FAULT | duplicate_key | yes |
| 2024-07-10 Wed | CMT sends cents (x100) | +2235.6% | yes | PROVEN_FAULT | unit_scale | yes |
| 2024-07-16 Tue | Payment file F05 loaded twice | +8.3% | no | PROVEN_FAULT | duplicate_key | yes |
| 2024-08-14 Wed | CMT sends cents (x100) | +2249.8% | yes | PROVEN_FAULT | unit_scale | yes |
| 2024-08-20 Tue | Payment file F05 loaded twice | +8.4% | no | PROVEN_FAULT | duplicate_key | yes |
| 2024-09-11 Wed | CMT sends cents (x100) | +2246.3% | yes | PROVEN_FAULT | unit_scale | yes |
| 2024-09-17 Tue | Payment file F05 loaded twice | +8.3% | no | PROVEN_FAULT | duplicate_key | yes |
| 2024-10-09 Wed | CMT sends cents (x100) | +2236.4% | yes | PROVEN_FAULT | unit_scale | yes |
| 2024-10-15 Tue | Payment file F05 loaded twice | +8.3% | no | PROVEN_FAULT | duplicate_key | yes |
| 2024-11-13 Wed | CMT sends cents (x100) | +2240.6% | yes | PROVEN_FAULT | unit_scale | yes |
| 2024-11-19 Tue | Payment file F05 loaded twice | +8.5% | no | PROVEN_FAULT | duplicate_key | yes |
| 2024-12-11 Wed | CMT sends cents (x100) | +2179.4% | yes | PROVEN_FAULT | unit_scale | yes |
| 2024-12-17 Tue | Payment file F05 loaded twice | +8.3% | no | PROVEN_FAULT | duplicate_key | yes |

Caught with the right cause: **45 of 46**.

## Timings

Measured on Exasol 2026.2.0-nano.3 (Python UDF: in-database), from the client. Building the database (adapter, load, pipeline, UDF, warm-up history) took 656 s.

| Measure | Median | Max |
|---|---|---|
| Gate run, end to end (742 runs) | 3,381 ms | 5,219 ms |
| Of which inside the database (sum over statements) | 2,708 ms | 5,095 ms |
| SQL statements per gate run | 19 | |

## Compared with the run on the DuckDB stand-in

* Gate runs compared: 75 (same days, same planted faults)
* Same verdict and same causes: **75 of 75**
* Same detectors fired: 75 of 75
* Largest relative difference in the metric value between the two databases: 9.67e-14

## All judged days

| Day | Revenue | Expected | Change | Normal range | Weekday baseline | Verdict | Fired |
|---|---|---|---|---|---|---|---|
| 2023-02-05 Sun | $2.37M | $2.46M | -3.9% | +/-13.7% | yes | NO_INCIDENT | - |
| 2023-02-06 Mon | $2.53M | $2.31M | +9.7% | +/-13.7% | yes | NO_INCIDENT | - |
| 2023-02-07 Tue | $2.79M | $2.68M | +4.0% | +/-12.5% | yes | NO_INCIDENT | - |
| 2023-02-08 Wed | $2.89M | $2.80M | +3.3% | +/-12.0% | yes | NO_INCIDENT | - |
| 2023-02-09 Thu | $3.19M | $3.01M | +5.9% | +/-11.7% | yes | NO_INCIDENT | - |
| 2023-02-10 Fri | $3.13M | $2.96M | +5.8% | +/-10.8% | yes | NO_INCIDENT | - |
| 2023-02-11 Sat | $2.93M | $2.73M | +7.3% | +/-10.1% | yes | NO_INCIDENT | - |
| 2023-02-12 Sun | $2.59M | $2.47M | +5.0% | +/-10.4% | yes | NO_INCIDENT | - |
| 2023-02-13 Mon | $2.55M | $2.40M | +6.3% | +/-10.5% | yes | NO_INCIDENT | - |
| 2023-02-14 Tue | $2.90M | $2.74M | +5.6% | +/-10.9% | yes | NO_INCIDENT | - |
| 2023-02-15 Wed | $3.12M | $2.84M | +9.8% | +/-10.9% | yes | NO_INCIDENT | - |
| 2023-02-16 Thu | $3.11M | $3.10M | +0.5% | +/-11.6% | yes | NO_INCIDENT | - |
| 2023-02-17 Fri | $3.07M | $3.03M | +1.1% | +/-11.6% | yes | NO_INCIDENT | - |
| 2023-02-18 Sat | $2.74M | $2.78M | -1.4% | +/-11.5% | yes | NO_INCIDENT | - |
| 2023-02-19 Sun | $2.49M | $2.50M | -0.4% | +/-11.1% | yes | NO_INCIDENT | - |
| 2023-02-20 Mon | $2.35M | $2.44M | -3.7% | +/-10.7% | yes | NO_INCIDENT | - |
| 2023-02-21 Tue | $2.77M | $2.79M | -0.9% | +/-10.6% | yes | NO_INCIDENT | - |
| 2023-02-22 Wed | $3.03M | $2.91M | +4.1% | +/-10.5% | yes | NO_INCIDENT | - |
| 2023-02-23 Thu | $3.18M | $3.10M | +2.7% | +/-10.6% | yes | NO_INCIDENT | - |
| 2023-02-24 Fri | $3.13M | $3.03M | +3.5% | +/-10.7% | yes | NO_INCIDENT | - |
| 2023-02-25 Sat | $2.92M | $2.74M | +6.6% | +/-10.7% | yes | NO_INCIDENT | - |
| 2023-02-26 Sun | $2.60M | $2.47M | +5.4% | +/-11.0% | yes | NO_INCIDENT | - |
| 2023-02-27 Mon | $2.62M | $2.44M | +7.3% | +/-11.3% | yes | NO_INCIDENT | - |
| 2023-02-28 Tue | $2.73M | $2.78M | -1.8% | +/-11.8% | yes | NO_INCIDENT | - |
| 2023-03-01 Wed | $3.19M | $2.94M | +8.5% | +/-11.8% | yes | NO_INCIDENT | - |
| 2023-03-02 Thu | $3.31M | $3.12M | +5.9% | +/-12.0% | yes | NO_INCIDENT | - |
| 2023-03-03 Fri | $3.14M | $3.06M | +2.7% | +/-12.3% | yes | NO_INCIDENT | - |
| 2023-03-04 Sat | $2.90M | $2.76M | +5.1% | +/-12.3% | yes | NO_INCIDENT | - |
| 2023-03-05 Sun | $2.76M | $2.50M | +10.3% | +/-12.4% | yes | NO_INCIDENT | - |
| 2023-03-06 Mon | $2.68M | $2.48M | +8.4% | +/-13.1% | yes | NO_INCIDENT | - |
| 2023-03-07 Tue | $3.06M | $2.77M | +10.3% | +/-12.9% | yes | NO_INCIDENT | - |
| 2023-03-08 Wed | $3.26M | $3.01M | +8.4% | +/-13.5% | yes | NO_INCIDENT | - |
| 2023-03-09 Thu | $3.39M | $3.16M | +7.5% | +/-13.3% | yes | NO_INCIDENT | - |
| 2023-03-10 Fri | $3.38M | $3.09M | +9.1% | +/-13.3% | yes | NO_INCIDENT | - |
| 2023-03-11 Sat | $2.86M | $2.79M | +2.8% | +/-13.7% | yes | NO_INCIDENT | - |
| 2023-03-12 Sun | $2.72M | $2.56M | +6.3% | +/-11.7% | yes | NO_INCIDENT | - |
| 2023-03-13 Mon | $2.86M | $2.55M | +12.4% | +/-11.1% | yes | REAL_CHANGE | - |
| 2023-03-14 Tue | $2.91M | $2.85M | +2.4% | +/-12.3% | yes | NO_INCIDENT | - |
| 2023-03-15 Wed | $3.43M | $3.10M | +10.8% | +/-12.2% | yes | NO_INCIDENT | - |
| 2023-03-16 Thu | $3.61M | $3.24M | +11.4% | +/-12.3% | yes | NO_INCIDENT | - |
| 2023-03-17 Fri | $3.29M | $3.17M | +3.7% | +/-13.1% | yes | NO_INCIDENT | - |
| 2023-03-18 Sat | $3.20M | $2.87M | +11.6% | +/-13.2% | yes | NO_INCIDENT | - |
| 2023-03-19 Sun | $2.97M | $2.63M | +12.9% | +/-14.2% | yes | NO_INCIDENT | - |
| 2023-03-20 Mon | $2.75M | $2.61M | +5.4% | +/-15.2% | yes | NO_INCIDENT | - |
| 2023-03-21 Tue | $2.88M | $2.87M | +0.4% | +/-15.2% | yes | NO_INCIDENT | - |
| 2023-03-22 Wed | $3.01M | $3.20M | -6.2% | +/-15.2% | yes | NO_INCIDENT | - |
| 2023-03-23 Thu | $3.29M | $3.32M | -0.9% | +/-15.5% | yes | NO_INCIDENT | - |
| 2023-03-24 Fri | $3.13M | $3.20M | -2.2% | +/-15.1% | yes | NO_INCIDENT | - |
| 2023-03-25 Sat | $2.98M | $2.93M | +1.8% | +/-14.9% | yes | NO_INCIDENT | - |
| 2023-03-26 Sun | $2.79M | $2.71M | +3.1% | +/-14.5% | yes | NO_INCIDENT | - |
| 2023-03-27 Mon | $2.79M | $2.65M | +5.3% | +/-13.7% | yes | NO_INCIDENT | - |
| 2023-03-28 Tue | $2.94M | $2.87M | +2.3% | +/-12.0% | yes | NO_INCIDENT | - |
| 2023-03-29 Wed | $3.16M | $3.18M | -0.8% | +/-11.9% | yes | NO_INCIDENT | - |
| 2023-03-30 Thu | $3.43M | $3.36M | +2.2% | +/-11.5% | yes | NO_INCIDENT | - |
| 2023-03-31 Fri | $3.29M | $3.21M | +2.2% | +/-11.2% | yes | NO_INCIDENT | - |
| 2023-04-01 Sat | $3.07M | $2.97M | +3.1% | +/-11.1% | yes | NO_INCIDENT | clock_shift:REJECTED |
| 2023-04-02 Sun | $2.89M | $2.77M | +4.5% | +/-11.1% | yes | NO_INCIDENT | - |
| 2023-04-03 Mon | $2.81M | $2.74M | +2.5% | +/-10.6% | yes | NO_INCIDENT | - |
| 2023-04-04 Tue | $2.99M | $2.90M | +2.8% | +/-10.3% | yes | NO_INCIDENT | - |
| 2023-04-05 Wed | $3.23M | $3.21M | +0.7% | +/-9.7% | yes | NO_INCIDENT | - |
| 2023-04-06 Thu | $3.06M | $3.41M | -10.2% | +/-9.7% | yes | REAL_CHANGE | - |
| 2023-04-07 Fri | $2.88M | $3.24M | -11.1% | +/-10.8% | yes | REAL_CHANGE | - |
| 2023-04-08 Sat | $2.58M | $3.00M | -14.1% | +/-12.0% | yes | REAL_CHANGE | - |
| 2023-04-09 Sun | $2.53M | $2.83M | -10.4% | +/-13.8% | yes | NO_INCIDENT | - |
| 2023-04-10 Mon | $2.68M | $2.78M | -3.8% | +/-14.6% | yes | NO_INCIDENT | - |
| 2023-04-11 Tue | $3.00M | $2.96M | +1.4% | +/-14.6% | yes | NO_INCIDENT | - |
| 2023-04-12 Wed | $3.16M | $3.22M | -1.9% | +/-14.6% | yes | NO_INCIDENT | - |
| 2023-04-13 Thu | $3.47M | $3.36M | +3.5% | +/-14.6% | yes | NO_INCIDENT | - |
| 2023-04-14 Fri | $3.49M | $3.19M | +9.2% | +/-14.6% | yes | NO_INCIDENT | - |
| 2023-04-15 Sat | $3.20M | $2.94M | +8.9% | +/-15.0% | yes | NO_INCIDENT | - |
| 2023-04-16 Sun | $2.90M | $2.78M | +4.3% | +/-15.3% | yes | NO_INCIDENT | - |
| 2023-04-17 Mon | $2.94M | $2.78M | +5.7% | +/-15.3% | yes | NO_INCIDENT | - |
| 2023-04-18 Tue | $3.31M | $2.94M | +12.4% | +/-15.5% | yes | NO_INCIDENT | - |
| 2023-04-19 Wed | $3.38M | $3.20M | +5.8% | +/-16.4% | yes | NO_INCIDENT | - |
| 2023-04-20 Thu | $3.74M | $3.37M | +10.8% | +/-16.3% | yes | NO_INCIDENT | - |
| 2023-04-21 Fri | $3.35M | $3.22M | +4.2% | +/-16.7% | yes | NO_INCIDENT | - |
| 2023-04-22 Sat | $3.12M | $3.00M | +4.0% | +/-16.8% | yes | NO_INCIDENT | - |
| 2023-04-23 Sun | $3.00M | $2.82M | +6.6% | +/-16.6% | yes | NO_INCIDENT | - |
| 2023-04-24 Mon | $3.04M | $2.79M | +8.6% | +/-16.7% | yes | NO_INCIDENT | - |
| 2023-04-25 Tue | $3.31M | $3.02M | +9.4% | +/-17.1% | yes | NO_INCIDENT | - |
| 2023-04-26 Wed | $3.49M | $3.19M | +9.5% | +/-17.2% | yes | NO_INCIDENT | - |
| 2023-04-27 Thu | $3.71M | $3.40M | +9.2% | +/-17.3% | yes | NO_INCIDENT | - |
| 2023-04-28 Fri | $3.55M | $3.23M | +10.0% | +/-17.5% | yes | NO_INCIDENT | - |
| 2023-04-29 Sat | $3.01M | $2.99M | +0.6% | +/-17.9% | yes | NO_INCIDENT | - |
| 2023-04-30 Sun | $2.84M | $2.82M | +0.6% | +/-17.9% | yes | NO_INCIDENT | - |
| 2023-05-01 Mon | $3.10M | $2.85M | +8.9% | +/-17.8% | yes | NO_INCIDENT | - |
| 2023-05-02 Tue | $3.31M | $3.11M | +6.5% | +/-18.2% | yes | NO_INCIDENT | - |
| 2023-05-03 Wed | $3.44M | $3.28M | +4.8% | +/-18.0% | yes | NO_INCIDENT | - |
| 2023-05-04 Thu | $3.69M | $3.48M | +5.9% | +/-17.9% | yes | NO_INCIDENT | - |
| 2023-05-05 Fri | $3.48M | $3.31M | +5.2% | +/-18.0% | yes | NO_INCIDENT | - |
| 2023-05-06 Sat | $3.23M | $2.99M | +7.8% | +/-18.1% | yes | NO_INCIDENT | - |
| 2023-05-07 Sun | $3.04M | $2.83M | +7.5% | +/-18.4% | yes | NO_INCIDENT | - |
| 2023-05-08 Mon | $2.97M | $2.91M | +2.0% | +/-18.7% | yes | NO_INCIDENT | - |
| 2023-05-09 Tue | $3.34M | $3.18M | +5.1% | +/-18.6% | yes | NO_INCIDENT | - |
| 2023-05-10 Wed | $3.61M | $3.34M | +8.0% | +/-18.3% | yes | NO_INCIDENT | - |
| 2023-05-11 Thu | $3.84M | $3.53M | +8.5% | +/-18.5% | yes | NO_INCIDENT | - |
| 2023-05-12 Fri | $3.69M | $3.35M | +10.0% | +/-17.0% | yes | NO_INCIDENT | - |
| 2023-05-13 Sat | $3.30M | $3.03M | +9.1% | +/-15.3% | yes | NO_INCIDENT | - |
| 2023-05-14 Sun | $3.21M | $2.86M | +12.1% | +/-12.9% | yes | NO_INCIDENT | - |
| 2023-05-15 Mon | $3.30M | $2.95M | +12.0% | +/-11.8% | yes | REAL_CHANGE | - |
| 2023-05-16 Tue | $3.67M | $3.25M | +12.9% | +/-11.4% | yes | REAL_CHANGE | - |
| 2023-05-17 Wed | $3.93M | $3.42M | +15.2% | +/-11.5% | yes | REAL_CHANGE | - |
| 2023-05-18 Thu | $4.09M | $3.69M | +10.9% | +/-12.1% | yes | NO_INCIDENT | - |
| 2023-05-19 Fri | $3.69M | $3.51M | +5.0% | +/-12.3% | yes | NO_INCIDENT | - |
| 2023-05-20 Sat | $3.32M | $3.17M | +4.6% | +/-12.5% | yes | NO_INCIDENT | - |
| 2023-05-21 Sun | $3.20M | $3.00M | +6.6% | +/-12.7% | yes | NO_INCIDENT | - |
| 2023-05-22 Mon | $3.10M | $3.07M | +0.9% | +/-12.8% | yes | NO_INCIDENT | - |
| 2023-05-23 Tue | $3.34M | $3.39M | -1.4% | +/-12.5% | yes | NO_INCIDENT | - |
| 2023-05-24 Wed | $3.59M | $3.57M | +0.6% | +/-12.5% | yes | NO_INCIDENT | - |
| 2023-05-25 Thu | $3.47M | $3.81M | -8.9% | +/-12.1% | yes | NO_INCIDENT | - |
| 2023-05-26 Fri | $2.99M | $3.55M | -15.7% | +/-12.8% | yes | REAL_CHANGE | - |
| 2023-05-27 Sat | $2.57M | $3.20M | -19.7% | +/-14.7% | yes | REAL_CHANGE | - |
| 2023-05-28 Sun | $2.42M | $3.06M | -21.0% | +/-17.5% | yes | REAL_CHANGE | - |
| 2023-05-29 Mon | $2.35M | $3.10M | -24.2% | +/-20.3% | yes | REAL_CHANGE | - |
| 2023-05-30 Tue | $2.98M | $3.39M | -12.3% | +/-23.4% | yes | NO_INCIDENT | - |
| 2023-05-31 Wed | $3.30M | $3.61M | -8.5% | +/-24.2% | yes | NO_INCIDENT | - |
| 2023-06-01 Thu | $3.63M | $3.76M | -3.5% | +/-24.5% | yes | NO_INCIDENT | - |
| 2023-06-02 Fri | $3.36M | $3.48M | -3.3% | +/-24.5% | yes | NO_INCIDENT | - |
| 2023-06-03 Sat | $3.18M | $3.08M | +3.0% | +/-24.6% | yes | NO_INCIDENT | - |
| 2023-06-04 Sun | $3.09M | $2.94M | +5.0% | +/-24.5% | yes | NO_INCIDENT | - |
| 2023-06-05 Mon | $3.09M | $2.96M | +4.1% | +/-24.4% | yes | NO_INCIDENT | - |
| 2023-06-06 Tue | $3.50M | $3.33M | +5.2% | +/-24.4% | yes | NO_INCIDENT | - |
| 2023-06-07 Wed | $3.60M | $3.58M | +0.8% | +/-24.5% | yes | NO_INCIDENT | - |
| 2023-06-08 Thu | $3.45M | $3.74M | -7.7% | +/-24.4% | yes | NO_INCIDENT | - |
| 2023-06-09 Fri | $3.30M | $3.44M | -4.1% | +/-24.6% | yes | NO_INCIDENT | - |
| 2023-06-10 Sat | $3.03M | $3.12M | -2.7% | +/-24.7% | yes | NO_INCIDENT | - |
| 2023-06-11 Sun | $3.00M | $2.99M | +0.3% | +/-24.7% | yes | NO_INCIDENT | - |
| 2023-06-12 Mon | $3.53M | $2.96M | +19.3% | +/-24.7% | yes | NO_INCIDENT | - |
| 2023-06-13 Tue | $3.41M | $3.37M | +1.2% | +/-25.9% | yes | NO_INCIDENT | - |
| 2023-06-14 Wed | $3.54M | $3.61M | -1.9% | +/-25.9% | yes | NO_INCIDENT | - |
| 2023-06-15 Thu | $3.77M | $3.70M | +2.0% | +/-25.9% | yes | NO_INCIDENT | - |
| 2023-06-16 Fri | $3.29M | $3.41M | -3.4% | +/-25.9% | yes | NO_INCIDENT | - |
| 2023-06-17 Sat | $2.87M | $3.08M | -6.9% | +/-25.5% | yes | NO_INCIDENT | - |
| 2023-06-18 Sun | $2.71M | $2.98M | -9.0% | +/-25.4% | yes | NO_INCIDENT | - |
| 2023-06-19 Mon | $2.67M | $3.07M | -13.1% | +/-25.4% | yes | NO_INCIDENT | - |
| 2023-06-20 Tue | $3.25M | $3.38M | -3.8% | +/-25.9% | yes | NO_INCIDENT | - |
| 2023-06-21 Wed | $3.43M | $3.60M | -4.7% | +/-25.5% | yes | NO_INCIDENT | - |
| 2023-06-22 Thu | $3.55M | $3.68M | -3.6% | +/-25.0% | yes | NO_INCIDENT | - |
| 2023-06-23 Fri | $3.33M | $3.33M | +0.0% | +/-24.2% | yes | NO_INCIDENT | - |
| 2023-06-24 Sat | $3.02M | $2.99M | +0.9% | +/-23.5% | yes | NO_INCIDENT | - |
| 2023-06-25 Sun | $2.92M | $2.88M | +1.4% | +/-22.7% | yes | NO_INCIDENT | - |
| 2023-06-26 Mon | $3.04M | $2.95M | +3.1% | +/-22.1% | yes | NO_INCIDENT | - |
| 2023-06-27 Tue | $3.23M | $3.30M | -1.8% | +/-22.0% | yes | NO_INCIDENT | - |
| 2023-06-28 Wed | $3.12M | $3.49M | -10.6% | +/-22.0% | yes | NO_INCIDENT | - |
| 2023-06-29 Thu | $3.22M | $3.58M | -9.9% | +/-22.4% | yes | NO_INCIDENT | - |
| 2023-06-30 Fri | $2.79M | $3.26M | -14.2% | +/-22.9% | yes | NO_INCIDENT | - |
| 2023-07-01 Sat | $2.26M | $2.93M | -23.1% | +/-23.6% | yes | NO_INCIDENT | - |
| 2023-07-02 Sun | $1.95M | $2.83M | -31.2% | +/-25.6% | yes | REAL_CHANGE | - |
| 2023-07-03 Mon | $1.85M | $2.93M | -36.9% | +/-29.3% | yes | REAL_CHANGE | - |
| 2023-07-04 Tue | $1.73M | $3.27M | -47.1% | +/-33.5% | yes | REAL_CHANGE | - |
| 2023-07-05 Wed | $2.46M | $2.82M | -12.7% | +/-62.9% | no | NO_INCIDENT | - |
| 2023-07-06 Thu | $2.66M | $2.75M | -3.1% | +/-62.4% | no | NO_INCIDENT | - |
| 2023-07-07 Fri | $2.55M | $2.69M | -4.9% | +/-58.8% | no | NO_INCIDENT | - |
| 2023-07-08 Sat | $2.50M | $2.63M | -5.0% | +/-56.6% | no | NO_INCIDENT | - |
| 2023-07-09 Sun | $2.32M | $2.59M | -10.4% | +/-56.1% | no | NO_INCIDENT | - |
| 2023-07-10 Mon | $2.69M | $2.55M | +5.5% | +/-56.5% | no | NO_INCIDENT | - |
| 2023-07-11 Tue | $3.02M | $2.53M | +19.7% | +/-55.0% | no | NO_INCIDENT | - |
| 2023-07-12 Wed | $3.14M | $2.51M | +25.0% | +/-52.9% | no | NO_INCIDENT | - |
| 2023-07-13 Thu | $3.23M | $2.51M | +28.7% | +/-53.0% | no | NO_INCIDENT | - |
| 2023-07-14 Fri | $2.85M | $2.51M | +13.5% | +/-53.1% | no | NO_INCIDENT | - |
| 2023-07-15 Sat | $2.78M | $2.52M | +10.6% | +/-53.4% | no | NO_INCIDENT | - |
| 2023-07-16 Sun | $2.43M | $2.55M | -4.8% | +/-52.5% | no | NO_INCIDENT | unit_scale:REJECTED |
| 2023-07-17 Mon | $2.86M | $2.59M | +10.4% | +/-48.2% | no | NO_INCIDENT | - |
| 2023-07-18 Tue | $3.09M | $2.66M | +16.0% | +/-41.3% | no | NO_INCIDENT | - |
| 2023-07-19 Wed | $3.23M | $2.76M | +17.1% | +/-30.1% | no | NO_INCIDENT | - |
| 2023-07-20 Thu | $3.25M | $2.81M | +15.7% | +/-30.8% | no | NO_INCIDENT | - |
| 2023-07-21 Fri | $2.89M | $2.85M | +1.2% | +/-32.2% | no | NO_INCIDENT | - |
| 2023-07-22 Sat | $2.75M | $2.88M | -4.6% | +/-30.7% | no | NO_INCIDENT | - |
| 2023-07-23 Sun | $2.57M | $2.89M | -11.1% | +/-28.8% | no | NO_INCIDENT | - |
| 2023-07-24 Mon | $2.63M | $2.91M | -9.6% | +/-25.5% | no | NO_INCIDENT | - |
| 2023-07-25 Tue | $2.95M | $2.91M | +1.4% | +/-26.0% | no | NO_INCIDENT | - |
| 2023-07-26 Wed | $3.21M | $2.90M | +10.5% | +/-25.8% | no | NO_INCIDENT | - |
| 2023-07-27 Thu | $3.20M | $2.91M | +10.2% | +/-26.3% | no | NO_INCIDENT | - |
| 2023-07-28 Fri | $2.96M | $2.91M | +1.8% | +/-26.1% | no | NO_INCIDENT | - |
| 2023-07-29 Sat | $2.63M | $2.91M | -9.6% | +/-26.0% | no | NO_INCIDENT | - |
| 2023-07-30 Sun | $2.68M | $2.90M | -7.7% | +/-27.0% | no | NO_INCIDENT | - |
| 2023-07-31 Mon | $2.56M | $2.92M | -12.4% | +/-24.2% | no | NO_INCIDENT | - |
| 2023-08-01 Tue | $2.81M | $2.90M | -3.0% | +/-26.2% | no | NO_INCIDENT | - |
| 2023-08-02 Wed | $2.87M | $2.88M | -0.2% | +/-25.9% | no | NO_INCIDENT | - |
| 2023-08-03 Thu | $2.95M | $2.85M | +3.5% | +/-24.1% | no | NO_INCIDENT | - |
| 2023-08-04 Fri | $2.67M | $2.83M | -5.8% | +/-21.6% | no | NO_INCIDENT | - |
| 2023-08-05 Sat | $2.51M | $2.82M | -11.0% | +/-22.1% | no | NO_INCIDENT | - |
| 2023-08-06 Sun | $2.39M | $2.80M | -14.8% | +/-23.7% | no | NO_INCIDENT | - |
| 2023-08-07 Mon | $2.42M | $2.79M | -13.1% | +/-25.8% | no | NO_INCIDENT | - |
| 2023-08-08 Tue | $2.76M | $2.77M | -0.3% | +/-27.6% | no | NO_INCIDENT | - |
| 2023-08-09 Wed | $2.82M | $2.98M | -5.4% | +/-18.7% | yes | NO_INCIDENT | - |
| 2023-08-10 Thu | $2.99M | $3.06M | -2.2% | +/-16.4% | yes | NO_INCIDENT | - |
| 2023-08-11 Fri | $2.67M | $2.78M | -4.0% | +/-14.8% | yes | NO_INCIDENT | - |
| 2023-08-12 Sat | $2.48M | $2.63M | -5.9% | +/-14.3% | yes | NO_INCIDENT | - |
| 2023-08-13 Sun | $2.50M | $2.48M | +0.9% | +/-14.4% | yes | NO_INCIDENT | - |
| 2023-08-14 Mon | $2.45M | $2.63M | -6.7% | +/-13.9% | yes | NO_INCIDENT | - |
| 2023-08-15 Tue | $2.62M | $2.93M | -10.5% | +/-14.2% | yes | NO_INCIDENT | - |
| 2023-08-16 Wed | $2.82M | $3.05M | -7.6% | +/-14.8% | yes | NO_INCIDENT | - |
| 2023-08-17 Thu | $2.86M | $3.13M | -8.6% | +/-15.2% | yes | NO_INCIDENT | - |
| 2023-08-18 Fri | $2.63M | $2.81M | -6.5% | +/-15.5% | yes | NO_INCIDENT | - |
| 2023-08-19 Sat | $2.54M | $2.63M | -3.5% | +/-15.7% | yes | NO_INCIDENT | - |
| 2023-08-20 Sun | $2.41M | $2.51M | -4.2% | +/-15.4% | yes | NO_INCIDENT | - |
| 2023-08-21 Mon | $2.37M | $2.58M | -8.3% | +/-15.5% | yes | NO_INCIDENT | - |
| 2023-08-22 Tue | $2.51M | $2.85M | -11.9% | +/-14.6% | yes | NO_INCIDENT | - |
| 2023-08-23 Wed | $2.64M | $2.99M | -11.6% | +/-14.6% | yes | NO_INCIDENT | - |
| 2023-08-24 Thu | $2.79M | $3.05M | -8.6% | +/-14.7% | yes | NO_INCIDENT | - |
| 2023-08-25 Fri | $2.59M | $2.76M | -6.2% | +/-14.6% | yes | NO_INCIDENT | - |
| 2023-08-26 Sat | $2.52M | $2.58M | -2.3% | +/-14.6% | yes | NO_INCIDENT | - |
| 2023-08-27 Sun | $2.46M | $2.51M | -2.1% | +/-14.2% | yes | NO_INCIDENT | - |
| 2023-08-28 Mon | $2.38M | $2.49M | -4.2% | +/-14.1% | yes | NO_INCIDENT | - |
| 2023-08-29 Tue | $2.74M | $2.73M | +0.5% | +/-13.8% | yes | NO_INCIDENT | - |
| 2023-08-30 Wed | $2.72M | $2.87M | -5.5% | +/-13.1% | yes | NO_INCIDENT | - |
| 2023-08-31 Thu | $2.80M | $2.96M | -5.4% | +/-11.4% | yes | NO_INCIDENT | - |
| 2023-09-01 Fri | $2.66M | $2.70M | -1.7% | +/-10.6% | yes | NO_INCIDENT | - |
| 2023-09-02 Sat | $2.51M | $2.54M | -0.8% | +/-9.1% | yes | NO_INCIDENT | - |
| 2023-09-03 Sun | $2.33M | $2.49M | -6.1% | +/-8.9% | yes | NO_INCIDENT | - |
| 2023-09-04 Mon | $2.35M | $2.44M | -3.7% | +/-8.0% | yes | NO_INCIDENT | - |
| 2023-09-05 Tue | $3.24M | $2.69M | +20.5% | +/-7.5% | yes | UNEXPLAINED | - |
| 2023-09-06 Wed | $3.46M | $2.77M | +24.5% | +/-7.2% | yes | REAL_CHANGE | - |
| 2023-09-07 Thu | $3.80M | $2.88M | +31.8% | +/-13.2% | yes | REAL_CHANGE | - |
| 2023-09-08 Fri | $3.76M | $2.64M | +42.4% | +/-19.2% | yes | REAL_CHANGE | - |
| 2023-09-09 Sat | $3.34M | $2.51M | +33.0% | +/-26.4% | yes | REAL_CHANGE | - |
| 2023-09-10 Sun | $3.13M | $2.84M | +10.2% | +/-52.8% | no | NO_INCIDENT | - |
| 2023-09-11 Mon | $3.37M | $2.89M | +16.7% | +/-51.7% | no | NO_INCIDENT | - |
| 2023-09-12 Tue | $3.63M | $2.95M | +22.9% | +/-50.4% | no | NO_INCIDENT | - |
| 2023-09-13 Wed | $3.50M | $3.04M | +15.0% | +/-49.1% | no | NO_INCIDENT | - |
| 2023-09-14 Thu | $3.77M | $3.10M | +21.7% | +/-48.8% | no | NO_INCIDENT | - |
| 2023-09-15 Fri | $3.47M | $3.17M | +9.4% | +/-49.1% | no | NO_INCIDENT | - |
| 2023-09-16 Sat | $3.06M | $3.22M | -4.9% | +/-47.9% | no | NO_INCIDENT | - |
| 2023-09-17 Sun | $3.05M | $3.25M | -6.2% | +/-45.5% | no | NO_INCIDENT | - |
| 2023-09-18 Mon | $3.12M | $3.29M | -5.1% | +/-41.3% | no | NO_INCIDENT | - |
| 2023-09-19 Tue | $3.18M | $3.34M | -4.8% | +/-33.5% | no | NO_INCIDENT | - |
| 2023-09-20 Wed | $3.34M | $3.40M | -1.9% | +/-22.8% | no | NO_INCIDENT | - |
| 2023-09-21 Thu | $1.24M | $3.39M | -63.3% | +/-22.8% | no | REAL_CHANGE | - |
| 2023-09-22 Fri | $0.14M | $3.21M | -95.7% | +/-55.4% | no | REAL_CHANGE | - |
| 2023-09-23 Sat | $0.16M | $2.95M | -94.6% | +/-98.4% | no | NO_INCIDENT | - |
| 2023-09-24 Sun | $0.13M | $2.73M | -95.1% | +/-131.8% | no | NO_INCIDENT | - |
| 2023-09-25 Mon | $2.63M | $2.51M | +4.7% | +/-162.7% | no | NO_INCIDENT | - |
| 2023-09-26 Tue | $3.29M | $2.46M | +33.8% | +/-163.8% | no | NO_INCIDENT | - |
| 2023-09-27 Wed | $3.48M | $2.43M | +43.0% | +/-163.1% | no | NO_INCIDENT | - |
| 2023-09-28 Thu | $3.83M | $2.43M | +57.2% | +/-163.1% | no | NO_INCIDENT | - |
| 2023-09-29 Fri | $3.53M | $2.44M | +45.0% | +/-163.3% | no | NO_INCIDENT | - |
| 2023-09-30 Sat | $3.07M | $2.44M | +25.8% | +/-163.5% | no | NO_INCIDENT | - |
| 2023-10-01 Sun | $3.12M | $2.44M | +27.8% | +/-163.5% | no | NO_INCIDENT | - |
| 2023-10-02 Mon | $3.04M | $2.45M | +24.3% | +/-163.4% | no | NO_INCIDENT | - |
| 2023-10-03 Tue | $3.25M | $2.44M | +33.2% | +/-163.5% | no | NO_INCIDENT | - |
| 2023-10-04 Wed | $3.43M | $2.45M | +40.0% | +/-163.5% | no | NO_INCIDENT | - |
| 2023-10-05 Thu | $3.67M | $2.45M | +49.6% | +/-163.6% | no | NO_INCIDENT | - |
| 2023-10-06 Fri | $3.44M | $2.63M | +31.1% | +/-151.6% | no | NO_INCIDENT | - |
| 2023-10-07 Sat | $3.01M | $2.86M | +5.2% | +/-120.0% | no | NO_INCIDENT | - |
| 2023-10-08 Sun | $2.99M | $3.07M | -2.7% | +/-84.7% | no | NO_INCIDENT | - |
| 2023-10-09 Mon | $2.65M | $3.27M | -19.0% | +/-28.0% | no | NO_INCIDENT | - |
| 2023-10-10 Tue | $3.32M | $3.27M | +1.5% | +/-27.8% | no | NO_INCIDENT | - |
| 2023-10-11 Wed | $3.50M | $3.27M | +6.9% | +/-27.8% | no | NO_INCIDENT | - |
| 2023-10-12 Thu | $3.92M | $3.28M | +19.8% | +/-27.9% | no | NO_INCIDENT | - |
| 2023-10-13 Fri | $3.50M | $3.28M | +6.7% | +/-29.0% | no | NO_INCIDENT | - |
| 2023-10-14 Sat | $3.33M | $3.28M | +1.4% | +/-28.9% | no | NO_INCIDENT | - |
| 2023-10-15 Sun | $3.11M | $3.30M | -5.8% | +/-28.3% | no | NO_INCIDENT | - |
| 2023-10-16 Mon | $3.13M | $3.30M | -5.1% | +/-28.3% | no | NO_INCIDENT | - |
| 2023-10-17 Tue | $3.43M | $3.30M | +3.7% | +/-27.9% | no | NO_INCIDENT | - |
| 2023-10-18 Wed | $3.61M | $3.32M | +8.7% | +/-27.9% | no | NO_INCIDENT | - |
| 2023-10-19 Thu | $3.87M | $3.33M | +16.4% | +/-28.5% | no | NO_INCIDENT | - |
| 2023-10-20 Fri | $3.68M | $3.34M | +9.9% | +/-30.1% | no | NO_INCIDENT | - |
| 2023-10-21 Sat | $3.28M | $3.36M | -2.3% | +/-30.9% | no | NO_INCIDENT | - |
| 2023-10-22 Sun | $3.23M | $3.38M | -4.5% | +/-29.6% | no | NO_INCIDENT | - |
| 2023-10-23 Mon | $3.09M | $3.40M | -9.1% | +/-28.1% | no | NO_INCIDENT | - |
| 2023-10-24 Tue | $3.37M | $3.43M | -1.7% | +/-22.7% | no | NO_INCIDENT | - |
| 2023-10-25 Wed | $3.60M | $3.43M | +4.9% | +/-22.6% | no | NO_INCIDENT | - |
| 2023-10-26 Thu | $3.90M | $3.44M | +13.4% | +/-22.8% | no | NO_INCIDENT | - |
| 2023-10-27 Fri | $3.82M | $3.44M | +11.1% | +/-22.5% | no | NO_INCIDENT | - |
| 2023-10-28 Sat | $3.69M | $3.46M | +6.8% | +/-23.9% | no | NO_INCIDENT | clock_shift:REJECTED |
| 2023-10-29 Sun | $3.17M | $2.51M | +25.9% | +/-55.4% | yes | NO_INCIDENT | - |
| 2023-10-30 Mon | $2.80M | $2.91M | -3.8% | +/-13.6% | yes | NO_INCIDENT | - |
| 2023-10-31 Tue | $2.80M | $3.33M | -15.9% | +/-12.8% | yes | UNEXPLAINED | - |
| 2023-11-01 Wed | $3.61M | $3.52M | +2.6% | +/-13.0% | yes | NO_INCIDENT | - |
| 2023-11-02 Thu | $3.78M | $3.84M | -1.6% | +/-13.0% | yes | NO_INCIDENT | - |
| 2023-11-03 Fri | $3.59M | $3.59M | -0.0% | +/-13.0% | yes | NO_INCIDENT | - |
| 2023-11-04 Sat | $3.31M | $3.28M | +1.0% | +/-13.0% | yes | NO_INCIDENT | - |
| 2023-11-05 Sun | $3.13M | $3.12M | +0.2% | +/-12.4% | yes | NO_INCIDENT | - |
| 2023-11-06 Mon | $3.16M | $2.94M | +7.4% | +/-12.4% | yes | NO_INCIDENT | - |
| 2023-11-07 Tue | $3.16M | $3.34M | -5.4% | +/-12.8% | yes | NO_INCIDENT | - |
| 2023-11-08 Wed | $3.63M | $3.55M | +2.2% | +/-13.0% | yes | NO_INCIDENT | - |
| 2023-11-09 Thu | $3.92M | $3.83M | +2.3% | +/-12.8% | yes | NO_INCIDENT | - |
| 2023-11-10 Fri | $3.59M | $3.61M | -0.5% | +/-12.6% | yes | NO_INCIDENT | - |
| 2023-11-11 Sat | $3.37M | $3.32M | +1.2% | +/-12.4% | yes | NO_INCIDENT | - |
| 2023-11-12 Sun | $3.19M | $3.12M | +2.1% | +/-11.1% | yes | NO_INCIDENT | - |
| 2023-11-13 Mon | $3.10M | $2.96M | +4.8% | +/-10.8% | yes | NO_INCIDENT | - |
| 2023-11-14 Tue | $3.41M | $3.32M | +2.9% | +/-8.9% | yes | NO_INCIDENT | - |
| 2023-11-15 Wed | $3.66M | $3.59M | +2.0% | +/-9.0% | yes | NO_INCIDENT | - |
| 2023-11-16 Thu | $3.85M | $3.88M | -0.8% | +/-8.9% | yes | NO_INCIDENT | - |
| 2023-11-17 Fri | $3.60M | $3.63M | -0.8% | +/-8.8% | yes | NO_INCIDENT | - |
| 2023-11-18 Sat | $3.35M | $3.40M | -1.5% | +/-8.6% | yes | NO_INCIDENT | - |
| 2023-11-19 Sun | $2.78M | $3.16M | -12.2% | +/-8.6% | yes | REAL_CHANGE | - |
| 2023-11-20 Mon | $2.84M | $3.05M | -7.1% | +/-10.4% | yes | NO_INCIDENT | - |
| 2023-11-21 Tue | $3.26M | $3.34M | -2.4% | +/-10.8% | yes | NO_INCIDENT | - |
| 2023-11-22 Wed | $2.66M | $3.62M | -26.6% | +/-10.7% | yes | REAL_CHANGE | - |
| 2023-11-23 Thu | $1.71M | $3.86M | -55.8% | +/-16.8% | yes | UNEXPLAINED | - |
| 2023-11-24 Fri | $2.15M | $3.66M | -41.2% | +/-17.1% | yes | UNEXPLAINED | - |
| 2023-11-25 Sat | $2.56M | $3.40M | -24.7% | +/-17.4% | yes | UNEXPLAINED | - |
| 2023-11-26 Sun | $2.65M | $3.10M | -14.4% | +/-17.5% | yes | NO_INCIDENT | - |
| 2023-11-27 Mon | $3.01M | $3.00M | +0.4% | +/-18.6% | yes | NO_INCIDENT | - |
| 2023-11-28 Tue | $3.54M | $3.30M | +7.3% | +/-18.6% | yes | NO_INCIDENT | - |
| 2023-11-29 Wed | $3.45M | $3.43M | +0.5% | +/-18.9% | yes | NO_INCIDENT | - |
| 2023-11-30 Thu | $3.79M | $3.86M | -1.9% | +/-18.8% | yes | NO_INCIDENT | - |
| 2023-12-01 Fri | $3.80M | $3.65M | +4.1% | +/-18.8% | yes | NO_INCIDENT | - |
| 2023-12-02 Sat | $3.35M | $3.43M | -2.3% | +/-18.7% | yes | NO_INCIDENT | - |
| 2023-12-03 Sun | $3.11M | $2.98M | +4.4% | +/-18.1% | yes | NO_INCIDENT | - |
| 2023-12-04 Mon | $3.11M | $2.98M | +4.4% | +/-17.9% | yes | NO_INCIDENT | - |
| 2023-12-05 Tue | $3.56M | $3.35M | +6.3% | +/-17.6% | yes | NO_INCIDENT | - |
| 2023-12-06 Wed | $3.84M | $3.40M | +12.8% | +/-17.5% | yes | NO_INCIDENT | - |
| 2023-12-07 Thu | $4.11M | $3.83M | +7.2% | +/-18.3% | yes | NO_INCIDENT | - |
| 2023-12-08 Fri | $3.89M | $3.65M | +6.8% | +/-18.5% | yes | NO_INCIDENT | - |
| 2023-12-09 Sat | $3.71M | $3.34M | +11.1% | +/-18.7% | yes | NO_INCIDENT | - |
| 2023-12-10 Sun | $3.21M | $2.97M | +8.0% | +/-19.3% | yes | NO_INCIDENT | - |
| 2023-12-11 Mon | $3.27M | $3.04M | +7.3% | +/-19.5% | yes | NO_INCIDENT | - |
| 2023-12-12 Tue | $3.73M | $3.39M | +10.2% | +/-19.8% | yes | NO_INCIDENT | - |
| 2023-12-13 Wed | $3.97M | $3.45M | +15.3% | +/-19.8% | yes | NO_INCIDENT | - |
| 2023-12-14 Thu | $4.39M | $3.92M | +12.1% | +/-20.8% | yes | NO_INCIDENT | - |
| 2023-12-15 Fri | $4.15M | $3.72M | +11.5% | +/-21.5% | yes | NO_INCIDENT | - |
| 2023-12-16 Sat | $3.73M | $3.44M | +8.3% | +/-21.8% | yes | NO_INCIDENT | - |
| 2023-12-17 Sun | $3.01M | $2.99M | +0.9% | +/-22.0% | yes | NO_INCIDENT | - |
| 2023-12-18 Mon | $2.85M | $3.07M | -6.9% | +/-21.7% | yes | NO_INCIDENT | - |
| 2023-12-19 Tue | $3.41M | $3.50M | -2.7% | +/-22.0% | yes | NO_INCIDENT | - |
| 2023-12-20 Wed | $3.33M | $3.51M | -5.2% | +/-22.0% | yes | NO_INCIDENT | - |
| 2023-12-21 Thu | $3.29M | $4.03M | -18.4% | +/-22.1% | yes | NO_INCIDENT | - |
| 2023-12-22 Fri | $3.05M | $3.86M | -21.0% | +/-24.0% | yes | NO_INCIDENT | - |
| 2023-12-23 Sat | $2.26M | $3.53M | -36.1% | +/-26.1% | yes | REAL_CHANGE | - |
| 2023-12-24 Sun | $1.69M | $3.40M | -50.4% | +/-47.3% | no | UNEXPLAINED | - |
| 2023-12-25 Mon | $1.33M | $3.40M | -60.9% | +/-47.3% | no | REAL_CHANGE | - |
| 2023-12-26 Tue | $2.09M | $3.27M | -36.1% | +/-69.5% | no | NO_INCIDENT | - |
| 2023-12-27 Wed | $2.49M | $3.19M | -21.7% | +/-76.8% | no | NO_INCIDENT | - |
| 2023-12-28 Thu | $2.58M | $3.10M | -16.7% | +/-79.3% | no | NO_INCIDENT | - |
| 2023-12-29 Fri | $2.59M | $3.00M | -13.7% | +/-79.2% | no | NO_INCIDENT | - |
| 2023-12-30 Sat | $2.41M | $2.87M | -16.1% | +/-72.6% | no | NO_INCIDENT | - |
| 2023-12-31 Sun | $2.11M | $2.74M | -23.0% | +/-66.1% | no | NO_INCIDENT | clock_shift:REJECTED |
| 2024-01-01 Mon | $2.48M | $2.63M | -5.8% | +/-63.7% | no | NO_INCIDENT | - |
| 2024-01-02 Tue | $2.31M | $2.59M | -10.8% | +/-63.5% | no | NO_INCIDENT | - |
| 2024-01-03 Wed | $2.39M | $2.55M | -6.4% | +/-64.4% | no | NO_INCIDENT | - |
| 2024-01-04 Thu | $2.83M | $2.48M | +14.3% | +/-59.8% | no | NO_INCIDENT | - |
| 2024-01-05 Fri | $2.76M | $2.44M | +13.0% | +/-55.0% | no | NO_INCIDENT | - |
| 2024-01-06 Sat | $2.47M | $2.41M | +2.5% | +/-49.1% | no | NO_INCIDENT | - |
| 2024-01-07 Sun | $1.93M | $2.36M | -18.5% | +/-44.6% | no | NO_INCIDENT | - |
| 2024-01-08 Mon | $2.24M | $2.34M | -4.2% | +/-47.3% | no | NO_INCIDENT | - |
| 2024-01-09 Tue | $2.39M | $2.41M | -0.7% | +/-30.5% | no | NO_INCIDENT | - |
| 2024-01-10 Wed | $2.58M | $2.43M | +6.2% | +/-28.3% | no | NO_INCIDENT | - |
| 2024-01-11 Thu | $2.94M | $2.43M | +20.7% | +/-28.6% | no | NO_INCIDENT | - |
| 2024-01-12 Fri | $2.89M | $2.46M | +17.7% | +/-32.2% | no | NO_INCIDENT | - |
| 2024-01-13 Sat | $2.68M | $2.48M | +8.1% | +/-34.5% | no | NO_INCIDENT | clock_shift:REJECTED |
| 2024-01-14 Sun | $2.49M | $2.50M | -0.3% | +/-34.7% | no | NO_INCIDENT | - |
| 2024-01-15 Mon | $2.19M | $2.53M | -13.3% | +/-31.9% | no | NO_INCIDENT | - |
| 2024-01-16 Tue | $2.66M | $2.51M | +6.2% | +/-33.8% | no | NO_INCIDENT | - |
| 2024-01-17 Wed | $3.01M | $2.53M | +18.9% | +/-33.1% | no | NO_INCIDENT | - |
| 2024-01-18 Thu | $2.97M | $2.58M | +15.5% | +/-35.1% | no | NO_INCIDENT | - |
| 2024-01-19 Fri | $2.51M | $2.59M | -3.0% | +/-36.2% | no | NO_INCIDENT | - |
| 2024-01-20 Sat | $2.65M | $2.57M | +3.1% | +/-36.1% | no | NO_INCIDENT | clock_shift:REJECTED |
| 2024-01-21 Sun | $2.29M | $2.58M | -11.1% | +/-35.8% | no | NO_INCIDENT | - |
| 2024-01-22 Mon | $2.39M | $2.61M | -8.3% | +/-30.4% | no | NO_INCIDENT | - |
| 2024-01-23 Tue | $2.66M | $2.62M | +1.8% | +/-28.9% | no | NO_INCIDENT | - |
| 2024-01-24 Wed | $2.82M | $2.76M | +2.2% | +/-33.4% | yes | NO_INCIDENT | - |
| 2024-01-25 Thu | $3.03M | $2.92M | +3.8% | +/-31.5% | yes | NO_INCIDENT | - |
| 2024-01-26 Fri | $2.84M | $2.76M | +3.1% | +/-30.9% | yes | NO_INCIDENT | - |
| 2024-01-27 Sat | $2.74M | $2.49M | +10.1% | +/-30.4% | yes | NO_INCIDENT | clock_shift:REJECTED |
| 2024-01-28 Sun | $2.46M | $2.21M | +11.7% | +/-30.1% | yes | NO_INCIDENT | - |
| 2024-01-29 Mon | $2.36M | $2.13M | +11.2% | +/-30.0% | yes | NO_INCIDENT | - |
| 2024-01-30 Tue | $2.67M | $2.42M | +10.2% | +/-21.2% | yes | NO_INCIDENT | - |
| 2024-01-31 Wed | $2.71M | $2.66M | +2.1% | +/-19.8% | yes | NO_INCIDENT | - |
| 2024-02-01 Thu | $3.01M | $2.87M | +4.8% | +/-19.4% | yes | NO_INCIDENT | - |
| 2024-02-02 Fri | $2.79M | $2.72M | +2.8% | +/-18.6% | yes | NO_INCIDENT | - |
| 2024-02-03 Sat | $2.70M | $2.59M | +4.2% | +/-18.4% | yes | NO_INCIDENT | clock_shift:REJECTED |
| 2024-02-04 Sun | $2.41M | $2.26M | +6.6% | +/-18.0% | yes | NO_INCIDENT | - |
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
| 2024-02-29 Thu | $3.58M | $3.13M | +14.0% | +/-23.7% | yes | NO_INCIDENT | - |
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
| 2024-03-14 Thu | $3.87M | $3.32M | +16.7% | +/-29.5% | yes | NO_INCIDENT | - |
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
| 2024-04-01 Mon | $2.72M | $2.71M | +0.1% | +/-13.4% | yes | NO_INCIDENT | - |
| 2024-04-02 Tue | $3.61M | $3.12M | +15.8% | +/-13.1% | yes | REAL_CHANGE | - |
| 2024-04-03 Wed | $3.80M | $3.34M | +13.9% | +/-14.8% | yes | NO_INCIDENT | - |
| 2024-04-04 Thu | $3.84M | $3.64M | +5.4% | +/-15.2% | yes | NO_INCIDENT | - |
| 2024-04-05 Fri | $3.66M | $3.30M | +10.9% | +/-15.3% | yes | NO_INCIDENT | - |
| 2024-04-06 Sat | $3.40M | $3.18M | +6.8% | +/-15.7% | yes | NO_INCIDENT | clock_shift:REJECTED |
| 2024-04-07 Sun | $2.98M | $2.86M | +4.2% | +/-15.8% | yes | NO_INCIDENT | - |
| 2024-04-08 Mon | $2.77M | $2.75M | +0.8% | +/-15.6% | yes | NO_INCIDENT | - |
| 2024-04-09 Tue | $3.39M | $3.21M | +5.7% | +/-15.5% | yes | NO_INCIDENT | - |
| 2024-04-10 Wed | $3.32M | $3.48M | -4.4% | +/-15.4% | yes | NO_INCIDENT | - |
| 2024-04-11 Thu | $3.93M | $3.69M | +6.3% | +/-15.4% | yes | NO_INCIDENT | - |
| 2024-04-12 Fri | $3.42M | $3.39M | +0.9% | +/-14.8% | yes | NO_INCIDENT | - |
| 2024-04-13 Sat | $3.28M | $3.24M | +1.3% | +/-14.6% | yes | NO_INCIDENT | - |
| 2024-04-14 Sun | $3.16M | $2.91M | +8.5% | +/-14.2% | yes | NO_INCIDENT | - |
| 2024-04-15 Mon | $2.99M | $2.76M | +8.2% | +/-14.7% | yes | NO_INCIDENT | - |
| 2024-04-16 Tue | $3.16M | $3.27M | -3.4% | +/-15.2% | yes | NO_INCIDENT | - |
| 2024-04-17 Wed | $3.56M | $3.43M | +3.9% | +/-15.2% | yes | NO_INCIDENT | - |
| 2024-04-18 Thu | $3.80M | $3.80M | -0.0% | +/-15.1% | yes | NO_INCIDENT | - |
| 2024-04-19 Fri | $3.31M | $3.42M | -3.3% | +/-15.1% | yes | NO_INCIDENT | - |
| 2024-04-20 Sat | $3.49M | $3.21M | +8.9% | +/-15.0% | yes | NO_INCIDENT | - |
| 2024-04-21 Sun | $2.97M | $2.96M | +0.3% | +/-15.2% | yes | NO_INCIDENT | - |
| 2024-04-22 Mon | $2.62M | $2.80M | -6.4% | +/-15.2% | yes | NO_INCIDENT | - |
| 2024-04-23 Tue | $2.80M | $3.27M | -14.5% | +/-15.5% | yes | NO_INCIDENT | - |
| 2024-04-24 Wed | $3.09M | $3.47M | -10.9% | +/-16.9% | yes | NO_INCIDENT | - |
| 2024-04-25 Thu | $3.59M | $3.79M | -5.3% | +/-17.6% | yes | NO_INCIDENT | - |
| 2024-04-26 Fri | $3.22M | $3.37M | -4.5% | +/-17.6% | yes | NO_INCIDENT | - |
| 2024-04-27 Sat | $3.11M | $3.22M | -3.3% | +/-17.7% | yes | NO_INCIDENT | - |
| 2024-04-28 Sun | $2.86M | $2.95M | -3.1% | +/-17.5% | yes | NO_INCIDENT | - |
| 2024-04-29 Mon | $2.86M | $2.76M | +3.3% | +/-17.6% | yes | NO_INCIDENT | - |
| 2024-04-30 Tue | $3.11M | $3.21M | -3.3% | +/-17.6% | yes | NO_INCIDENT | - |
| 2024-05-01 Wed | $3.53M | $3.43M | +2.9% | +/-17.6% | yes | NO_INCIDENT | - |
| 2024-05-02 Thu | $3.85M | $3.78M | +1.8% | +/-17.6% | yes | NO_INCIDENT | - |
| 2024-05-03 Fri | $3.62M | $3.37M | +7.4% | +/-17.6% | yes | NO_INCIDENT | - |
| 2024-05-04 Sat | $3.46M | $3.23M | +7.1% | +/-17.7% | yes | NO_INCIDENT | - |
| 2024-05-05 Sun | $3.41M | $2.94M | +15.9% | +/-16.6% | yes | NO_INCIDENT | - |
| 2024-05-06 Mon | $3.14M | $2.79M | +12.7% | +/-17.2% | yes | NO_INCIDENT | - |
| 2024-05-07 Tue | $3.43M | $3.21M | +6.9% | +/-17.8% | yes | NO_INCIDENT | - |
| 2024-05-08 Wed | $3.70M | $3.46M | +7.1% | +/-17.1% | yes | NO_INCIDENT | - |
| 2024-05-09 Thu | $3.99M | $3.80M | +5.0% | +/-16.7% | yes | NO_INCIDENT | - |
| 2024-05-10 Fri | $3.91M | $3.45M | +13.5% | +/-16.9% | yes | NO_INCIDENT | - |
| 2024-05-11 Sat | $3.44M | $3.35M | +2.7% | +/-17.8% | yes | NO_INCIDENT | - |
| 2024-05-12 Sun | $3.18M | $3.08M | +3.4% | +/-17.9% | yes | NO_INCIDENT | - |
| 2024-05-13 Mon | $3.35M | $2.88M | +16.4% | +/-17.8% | yes | NO_INCIDENT | - |
| 2024-05-14 Tue | $3.88M | $3.18M | +22.0% | +/-18.8% | yes | REAL_CHANGE | - |
| 2024-05-15 Wed | $4.11M | $3.44M | +19.5% | +/-21.1% | yes | NO_INCIDENT | - |
| 2024-05-16 Thu | $4.23M | $3.83M | +10.5% | +/-22.4% | yes | NO_INCIDENT | - |
| 2024-05-17 Fri | $3.81M | $3.50M | +9.1% | +/-22.9% | yes | NO_INCIDENT | - |
| 2024-05-18 Sat | $3.70M | $3.36M | +10.1% | +/-23.1% | yes | NO_INCIDENT | - |
| 2024-05-19 Sun | $3.68M | $3.12M | +18.1% | +/-23.5% | yes | NO_INCIDENT | - |
| 2024-05-20 Mon | $3.16M | $2.99M | +5.7% | +/-24.8% | yes | NO_INCIDENT | - |
| 2024-05-21 Tue | $3.47M | $3.27M | +5.9% | +/-24.8% | yes | NO_INCIDENT | - |
| 2024-05-22 Wed | $3.77M | $3.60M | +4.7% | +/-24.7% | yes | NO_INCIDENT | - |
| 2024-05-23 Thu | $3.57M | $3.89M | -8.3% | +/-24.8% | yes | NO_INCIDENT | - |
| 2024-05-24 Fri | $3.19M | $3.58M | -10.9% | +/-25.1% | yes | NO_INCIDENT | - |
| 2024-05-25 Sat | $2.40M | $3.44M | -30.3% | +/-25.4% | yes | REAL_CHANGE | - |
| 2024-05-26 Sun | $2.36M | $3.54M | -33.4% | +/-38.2% | no | NO_INCIDENT | - |
| 2024-05-27 Mon | $2.15M | $3.48M | -38.2% | +/-46.4% | no | NO_INCIDENT | - |
| 2024-05-28 Tue | $3.14M | $3.39M | -7.5% | +/-56.4% | no | NO_INCIDENT | - |
| 2024-05-29 Wed | $3.47M | $3.34M | +3.8% | +/-56.3% | no | NO_INCIDENT | - |
| 2024-05-30 Thu | $3.59M | $3.85M | -6.7% | +/-32.9% | yes | NO_INCIDENT | - |
| 2024-05-31 Fri | $3.33M | $3.55M | -6.2% | +/-32.9% | yes | NO_INCIDENT | - |
| 2024-06-01 Sat | $3.46M | $3.22M | +7.5% | +/-32.7% | yes | NO_INCIDENT | - |
| 2024-06-02 Sun | $3.22M | $3.10M | +3.9% | +/-32.6% | yes | NO_INCIDENT | - |
| 2024-06-03 Mon | $3.22M | $3.16M | +1.7% | +/-45.9% | no | NO_INCIDENT | - |
| 2024-06-04 Tue | $3.60M | $3.17M | +13.6% | +/-45.9% | no | NO_INCIDENT | - |
| 2024-06-05 Wed | $3.81M | $3.17M | +20.1% | +/-46.4% | no | NO_INCIDENT | - |
| 2024-06-06 Thu | $4.16M | $3.18M | +30.9% | +/-46.7% | no | NO_INCIDENT | - |
| 2024-06-07 Fri | $3.71M | $3.22M | +15.1% | +/-51.1% | no | NO_INCIDENT | - |
| 2024-06-08 Sat | $3.48M | $3.26M | +6.8% | +/-51.8% | no | NO_INCIDENT | - |
| 2024-06-09 Sun | $3.22M | $3.33M | -3.5% | +/-46.0% | no | NO_INCIDENT | - |
| 2024-06-10 Mon | $3.12M | $3.00M | +3.9% | +/-31.7% | yes | NO_INCIDENT | - |
| 2024-06-11 Tue | $3.34M | $3.50M | -4.6% | +/-31.6% | yes | NO_INCIDENT | - |
| 2024-06-12 Wed | $3.39M | $3.77M | -10.0% | +/-31.7% | yes | NO_INCIDENT | - |
| 2024-06-13 Thu | $3.58M | $3.47M | +3.1% | +/-23.5% | no | NO_INCIDENT | - |
| 2024-06-14 Fri | $3.37M | $3.47M | -2.9% | +/-23.4% | no | NO_INCIDENT | - |
| 2024-06-15 Sat | $3.05M | $3.48M | -12.2% | +/-23.3% | no | NO_INCIDENT | - |
| 2024-06-16 Sun | $3.01M | $3.45M | -12.7% | +/-25.4% | no | NO_INCIDENT | - |
| 2024-06-17 Mon | $2.84M | $3.43M | -17.2% | +/-26.9% | no | NO_INCIDENT | - |
| 2024-06-18 Tue | $3.33M | $3.48M | -4.4% | +/-31.9% | yes | NO_INCIDENT | - |
| 2024-06-19 Wed | $2.84M | $3.71M | -23.4% | +/-31.3% | yes | NO_INCIDENT | - |
| 2024-06-20 Thu | $3.55M | $3.32M | +6.9% | +/-30.9% | no | NO_INCIDENT | - |
| 2024-06-21 Fri | $3.33M | $3.27M | +1.8% | +/-23.9% | no | NO_INCIDENT | - |
| 2024-06-22 Sat | $3.08M | $3.25M | -5.2% | +/-21.5% | no | NO_INCIDENT | - |
| 2024-06-23 Sun | $2.90M | $3.22M | -9.9% | +/-21.1% | no | NO_INCIDENT | - |
| 2024-06-24 Mon | $3.32M | $2.90M | +14.5% | +/-28.9% | yes | NO_INCIDENT | - |
| 2024-06-25 Tue | $3.67M | $3.21M | +14.2% | +/-22.6% | no | NO_INCIDENT | - |
| 2024-06-26 Wed | $3.82M | $3.23M | +18.1% | +/-24.9% | no | NO_INCIDENT | - |
| 2024-06-27 Thu | $3.89M | $3.26M | +19.2% | +/-28.1% | no | NO_INCIDENT | - |
| 2024-06-28 Fri | $3.28M | $3.39M | -3.1% | +/-29.7% | yes | NO_INCIDENT | - |
| 2024-06-29 Sat | $2.95M | $3.09M | -4.7% | +/-29.6% | yes | NO_INCIDENT | clock_shift:REJECTED |
| 2024-06-30 Sun | $2.67M | $2.94M | -9.2% | +/-27.1% | yes | NO_INCIDENT | - |
| 2024-07-01 Mon | $2.53M | $2.93M | -13.8% | +/-25.4% | yes | NO_INCIDENT | - |
| 2024-07-02 Tue | $2.44M | $3.41M | -28.6% | +/-22.3% | yes | REAL_CHANGE | - |
| 2024-07-03 Wed | $2.25M | $3.16M | -29.0% | +/-42.6% | no | NO_INCIDENT | - |
| 2024-07-04 Thu | $1.74M | $3.12M | -44.2% | +/-48.4% | no | NO_INCIDENT | - |
| 2024-07-05 Fri | $2.07M | $2.99M | -30.9% | +/-60.1% | no | NO_INCIDENT | - |
| 2024-07-06 Sat | $2.17M | $2.90M | -25.2% | +/-65.7% | no | NO_INCIDENT | - |
| 2024-07-07 Sun | $2.39M | $2.83M | -15.6% | +/-69.8% | no | NO_INCIDENT | - |
| 2024-07-08 Mon | $2.77M | $2.80M | -1.2% | +/-71.7% | no | NO_INCIDENT | - |
| 2024-07-09 Tue | $3.15M | $2.76M | +14.2% | +/-71.0% | no | NO_INCIDENT | - |
| 2024-07-10 Wed | $3.31M | $2.72M | +21.8% | +/-67.7% | no | NO_INCIDENT | - |
| 2024-07-11 Thu | $3.42M | $2.69M | +27.3% | +/-62.6% | no | NO_INCIDENT | - |
| 2024-07-12 Fri | $2.85M | $2.65M | +7.4% | +/-56.3% | no | NO_INCIDENT | - |
| 2024-07-13 Sat | $2.71M | $2.62M | +3.2% | +/-53.9% | no | NO_INCIDENT | - |
| 2024-07-14 Sun | $2.76M | $2.60M | +5.8% | +/-53.3% | no | NO_INCIDENT | - |
| 2024-07-15 Mon | $3.02M | $2.61M | +15.6% | +/-53.4% | no | NO_INCIDENT | - |
| 2024-07-16 Tue | $3.56M | $2.64M | +34.8% | +/-53.9% | no | NO_INCIDENT | - |
| 2024-07-17 Wed | $3.56M | $2.73M | +30.7% | +/-57.9% | no | NO_INCIDENT | - |
| 2024-07-18 Thu | $3.57M | $2.82M | +26.7% | +/-58.4% | no | NO_INCIDENT | - |
| 2024-07-19 Fri | $3.03M | $2.95M | +2.6% | +/-49.9% | no | NO_INCIDENT | - |
| 2024-07-20 Sat | $2.87M | $3.02M | -4.8% | +/-42.3% | no | NO_INCIDENT | - |
| 2024-07-21 Sun | $2.72M | $3.07M | -11.3% | +/-35.0% | no | NO_INCIDENT | - |
| 2024-07-22 Mon | $2.75M | $3.09M | -11.1% | +/-31.3% | no | NO_INCIDENT | - |
| 2024-07-23 Tue | $3.13M | $3.09M | +1.4% | +/-31.4% | no | NO_INCIDENT | - |
| 2024-07-24 Wed | $3.23M | $3.09M | +4.4% | +/-31.4% | no | NO_INCIDENT | - |
| 2024-07-25 Thu | $3.34M | $3.08M | +8.2% | +/-31.1% | no | NO_INCIDENT | - |
| 2024-07-26 Fri | $2.84M | $3.08M | -7.8% | +/-30.6% | no | NO_INCIDENT | - |
| 2024-07-27 Sat | $2.64M | $3.08M | -14.3% | +/-30.7% | no | NO_INCIDENT | - |
| 2024-07-28 Sun | $2.60M | $3.07M | -15.4% | +/-31.4% | no | NO_INCIDENT | - |
| 2024-07-29 Mon | $2.57M | $3.06M | -16.0% | +/-32.8% | no | NO_INCIDENT | - |
| 2024-07-30 Tue | $2.84M | $3.03M | -6.1% | +/-35.4% | no | NO_INCIDENT | - |
| 2024-07-31 Wed | $3.09M | $2.98M | +3.6% | +/-33.0% | no | NO_INCIDENT | - |
| 2024-08-01 Thu | $3.30M | $2.94M | +12.2% | +/-29.3% | no | NO_INCIDENT | - |
| 2024-08-02 Fri | $3.01M | $2.92M | +2.8% | +/-25.8% | no | NO_INCIDENT | - |
| 2024-08-03 Sat | $3.06M | $2.92M | +4.7% | +/-25.8% | no | NO_INCIDENT | - |
| 2024-08-04 Sun | $2.59M | $2.94M | -11.8% | +/-25.9% | no | NO_INCIDENT | - |
| 2024-08-05 Mon | $2.78M | $2.93M | -4.9% | +/-27.0% | no | NO_INCIDENT | - |
| 2024-08-06 Tue | $3.30M | $2.93M | +12.6% | +/-26.8% | no | NO_INCIDENT | - |
| 2024-08-07 Wed | $3.21M | $2.94M | +9.2% | +/-28.0% | no | NO_INCIDENT | - |
| 2024-08-08 Thu | $3.15M | $2.94M | +7.1% | +/-27.9% | no | NO_INCIDENT | - |
| 2024-08-09 Fri | $2.60M | $2.76M | -5.8% | +/-23.6% | yes | NO_INCIDENT | - |
| 2024-08-10 Sat | $2.62M | $2.69M | -2.5% | +/-19.5% | yes | NO_INCIDENT | - |
| 2024-08-11 Sun | $2.50M | $2.61M | -4.1% | +/-16.4% | yes | NO_INCIDENT | - |
| 2024-08-12 Mon | $2.39M | $2.78M | -13.8% | +/-16.0% | yes | NO_INCIDENT | - |
| 2024-08-13 Tue | $2.58M | $3.20M | -19.4% | +/-17.3% | yes | REAL_CHANGE | - |
| 2024-08-14 Wed | $2.79M | $3.28M | -15.0% | +/-19.7% | yes | NO_INCIDENT | - |
| 2024-08-15 Thu | $2.90M | $3.36M | -13.5% | +/-20.9% | yes | NO_INCIDENT | - |
| 2024-08-16 Fri | $2.69M | $2.86M | -5.9% | +/-21.8% | yes | NO_INCIDENT | - |
| 2024-08-17 Sat | $2.56M | $2.78M | -7.8% | +/-22.0% | yes | NO_INCIDENT | - |
| 2024-08-18 Sun | $2.42M | $2.63M | -8.2% | +/-22.3% | yes | NO_INCIDENT | - |
| 2024-08-19 Mon | $2.66M | $2.70M | -1.4% | +/-22.4% | yes | NO_INCIDENT | - |
| 2024-08-20 Tue | $2.75M | $3.08M | -10.7% | +/-21.5% | yes | NO_INCIDENT | - |
| 2024-08-21 Wed | $2.71M | $3.17M | -14.6% | +/-20.1% | yes | NO_INCIDENT | - |
| 2024-08-22 Thu | $2.85M | $3.25M | -12.5% | +/-19.8% | yes | NO_INCIDENT | - |
| 2024-08-23 Fri | $2.68M | $2.83M | -5.5% | +/-19.6% | yes | NO_INCIDENT | - |
| 2024-08-24 Sat | $2.52M | $2.75M | -8.6% | +/-19.3% | yes | NO_INCIDENT | - |
| 2024-08-25 Sun | $2.52M | $2.57M | -1.8% | +/-19.6% | yes | NO_INCIDENT | - |
| 2024-08-26 Mon | $2.56M | $2.63M | -2.8% | +/-19.3% | yes | NO_INCIDENT | - |
| 2024-08-27 Tue | $2.71M | $2.92M | -7.4% | +/-19.1% | yes | NO_INCIDENT | - |
| 2024-08-28 Wed | $2.99M | $3.00M | -0.5% | +/-19.0% | yes | NO_INCIDENT | - |
| 2024-08-29 Thu | $3.00M | $3.11M | -3.5% | +/-18.6% | yes | NO_INCIDENT | - |
| 2024-08-30 Fri | $2.82M | $2.76M | +1.9% | +/-18.2% | yes | NO_INCIDENT | - |
| 2024-08-31 Sat | $2.58M | $2.68M | -3.9% | +/-18.2% | yes | NO_INCIDENT | - |
| 2024-09-01 Sun | $2.63M | $2.53M | +4.0% | +/-18.3% | yes | NO_INCIDENT | - |
| 2024-09-02 Mon | $2.60M | $2.59M | +0.1% | +/-18.3% | yes | NO_INCIDENT | - |
| 2024-09-03 Tue | $3.16M | $2.84M | +11.3% | +/-18.3% | yes | NO_INCIDENT | - |
| 2024-09-04 Wed | $3.49M | $2.96M | +17.9% | +/-18.9% | yes | NO_INCIDENT | - |
| 2024-09-05 Thu | $3.82M | $3.04M | +25.7% | +/-20.5% | yes | REAL_CHANGE | - |
| 2024-09-06 Fri | $3.67M | $2.76M | +33.1% | +/-23.3% | yes | REAL_CHANGE | - |
| 2024-09-07 Sat | $3.42M | $2.93M | +16.7% | +/-44.0% | no | NO_INCIDENT | clock_shift:REJECTED |
| 2024-09-08 Sun | $3.29M | $3.00M | +9.7% | +/-43.1% | no | NO_INCIDENT | - |
| 2024-09-09 Mon | $3.22M | $3.05M | +5.5% | +/-40.8% | no | NO_INCIDENT | - |
| 2024-09-10 Tue | $3.52M | $3.10M | +13.8% | +/-38.1% | no | NO_INCIDENT | - |
| 2024-09-11 Wed | $3.41M | $3.16M | +7.9% | +/-37.2% | no | NO_INCIDENT | - |
| 2024-09-12 Thu | $4.01M | $3.19M | +25.9% | +/-37.0% | no | NO_INCIDENT | - |
| 2024-09-13 Fri | $3.61M | $3.26M | +10.8% | +/-40.7% | no | NO_INCIDENT | - |
| 2024-09-14 Sat | $3.53M | $3.32M | +6.5% | +/-39.1% | no | NO_INCIDENT | - |
| 2024-09-15 Sun | $3.39M | $3.38M | +0.0% | +/-34.0% | no | NO_INCIDENT | - |
| 2024-09-16 Mon | $3.18M | $3.44M | -7.4% | +/-28.0% | no | NO_INCIDENT | - |
| 2024-09-17 Tue | $3.60M | $3.48M | +3.6% | +/-20.2% | no | NO_INCIDENT | - |
| 2024-09-18 Wed | $3.86M | $3.51M | +9.9% | +/-18.7% | no | NO_INCIDENT | - |
| 2024-09-19 Thu | $4.17M | $3.54M | +17.8% | +/-20.0% | no | NO_INCIDENT | - |
| 2024-09-20 Fri | $3.91M | $3.56M | +9.6% | +/-23.5% | no | NO_INCIDENT | - |
| 2024-09-21 Sat | $3.78M | $3.58M | +5.6% | +/-24.4% | no | NO_INCIDENT | - |
| 2024-09-22 Sun | $3.52M | $3.61M | -2.4% | +/-24.3% | no | NO_INCIDENT | - |
| 2024-09-23 Mon | $3.42M | $3.62M | -5.5% | +/-23.2% | no | NO_INCIDENT | - |
| 2024-09-24 Tue | $3.48M | $3.64M | -4.3% | +/-21.8% | no | NO_INCIDENT | - |
| 2024-09-25 Wed | $3.73M | $3.63M | +2.7% | +/-21.9% | no | NO_INCIDENT | - |
| 2024-09-26 Thu | $4.05M | $3.66M | +10.9% | +/-21.2% | no | NO_INCIDENT | - |
| 2024-09-27 Fri | $3.59M | $3.66M | -1.9% | +/-21.6% | no | NO_INCIDENT | - |
| 2024-09-28 Sat | $3.73M | $3.66M | +1.8% | +/-21.6% | no | NO_INCIDENT | - |
| 2024-09-29 Sun | $3.37M | $3.67M | -8.2% | +/-21.4% | no | NO_INCIDENT | - |
| 2024-09-30 Mon | $3.15M | $3.67M | -14.1% | +/-21.5% | no | NO_INCIDENT | - |
| 2024-10-01 Tue | $3.35M | $3.67M | -8.8% | +/-21.8% | no | NO_INCIDENT | - |
| 2024-10-02 Wed | $3.24M | $3.65M | -11.1% | +/-22.9% | no | NO_INCIDENT | - |
| 2024-10-03 Thu | $3.05M | $3.61M | -15.4% | +/-24.2% | no | NO_INCIDENT | - |
| 2024-10-04 Fri | $3.17M | $3.53M | -10.1% | +/-23.7% | no | NO_INCIDENT | - |
| 2024-10-05 Sat | $3.34M | $3.47M | -3.9% | +/-23.4% | no | NO_INCIDENT | clock_shift:REJECTED |
| 2024-10-06 Sun | $3.15M | $3.44M | -8.5% | +/-22.6% | no | NO_INCIDENT | - |
| 2024-10-07 Mon | $3.16M | $3.42M | -7.5% | +/-23.6% | no | NO_INCIDENT | - |
| 2024-10-08 Tue | $3.52M | $3.40M | +3.6% | +/-24.4% | no | NO_INCIDENT | - |
| 2024-10-09 Wed | $3.73M | $3.40M | +9.6% | +/-24.5% | no | NO_INCIDENT | - |
| 2024-10-10 Thu | $4.13M | $3.40M | +21.5% | +/-24.5% | no | NO_INCIDENT | - |
| 2024-10-11 Fri | $3.68M | $3.59M | +2.6% | +/-18.0% | yes | NO_INCIDENT | - |
| 2024-10-12 Sat | $3.39M | $3.56M | -4.7% | +/-18.1% | yes | NO_INCIDENT | - |
| 2024-10-13 Sun | $3.22M | $3.39M | -5.1% | +/-25.0% | no | NO_INCIDENT | - |
| 2024-10-14 Mon | $2.97M | $3.23M | -8.0% | +/-18.2% | yes | NO_INCIDENT | - |
| 2024-10-15 Tue | $3.80M | $3.50M | +8.6% | +/-18.6% | yes | NO_INCIDENT | - |
| 2024-10-16 Wed | $3.97M | $3.59M | +10.4% | +/-19.0% | yes | NO_INCIDENT | - |
| 2024-10-17 Thu | $4.11M | $3.88M | +5.9% | +/-19.1% | yes | NO_INCIDENT | - |
| 2024-10-18 Fri | $3.86M | $3.59M | +7.4% | +/-19.2% | yes | NO_INCIDENT | - |
| 2024-10-19 Sat | $3.70M | $3.55M | +4.0% | +/-19.5% | yes | NO_INCIDENT | - |
| 2024-10-20 Sun | $3.49M | $3.33M | +4.9% | +/-19.5% | yes | NO_INCIDENT | - |
| 2024-10-21 Mon | $3.31M | $3.18M | +4.2% | +/-19.6% | yes | NO_INCIDENT | - |
| 2024-10-22 Tue | $3.53M | $3.55M | -0.5% | +/-19.7% | yes | NO_INCIDENT | - |
| 2024-10-23 Wed | $3.77M | $3.71M | +1.8% | +/-19.7% | yes | NO_INCIDENT | - |
| 2024-10-24 Thu | $4.08M | $3.90M | +4.5% | +/-19.6% | yes | NO_INCIDENT | - |
| 2024-10-25 Fri | $3.94M | $3.64M | +8.1% | +/-19.5% | yes | NO_INCIDENT | - |
| 2024-10-26 Sat | $4.04M | $3.65M | +10.6% | +/-27.2% | no | NO_INCIDENT | - |
| 2024-10-27 Sun | $3.53M | $3.70M | -4.7% | +/-27.3% | no | NO_INCIDENT | - |
| 2024-10-28 Mon | $3.34M | $3.72M | -10.2% | +/-25.3% | no | NO_INCIDENT | - |
| 2024-10-29 Tue | $3.68M | $3.75M | -1.9% | +/-20.8% | no | NO_INCIDENT | - |
| 2024-10-30 Wed | $3.86M | $3.74M | +3.2% | +/-20.9% | no | NO_INCIDENT | - |
| 2024-10-31 Thu | $3.65M | $3.73M | -2.3% | +/-20.5% | no | NO_INCIDENT | - |
| 2024-11-01 Fri | $4.16M | $3.70M | +12.5% | +/-18.9% | no | NO_INCIDENT | - |
| 2024-11-02 Sat | $3.54M | $3.72M | -4.8% | +/-20.9% | no | NO_INCIDENT | - |
| 2024-11-03 Sun | $3.39M | $3.71M | -8.6% | +/-21.3% | no | NO_INCIDENT | - |
| 2024-11-04 Mon | $3.00M | $3.70M | -19.0% | +/-21.9% | no | NO_INCIDENT | - |
| 2024-11-05 Tue | $2.57M | $3.68M | -30.1% | +/-25.4% | no | UNEXPLAINED | - |
| 2024-11-06 Wed | $3.27M | $3.68M | -11.2% | +/-25.4% | no | NO_INCIDENT | - |
| 2024-11-07 Thu | $3.74M | $3.66M | +2.3% | +/-26.8% | no | NO_INCIDENT | - |
| 2024-11-08 Fri | $3.72M | $3.76M | -1.2% | +/-18.1% | yes | NO_INCIDENT | - |
| 2024-11-09 Sat | $3.65M | $3.60M | +1.4% | +/-15.8% | yes | NO_INCIDENT | - |
| 2024-11-10 Sun | $3.29M | $3.35M | -2.0% | +/-15.2% | yes | NO_INCIDENT | - |
| 2024-11-11 Mon | $3.01M | $3.16M | -4.7% | +/-14.9% | yes | NO_INCIDENT | - |
| 2024-11-12 Tue | $3.66M | $3.63M | +0.9% | +/-15.0% | yes | NO_INCIDENT | - |
| 2024-11-13 Wed | $3.88M | $3.72M | +4.3% | +/-14.9% | yes | NO_INCIDENT | - |
| 2024-11-14 Thu | $4.12M | $3.94M | +4.6% | +/-15.0% | yes | NO_INCIDENT | - |
| 2024-11-15 Fri | $3.92M | $3.87M | +1.4% | +/-15.0% | yes | NO_INCIDENT | - |
| 2024-11-16 Sat | $3.88M | $3.66M | +5.9% | +/-14.7% | yes | NO_INCIDENT | - |
| 2024-11-17 Sun | $3.51M | $3.38M | +3.7% | +/-14.2% | yes | NO_INCIDENT | - |
| 2024-11-18 Mon | $3.30M | $3.13M | +5.5% | +/-13.9% | yes | NO_INCIDENT | - |
| 2024-11-19 Tue | $3.53M | $3.67M | -3.7% | +/-13.7% | yes | NO_INCIDENT | - |
| 2024-11-20 Wed | $3.80M | $3.75M | +1.3% | +/-13.6% | yes | NO_INCIDENT | - |
| 2024-11-21 Thu | $4.46M | $3.94M | +13.3% | +/-13.3% | yes | NO_INCIDENT | - |
| 2024-11-22 Fri | $4.17M | $3.92M | +6.5% | +/-14.5% | yes | NO_INCIDENT | - |
| 2024-11-23 Sat | $3.51M | $3.76M | -6.7% | +/-14.7% | yes | NO_INCIDENT | - |
| 2024-11-24 Sun | $2.95M | $3.44M | -14.2% | +/-15.1% | yes | NO_INCIDENT | - |
| 2024-11-25 Mon | $2.88M | $3.19M | -9.8% | +/-16.5% | yes | NO_INCIDENT | - |
| 2024-11-26 Tue | $3.23M | $3.60M | -10.4% | +/-16.9% | yes | NO_INCIDENT | - |
| 2024-11-27 Wed | $3.06M | $3.71M | -17.5% | +/-17.6% | yes | NO_INCIDENT | - |
| 2024-11-28 Thu | $2.00M | $4.01M | -50.0% | +/-19.5% | yes | UNEXPLAINED | - |
| 2024-11-29 Fri | $2.39M | $3.98M | -39.9% | +/-19.8% | yes | REAL_CHANGE | - |
| 2024-11-30 Sat | $2.93M | $3.47M | -15.6% | +/-46.2% | no | NO_INCIDENT | - |
| 2024-12-01 Sun | $2.94M | $3.40M | -13.6% | +/-47.3% | no | NO_INCIDENT | - |
| 2024-12-02 Mon | $3.50M | $3.33M | +5.0% | +/-47.8% | no | NO_INCIDENT | - |
| 2024-12-03 Tue | $3.86M | $3.33M | +16.0% | +/-47.8% | no | NO_INCIDENT | - |
| 2024-12-04 Wed | $4.00M | $3.37M | +18.6% | +/-48.7% | no | NO_INCIDENT | - |
| 2024-12-05 Thu | $4.48M | $3.41M | +31.4% | +/-50.2% | no | NO_INCIDENT | - |
| 2024-12-06 Fri | $4.35M | $3.45M | +26.1% | +/-54.5% | no | NO_INCIDENT | - |
| 2024-12-07 Sat | $3.97M | $3.45M | +15.1% | +/-53.6% | no | NO_INCIDENT | - |
| 2024-12-08 Sun | $3.57M | $3.43M | +4.0% | +/-52.5% | no | NO_INCIDENT | - |
| 2024-12-09 Mon | $3.61M | $3.44M | +5.1% | +/-52.5% | no | NO_INCIDENT | - |
| 2024-12-10 Tue | $4.15M | $3.48M | +19.0% | +/-50.5% | no | NO_INCIDENT | - |
| 2024-12-11 Wed | $4.38M | $3.57M | +22.5% | +/-49.0% | no | NO_INCIDENT | - |
| 2024-12-12 Thu | $4.89M | $3.66M | +33.9% | +/-50.1% | no | NO_INCIDENT | - |
| 2024-12-13 Fri | $4.62M | $3.71M | +24.4% | +/-33.0% | yes | NO_INCIDENT | - |
| 2024-12-14 Sat | $4.28M | $3.95M | +8.5% | +/-43.3% | no | NO_INCIDENT | - |
| 2024-12-15 Sun | $3.59M | $4.04M | -11.3% | +/-37.0% | no | NO_INCIDENT | - |
| 2024-12-16 Mon | $3.35M | $4.09M | -18.0% | +/-30.6% | no | NO_INCIDENT | - |
| 2024-12-17 Tue | $3.68M | $4.08M | -9.8% | +/-31.9% | no | NO_INCIDENT | - |
| 2024-12-18 Wed | $4.01M | $4.07M | -1.5% | +/-32.6% | no | NO_INCIDENT | - |
| 2024-12-19 Thu | $4.09M | $4.07M | +0.6% | +/-32.6% | no | NO_INCIDENT | - |
| 2024-12-20 Fri | $3.84M | $4.04M | -4.9% | +/-31.8% | no | NO_INCIDENT | - |
| 2024-12-21 Sat | $3.45M | $4.00M | -13.7% | +/-31.6% | no | NO_INCIDENT | - |
| 2024-12-22 Sun | $2.86M | $3.97M | -28.0% | +/-33.6% | no | NO_INCIDENT | - |
| 2024-12-23 Mon | $2.70M | $3.91M | -31.0% | +/-39.9% | no | NO_INCIDENT | - |
| 2024-12-24 Tue | $2.04M | $3.85M | -46.9% | +/-47.1% | no | NO_INCIDENT | - |
| 2024-12-25 Wed | $1.47M | $3.70M | -60.3% | +/-61.2% | no | NO_INCIDENT | - |
| 2024-12-26 Thu | $2.21M | $3.49M | -36.7% | +/-79.2% | no | NO_INCIDENT | - |
| 2024-12-27 Fri | $2.52M | $3.30M | -23.6% | +/-80.7% | no | NO_INCIDENT | - |
| 2024-12-28 Sat | $2.44M | $3.15M | -22.5% | +/-78.9% | no | NO_INCIDENT | - |
| 2024-12-29 Sun | $2.37M | $3.02M | -21.3% | +/-77.8% | no | NO_INCIDENT | - |
| 2024-12-30 Mon | $2.43M | $2.93M | -17.1% | +/-80.0% | no | NO_INCIDENT | - |
| 2024-12-31 Tue | $2.23M | $2.87M | -22.3% | +/-81.9% | no | NO_INCIDENT | - |
