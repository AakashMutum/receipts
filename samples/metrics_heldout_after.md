# Held-out faults for the configured metrics (after)

Metrics from `receipts.yaml`: daily_order_count, avg_basket_inr. On the DuckDB stand-in, synthetic data, 8,000 orders a day, seeds 31, 32. Generated 2026-10-27 07:12:29 in 48 s. Reproduce: `receipts connect --heldout --orders-per-day 8000`.

Each scenario is landed once and judged for every metric. The error is the metric's candidate value against the same night without the fault. A fault that does not move a metric should be published for that metric; a move of 4% or more should be held. Metrics other than revenue are judged without write-back. The six detectors and the slice breakdown are the revenue pipeline's own, so the causes they name are about the shared raw tables.

| Metric | Held, right | Published, right | Held, metric was fine | Published WRONG |
|---|---|---|---|---|
| daily_order_count | 2 | 12 | 2 | 0 |
| avg_basket_inr | 14 | 2 | 0 | 0 |

## Every run

| Seed | Metric | Scenario | Error | Verdict | Causes | Outcome |
|---|---|---|---|---|---|---|
| 31 | daily_order_count | Merchant table fans out, 5% of merchants | +0.00% | NO_INCIDENT | - | published, right |
| 31 | avg_basket_inr | Merchant table fans out, 5% of merchants | +6.49% | PROVEN_FAULT | key_fanout | held, right |
| 31 | daily_order_count | Merchant table fans out, 25% of merchants | +0.00% | NO_INCIDENT | - | published, right |
| 31 | avg_basket_inr | Merchant table fans out, 25% of merchants | +31.86% | PROVEN_FAULT | key_fanout | held, right |
| 31 | daily_order_count | Merchant table fans out, 100% of merchants | +0.00% | NO_INCIDENT | - | published, right |
| 31 | avg_basket_inr | Merchant table fans out, 100% of merchants | +100.00% | PROVEN_FAULT | key_fanout | held, right |
| 31 | daily_order_count | New category code, 25% of Electronics orders | -3.97% | PROVEN_FAULT | orphan_code | held, metric was fine |
| 31 | avg_basket_inr | New category code, 25% of Electronics orders | -5.80% | PROVEN_FAULT | orphan_code | held, right |
| 31 | daily_order_count | Payment rows loaded twice, 25% of today's payment rows | +0.00% | NO_INCIDENT | - | published, right |
| 31 | avg_basket_inr | Payment rows loaded twice, 25% of today's payment rows | +25.71% | PROVEN_FAULT | duplicate_key | held, right |
| 31 | daily_order_count | IST written as UTC, 100% of payments on the gateway (GW_A) | -21.92% | PROVEN_FAULT | clock_shift | held, right |
| 31 | avg_basket_inr | IST written as UTC, 100% of payments on the gateway (GW_A) | -0.56% | NO_INCIDENT | - | published, right |
| 31 | daily_order_count | Unit change (amounts x100), 10% of payments on the gateway (GW_B) | +0.00% | NO_INCIDENT | - | published, right |
| 31 | avg_basket_inr | Unit change (amounts x100), 10% of payments on the gateway (GW_B) | +375.82% | PROVEN_FAULT | unit_scale | held, right |
| 31 | daily_order_count | FX feed misses today | +0.00% | NO_INCIDENT | - | published, right |
| 31 | avg_basket_inr | FX feed misses today | -9.80% | PROVEN_FAULT | stale_feed | held, right |
| 32 | daily_order_count | Merchant table fans out, 5% of merchants | +0.00% | NO_INCIDENT | - | published, right |
| 32 | avg_basket_inr | Merchant table fans out, 5% of merchants | +9.72% | PROVEN_FAULT | key_fanout | held, right |
| 32 | daily_order_count | Merchant table fans out, 25% of merchants | +0.00% | NO_INCIDENT | - | published, right |
| 32 | avg_basket_inr | Merchant table fans out, 25% of merchants | +34.56% | PROVEN_FAULT | key_fanout | held, right |
| 32 | daily_order_count | Merchant table fans out, 100% of merchants | +0.00% | NO_INCIDENT | - | published, right |
| 32 | avg_basket_inr | Merchant table fans out, 100% of merchants | +100.00% | PROVEN_FAULT | key_fanout | held, right |
| 32 | daily_order_count | New category code, 25% of Electronics orders | -3.72% | PROVEN_FAULT | orphan_code | held, metric was fine |
| 32 | avg_basket_inr | New category code, 25% of Electronics orders | -4.98% | PROVEN_FAULT | orphan_code | held, right |
| 32 | daily_order_count | Payment rows loaded twice, 25% of today's payment rows | +0.00% | NO_INCIDENT | - | published, right |
| 32 | avg_basket_inr | Payment rows loaded twice, 25% of today's payment rows | +25.04% | PROVEN_FAULT | duplicate_key | held, right |
| 32 | daily_order_count | IST written as UTC, 100% of payments on the gateway (GW_A) | -21.41% | PROVEN_FAULT | clock_shift | held, right |
| 32 | avg_basket_inr | IST written as UTC, 100% of payments on the gateway (GW_A) | -0.14% | NO_INCIDENT | - | published, right |
| 32 | daily_order_count | Unit change (amounts x100), 10% of payments on the gateway (GW_B) | +0.00% | NO_INCIDENT | - | published, right |
| 32 | avg_basket_inr | Unit change (amounts x100), 10% of payments on the gateway (GW_B) | +361.73% | PROVEN_FAULT | unit_scale | held, right |
| 32 | daily_order_count | FX feed misses today | +0.00% | NO_INCIDENT | - | published, right |
| 32 | avg_basket_inr | FX feed misses today | -9.05% | PROVEN_FAULT | stale_feed | held, right |
