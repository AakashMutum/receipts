# Red team: where Receipts breaks

**Run this on the built-in synthetic data or a sandbox copy, never on live production tables.** Every attack writes a planted fault into RAW.

On Exasol 2026.2.0-nano.3, 20,000 orders a day, seeds 11, 22, 33, 44, 55, 66, 77, 88, 99, 110, 121, 132, 143, 154, 165, 176, 187, 198, 209, 220, 231, 242, 253, 264, 275. Generated 2026-10-31 05:30:45 in 130 minutes. Reproduce: `python scripts/evidence_seeds.py redteam --backend exasol`.

For each fault class an attacker shrinks the share of rows affected (100, 50, 25, 10, 5, 2 percent). After the first step the gate no longer proves, it keeps shrinking while the fault still moves the number by 4% or more (a smaller one cannot be published as a wrong number), then stops. The detection floor is the smallest share proven with the right cause at every step down to it; with several seeds the worst seed counts. Nothing was tuned for this run.

## Detection floor per fault class

| Fault class | Detection floor | What happened below the floor | Holes |
|---|---|---|---|
| Unit change (amounts x100) | 100% | held, nothing proven | 0 |
| Payment rows loaded twice | 2% | not reached: proven at every step | 0 |
| Merchant table fans out | 2% | not reached: proven at every step | 0 |
| FX feed misses today | 100% (binary: one rate is missing or not) | binary fault, nothing to shrink | 0 |
| IST written as UTC | 100% | published a number more than 4% off, held, nothing proven, published, under 4% off | 13 |
| New category code | 10% | published, under 4% off | 0 |

## Every step

