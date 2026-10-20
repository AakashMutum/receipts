# Receipts evaluation

30 runs: 10 scenarios x 3 seeds (3,000 orders a day, 42 days of history, backend duckdb). Generated 2026-10-20 10:39:41.

**Receipts passed 29 of 30 runs** (right verdict and exactly the right causes).

| System | Hold decision right | Cause precision | Cause recall | Wrong causes named | Causes missed |
|---|---|---|---|---|---|
| Receipts | 97% | 100% | 100% | 0 | 0 |
| Detectors only (ablation, no undo test) | 80% | 89% | 100% | 3 | 0 |
| Threshold alert (typical monitor) | 73% | 100% | 0% | 0 | 24 |

Corrected value after the proven fix, against the true clean value: mean error 0.001%, max 0.009%.
Gate latency per run: median 454 ms, max 602 ms.

## Per scenario

| Scenario | Seed | Change | Expected | Receipts verdict | Causes | Pass |
|---|---|---|---|---|---|---|
| healthy | 11 | +4.0% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 11 | +26.1% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 11 | +558.6% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 11 | +16.9% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 11 | +25.6% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 11 | -5.2% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 11 | -11.7% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 11 | -14.4% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 11 | +10.9% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 11 | -7.8% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 22 | -1.4% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 22 | +21.9% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 22 | +388.9% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 22 | +10.0% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 22 | +15.0% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 22 | -8.7% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 22 | -16.3% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 22 | -20.6% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 22 | +4.0% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 22 | -11.2% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 33 | +1.1% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 33 | +25.9% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 33 | +355.0% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 33 | +13.2% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 33 | +23.0% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 33 | -6.1% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 33 | -15.8% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 33 | -16.3% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 33 | +4.5% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 33 | -8.8% | UNEXPLAINED | NO_INCIDENT | - | NO |

## What the rows mean

* **Hold decision right**: faulty batches held, healthy and genuinely changed batches published.
* **Detectors only** is the ablation. It names every check that fired. On the festival day the retry burst trips the duplicate check, so it blames a fault that is not there. The undo test removes it.
* **Threshold alert** never names a cause, holds the real festival surge, and misses the masked pair because the total looks normal.
* The unknown fault has no detector by design. The right answer is UNEXPLAINED (held, no cause named), and that is what is scored.
