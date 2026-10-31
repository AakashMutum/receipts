# Data manifest

Public data used by the real-data backtests. None of it is committed: the files live outside the repository (on the
author's machine in `D:\Hackathon\data`), and the scripts download them or say where to put them. Dates are the
download dates in IST.

## UCI Online Retail II with ECB reference rates

Used by [`scripts/backtest_retail.py`](../scripts/backtest_retail.py), report
[`samples/exasol/real_backtest_retail.md`](../samples/exasol/real_backtest_retail.md).

| File | Bytes | SHA-256 | Source | Downloaded |
|---|---|---|---|---|
| online_retail_ii.zip | 45,622,418 | `572e36277c2390fbfde10664750731e0a86f55e33470d91919085f0408e67bfb` | https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip | 2026-10-30 |
| eurofxref-hist.zip | 642,255 | `73db21584dd46cebf5cd6df75ebb6de7afcdeebff52f54d5046ca8e459c0fbb3` | https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip | 2026-10-30 |

* UCI: "This dataset is licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license."
  Chen, D. (2012), Online Retail II, UCI Machine Learning Repository, https://doi.org/10.24432/C5CG6D.
* ECB: "The reference rates are published for information purposes only." Source: European Central Bank.

## NYC TLC yellow taxi trips, 2023 and 2024

Used by [`scripts/backtest_taxi_chunks.py`](../scripts/backtest_taxi_chunks.py), report
[`samples/exasol/real_backtest_taxi_2023_2024.md`](../samples/exasol/real_backtest_taxi_2023_2024.md).

| File | Bytes | SHA-256 | Source | Downloaded |
|---|---|---|---|---|
| yellow_tripdata_2023-01.parquet | 47,673,370 | `32df6f67578fa86c484a6b5ef23a5281992ff085521082340b0f9e5889e9a572` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet | 2026-10-31 |
| yellow_tripdata_2023-02.parquet | 47,748,012 | `4809e6aaac64f05a62d16a25d55713be1537ad64fc261e895eaf2d2120fe750a` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-02.parquet | 2026-10-31 |
| yellow_tripdata_2023-03.parquet | 56,127,762 | `e7d44943111b007bf0e7084863511886e0db29f862f9a96239383a1f86c6c26e` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-03.parquet | 2026-10-31 |
| yellow_tripdata_2023-04.parquet | 54,222,699 | `95c01c53c865e06489179bdecce3a59603697a1557c4d5d183c20ae13a144dc6` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-04.parquet | 2026-10-31 |
| yellow_tripdata_2023-05.parquet | 58,654,627 | `9bd7d1c557bb9d0413619ba296b4828b884852a70bd07f2230b83f080d9a8591` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-05.parquet | 2026-10-31 |
| yellow_tripdata_2023-06.parquet | 54,999,465 | `3e60e29b5df45683948b68acbfb503aa459d14162c610622585c6580fdbfc73a` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-06.parquet | 2026-10-31 |
| yellow_tripdata_2023-07.parquet | 48,361,828 | `98504ae351d920e9e0b61241f5707f90ee1588cfb199c378459234b5035805ab` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-07.parquet | 2026-10-31 |
| yellow_tripdata_2023-08.parquet | 48,152,353 | `84ce36a2f84fa14c12fd976c79a7d4f30c871f1782b08ca7c27bb76ab946e66b` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-08.parquet | 2026-10-31 |
| yellow_tripdata_2023-09.parquet | 47,895,515 | `091bf156bea5bb10bd217f5f12375f966f8789349af45d5ee4153e3e1e077a87` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-09.parquet | 2026-10-31 |
| yellow_tripdata_2023-10.parquet | 59,009,059 | `dc5f069476d350df802ed8120f3b39ec321c34cfa905381e87f608c78ca0c645` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-10.parquet | 2026-10-31 |
| yellow_tripdata_2023-11.parquet | 56,094,653 | `af203de0e73a92d640121f02a34326f25037d62380fc406237c87c2a4231ae58` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-11.parquet | 2026-10-31 |
| yellow_tripdata_2023-12.parquet | 56,804,275 | `ab4f4db11cb31484747f62eb507c13fcfaff290aaf59c13e6465dea0b1166b9c` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-12.parquet | 2026-10-31 |
| yellow_tripdata_2024-01.parquet | 49,961,641 | `c4d59da7bbc8abaeeeb1727947ee93d9891a71acb42854bd80db1571b2030510` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet | 2026-10-31 |
| yellow_tripdata_2024-02.parquet | 50,349,284 | `c76c43c18c6c6664080dd920baab4928988d5786a6b65980792ca7cd796f9f20` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-02.parquet | 2026-10-31 |
| yellow_tripdata_2024-03.parquet | 60,078,280 | `2d4cdc8fb96726cdd3803b13b02d2e61e71d45720aff0ebc693a8bdd1f249823` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-03.parquet | 2026-10-31 |
| yellow_tripdata_2024-04.parquet | 59,133,625 | `ce37f736c7cf9e92164c850ef2b502a8f7bb590fc1804b6edbcb80293da01b89` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-04.parquet | 2026-10-31 |
| yellow_tripdata_2024-05.parquet | 62,553,128 | `1974230be2b5a3ea92e47b5eb77f32dbf1de896d81ad8df4ab6faba52749ad23` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-05.parquet | 2026-10-31 |
| yellow_tripdata_2024-06.parquet | 59,859,922 | `677cf14c8347f745b583f012fbdba072334c6c4efa17bfd6a64369f2ba30329c` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-06.parquet | 2026-10-31 |
| yellow_tripdata_2024-07.parquet | 52,299,432 | `af12d6b04daeb78550799ae99933d495b27d715b6dbb0fad9bb750a4537d3070` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-07.parquet | 2026-10-31 |
| yellow_tripdata_2024-08.parquet | 51,067,350 | `7315643dd16bafc03e27d9903edbfd35404c2550a695d0da0a3e73852d940cfb` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-08.parquet | 2026-10-31 |
| yellow_tripdata_2024-09.parquet | 61,170,186 | `2f42e4a383a6635de803001462848d0aee2b47f6ce899126805d2d05361fb843` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-09.parquet | 2026-10-31 |
| yellow_tripdata_2024-10.parquet | 64,346,071 | `d19fe05aa0b259af24eb47051735293287f1e6dc263ba04030ec1ab4c6ec2650` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-10.parquet | 2026-10-31 |
| yellow_tripdata_2024-11.parquet | 60,658,709 | `5ef321876de5007a7c147a347389133fc94fd7ac28f82eb1d57d8f2cf05cfd3b` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-11.parquet | 2026-10-31 |
| yellow_tripdata_2024-12.parquet | 61,524,085 | `41ebf7db80bebde60c58e5143c14cdf38ad04a0f3e3ff44215b3e240d55f6c78` | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-12.parquet | 2026-10-31 |
| taxi_zone_lookup.csv | 12,331 | `1a99e105092230f8620f301edcca7f80d3080642ff404d28ed957d3fa222c8ed` | https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv | 2026-10-31 |

* TLC: "The trip data was not created by the TLC, and TLC makes no representations as to the accuracy of these
  data." (https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
* NYC Open Data FAQ: "Open Data belongs to all New Yorkers. There are no restrictions on the use of Open Data."
  (https://www.nyc.gov/opendata/get-started/FAQs)