| Seed | Fault | Gateway | Share | Outcome | Verdict | Causes named | Error |
|---|---|---|---|---|---|---|---|
| 11 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +448.62% |
| 11 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +230.23% |
| 11 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +127.25% |
| 11 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +44.20% |
| 11 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +19.51% |
| 11 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +6.47% |
| 11 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 11 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +49.95% |
| 11 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +24.96% |
| 11 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +9.95% |
| 11 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.92% |
| 11 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +1.90% |
| 11 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 11 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +68.80% |
| 11 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +33.77% |
| 11 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +13.24% |
| 11 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +5.89% |
| 11 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +1.98% |
| 11 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -8.48% |
| 11 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.93% |
| 11 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -7.85% |
| 11 | clock_shift | GW_B | 25% | held | UNEXPLAINED | none | -3.81% |
| 11 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.14% |
| 11 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.10% |
| 11 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.83% |
| 11 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.48% |
| 11 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.79% |
| 11 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.70% |
| 22 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +465.20% |
| 22 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +242.41% |
| 22 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +123.31% |
| 22 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +61.85% |
| 22 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +33.99% |
| 22 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +15.55% |
| 22 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 22 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +49.89% |
| 22 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +25.02% |
| 22 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +10.10% |
| 22 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +5.09% |
| 22 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +2.01% |
| 22 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 22 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +64.48% |
| 22 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +30.05% |
| 22 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +11.90% |
| 22 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +5.87% |
| 22 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +2.34% |
| 22 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -9.25% |
| 22 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.83% |
| 22 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -7.83% |
| 22 | clock_shift | GW_B | 25% | small | NO_INCIDENT | none | -3.68% |
| 22 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.90% |
| 22 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.24% |
| 22 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.48% |
| 22 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.42% |
| 22 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.60% |
| 22 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.70% |
| 33 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +459.84% |
| 33 | unit_scale | GW_C | 50% | held | UNEXPLAINED | none | +208.62% |
| 33 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +119.80% |
| 33 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +42.89% |
| 33 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +19.21% |
| 33 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +9.07% |
| 33 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 33 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +51.30% |
| 33 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +25.97% |
| 33 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +10.34% |
| 33 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +5.05% |
| 33 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +1.95% |
| 33 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 33 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +64.76% |
| 33 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +33.25% |
| 33 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +14.17% |
| 33 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +7.96% |
| 33 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +2.09% |
| 33 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -9.12% |
| 33 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -16.82% |
| 33 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -8.82% |
| 33 | clock_shift | GW_B | 25% | WRONG | NO_INCIDENT | none | -4.37% |
| 33 | clock_shift | GW_B | 10% | small | NO_INCIDENT | none | -1.65% |
| 33 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.55% |
| 33 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.72% |
| 33 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.93% |
| 33 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.65% |
| 33 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.76% |
| 33 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.65% |
| 44 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +488.49% |
| 44 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +247.97% |
| 44 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +127.92% |
| 44 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +52.24% |
| 44 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +25.15% |
| 44 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +10.20% |
| 44 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 44 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +50.18% |
| 44 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +25.09% |
| 44 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +10.10% |
| 44 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +5.14% |
| 44 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +2.08% |
| 44 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 44 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +67.02% |
| 44 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +35.40% |
| 44 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +16.10% |
| 44 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +8.58% |
| 44 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +3.04% |
| 44 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -8.66% |
| 44 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -16.19% |
| 44 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -8.18% |
| 44 | clock_shift | GW_B | 25% | small | NO_INCIDENT | none | -3.99% |
| 44 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.92% |
| 44 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.61% |
| 44 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.92% |
| 44 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.66% |
| 44 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.75% |
| 44 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.68% |
| 55 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +462.74% |
| 55 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +235.24% |
| 55 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +120.10% |
| 55 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +48.23% |
| 55 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +28.63% |
| 55 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +7.18% |
| 55 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 55 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +50.61% |
| 55 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +25.77% |
| 55 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +10.54% |
| 55 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +5.18% |
| 55 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +2.03% |
| 55 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 55 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +59.73% |
| 55 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +30.08% |
| 55 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +10.57% |
| 55 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +6.08% |
| 55 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +1.55% |
| 55 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -8.67% |
| 55 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.91% |
| 55 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -8.28% |
| 55 | clock_shift | GW_B | 25% | WRONG | NO_INCIDENT | none | -4.15% |
| 55 | clock_shift | GW_B | 10% | small | NO_INCIDENT | none | -1.63% |
| 55 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -33.65% |
| 55 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.25% |
| 55 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -9.06% |
| 55 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.66% |
| 55 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.67% |
| 55 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.61% |
| 66 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +470.69% |
| 66 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +236.50% |
| 66 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +124.49% |
| 66 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +58.04% |
| 66 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +24.26% |
| 66 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +8.10% |
| 66 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 66 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +50.29% |
| 66 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +25.10% |
| 66 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +9.97% |
| 66 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.72% |
| 66 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +1.80% |
| 66 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 66 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +64.31% |
| 66 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +31.16% |
| 66 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +11.53% |
| 66 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +5.79% |
| 66 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +2.58% |
| 66 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -8.85% |
| 66 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.57% |
| 66 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -7.74% |
| 66 | clock_shift | GW_B | 25% | WRONG | NO_INCIDENT | none | -4.04% |
| 66 | clock_shift | GW_B | 10% | small | NO_INCIDENT | none | -1.80% |
| 66 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -33.95% |
| 66 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -16.58% |
| 66 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.16% |
| 66 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.37% |
| 66 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.54% |
| 66 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.51% |
| 77 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +424.73% |
| 77 | unit_scale | GW_C | 50% | held | UNEXPLAINED | none | +207.43% |
| 77 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +97.82% |
| 77 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +38.89% |
| 77 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +16.91% |
| 77 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +7.53% |
| 77 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 77 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +49.29% |
| 77 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +24.61% |
| 77 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +9.72% |
| 77 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.77% |
| 77 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +1.96% |
| 77 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 77 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +60.45% |
| 77 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +28.42% |
| 77 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +13.41% |
| 77 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +5.78% |
| 77 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +2.36% |
| 77 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -8.71% |
| 77 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.96% |
| 77 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -7.84% |
| 77 | clock_shift | GW_B | 25% | small | NO_INCIDENT | none | -3.82% |
| 77 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -35.24% |
| 77 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -16.93% |
| 77 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.26% |
| 77 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.11% |
| 77 | orphan_code | - | 5% | small | NO_INCIDENT | none | -1.38% |
| 88 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +447.63% |
| 88 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +205.53% |
| 88 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +99.44% |
| 88 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +43.45% |
| 88 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +23.82% |
| 88 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +6.41% |
| 88 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 88 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +50.28% |
| 88 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +25.63% |
| 88 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +10.18% |
| 88 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.98% |
| 88 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +1.89% |
| 88 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 88 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +66.77% |
| 88 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +30.54% |
| 88 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +12.98% |
| 88 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +5.96% |
| 88 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +2.10% |
| 88 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -9.34% |
| 88 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -16.10% |
| 88 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -7.74% |
| 88 | clock_shift | GW_B | 25% | held | UNEXPLAINED | none | -3.81% |
| 88 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.97% |
| 88 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.27% |
| 88 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.32% |
| 88 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.20% |
| 88 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.63% |
| 88 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.62% |
| 99 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +452.16% |
| 99 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +223.44% |
| 99 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +97.14% |
| 99 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +46.23% |
| 99 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +27.14% |
| 99 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +8.54% |
| 99 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 99 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +49.98% |
| 99 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +25.00% |
| 99 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +9.89% |
| 99 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.87% |
| 99 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +1.92% |
| 99 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 99 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +66.31% |
| 99 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +32.44% |
| 99 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +12.24% |
| 99 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +6.96% |
| 99 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +3.23% |
| 99 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -9.08% |
| 99 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -16.13% |
| 99 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -8.07% |
| 99 | clock_shift | GW_B | 25% | WRONG | NO_INCIDENT | none | -4.15% |
| 99 | clock_shift | GW_B | 10% | small | NO_INCIDENT | none | -1.63% |
| 99 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.05% |
| 99 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.01% |
| 99 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.35% |
| 99 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.39% |
| 99 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.69% |
| 99 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.64% |
| 110 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +463.86% |
| 110 | unit_scale | GW_C | 50% | held | UNEXPLAINED | none | +234.85% |
| 110 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +109.44% |
| 110 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +46.88% |
| 110 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +22.86% |
| 110 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +10.45% |
| 110 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 110 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +49.48% |
| 110 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +24.11% |
| 110 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +9.97% |
| 110 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +5.09% |
| 110 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +1.98% |
| 110 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 110 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +76.64% |
| 110 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +55.34% |
| 110 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +42.91% |
| 110 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +3.67% |
| 110 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +1.61% |
| 110 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -9.03% |
| 110 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.50% |
| 110 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -7.37% |
| 110 | clock_shift | GW_B | 25% | small | NO_INCIDENT | none | -3.53% |
| 110 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.80% |
| 110 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.08% |
| 110 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.16% |
| 110 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.56% |
| 110 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.87% |
| 110 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.66% |
| 121 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +431.63% |
| 121 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +225.86% |
| 121 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +115.12% |
| 121 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +50.21% |
| 121 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +21.49% |
| 121 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +5.84% |
| 121 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 121 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +49.34% |
| 121 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +24.84% |
| 121 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +9.82% |
| 121 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.91% |
| 121 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +2.00% |
| 121 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 121 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +67.52% |
| 121 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +27.90% |
| 121 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +12.72% |
| 121 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +7.06% |
| 121 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +1.93% |
| 121 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -9.37% |
| 121 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.81% |
| 121 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -7.91% |
| 121 | clock_shift | GW_B | 25% | WRONG | NO_INCIDENT | none | -4.15% |
| 121 | clock_shift | GW_B | 10% | small | NO_INCIDENT | none | -1.67% |
| 121 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -35.06% |
| 121 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -16.82% |
| 121 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.58% |
| 121 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.25% |
| 121 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.71% |
| 121 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.72% |
| 132 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +473.88% |
| 132 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +245.00% |
| 132 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +119.57% |
| 132 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +38.97% |
| 132 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +19.34% |
| 132 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +6.19% |
| 132 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 132 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +49.77% |
| 132 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +25.46% |
| 132 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +10.07% |
| 132 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.91% |
| 132 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +1.96% |
| 132 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 132 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +62.25% |
| 132 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +32.31% |
| 132 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +12.32% |
| 132 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +6.12% |
| 132 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +3.40% |
| 132 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -8.81% |
| 132 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.51% |
| 132 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -7.74% |
| 132 | clock_shift | GW_B | 25% | held | UNEXPLAINED | none | -4.14% |
| 132 | clock_shift | GW_B | 10% | small | NO_INCIDENT | none | -1.56% |
| 132 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.23% |
| 132 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -16.72% |
| 132 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.69% |
| 132 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.34% |
| 132 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.61% |
| 132 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.62% |
| 143 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +428.52% |
| 143 | unit_scale | GW_C | 50% | held | UNEXPLAINED | none | +218.31% |
| 143 | unit_scale | GW_C | 25% | held | UNEXPLAINED | none | +101.90% |
| 143 | unit_scale | GW_C | 10% | held | UNEXPLAINED | none | +37.61% |
| 143 | unit_scale | GW_C | 5% | held | UNEXPLAINED | none | +19.92% |
| 143 | unit_scale | GW_C | 2% | held | UNEXPLAINED | none | +10.50% |
| 143 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 143 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +49.43% |
| 143 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +24.43% |
| 143 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +9.83% |
| 143 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +5.03% |
| 143 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +2.03% |
| 143 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 143 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +64.76% |
| 143 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +32.77% |
| 143 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +11.94% |
| 143 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +6.18% |
| 143 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +2.00% |
| 143 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -9.10% |
| 143 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -16.39% |
| 143 | clock_shift | GW_B | 50% | WRONG | NO_INCIDENT | none | -8.02% |
| 143 | clock_shift | GW_B | 25% | small | NO_INCIDENT | none | -3.88% |
| 143 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.04% |
| 143 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -16.84% |
| 143 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.41% |
| 143 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.64% |
| 143 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.92% |
| 143 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.77% |
| 154 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +472.98% |
| 154 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +218.96% |
| 154 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +106.46% |
| 154 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +35.69% |
| 154 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +12.16% |
| 154 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +5.11% |
| 154 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 154 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +50.74% |
| 154 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +25.54% |
| 154 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +9.82% |
| 154 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.83% |
| 154 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +2.07% |
| 154 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 154 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +68.00% |
| 154 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +35.57% |
| 154 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +13.66% |
| 154 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +7.90% |
| 154 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +3.98% |
| 154 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -8.88% |
| 154 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -16.20% |
| 154 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -8.11% |
| 154 | clock_shift | GW_B | 25% | held | UNEXPLAINED | none | -4.16% |
| 154 | clock_shift | GW_B | 10% | small | NO_INCIDENT | none | -1.61% |
| 154 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.96% |
| 154 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.93% |
| 154 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -9.27% |
| 154 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.44% |
| 154 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.61% |
| 154 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.71% |
| 165 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +462.58% |
| 165 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +225.12% |
| 165 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +115.13% |
| 165 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +40.18% |
| 165 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +27.10% |
| 165 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +5.29% |
| 165 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 165 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +50.03% |
| 165 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +24.76% |
| 165 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +10.02% |
| 165 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +5.25% |
| 165 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +2.18% |
| 165 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 165 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +68.22% |
| 165 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +35.15% |
| 165 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +13.91% |
| 165 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +5.86% |
| 165 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +2.40% |
| 165 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -9.06% |
| 165 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.80% |
| 165 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -7.97% |
| 165 | clock_shift | GW_B | 25% | WRONG | NO_INCIDENT | none | -4.04% |
| 165 | clock_shift | GW_B | 10% | small | NO_INCIDENT | none | -1.65% |
| 165 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.53% |
| 165 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.14% |
| 165 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.31% |
| 165 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.58% |
| 165 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.97% |
| 165 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.79% |
| 176 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +445.87% |
| 176 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +215.90% |
| 176 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +106.31% |
| 176 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +42.79% |
| 176 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +20.13% |
| 176 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +10.72% |
| 176 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 176 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +50.00% |
| 176 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +25.17% |
| 176 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +10.20% |
| 176 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +5.24% |
| 176 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +2.18% |
| 176 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 176 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +68.57% |
| 176 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +32.46% |
| 176 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +15.46% |
| 176 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +8.89% |
| 176 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +4.18% |
| 176 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -8.53% |
| 176 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -16.57% |
| 176 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -8.11% |
| 176 | clock_shift | GW_B | 25% | held | UNEXPLAINED | none | -4.07% |
| 176 | clock_shift | GW_B | 10% | small | NO_INCIDENT | none | -1.61% |
| 176 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.31% |
| 176 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.65% |
| 176 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -9.02% |
| 176 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.76% |
| 176 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -2.01% |
| 176 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.88% |
| 187 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +489.16% |
| 187 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +256.35% |
| 187 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +131.12% |
| 187 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +48.36% |
| 187 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +26.57% |
| 187 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +10.34% |
| 187 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 187 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +49.69% |
| 187 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +25.06% |
| 187 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +9.76% |
| 187 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.76% |
| 187 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +2.03% |
| 187 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 187 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +72.15% |
| 187 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +37.87% |
| 187 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +17.61% |
| 187 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +8.82% |
| 187 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +4.54% |
| 187 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -8.87% |
| 187 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.85% |
| 187 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -7.82% |
| 187 | clock_shift | GW_B | 25% | small | NO_INCIDENT | none | -3.63% |
| 187 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.66% |
| 187 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -16.96% |
| 187 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.68% |
| 187 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.37% |
| 187 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.60% |
| 187 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.60% |
| 198 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +447.12% |
| 198 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +219.11% |
| 198 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +110.27% |
| 198 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +31.22% |
| 198 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +12.14% |
| 198 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +4.39% |
| 198 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 198 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +50.93% |
| 198 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +25.85% |
| 198 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +9.76% |
| 198 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.94% |
| 198 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +2.03% |
| 198 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 198 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +62.90% |
| 198 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +30.23% |
| 198 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +12.59% |
| 198 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +5.25% |
| 198 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +2.01% |
| 198 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -8.74% |
| 198 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.48% |
| 198 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -8.03% |
| 198 | clock_shift | GW_B | 25% | WRONG | NO_INCIDENT | none | -4.11% |
| 198 | clock_shift | GW_B | 10% | small | NO_INCIDENT | none | -1.44% |
| 198 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.53% |
| 198 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.58% |
| 198 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -9.00% |
| 198 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.07% |
| 198 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.67% |
| 198 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.78% |
| 209 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +458.35% |
| 209 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +251.28% |
| 209 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +124.65% |
| 209 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +57.60% |
| 209 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +26.85% |
| 209 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +4.33% |
| 209 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 209 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +49.84% |
| 209 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +25.39% |
| 209 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +9.83% |
| 209 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.82% |
| 209 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +1.81% |
| 209 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 209 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +68.49% |
| 209 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +34.10% |
| 209 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +14.52% |
| 209 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +5.74% |
| 209 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +2.33% |
| 209 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -9.15% |
| 209 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.53% |
| 209 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -7.22% |
| 209 | clock_shift | GW_B | 25% | small | NO_INCIDENT | none | -3.61% |
| 209 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.30% |
| 209 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -16.75% |
| 209 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.56% |
| 209 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.06% |
| 209 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.50% |
| 209 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.52% |
| 220 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +456.52% |
| 220 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +231.43% |
| 220 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +108.33% |
| 220 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +41.49% |
| 220 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +18.25% |
| 220 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +8.59% |
| 220 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 220 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +50.34% |
| 220 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +24.96% |
| 220 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +10.20% |
| 220 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.98% |
| 220 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +2.02% |
| 220 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 220 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +70.04% |
| 220 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +31.71% |
| 220 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +13.11% |
| 220 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +6.62% |
| 220 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +3.65% |
| 220 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -8.70% |
| 220 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -16.66% |
| 220 | clock_shift | GW_B | 50% | WRONG | NO_INCIDENT | none | -8.07% |
| 220 | clock_shift | GW_B | 25% | WRONG | NO_INCIDENT | none | -4.04% |
| 220 | clock_shift | GW_B | 10% | small | NO_INCIDENT | none | -1.64% |
| 220 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -33.51% |
| 220 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -16.68% |
| 220 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.03% |
| 220 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.28% |
| 220 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.55% |
| 220 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.62% |
| 231 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +499.84% |
| 231 | unit_scale | GW_C | 50% | held | UNEXPLAINED | none | +248.39% |
| 231 | unit_scale | GW_C | 25% | held | UNEXPLAINED | none | +130.62% |
| 231 | unit_scale | GW_C | 10% | held | UNEXPLAINED | none | +53.97% |
| 231 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +23.06% |
| 231 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +6.03% |
| 231 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 231 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +50.14% |
| 231 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +24.58% |
| 231 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +9.81% |
| 231 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.83% |
| 231 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +1.87% |
| 231 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 231 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +66.77% |
| 231 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +31.95% |
| 231 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +11.74% |
| 231 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +6.32% |
| 231 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +2.16% |
| 231 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -8.76% |
| 231 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.33% |
| 231 | clock_shift | GW_B | 50% | WRONG | NO_INCIDENT | none | -7.40% |
| 231 | clock_shift | GW_B | 25% | small | NO_INCIDENT | none | -3.48% |
| 231 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.92% |
| 231 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.53% |
| 231 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.19% |
| 231 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.22% |
| 231 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.50% |
| 231 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.58% |
| 242 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +438.37% |
| 242 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +225.35% |
| 242 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +123.00% |
| 242 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +45.26% |
| 242 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +19.28% |
| 242 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +4.56% |
| 242 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 242 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +50.41% |
| 242 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +25.16% |
| 242 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +10.49% |
| 242 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +5.11% |
| 242 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +2.09% |
| 242 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 242 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +68.28% |
| 242 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +38.07% |
| 242 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +15.38% |
| 242 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +8.72% |
| 242 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +4.04% |
| 242 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -9.01% |
| 242 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.76% |
| 242 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -8.20% |
| 242 | clock_shift | GW_B | 25% | WRONG | NO_INCIDENT | none | -4.12% |
| 242 | clock_shift | GW_B | 10% | small | NO_INCIDENT | none | -1.64% |
| 242 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.31% |
| 242 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.32% |
| 242 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.74% |
| 242 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.78% |
| 242 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.66% |
| 242 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.72% |
| 253 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +437.67% |
| 253 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +201.82% |
| 253 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +92.49% |
| 253 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +45.34% |
| 253 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +17.89% |
| 253 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +9.31% |
| 253 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 253 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +49.32% |
| 253 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +24.95% |
| 253 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +10.12% |
| 253 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.95% |
| 253 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +1.97% |
| 253 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 253 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +55.81% |
| 253 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +28.31% |
| 253 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +10.87% |
| 253 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +5.84% |
| 253 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +2.02% |
| 253 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -9.54% |
| 253 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.60% |
| 253 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -7.93% |
| 253 | clock_shift | GW_B | 25% | WRONG | NO_INCIDENT | none | -4.01% |
| 253 | clock_shift | GW_B | 10% | small | NO_INCIDENT | none | -1.57% |
| 253 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.55% |
| 253 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.10% |
| 253 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.58% |
| 253 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.68% |
| 253 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.81% |
| 253 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.72% |
| 264 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +447.13% |
| 264 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +234.56% |
| 264 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +119.81% |
| 264 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +52.79% |
| 264 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +29.33% |
| 264 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +15.64% |
| 264 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 264 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +50.19% |
| 264 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +24.80% |
| 264 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +9.90% |
| 264 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.97% |
| 264 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +2.09% |
| 264 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 264 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +68.54% |
| 264 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +35.78% |
| 264 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +11.26% |
| 264 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +6.14% |
| 264 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +2.38% |
| 264 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -9.17% |
| 264 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.78% |
| 264 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -7.80% |
| 264 | clock_shift | GW_B | 25% | small | NO_INCIDENT | none | -3.87% |
| 264 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -34.42% |
| 264 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.06% |
| 264 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.33% |
| 264 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.51% |
| 264 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.65% |
| 264 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.66% |
| 275 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +495.42% |
| 275 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +253.44% |
| 275 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +139.00% |
| 275 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +64.54% |
| 275 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +34.85% |
| 275 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +17.35% |
| 275 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 275 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +49.64% |
| 275 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +24.59% |
| 275 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +9.70% |
| 275 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.84% |
| 275 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +1.93% |
| 275 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 275 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +60.98% |
| 275 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +28.59% |
| 275 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +12.48% |
| 275 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +5.98% |
| 275 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +2.85% |
| 275 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -9.27% |
| 275 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.60% |
| 275 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -7.75% |
| 275 | clock_shift | GW_B | 25% | small | NO_INCIDENT | none | -3.69% |
| 275 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -35.06% |
| 275 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -17.67% |
| 275 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -8.63% |
| 275 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -3.40% |
| 275 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.69% |
| 275 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.61% |

