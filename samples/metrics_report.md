# Configured metrics through the same gate

Metrics from `receipts.yaml`: daily_revenue_inr, daily_order_count, avg_basket_inr. On the DuckDB stand-in, synthetic data, 8,000 orders a day, seeds 11, 22. Generated 2026-10-27 06:31:04 in 95 s. Reproduce: `receipts connect --scenarios --seeds 11 22 --orders-per-day 8000`.

Each scenario is landed once and judged for every metric. The error is the metric's candidate value against the same night without the fault. A fault that does not move a metric should be published for that metric; a move of 4% or more should be held. Metrics other than revenue are judged without write-back. The six detectors and the slice breakdown are the revenue pipeline's own, so the causes they name are about the shared raw tables.

| Metric | Held, right | Published, right | Held, metric was fine | Published WRONG |
|---|---|---|---|---|
| daily_revenue_inr | 16 | 4 | 0 | 0 |
| daily_order_count | 6 | 14 | 0 | 0 |
| avg_basket_inr | 12 | 6 | 0 | 2 |

## Every run

| Seed | Metric | Scenario | Error | Verdict | Causes | Outcome |
|---|---|---|---|---|---|---|
| 11 | daily_revenue_inr | healthy | -0.00% | NO_INCIDENT | - | published, right |
| 11 | daily_order_count | healthy | +0.00% | NO_INCIDENT | - | published, right |
| 11 | avg_basket_inr | healthy | -0.00% | NO_INCIDENT | - | published, right |
| 11 | daily_revenue_inr | festival | -0.00% | REAL_CHANGE | - | published, right |
| 11 | daily_order_count | festival | +0.00% | REAL_CHANGE | - | published, right |
| 11 | avg_basket_inr | festival | +0.00% | NO_INCIDENT | - | published, right |
| 11 | daily_revenue_inr | unit_paise | +439.41% | PROVEN_FAULT | unit_scale | held, right |
| 11 | daily_order_count | unit_paise | +0.00% | NO_INCIDENT | - | published, right |
| 11 | avg_basket_inr | unit_paise | +439.41% | PROVEN_FAULT | unit_scale | held, right |
| 11 | daily_revenue_inr | duplicate_load | +12.61% | PROVEN_FAULT | duplicate_key | held, right |
| 11 | daily_order_count | duplicate_load | +0.00% | NO_INCIDENT | - | published, right |
| 11 | avg_basket_inr | duplicate_load | +12.61% | PROVEN_FAULT | duplicate_key | held, right |
| 11 | daily_revenue_inr | join_fanout | +20.81% | PROVEN_FAULT | key_fanout | held, right |
| 11 | daily_order_count | join_fanout | +0.00% | NO_INCIDENT | - | published, right |
| 11 | avg_basket_inr | join_fanout | +20.81% | NO_INCIDENT | - | published WRONG |
| 11 | daily_revenue_inr | stale_fx | -8.08% | PROVEN_FAULT | stale_feed | held, right |
| 11 | daily_order_count | stale_fx | +0.00% | NO_INCIDENT | - | published, right |
| 11 | avg_basket_inr | stale_fx | -8.08% | PROVEN_FAULT | stale_feed | held, right |
| 11 | daily_revenue_inr | ist_utc | -15.36% | PROVEN_FAULT | clock_shift | held, right |
| 11 | daily_order_count | ist_utc | -15.73% | PROVEN_FAULT | clock_shift | held, right |
| 11 | avg_basket_inr | ist_utc | +0.44% | NO_INCIDENT | - | published, right |
| 11 | daily_revenue_inr | new_code | -16.42% | PROVEN_FAULT | orphan_code | held, right |
| 11 | daily_order_count | new_code | -7.34% | PROVEN_FAULT | orphan_code | held, right |
| 11 | avg_basket_inr | new_code | -9.80% | PROVEN_FAULT | orphan_code | held, right |
| 11 | daily_revenue_inr | masked_pair | +5.57% | PROVEN_FAULT | clock_shift, duplicate_key | held, right |
| 11 | daily_order_count | masked_pair | -15.73% | PROVEN_FAULT | clock_shift | held, right |
| 11 | avg_basket_inr | masked_pair | +25.28% | PROVEN_FAULT | duplicate_key | held, right |
| 11 | daily_revenue_inr | unknown_discount | -9.52% | UNEXPLAINED | - | held, right |
| 11 | daily_order_count | unknown_discount | +0.00% | NO_INCIDENT | - | published, right |
| 11 | avg_basket_inr | unknown_discount | -9.52% | UNEXPLAINED | - | held, right |
| 22 | daily_revenue_inr | healthy | -0.00% | NO_INCIDENT | - | published, right |
| 22 | daily_order_count | healthy | +0.00% | NO_INCIDENT | - | published, right |
| 22 | avg_basket_inr | healthy | -0.00% | NO_INCIDENT | - | published, right |
| 22 | daily_revenue_inr | festival | -0.00% | REAL_CHANGE | - | published, right |
| 22 | daily_order_count | festival | +0.00% | REAL_CHANGE | - | published, right |
| 22 | avg_basket_inr | festival | -0.00% | NO_INCIDENT | - | published, right |
| 22 | daily_revenue_inr | unit_paise | +435.09% | PROVEN_FAULT | unit_scale | held, right |
| 22 | daily_order_count | unit_paise | +0.00% | NO_INCIDENT | - | published, right |
| 22 | avg_basket_inr | unit_paise | +435.09% | PROVEN_FAULT | unit_scale | held, right |
| 22 | daily_revenue_inr | duplicate_load | +12.63% | PROVEN_FAULT | duplicate_key | held, right |
| 22 | daily_order_count | duplicate_load | +0.00% | NO_INCIDENT | - | published, right |
| 22 | avg_basket_inr | duplicate_load | +12.63% | PROVEN_FAULT | duplicate_key | held, right |
| 22 | daily_revenue_inr | join_fanout | +16.74% | PROVEN_FAULT | key_fanout | held, right |
| 22 | daily_order_count | join_fanout | +0.00% | NO_INCIDENT | - | published, right |
| 22 | avg_basket_inr | join_fanout | +16.74% | NO_INCIDENT | - | published WRONG |
| 22 | daily_revenue_inr | stale_fx | -8.41% | PROVEN_FAULT | stale_feed | held, right |
| 22 | daily_order_count | stale_fx | +0.00% | NO_INCIDENT | - | published, right |
| 22 | avg_basket_inr | stale_fx | -8.41% | PROVEN_FAULT | stale_feed | held, right |
| 22 | daily_revenue_inr | ist_utc | -15.55% | PROVEN_FAULT | clock_shift | held, right |
| 22 | daily_order_count | ist_utc | -15.56% | PROVEN_FAULT | clock_shift | held, right |
| 22 | avg_basket_inr | ist_utc | +0.01% | NO_INCIDENT | - | published, right |
| 22 | daily_revenue_inr | new_code | -17.67% | PROVEN_FAULT | orphan_code | held, right |
| 22 | daily_order_count | new_code | -7.17% | PROVEN_FAULT | orphan_code | held, right |
| 22 | avg_basket_inr | new_code | -11.31% | PROVEN_FAULT | orphan_code | held, right |
| 22 | daily_revenue_inr | masked_pair | +5.44% | PROVEN_FAULT | clock_shift, duplicate_key | held, right |
| 22 | daily_order_count | masked_pair | -15.56% | PROVEN_FAULT | clock_shift | held, right |
| 22 | avg_basket_inr | masked_pair | +24.87% | PROVEN_FAULT | duplicate_key | held, right |
| 22 | daily_revenue_inr | unknown_discount | -11.00% | UNEXPLAINED | - | held, right |
| 22 | daily_order_count | unknown_discount | +0.00% | NO_INCIDENT | - | published, right |
| 22 | avg_basket_inr | unknown_discount | -11.00% | UNEXPLAINED | - | held, right |
