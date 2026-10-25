# Red team: where Receipts breaks

**Run this on the built-in synthetic data or a sandbox copy, never on live production tables.** Every attack writes a planted fault into RAW.

On Exasol 2026.2.0-nano.3, 20,000 orders a day, seeds 11. Generated 2026-10-26 01:25:06 in 6 minutes. Reproduce: `receipts redteam --backend exasol --seeds 11 --orders-per-day 20000`.

For each fault class an attacker shrinks the share of rows affected (100, 50, 25, 10, 5, 2 percent). After the first step the gate no longer proves, it keeps shrinking while the fault still moves the number by 4% or more (a smaller one cannot be published as a wrong number), then stops. The detection floor is the smallest share proven with the right cause at every step down to it; with several seeds the worst seed counts. Nothing was tuned for this run.

## Detection floor per fault class

| Fault class | Detection floor | What happened below the floor | Holes |
|---|---|---|---|
| Unit change (amounts x100) | 2% | not reached: proven at every step | 0 |
| Payment rows loaded twice | 2% | not reached: proven at every step | 0 |
| Merchant table fans out | 2% | not reached: proven at every step | 0 |
| FX feed misses today | 100% (binary: one rate is missing or not) | binary fault, nothing to shrink | 0 |
| IST written as UTC | 100% | held, nothing proven | 0 |
| New category code | 5% | published, under 4% off | 0 |

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

## Unit errors by gateway (all of the gateway's rows)

| Seed | Gateway | Outcome | Verdict | Error |
|---|---|---|---|---|
| 11 | GW_A | caught | PROVEN_FAULT | +4980.18% |
| 11 | GW_B | caught | PROVEN_FAULT | +3621.77% |
| 11 | GW_C | caught | PROVEN_FAULT | +448.62% |

## Two faults that push in opposite directions, each at its floor

9 pairs: proven, right cause 8, held, part of the cause proven 1.

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

## Holes

No attack got a wrong number published or a wrong cause named. Below each floor the gate either held the number with nothing proven (safe, a person looks) or published a number that was less than 4% off (inside the normal noise).

## What the outcomes mean

* `caught`: proven, right cause
* `held`: held, nothing proven
* `held_partial`: held, part of the cause proven
* `wrong_cause`: a cause that was not planted was named
* `small`: published, under 4% off
* `WRONG`: published a number more than 4% off
* Holes are `wrong_cause` and `WRONG`. Held is safe: the number is not shown and a person decides.