## Unit errors by gateway (all of the gateway's rows)

| Seed | Gateway | Outcome | Verdict | Error |
|---|---|---|---|---|
| 11 | GW_A | caught | PROVEN_FAULT | +4980.18% |
| 11 | GW_B | caught | PROVEN_FAULT | +3621.77% |
| 11 | GW_C | caught | PROVEN_FAULT | +448.62% |
| 22 | GW_A | caught | PROVEN_FAULT | +4910.75% |
| 22 | GW_B | caught | PROVEN_FAULT | +3597.68% |
| 22 | GW_C | caught | PROVEN_FAULT | +465.20% |
| 33 | GW_A | caught | PROVEN_FAULT | +4899.99% |
| 33 | GW_B | caught | PROVEN_FAULT | +3626.27% |
| 33 | GW_C | caught | PROVEN_FAULT | +459.84% |
| 44 | GW_A | caught | PROVEN_FAULT | +4927.15% |
| 44 | GW_B | caught | PROVEN_FAULT | +3617.05% |
| 44 | GW_C | caught | PROVEN_FAULT | +488.49% |
| 55 | GW_A | caught | PROVEN_FAULT | +5001.89% |
| 55 | GW_B | caught | PROVEN_FAULT | +3566.65% |
| 55 | GW_C | caught | PROVEN_FAULT | +462.74% |
| 66 | GW_A | caught | PROVEN_FAULT | +5001.41% |
| 66 | GW_B | caught | PROVEN_FAULT | +3541.13% |
| 66 | GW_C | caught | PROVEN_FAULT | +470.69% |
| 77 | GW_A | caught | PROVEN_FAULT | +4959.08% |
| 77 | GW_B | caught | PROVEN_FAULT | +3643.67% |
| 77 | GW_C | caught | PROVEN_FAULT | +424.73% |
| 88 | GW_A | caught | PROVEN_FAULT | +4905.35% |
| 88 | GW_B | caught | PROVEN_FAULT | +3611.36% |
| 88 | GW_C | caught | PROVEN_FAULT | +447.63% |
| 99 | GW_A | caught | PROVEN_FAULT | +4916.66% |
| 99 | GW_B | caught | PROVEN_FAULT | +3621.56% |
| 99 | GW_C | caught | PROVEN_FAULT | +452.16% |
| 110 | GW_A | caught | PROVEN_FAULT | +4958.76% |
| 110 | GW_B | caught | PROVEN_FAULT | +3573.01% |
| 110 | GW_C | caught | PROVEN_FAULT | +463.86% |
| 121 | GW_A | caught | PROVEN_FAULT | +4956.33% |
| 121 | GW_B | caught | PROVEN_FAULT | +3573.41% |
| 121 | GW_C | caught | PROVEN_FAULT | +431.63% |
| 132 | GW_A | caught | PROVEN_FAULT | +4988.57% |
| 132 | GW_B | caught | PROVEN_FAULT | +3554.54% |
| 132 | GW_C | caught | PROVEN_FAULT | +473.88% |
| 143 | GW_A | caught | PROVEN_FAULT | +4875.40% |
| 143 | GW_B | caught | PROVEN_FAULT | +3683.96% |
| 143 | GW_C | caught | PROVEN_FAULT | +428.52% |
| 154 | GW_A | caught | PROVEN_FAULT | +4950.50% |
| 154 | GW_B | caught | PROVEN_FAULT | +3586.58% |
| 154 | GW_C | caught | PROVEN_FAULT | +472.98% |
| 165 | GW_A | caught | PROVEN_FAULT | +4971.82% |
| 165 | GW_B | caught | PROVEN_FAULT | +3558.02% |
| 165 | GW_C | caught | PROVEN_FAULT | +462.58% |
| 176 | GW_A | caught | PROVEN_FAULT | +5025.16% |
| 176 | GW_B | caught | PROVEN_FAULT | +3574.36% |
| 176 | GW_C | caught | PROVEN_FAULT | +445.87% |
| 187 | GW_A | caught | PROVEN_FAULT | +4932.89% |
| 187 | GW_B | caught | PROVEN_FAULT | +3588.98% |
| 187 | GW_C | caught | PROVEN_FAULT | +489.16% |
| 198 | GW_A | caught | PROVEN_FAULT | +5016.51% |
| 198 | GW_B | caught | PROVEN_FAULT | +3560.63% |
| 198 | GW_C | caught | PROVEN_FAULT | +447.12% |
| 209 | GW_A | caught | PROVEN_FAULT | +4962.68% |
| 209 | GW_B | caught | PROVEN_FAULT | +3562.27% |
| 209 | GW_C | caught | PROVEN_FAULT | +458.35% |
| 220 | GW_A | caught | PROVEN_FAULT | +4901.64% |
| 220 | GW_B | caught | PROVEN_FAULT | +3669.83% |
| 220 | GW_C | caught | PROVEN_FAULT | +456.52% |
| 231 | GW_A | caught | PROVEN_FAULT | +5006.70% |
| 231 | GW_B | caught | PROVEN_FAULT | +3515.97% |
| 231 | GW_C | caught | PROVEN_FAULT | +499.84% |
| 242 | GW_A | caught | PROVEN_FAULT | +4994.76% |
| 242 | GW_B | caught | PROVEN_FAULT | +3564.61% |
| 242 | GW_C | caught | PROVEN_FAULT | +438.37% |
| 253 | GW_A | caught | PROVEN_FAULT | +4962.01% |
| 253 | GW_B | caught | PROVEN_FAULT | +3544.49% |
| 253 | GW_C | caught | PROVEN_FAULT | +437.67% |
| 264 | GW_A | caught | PROVEN_FAULT | +4951.50% |
| 264 | GW_B | caught | PROVEN_FAULT | +3582.84% |
| 264 | GW_C | caught | PROVEN_FAULT | +447.13% |
| 275 | GW_A | caught | PROVEN_FAULT | +4915.82% |
| 275 | GW_B | caught | PROVEN_FAULT | +3559.91% |
| 275 | GW_C | caught | PROVEN_FAULT | +495.42% |

