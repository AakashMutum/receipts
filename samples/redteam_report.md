# Red team: where Receipts breaks

**Run this on the built-in synthetic data or a sandbox copy, never on live production tables.** Every attack writes a planted fault into RAW.

On the DuckDB stand-in, 8,000 orders a day, seeds 11. Generated 2026-10-26 01:25:55 in 1 minutes. Reproduce: `receipts redteam --backend duckdb --seeds 11 --orders-per-day 8000`.

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
| 11 | unit_scale | GW_C | 100% | caught | PROVEN_FAULT | unit_scale | +439.41% |
| 11 | unit_scale | GW_C | 50% | caught | PROVEN_FAULT | unit_scale | +231.56% |
| 11 | unit_scale | GW_C | 25% | caught | PROVEN_FAULT | unit_scale | +126.32% |
| 11 | unit_scale | GW_C | 10% | caught | PROVEN_FAULT | unit_scale | +43.87% |
| 11 | unit_scale | GW_C | 5% | caught | PROVEN_FAULT | unit_scale | +18.96% |
| 11 | unit_scale | GW_C | 2% | caught | PROVEN_FAULT | unit_scale | +5.72% |
| 11 | duplicate_key | - | 100% | caught | PROVEN_FAULT | duplicate_key | +100.00% |
| 11 | duplicate_key | - | 50% | caught | PROVEN_FAULT | duplicate_key | +50.73% |
| 11 | duplicate_key | - | 25% | caught | PROVEN_FAULT | duplicate_key | +24.84% |
| 11 | duplicate_key | - | 10% | caught | PROVEN_FAULT | duplicate_key | +9.52% |
| 11 | duplicate_key | - | 5% | caught | PROVEN_FAULT | duplicate_key | +4.97% |
| 11 | duplicate_key | - | 2% | caught | PROVEN_FAULT | duplicate_key | +1.87% |
| 11 | key_fanout | - | 100% | caught | PROVEN_FAULT | key_fanout | +100.00% |
| 11 | key_fanout | - | 50% | caught | PROVEN_FAULT | key_fanout | +67.30% |
| 11 | key_fanout | - | 25% | caught | PROVEN_FAULT | key_fanout | +31.97% |
| 11 | key_fanout | - | 10% | caught | PROVEN_FAULT | key_fanout | +12.66% |
| 11 | key_fanout | - | 5% | caught | PROVEN_FAULT | key_fanout | +5.85% |
| 11 | key_fanout | - | 2% | caught | PROVEN_FAULT | key_fanout | +1.70% |
| 11 | stale_feed | - | 100% | caught | PROVEN_FAULT | stale_feed | -8.08% |
| 11 | clock_shift | GW_B | 100% | caught | PROVEN_FAULT | clock_shift | -15.36% |
| 11 | clock_shift | GW_B | 50% | held | UNEXPLAINED | none | -7.76% |
| 11 | clock_shift | GW_B | 25% | held | UNEXPLAINED | none | -3.80% |
| 11 | orphan_code | - | 100% | caught | PROVEN_FAULT | orphan_code | -32.40% |
| 11 | orphan_code | - | 50% | caught | PROVEN_FAULT | orphan_code | -16.41% |
| 11 | orphan_code | - | 25% | caught | PROVEN_FAULT | orphan_code | -7.46% |
| 11 | orphan_code | - | 10% | caught | PROVEN_FAULT | orphan_code | -2.92% |
| 11 | orphan_code | - | 5% | caught | PROVEN_FAULT | orphan_code | -1.74% |
| 11 | orphan_code | - | 2% | small | NO_INCIDENT | none | -0.60% |

## Unit errors by gateway (all of the gateway's rows)

| Seed | Gateway | Outcome | Verdict | Error |
|---|---|---|---|---|
| 11 | GW_A | caught | PROVEN_FAULT | +4967.89% |
| 11 | GW_B | caught | PROVEN_FAULT | +3683.36% |
| 11 | GW_C | caught | PROVEN_FAULT | +439.41% |

## Two faults that push in opposite directions, each at its floor

9 pairs: proven, right cause 8, held, part of the cause proven 1.

| Seed | Faults | Outcome | Verdict | Causes named | Error |
|---|---|---|---|---|---|
| 11 | unit_scale 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, unit_scale | -9.65% |
| 11 | unit_scale 2% + orphan_code 5% | caught | PROVEN_FAULT | orphan_code, unit_scale | +3.97% |
| 11 | unit_scale 2% + stale_feed 100% | caught | PROVEN_FAULT | stale_feed, unit_scale | -2.36% |
| 11 | duplicate_key 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, duplicate_key | -13.97% |
| 11 | duplicate_key 2% + orphan_code 5% | held_partial | PROVEN_FAULT | orphan_code | -0.48% |
| 11 | duplicate_key 2% + stale_feed 100% | caught | PROVEN_FAULT | duplicate_key, stale_feed | -6.34% |
| 11 | key_fanout 2% + clock_shift 100% | caught | PROVEN_FAULT | clock_shift, key_fanout | -13.96% |
| 11 | key_fanout 2% + orphan_code 5% | caught | PROVEN_FAULT | key_fanout, orphan_code | -0.06% |
| 11 | key_fanout 2% + stale_feed 100% | caught | PROVEN_FAULT | key_fanout, stale_feed | -6.47% |

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
