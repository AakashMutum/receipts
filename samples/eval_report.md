# Receipts evaluation

50 runs: 10 scenarios x 5 seeds (20,000 orders a day, 42 days of history, backend exasol). Generated 2026-10-21 14:02:40.

**Receipts passed 50 of 50 runs** (right verdict and exactly the right causes).

| System | Hold decision right | Cause precision | Cause recall | Wrong causes named | Causes missed |
|---|---|---|---|---|---|
| Receipts | 100% | 100% | 100% | 0 | 0 |
| Detectors only (ablation, no undo test) | 80% | 89% | 100% | 5 | 0 |
| Threshold alert (typical monitor) | 88% | 100% | 0% | 0 | 40 |

Corrected value after the proven fix, against the true clean value: mean error 0.001%, max 0.017%.
Gate latency per run: median 3047 ms, max 6200 ms.

## Per scenario

| Scenario | Seed | Change | Expected | Receipts verdict | Causes | Pass |
|---|---|---|---|---|---|---|
| healthy | 11 | -0.2% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 11 | +22.6% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 11 | +447.3% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 11 | +12.3% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 11 | +20.8% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 11 | -8.7% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 11 | -16.1% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 11 | -17.3% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 11 | +4.7% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 11 | -10.3% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 22 | +1.3% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 22 | +24.7% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 22 | +472.5% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 22 | +13.6% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 22 | +17.6% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 22 | -8.1% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 22 | -14.7% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 22 | -16.3% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 22 | +7.0% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 22 | -9.5% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 33 | +2.0% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 33 | +25.2% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 33 | +470.8% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 33 | +14.8% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 33 | +22.6% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 33 | -7.3% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 33 | -15.2% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 33 | -15.2% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 33 | +6.6% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 33 | -8.8% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 44 | -1.4% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 44 | +21.6% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 44 | +480.4% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 44 | +11.2% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 44 | +18.6% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 44 | -9.9% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 44 | -17.3% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 44 | -19.1% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 44 | +4.0% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 44 | -11.7% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 55 | +2.0% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 55 | +25.1% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 55 | +473.8% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 55 | +14.5% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 55 | +25.1% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 55 | -6.9% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 55 | -14.3% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 55 | -15.3% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 55 | +7.4% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 55 | -8.5% | UNEXPLAINED | UNEXPLAINED | - | yes |

## What the rows mean

* **Hold decision right**: faulty batches held, healthy and genuinely changed batches published.
* **Detectors only** is the ablation. It names every check that fired. On the festival day the retry burst trips the duplicate check, so it blames a fault that is not there. The undo test removes it.
* **Threshold alert** never names a cause, holds the real festival surge, and misses the masked pair because the total looks normal.
* The unknown fault has no detector by design. The right answer is UNEXPLAINED (held, no cause named), and that is what is scored.