## Two faults that push in opposite directions, each at its floor

225 pairs: proven, right cause 197, held, nothing proven 5, held, part of the cause proven 23.

| Seed | Faults | Outcome | Verdict | Causes named | Error |
|---|---|---|---|---|---|
| 11 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -9.47% |
| 11 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +1.91% |
| 11 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | -2.01% |
| 11 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.36% |
| 11 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.58% |
| 11 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -6.71% |
| 11 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -14.27% |
| 11 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +0.18% |
| 11 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -6.65% |
| 22 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -0.28% |
| 22 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +6.54% |
| 22 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | +6.30% |
| 22 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.09% |
| 22 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.29% |
| 22 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.41% |
| 22 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -13.78% |
| 22 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +0.72% |
| 22 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -7.04% |
| 33 | unit_scale 100% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | +443.03% |
| 33 | unit_scale 100% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +451.35% |
| 33 | unit_scale 100% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | +450.72% |
| 33 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -15.16% |
| 33 | duplicate_key 2% + orphan_code 5% | held | UNEXPLAINED | none | -0.46% |
| 33 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.38% |
| 33 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -15.17% |
| 33 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +0.29% |
| 33 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -7.23% |
| 44 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -6.00% |
| 44 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +7.25% |
| 44 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | +1.54% |
| 44 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.51% |
| 44 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.35% |
| 44 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -6.76% |
| 44 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -13.72% |
| 44 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +1.22% |
| 44 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -5.80% |
| 55 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -8.73% |
| 55 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +3.14% |
| 55 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | -1.49% |
| 55 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.19% |
| 55 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.24% |
| 55 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -6.81% |
| 55 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -14.60% |
| 55 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | -0.12% |
| 55 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -7.28% |
| 66 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -7.46% |
| 66 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +5.54% |
| 66 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | -0.75% |
| 66 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.10% |
| 66 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.25% |
| 66 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.21% |
| 66 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -13.38% |
| 66 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +0.99% |
| 66 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -6.60% |
| 77 | unit_scale 100% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | +408.77% |
| 77 | unit_scale 100% + orphan_code 10% | caught | PROVEN_FAULT | orphan_code, unit_scale | +410.02% |
| 77 | unit_scale 100% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | +416.02% |
| 77 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.27% |
| 77 | duplicate_key 2% + orphan_code 10% | held_partial | PROVEN_FAULT | orphan_code | -1.80% |
| 77 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -6.97% |
| 77 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -13.95% |
| 77 | key_fanout 2% + orphan_code 10% | caught | PROVEN_FAULT | key_fanout, orphan_code | -0.83% |
| 77 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -6.50% |
| 88 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -9.69% |
| 88 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +4.19% |
| 88 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | -2.93% |
| 88 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.48% |
| 88 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.35% |
| 88 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.65% |
| 88 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -14.41% |
| 88 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +0.44% |
| 88 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -7.39% |
| 99 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -7.58% |
| 99 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +0.40% |
| 99 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | -0.54% |
| 99 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.47% |
| 99 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.41% |
| 99 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.37% |
| 99 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -13.33% |
| 99 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +1.52% |
| 99 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -6.10% |
| 110 | unit_scale 100% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | +448.36% |
| 110 | unit_scale 100% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +455.43% |
| 110 | unit_scale 100% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | +454.83% |
| 110 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -13.76% |
| 110 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.54% |
| 110 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.25% |
| 110 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -14.12% |
| 110 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | -0.30% |
| 110 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -7.56% |
| 121 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -9.97% |
| 121 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +2.35% |
| 121 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | -3.53% |
| 121 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.17% |
| 121 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.43% |
| 121 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.54% |
| 121 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -14.16% |
| 121 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +0.21% |
| 121 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -7.66% |
| 132 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -9.32% |
| 132 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +3.11% |
| 132 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | -2.62% |
| 132 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -13.83% |
| 132 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.28% |
| 132 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.04% |
| 132 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -12.68% |
| 132 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +1.77% |
| 132 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -5.72% |
| 143 | unit_scale 100% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | +412.13% |
| 143 | unit_scale 100% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +416.62% |
| 143 | unit_scale 100% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | +419.42% |
| 143 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.77% |
| 143 | duplicate_key 2% + orphan_code 5% | held | UNEXPLAINED | none | -0.66% |
| 143 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.27% |
| 143 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -14.67% |
| 143 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +0.04% |
| 143 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -7.28% |
| 154 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -11.08% |
| 154 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +1.92% |
| 154 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | -3.77% |
| 154 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.34% |
| 154 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.24% |
| 154 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.03% |
| 154 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -12.83% |
| 154 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +2.25% |
| 154 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -5.23% |
| 165 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -10.51% |
| 165 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +2.04% |
| 165 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | -3.77% |
| 165 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.02% |
| 165 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.58% |
| 165 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.01% |
| 165 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -13.69% |
| 165 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +0.40% |
| 165 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -6.88% |
| 176 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -5.85% |
| 176 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +2.96% |
| 176 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | +2.19% |
| 176 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.75% |
| 176 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.71% |
| 176 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -6.49% |
| 176 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -13.06% |
| 176 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +2.07% |
| 176 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -4.67% |
| 187 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -5.51% |
| 187 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +4.72% |
| 187 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | +1.47% |
| 187 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.18% |
| 187 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.17% |
| 187 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.04% |
| 187 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -11.95% |
| 187 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +2.88% |
| 187 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -4.78% |
| 198 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -11.09% |
| 198 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +2.72% |
| 198 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | -4.35% |
| 198 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -13.73% |
| 198 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.42% |
| 198 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -6.87% |
| 198 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -13.78% |
| 198 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +0.30% |
| 198 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -6.86% |
| 209 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -11.20% |
| 209 | unit_scale 2% + orphan_code 5% | held_partial | PROVEN_FAULT | unit_scale | +2.83% |
| 209 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | -4.82% |
| 209 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.05% |
| 209 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.21% |
| 209 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.49% |
| 209 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -13.57% |
| 209 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +0.81% |
| 209 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -7.04% |
| 220 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -8.07% |
| 220 | unit_scale 2% + orphan_code 5% | held_partial | PROVEN_FAULT | unit_scale | +7.04% |
| 220 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | -0.11% |
| 220 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.93% |
| 220 | duplicate_key 2% + orphan_code 5% | held | UNEXPLAINED | none | -0.15% |
| 220 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -6.80% |
| 220 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -13.70% |
| 220 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +2.05% |
| 220 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -5.40% |
| 231 | unit_scale 100% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | +484.51% |
| 231 | unit_scale 100% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +485.64% |
| 231 | unit_scale 100% + stale_feed 100% | held | UNEXPLAINED | none | +491.08% |
| 231 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -13.72% |
| 231 | duplicate_key 2% + orphan_code 5% | held | UNEXPLAINED | none | -0.21% |
| 231 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.06% |
| 231 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -13.53% |
| 231 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +0.62% |
| 231 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -6.80% |
| 242 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -11.20% |
| 242 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +2.69% |
| 242 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | -4.45% |
| 242 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -13.99% |
| 242 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.29% |
| 242 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.12% |
| 242 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -12.36% |
| 242 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +2.33% |
| 242 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -5.29% |
| 253 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -6.29% |
| 253 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +5.08% |
| 253 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | -0.23% |
| 253 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -13.85% |
| 253 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.56% |
| 253 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.72% |
| 253 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -13.85% |
| 253 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +0.20% |
| 253 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -7.67% |
| 264 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -0.14% |
| 264 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +6.43% |
| 264 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | +6.47% |
| 264 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -14.02% |
| 264 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.23% |
| 264 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.16% |
| 264 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -13.85% |
| 264 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +0.73% |
| 264 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -7.05% |
| 275 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | +1.75% |
| 275 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +11.51% |
| 275 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | +8.08% |
| 275 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -13.88% |
| 275 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.38% |
| 275 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -7.61% |
| 275 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -13.17% |
| 275 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | +1.14% |
| 275 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -6.76% |

## Holes

Each of these is a way to get past Receipts today. None is hidden.

* **clock_shift on GW_B at 25% of payments on the gateway (seed 33)**: published a number -4.37% off as trusted, verdict NO_INCIDENT.
* **clock_shift on GW_B at 25% of payments on the gateway (seed 55)**: published a number -4.15% off as trusted, verdict NO_INCIDENT.
* **clock_shift on GW_B at 25% of payments on the gateway (seed 66)**: published a number -4.04% off as trusted, verdict NO_INCIDENT.
* **clock_shift on GW_B at 25% of payments on the gateway (seed 99)**: published a number -4.15% off as trusted, verdict NO_INCIDENT.
* **clock_shift on GW_B at 25% of payments on the gateway (seed 121)**: published a number -4.15% off as trusted, verdict NO_INCIDENT.
* **clock_shift on GW_B at 50% of payments on the gateway (seed 143)**: published a number -8.02% off as trusted, verdict NO_INCIDENT.
* **clock_shift on GW_B at 25% of payments on the gateway (seed 165)**: published a number -4.04% off as trusted, verdict NO_INCIDENT.
* **clock_shift on GW_B at 25% of payments on the gateway (seed 198)**: published a number -4.11% off as trusted, verdict NO_INCIDENT.
* **clock_shift on GW_B at 50% of payments on the gateway (seed 220)**: published a number -8.07% off as trusted, verdict NO_INCIDENT.
* **clock_shift on GW_B at 25% of payments on the gateway (seed 220)**: published a number -4.04% off as trusted, verdict NO_INCIDENT.
* **clock_shift on GW_B at 50% of payments on the gateway (seed 231)**: published a number -7.40% off as trusted, verdict NO_INCIDENT.
* **clock_shift on GW_B at 25% of payments on the gateway (seed 242)**: published a number -4.12% off as trusted, verdict NO_INCIDENT.
* **clock_shift on GW_B at 25% of payments on the gateway (seed 253)**: published a number -4.01% off as trusted, verdict NO_INCIDENT.

## Wrong-fix control

Each fault class at 100%, then deliberately wrong corrections (wrong gateway, wrong factor, every day instead of tonight, or the fix for another cause) judged by the gate's own rules. Accepted means it moves today by at least 1.5%, keeps history and lands in range.

Tried 1050, rejected 988, accepted 62.
* Accepted: unit fix (divide by 100) on GW_A (-49.80%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.80%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: divide GW_C by 1000 instead of 100 (-83.06%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_A (-49.11%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.11%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: divide GW_C by 1000 instead of 100 (-82.88%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: divide GW_C by 1000 instead of 100 (-83.76%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_A (-49.27%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.27%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: divide GW_C by 1000 instead of 100 (-82.98%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_A (-50.02%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-50.02%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: divide GW_C by 1000 instead of 100 (-83.23%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_A (-50.01%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-50.01%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: divide GW_C by 1000 instead of 100 (-81.68%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_A (-49.59%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.59%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: unit fix (divide by 100) on GW_A (-49.05%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.05%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: divide GW_C by 1000 instead of 100 (-82.63%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_A (-49.17%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.17%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: divide GW_C by 1000 instead of 100 (-83.01%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_A (-49.59%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.59%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: divide GW_C by 1000 instead of 100 (-81.93%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_A (-49.56%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.56%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: unit fix (divide by 100) on GW_A (-49.89%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.89%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: divide GW_C by 1000 instead of 100 (-81.82%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_A (-49.51%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.51%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: unit fix (divide by 100) on GW_A (-49.72%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.72%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: unit fix (divide by 100) on GW_A (-50.25%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-50.25%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: unit fix (divide by 100) on GW_A (-49.33%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.33%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: divide GW_C by 1000 instead of 100 (-82.47%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_A (-50.17%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-50.17%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: divide GW_C by 1000 instead of 100 (-82.84%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_A (-49.63%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.63%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: divide GW_C by 1000 instead of 100 (-82.78%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: divide GW_C by 1000 instead of 100 (-84.09%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_A (-50.07%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-50.07%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: divide GW_C by 1000 instead of 100 (-82.17%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_A (-49.95%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.95%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: divide GW_C by 1000 instead of 100 (-82.14%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_A (-49.62%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.62%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: divide GW_C by 1000 instead of 100 (-82.47%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_A (-49.52%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.52%), gate verdict PROVEN_FAULT, confirmed key_fanout.
* Accepted: divide GW_C by 1000 instead of 100 (-83.96%), gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_A (-49.16%), gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_A (-49.16%), gate verdict PROVEN_FAULT, confirmed key_fanout.

## What the outcomes mean

* `caught`: proven, right cause
* `held`: held, nothing proven
* `held_partial`: held, part of the cause proven
* `wrong_cause`: a cause that was not planted was named
* `small`: published, under 4% off
* `WRONG`: published a number more than 4% off
* Holes are `wrong_cause` and `WRONG`. Held is safe: the number is not shown and a person decides.

## Every hole and every miss, by seed

A hole is a wrong number published or a wrong cause named. A miss below the floor is listed too.

| Seed | Where | Outcome | Verdict | Causes | Error |
|---|---|---|---|---|---|
| 11 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -7.85% |
| 11 | clock_shift on GW_B at 25% | held | UNEXPLAINED | - | -3.81% |
| 11 | orphan_code at 2% | small | NO_INCIDENT | - | -0.70% |
| 11 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.58% |
| 22 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -7.83% |
| 22 | clock_shift on GW_B at 25% | small | NO_INCIDENT | - | -3.68% |
| 22 | orphan_code at 2% | small | NO_INCIDENT | - | -0.70% |
| 22 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.29% |
| 33 | unit_scale on GW_C at 50% | held | UNEXPLAINED | - | +208.62% |
| 33 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -8.82% |
| 33 | clock_shift on GW_B at 25% | WRONG (HOLE) | NO_INCIDENT | - | -4.37% |
| 33 | clock_shift on GW_B at 10% | small | NO_INCIDENT | - | -1.65% |
| 33 | orphan_code at 2% | small | NO_INCIDENT | - | -0.65% |
| 33 | duplicate_key at 2% + orphan_code at 5% | held | UNEXPLAINED | - | -0.46% |
| 44 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -8.18% |
| 44 | clock_shift on GW_B at 25% | small | NO_INCIDENT | - | -3.99% |
| 44 | orphan_code at 2% | small | NO_INCIDENT | - | -0.68% |
| 44 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.35% |
| 55 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -8.28% |
| 55 | clock_shift on GW_B at 25% | WRONG (HOLE) | NO_INCIDENT | - | -4.15% |
| 55 | clock_shift on GW_B at 10% | small | NO_INCIDENT | - | -1.63% |
| 55 | orphan_code at 2% | small | NO_INCIDENT | - | -0.61% |
| 55 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.24% |
| 66 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -7.74% |
| 66 | clock_shift on GW_B at 25% | WRONG (HOLE) | NO_INCIDENT | - | -4.04% |
| 66 | clock_shift on GW_B at 10% | small | NO_INCIDENT | - | -1.80% |
| 66 | orphan_code at 2% | small | NO_INCIDENT | - | -0.51% |
| 66 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.25% |
| 77 | unit_scale on GW_C at 50% | held | UNEXPLAINED | - | +207.43% |
| 77 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -7.84% |
| 77 | clock_shift on GW_B at 25% | small | NO_INCIDENT | - | -3.82% |
| 77 | orphan_code at 5% | small | NO_INCIDENT | - | -1.38% |
| 77 | duplicate_key at 2% + orphan_code at 10% | held_partial | PROVEN_FAULT | orphan_code | -1.80% |
| 88 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -7.74% |
| 88 | clock_shift on GW_B at 25% | held | UNEXPLAINED | - | -3.81% |
| 88 | orphan_code at 2% | small | NO_INCIDENT | - | -0.62% |
| 88 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.35% |
| 99 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -8.07% |
| 99 | clock_shift on GW_B at 25% | WRONG (HOLE) | NO_INCIDENT | - | -4.15% |
| 99 | clock_shift on GW_B at 10% | small | NO_INCIDENT | - | -1.63% |
| 99 | orphan_code at 2% | small | NO_INCIDENT | - | -0.64% |
| 99 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.41% |
| 110 | unit_scale on GW_C at 50% | held | UNEXPLAINED | - | +234.85% |
| 110 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -7.37% |
| 110 | clock_shift on GW_B at 25% | small | NO_INCIDENT | - | -3.53% |
| 110 | orphan_code at 2% | small | NO_INCIDENT | - | -0.66% |
| 110 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.54% |
| 121 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -7.91% |
| 121 | clock_shift on GW_B at 25% | WRONG (HOLE) | NO_INCIDENT | - | -4.15% |
| 121 | clock_shift on GW_B at 10% | small | NO_INCIDENT | - | -1.67% |
| 121 | orphan_code at 2% | small | NO_INCIDENT | - | -0.72% |
| 121 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.43% |
| 132 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -7.74% |
| 132 | clock_shift on GW_B at 25% | held | UNEXPLAINED | - | -4.14% |
| 132 | clock_shift on GW_B at 10% | small | NO_INCIDENT | - | -1.56% |
| 132 | orphan_code at 2% | small | NO_INCIDENT | - | -0.62% |
| 132 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.28% |
| 143 | unit_scale on GW_C at 50% | held | UNEXPLAINED | - | +218.31% |
| 143 | unit_scale on GW_C at 25% | held | UNEXPLAINED | - | +101.90% |
| 143 | unit_scale on GW_C at 10% | held | UNEXPLAINED | - | +37.61% |
| 143 | unit_scale on GW_C at 5% | held | UNEXPLAINED | - | +19.92% |
| 143 | unit_scale on GW_C at 2% | held | UNEXPLAINED | - | +10.50% |
| 143 | clock_shift on GW_B at 50% | WRONG (HOLE) | NO_INCIDENT | - | -8.02% |
| 143 | clock_shift on GW_B at 25% | small | NO_INCIDENT | - | -3.88% |
| 143 | orphan_code at 2% | small | NO_INCIDENT | - | -0.77% |
| 143 | duplicate_key at 2% + orphan_code at 5% | held | UNEXPLAINED | - | -0.66% |
| 154 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -8.11% |
| 154 | clock_shift on GW_B at 25% | held | UNEXPLAINED | - | -4.16% |
| 154 | clock_shift on GW_B at 10% | small | NO_INCIDENT | - | -1.61% |
| 154 | orphan_code at 2% | small | NO_INCIDENT | - | -0.71% |
| 154 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.24% |
| 165 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -7.97% |
| 165 | clock_shift on GW_B at 25% | WRONG (HOLE) | NO_INCIDENT | - | -4.04% |
| 165 | clock_shift on GW_B at 10% | small | NO_INCIDENT | - | -1.65% |
| 165 | orphan_code at 2% | small | NO_INCIDENT | - | -0.79% |
| 165 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.58% |
| 176 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -8.11% |
| 176 | clock_shift on GW_B at 25% | held | UNEXPLAINED | - | -4.07% |
| 176 | clock_shift on GW_B at 10% | small | NO_INCIDENT | - | -1.61% |
| 176 | orphan_code at 2% | small | NO_INCIDENT | - | -0.88% |
| 176 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.71% |
| 187 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -7.82% |
| 187 | clock_shift on GW_B at 25% | small | NO_INCIDENT | - | -3.63% |
| 187 | orphan_code at 2% | small | NO_INCIDENT | - | -0.60% |
| 187 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.17% |
| 198 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -8.03% |
| 198 | clock_shift on GW_B at 25% | WRONG (HOLE) | NO_INCIDENT | - | -4.11% |
| 198 | clock_shift on GW_B at 10% | small | NO_INCIDENT | - | -1.44% |
| 198 | orphan_code at 2% | small | NO_INCIDENT | - | -0.78% |
| 198 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.42% |
| 209 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -7.22% |
| 209 | clock_shift on GW_B at 25% | small | NO_INCIDENT | - | -3.61% |
| 209 | orphan_code at 2% | small | NO_INCIDENT | - | -0.52% |
| 209 | unit_scale at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | unit_scale | +2.83% |
| 209 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.21% |
| 220 | clock_shift on GW_B at 50% | WRONG (HOLE) | NO_INCIDENT | - | -8.07% |
| 220 | clock_shift on GW_B at 25% | WRONG (HOLE) | NO_INCIDENT | - | -4.04% |
| 220 | clock_shift on GW_B at 10% | small | NO_INCIDENT | - | -1.64% |
| 220 | orphan_code at 2% | small | NO_INCIDENT | - | -0.62% |
| 220 | unit_scale at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | unit_scale | +7.04% |
| 220 | duplicate_key at 2% + orphan_code at 5% | held | UNEXPLAINED | - | -0.15% |
| 231 | unit_scale on GW_C at 50% | held | UNEXPLAINED | - | +248.39% |
| 231 | unit_scale on GW_C at 25% | held | UNEXPLAINED | - | +130.62% |
| 231 | unit_scale on GW_C at 10% | held | UNEXPLAINED | - | +53.97% |
| 231 | clock_shift on GW_B at 50% | WRONG (HOLE) | NO_INCIDENT | - | -7.40% |
| 231 | clock_shift on GW_B at 25% | small | NO_INCIDENT | - | -3.48% |
| 231 | orphan_code at 2% | small | NO_INCIDENT | - | -0.58% |
| 231 | unit_scale at 100% + stale_feed at 100% | held | UNEXPLAINED | - | +491.08% |
| 231 | duplicate_key at 2% + orphan_code at 5% | held | UNEXPLAINED | - | -0.21% |
| 242 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -8.20% |
| 242 | clock_shift on GW_B at 25% | WRONG (HOLE) | NO_INCIDENT | - | -4.12% |
| 242 | clock_shift on GW_B at 10% | small | NO_INCIDENT | - | -1.64% |
| 242 | orphan_code at 2% | small | NO_INCIDENT | - | -0.72% |
| 242 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.29% |
| 253 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -7.93% |
| 253 | clock_shift on GW_B at 25% | WRONG (HOLE) | NO_INCIDENT | - | -4.01% |
| 253 | clock_shift on GW_B at 10% | small | NO_INCIDENT | - | -1.57% |
| 253 | orphan_code at 2% | small | NO_INCIDENT | - | -0.72% |
| 253 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.56% |
| 264 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -7.80% |
| 264 | clock_shift on GW_B at 25% | small | NO_INCIDENT | - | -3.87% |
| 264 | orphan_code at 2% | small | NO_INCIDENT | - | -0.66% |
| 264 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.23% |
| 275 | clock_shift on GW_B at 50% | held | UNEXPLAINED | - | -7.75% |
| 275 | clock_shift on GW_B at 25% | small | NO_INCIDENT | - | -3.69% |
| 275 | orphan_code at 2% | small | NO_INCIDENT | - | -0.61% |
| 275 | duplicate_key at 2% + orphan_code at 5% | held_partial | PROVEN_FAULT | orphan_code | -0.38% |
