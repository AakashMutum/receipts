# Wrong-fix control

Is the undo test circular? For every scenario with a planted fault, the gate's own rules are shown corrections that are deliberately wrong: the right fix on the wrong gateway, the wrong factor, the right fix applied to every day instead of tonight, or the fix for a cause that was not planted. A wrong fix is **accepted** if it moves today's number by at least 1.5%, keeps history as published and lands inside the normal range, which is what the gate needs to confirm a cause.

On Exasol 2026.2.0-nano.3, 20,000 orders a day, seeds 11, 22, 33, 44, 55, 66, 77, 88, 99, 110, 121, 132, 143, 154, 165, 176, 187, 198, 209, 220, 231, 242, 253, 264, 275. Generated 2026-10-31 03:20:35 in 2106 s. Reproduce: `python scripts/evidence_seeds.py wrongfix --backend exasol`.

**Wrong fixes tried 1175, rejected 1129, accepted 46.**

| Kind of wrong fix | Tried | Rejected | Accepted |
|---|---|---|---|
| wrong factor | 50 | 32 | 18 |
| every day | 25 | 25 | 0 |
| wrong gateway | 150 | 150 | 0 |
| different cause | 950 | 922 | 28 |

## Accepted wrong fixes

Each of these would have been confirmed if a detector had nominated it. In every one the gate's own verdict did not use it (the confirmed causes are listed).

* seed 11, masked_pair: unit fix (divide by 100) on GW_C moves today -5.41%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 22, unit_paise: divide GW_C by 1000 instead of 100 moves today -83.06%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 22, masked_pair: unit fix (divide by 100) on GW_C moves today -5.46%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 33, unit_paise: divide GW_C by 1000 instead of 100 moves today -82.88%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 33, masked_pair: unit fix (divide by 100) on GW_C moves today -5.55%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 44, unit_paise: divide GW_C by 1000 instead of 100 moves today -83.76%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 44, duplicate_load: unit fix (divide by 100) on GW_C moves today -4.92%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed duplicate_key.
* seed 44, masked_pair: unit fix (divide by 100) on GW_C moves today -5.90%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 55, unit_paise: divide GW_C by 1000 instead of 100 moves today -82.98%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 55, masked_pair: unit fix (divide by 100) on GW_C moves today -5.47%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 66, unit_paise: divide GW_C by 1000 instead of 100 moves today -83.23%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 66, masked_pair: unit fix (divide by 100) on GW_C moves today -5.59%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 77, unit_paise: divide GW_C by 1000 instead of 100 moves today -81.68%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 77, masked_pair: unit fix (divide by 100) on GW_C moves today -4.86%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 88, masked_pair: unit fix (divide by 100) on GW_C moves today -5.17%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 99, unit_paise: divide GW_C by 1000 instead of 100 moves today -82.63%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 99, masked_pair: unit fix (divide by 100) on GW_C moves today -5.38%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 110, unit_paise: divide GW_C by 1000 instead of 100 moves today -83.01%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 110, duplicate_load: unit fix (divide by 100) on GW_C moves today -4.58%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed duplicate_key.
* seed 110, masked_pair: unit fix (divide by 100) on GW_C moves today -5.38%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 121, unit_paise: divide GW_C by 1000 instead of 100 moves today -81.93%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 121, masked_pair: unit fix (divide by 100) on GW_C moves today -5.02%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 132, masked_pair: unit fix (divide by 100) on GW_C moves today -5.72%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 143, unit_paise: divide GW_C by 1000 instead of 100 moves today -81.82%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 143, masked_pair: unit fix (divide by 100) on GW_C moves today -5.21%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 154, masked_pair: unit fix (divide by 100) on GW_C moves today -5.67%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 165, masked_pair: unit fix (divide by 100) on GW_C moves today -5.43%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 176, masked_pair: unit fix (divide by 100) on GW_C moves today -5.38%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 187, masked_pair: unit fix (divide by 100) on GW_C moves today -5.85%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 198, unit_paise: divide GW_C by 1000 instead of 100 moves today -82.47%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 198, masked_pair: unit fix (divide by 100) on GW_C moves today -5.33%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 209, unit_paise: divide GW_C by 1000 instead of 100 moves today -82.84%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 209, duplicate_load: unit fix (divide by 100) on GW_C moves today -4.52%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed duplicate_key.
* seed 209, masked_pair: unit fix (divide by 100) on GW_C moves today -5.35%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 220, unit_paise: divide GW_C by 1000 instead of 100 moves today -82.78%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 220, masked_pair: unit fix (divide by 100) on GW_C moves today -5.51%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 231, unit_paise: divide GW_C by 1000 instead of 100 moves today -84.09%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 231, masked_pair: unit fix (divide by 100) on GW_C moves today -5.86%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 242, unit_paise: divide GW_C by 1000 instead of 100 moves today -82.17%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 242, masked_pair: unit fix (divide by 100) on GW_C moves today -5.23%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 253, unit_paise: divide GW_C by 1000 instead of 100 moves today -82.14%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 253, masked_pair: unit fix (divide by 100) on GW_C moves today -5.06%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 264, unit_paise: divide GW_C by 1000 instead of 100 moves today -82.47%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 264, masked_pair: unit fix (divide by 100) on GW_C moves today -5.28%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* seed 275, unit_paise: divide GW_C by 1000 instead of 100 moves today -83.96%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed unit_scale.
* seed 275, masked_pair: unit fix (divide by 100) on GW_C moves today -5.87%, history unchanged, lands in range. Gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.

## Every wrong fix

| Seed | Scenario | Wrong fix | Move | History | In range | Result |
|---|---|---|---|---|---|---|
| 11 | unit_paise | divide GW_C by 10 instead of 100 | -74.34% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | unit_paise | divide GW_C by 1000 instead of 100 | -82.52% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | unit_paise | divide GW_C by 100 on every day, not only tonight | -81.77% | altered | yes | rejected: history would change |
| 11 | unit_paise | unit fix (divide by 100) on GW_A | -9.08% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.56% | altered | no | rejected: history would change |
| 11 | unit_paise | unit fix (divide by 100) on GW_B | -6.60% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.37% | altered | no | rejected: history would change |
| 11 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -2.75% | altered | no | rejected: history would change |
| 11 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 11 | duplicate_load | unit fix (divide by 100) on GW_A | -49.73% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -3.06% | altered | no | rejected: history would change |
| 11 | duplicate_load | unit fix (divide by 100) on GW_B | -36.12% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.99% | altered | no | rejected: history would change |
| 11 | duplicate_load | unit fix (divide by 100) on GW_C | -4.57% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.14% | altered | no | rejected: history would change |
| 11 | join_fanout | unit fix (divide by 100) on GW_A | -49.84% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -3.09% | altered | no | rejected: history would change |
| 11 | join_fanout | unit fix (divide by 100) on GW_B | -36.04% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -2.06% | altered | no | rejected: history would change |
| 11 | join_fanout | unit fix (divide by 100) on GW_C | -4.51% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.15% | altered | no | rejected: history would change |
| 11 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 11 | stale_fx | unit fix (divide by 100) on GW_A | -54.41% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -3.34% | altered | no | rejected: history would change |
| 11 | stale_fx | unit fix (divide by 100) on GW_B | -39.57% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.21% | altered | no | rejected: history would change |
| 11 | stale_fx | unit fix (divide by 100) on GW_C | -4.90% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.16% | altered | no | rejected: history would change |
| 11 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 11 | ist_utc | unit fix (divide by 100) on GW_A | -59.24% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.64% | altered | no | rejected: history would change |
| 11 | ist_utc | unit fix (divide by 100) on GW_B | -24.32% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | ist_utc | unit fix (divide by 100) on GW_C | -5.34% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.18% | altered | no | rejected: history would change |
| 11 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 11 | new_code | unit fix (divide by 100) on GW_A | -49.90% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.92% | altered | no | rejected: history would change |
| 11 | new_code | unit fix (divide by 100) on GW_B | -36.10% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | new_code | clock fix (shift back 5.5 hours) on GW_B | -2.07% | altered | no | rejected: history would change |
| 11 | new_code | unit fix (divide by 100) on GW_C | -4.40% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.14% | altered | no | rejected: history would change |
| 11 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 11 | masked_pair | unit fix (divide by 100) on GW_A | -59.08% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.64% | altered | yes | rejected: history would change |
| 11 | masked_pair | unit fix (divide by 100) on GW_B | -24.34% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 11 | masked_pair | unit fix (divide by 100) on GW_C | -5.41% | unchanged | yes | ACCEPTED |
| 11 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.16% | altered | no | rejected: history would change |
| 22 | unit_paise | divide GW_C by 10 instead of 100 | -74.82% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | unit_paise | divide GW_C by 1000 instead of 100 | -83.06% | unchanged | yes | ACCEPTED |
| 22 | unit_paise | divide GW_C by 100 on every day, not only tonight | -82.31% | altered | yes | rejected: history would change |
| 22 | unit_paise | unit fix (divide by 100) on GW_A | -8.69% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.48% | altered | no | rejected: history would change |
| 22 | unit_paise | unit fix (divide by 100) on GW_B | -6.37% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.35% | altered | no | rejected: history would change |
| 22 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -5.11% | altered | no | rejected: history would change |
| 22 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 22 | duplicate_load | unit fix (divide by 100) on GW_A | -49.10% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.71% | altered | no | rejected: history would change |
| 22 | duplicate_load | unit fix (divide by 100) on GW_B | -35.83% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.95% | altered | no | rejected: history would change |
| 22 | duplicate_load | unit fix (divide by 100) on GW_C | -4.61% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.27% | altered | no | rejected: history would change |
| 22 | join_fanout | unit fix (divide by 100) on GW_A | -49.02% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.80% | altered | no | rejected: history would change |
| 22 | join_fanout | unit fix (divide by 100) on GW_B | -36.07% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -1.93% | altered | no | rejected: history would change |
| 22 | join_fanout | unit fix (divide by 100) on GW_C | -4.60% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.30% | altered | no | rejected: history would change |
| 22 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 22 | stale_fx | unit fix (divide by 100) on GW_A | -54.11% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -2.99% | altered | no | rejected: history would change |
| 22 | stale_fx | unit fix (divide by 100) on GW_B | -39.64% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.16% | altered | no | rejected: history would change |
| 22 | stale_fx | unit fix (divide by 100) on GW_C | -5.13% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.32% | altered | no | rejected: history would change |
| 22 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 22 | ist_utc | unit fix (divide by 100) on GW_A | -58.34% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.23% | altered | no | rejected: history would change |
| 22 | ist_utc | unit fix (divide by 100) on GW_B | -24.12% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | ist_utc | unit fix (divide by 100) on GW_C | -5.53% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.34% | altered | no | rejected: history would change |
| 22 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 22 | new_code | unit fix (divide by 100) on GW_A | -48.77% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.60% | altered | no | rejected: history would change |
| 22 | new_code | unit fix (divide by 100) on GW_B | -36.70% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.98% | altered | no | rejected: history would change |
| 22 | new_code | unit fix (divide by 100) on GW_C | -4.27% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.29% | altered | no | rejected: history would change |
| 22 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 22 | masked_pair | unit fix (divide by 100) on GW_A | -58.35% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.30% | altered | yes | rejected: history would change |
| 22 | masked_pair | unit fix (divide by 100) on GW_B | -24.14% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 22 | masked_pair | unit fix (divide by 100) on GW_C | -5.46% | unchanged | yes | ACCEPTED |
| 22 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.31% | altered | no | rejected: history would change |
| 33 | unit_paise | divide GW_C by 10 instead of 100 | -74.67% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | unit_paise | divide GW_C by 1000 instead of 100 | -82.88% | unchanged | yes | ACCEPTED |
| 33 | unit_paise | divide GW_C by 100 on every day, not only tonight | -82.14% | altered | yes | rejected: history would change |
| 33 | unit_paise | unit fix (divide by 100) on GW_A | -8.75% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.52% | altered | no | rejected: history would change |
| 33 | unit_paise | unit fix (divide by 100) on GW_B | -6.48% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.36% | altered | no | rejected: history would change |
| 33 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -4.52% | altered | no | rejected: history would change |
| 33 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 33 | duplicate_load | unit fix (divide by 100) on GW_A | -49.01% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.94% | altered | no | rejected: history would change |
| 33 | duplicate_load | unit fix (divide by 100) on GW_B | -36.28% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -2.09% | altered | no | rejected: history would change |
| 33 | duplicate_load | unit fix (divide by 100) on GW_C | -4.60% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.24% | altered | no | rejected: history would change |
| 33 | join_fanout | unit fix (divide by 100) on GW_A | -49.03% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.85% | altered | no | rejected: history would change |
| 33 | join_fanout | unit fix (divide by 100) on GW_B | -36.27% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -2.11% | altered | no | rejected: history would change |
| 33 | join_fanout | unit fix (divide by 100) on GW_C | -4.68% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.24% | altered | no | rejected: history would change |
| 33 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 33 | stale_fx | unit fix (divide by 100) on GW_A | -53.92% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -3.23% | altered | no | rejected: history would change |
| 33 | stale_fx | unit fix (divide by 100) on GW_B | -39.90% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.23% | altered | no | rejected: history would change |
| 33 | stale_fx | unit fix (divide by 100) on GW_C | -5.06% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.28% | altered | no | rejected: history would change |
| 33 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 33 | ist_utc | unit fix (divide by 100) on GW_A | -58.91% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.52% | altered | no | rejected: history would change |
| 33 | ist_utc | unit fix (divide by 100) on GW_B | -23.58% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | ist_utc | unit fix (divide by 100) on GW_C | -5.53% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.30% | altered | no | rejected: history would change |
| 33 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 33 | new_code | unit fix (divide by 100) on GW_A | -49.12% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.93% | altered | no | rejected: history would change |
| 33 | new_code | unit fix (divide by 100) on GW_B | -36.20% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.99% | altered | no | rejected: history would change |
| 33 | new_code | unit fix (divide by 100) on GW_C | -4.61% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.23% | altered | no | rejected: history would change |
| 33 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 33 | masked_pair | unit fix (divide by 100) on GW_A | -58.98% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.58% | altered | yes | rejected: history would change |
| 33 | masked_pair | unit fix (divide by 100) on GW_B | -23.60% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 33 | masked_pair | unit fix (divide by 100) on GW_C | -5.55% | unchanged | yes | ACCEPTED |
| 33 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.30% | altered | no | rejected: history would change |
| 44 | unit_paise | divide GW_C by 10 instead of 100 | -75.46% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | unit_paise | divide GW_C by 1000 instead of 100 | -83.76% | unchanged | yes | ACCEPTED |
| 44 | unit_paise | divide GW_C by 100 on every day, not only tonight | -83.01% | altered | yes | rejected: history would change |
| 44 | unit_paise | unit fix (divide by 100) on GW_A | -8.37% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.49% | altered | no | rejected: history would change |
| 44 | unit_paise | unit fix (divide by 100) on GW_B | -6.15% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.39% | altered | no | rejected: history would change |
| 44 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -2.88% | altered | no | rejected: history would change |
| 44 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 44 | duplicate_load | unit fix (divide by 100) on GW_A | -49.29% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.86% | altered | no | rejected: history would change |
| 44 | duplicate_load | unit fix (divide by 100) on GW_B | -36.09% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -2.37% | altered | no | rejected: history would change |
| 44 | duplicate_load | unit fix (divide by 100) on GW_C | -4.92% | unchanged | yes | ACCEPTED |
| 44 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.17% | altered | no | rejected: history would change |
| 44 | join_fanout | unit fix (divide by 100) on GW_A | -49.22% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.84% | altered | no | rejected: history would change |
| 44 | join_fanout | unit fix (divide by 100) on GW_B | -36.07% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -2.29% | altered | no | rejected: history would change |
| 44 | join_fanout | unit fix (divide by 100) on GW_C | -4.92% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.15% | altered | no | rejected: history would change |
| 44 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 44 | stale_fx | unit fix (divide by 100) on GW_A | -53.94% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -3.13% | altered | no | rejected: history would change |
| 44 | stale_fx | unit fix (divide by 100) on GW_B | -39.60% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.51% | altered | no | rejected: history would change |
| 44 | stale_fx | unit fix (divide by 100) on GW_C | -5.35% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.19% | altered | no | rejected: history would change |
| 44 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 44 | ist_utc | unit fix (divide by 100) on GW_A | -58.79% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.41% | altered | no | rejected: history would change |
| 44 | ist_utc | unit fix (divide by 100) on GW_B | -24.03% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | ist_utc | unit fix (divide by 100) on GW_C | -5.83% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.20% | altered | no | rejected: history would change |
| 44 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 44 | new_code | unit fix (divide by 100) on GW_A | -49.35% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.67% | altered | no | rejected: history would change |
| 44 | new_code | unit fix (divide by 100) on GW_B | -36.20% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | new_code | clock fix (shift back 5.5 hours) on GW_B | -2.29% | altered | no | rejected: history would change |
| 44 | new_code | unit fix (divide by 100) on GW_C | -4.88% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.15% | altered | no | rejected: history would change |
| 44 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 44 | masked_pair | unit fix (divide by 100) on GW_A | -58.57% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.36% | altered | yes | rejected: history would change |
| 44 | masked_pair | unit fix (divide by 100) on GW_B | -24.10% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 44 | masked_pair | unit fix (divide by 100) on GW_C | -5.90% | unchanged | yes | ACCEPTED |
| 44 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.21% | altered | yes | rejected: history would change |
| 55 | unit_paise | divide GW_C by 10 instead of 100 | -74.75% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | unit_paise | divide GW_C by 1000 instead of 100 | -82.98% | unchanged | yes | ACCEPTED |
| 55 | unit_paise | divide GW_C by 100 on every day, not only tonight | -82.23% | altered | yes | rejected: history would change |
| 55 | unit_paise | unit fix (divide by 100) on GW_A | -8.89% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.46% | altered | no | rejected: history would change |
| 55 | unit_paise | unit fix (divide by 100) on GW_B | -6.34% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.36% | altered | no | rejected: history would change |
| 55 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -4.22% | altered | no | rejected: history would change |
| 55 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 55 | duplicate_load | unit fix (divide by 100) on GW_A | -50.22% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.53% | altered | no | rejected: history would change |
| 55 | duplicate_load | unit fix (divide by 100) on GW_B | -35.62% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -2.06% | altered | no | rejected: history would change |
| 55 | duplicate_load | unit fix (divide by 100) on GW_C | -4.62% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.22% | altered | no | rejected: history would change |
| 55 | join_fanout | unit fix (divide by 100) on GW_A | -50.04% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.64% | altered | no | rejected: history would change |
| 55 | join_fanout | unit fix (divide by 100) on GW_B | -35.74% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -2.07% | altered | no | rejected: history would change |
| 55 | join_fanout | unit fix (divide by 100) on GW_C | -4.60% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.22% | altered | no | rejected: history would change |
| 55 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 55 | stale_fx | unit fix (divide by 100) on GW_A | -54.77% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -2.82% | altered | no | rejected: history would change |
| 55 | stale_fx | unit fix (divide by 100) on GW_B | -39.05% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.22% | altered | no | rejected: history would change |
| 55 | stale_fx | unit fix (divide by 100) on GW_C | -5.07% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.26% | altered | no | rejected: history would change |
| 55 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 55 | ist_utc | unit fix (divide by 100) on GW_A | -59.48% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.07% | altered | no | rejected: history would change |
| 55 | ist_utc | unit fix (divide by 100) on GW_B | -23.68% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | ist_utc | unit fix (divide by 100) on GW_C | -5.50% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.28% | altered | no | rejected: history would change |
| 55 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 55 | new_code | unit fix (divide by 100) on GW_A | -49.77% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.58% | altered | no | rejected: history would change |
| 55 | new_code | unit fix (divide by 100) on GW_B | -35.99% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | new_code | clock fix (shift back 5.5 hours) on GW_B | -2.10% | altered | no | rejected: history would change |
| 55 | new_code | unit fix (divide by 100) on GW_C | -4.69% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.20% | altered | no | rejected: history would change |
| 55 | new_code | remove duplicate payments in tonight's batch | -0.00% | unchanged | no | rejected: moves today's number only -0.00% |
| 55 | masked_pair | unit fix (divide by 100) on GW_A | -59.64% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -2.99% | altered | yes | rejected: history would change |
| 55 | masked_pair | unit fix (divide by 100) on GW_B | -23.66% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | masked_pair | unit fix (divide by 100) on GW_C | -5.47% | unchanged | yes | ACCEPTED |
| 55 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.27% | altered | no | rejected: history would change |
| 66 | unit_paise | divide GW_C by 10 instead of 100 | -74.98% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | unit_paise | divide GW_C by 1000 instead of 100 | -83.23% | unchanged | yes | ACCEPTED |
| 66 | unit_paise | divide GW_C by 100 on every day, not only tonight | -82.48% | altered | yes | rejected: history would change |
| 66 | unit_paise | unit fix (divide by 100) on GW_A | -8.76% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.47% | altered | no | rejected: history would change |
| 66 | unit_paise | unit fix (divide by 100) on GW_B | -6.20% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.34% | altered | no | rejected: history would change |
| 66 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -3.26% | altered | no | rejected: history would change |
| 66 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 66 | duplicate_load | unit fix (divide by 100) on GW_A | -50.14% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.70% | altered | no | rejected: history would change |
| 66 | duplicate_load | unit fix (divide by 100) on GW_B | -35.43% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.88% | altered | no | rejected: history would change |
| 66 | duplicate_load | unit fix (divide by 100) on GW_C | -4.70% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.17% | altered | no | rejected: history would change |
| 66 | join_fanout | unit fix (divide by 100) on GW_A | -49.81% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.69% | altered | no | rejected: history would change |
| 66 | join_fanout | unit fix (divide by 100) on GW_B | -35.59% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -1.91% | altered | no | rejected: history would change |
| 66 | join_fanout | unit fix (divide by 100) on GW_C | -4.74% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.21% | altered | no | rejected: history would change |
| 66 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 66 | stale_fx | unit fix (divide by 100) on GW_A | -54.87% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -2.93% | altered | no | rejected: history would change |
| 66 | stale_fx | unit fix (divide by 100) on GW_B | -38.85% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.11% | altered | no | rejected: history would change |
| 66 | stale_fx | unit fix (divide by 100) on GW_C | -5.16% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.20% | altered | no | rejected: history would change |
| 66 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 66 | ist_utc | unit fix (divide by 100) on GW_A | -59.24% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.16% | altered | no | rejected: history would change |
| 66 | ist_utc | unit fix (divide by 100) on GW_B | -23.69% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | ist_utc | unit fix (divide by 100) on GW_C | -5.57% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.22% | altered | no | rejected: history would change |
| 66 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 66 | new_code | unit fix (divide by 100) on GW_A | -49.81% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.73% | altered | no | rejected: history would change |
| 66 | new_code | unit fix (divide by 100) on GW_B | -35.55% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.96% | altered | no | rejected: history would change |
| 66 | new_code | unit fix (divide by 100) on GW_C | -4.72% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.20% | altered | no | rejected: history would change |
| 66 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 66 | masked_pair | unit fix (divide by 100) on GW_A | -59.34% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.23% | altered | yes | rejected: history would change |
| 66 | masked_pair | unit fix (divide by 100) on GW_B | -23.61% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 66 | masked_pair | unit fix (divide by 100) on GW_C | -5.59% | unchanged | yes | ACCEPTED |
| 66 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.20% | altered | no | rejected: history would change |
| 77 | unit_paise | divide GW_C by 10 instead of 100 | -73.58% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | unit_paise | divide GW_C by 1000 instead of 100 | -81.68% | unchanged | yes | ACCEPTED |
| 77 | unit_paise | divide GW_C by 100 on every day, not only tonight | -80.94% | altered | yes | rejected: history would change |
| 77 | unit_paise | unit fix (divide by 100) on GW_A | -9.45% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.49% | altered | no | rejected: history would change |
| 77 | unit_paise | unit fix (divide by 100) on GW_B | -6.94% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.38% | altered | no | rejected: history would change |
| 77 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -5.30% | altered | no | rejected: history would change |
| 77 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 77 | duplicate_load | unit fix (divide by 100) on GW_A | -49.66% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.68% | altered | no | rejected: history would change |
| 77 | duplicate_load | unit fix (divide by 100) on GW_B | -36.44% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.89% | altered | no | rejected: history would change |
| 77 | duplicate_load | unit fix (divide by 100) on GW_C | -4.18% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.28% | altered | no | rejected: history would change |
| 77 | join_fanout | unit fix (divide by 100) on GW_A | -49.82% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.54% | altered | no | rejected: history would change |
| 77 | join_fanout | unit fix (divide by 100) on GW_B | -36.26% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -2.08% | altered | no | rejected: history would change |
| 77 | join_fanout | unit fix (divide by 100) on GW_C | -4.19% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.26% | altered | no | rejected: history would change |
| 77 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 77 | stale_fx | unit fix (divide by 100) on GW_A | -54.32% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -2.84% | altered | no | rejected: history would change |
| 77 | stale_fx | unit fix (divide by 100) on GW_B | -39.91% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.17% | altered | no | rejected: history would change |
| 77 | stale_fx | unit fix (divide by 100) on GW_C | -4.65% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.30% | altered | no | rejected: history would change |
| 77 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 77 | ist_utc | unit fix (divide by 100) on GW_A | -59.01% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.09% | altered | no | rejected: history would change |
| 77 | ist_utc | unit fix (divide by 100) on GW_B | -24.56% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | ist_utc | unit fix (divide by 100) on GW_C | -5.05% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.33% | altered | no | rejected: history would change |
| 77 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 77 | new_code | unit fix (divide by 100) on GW_A | -49.20% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.55% | altered | no | rejected: history would change |
| 77 | new_code | unit fix (divide by 100) on GW_B | -36.65% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.97% | altered | no | rejected: history would change |
| 77 | new_code | unit fix (divide by 100) on GW_C | -4.44% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.32% | altered | no | rejected: history would change |
| 77 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 77 | masked_pair | unit fix (divide by 100) on GW_A | -59.32% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.19% | altered | yes | rejected: history would change |
| 77 | masked_pair | unit fix (divide by 100) on GW_B | -24.38% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 77 | masked_pair | unit fix (divide by 100) on GW_C | -4.86% | unchanged | yes | ACCEPTED |
| 77 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.33% | altered | no | rejected: history would change |
| 88 | unit_paise | divide GW_C by 10 instead of 100 | -74.31% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | unit_paise | divide GW_C by 1000 instead of 100 | -82.48% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | unit_paise | divide GW_C by 100 on every day, not only tonight | -81.74% | altered | yes | rejected: history would change |
| 88 | unit_paise | unit fix (divide by 100) on GW_A | -8.96% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.50% | altered | no | rejected: history would change |
| 88 | unit_paise | unit fix (divide by 100) on GW_B | -6.59% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.33% | altered | no | rejected: history would change |
| 88 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -4.28% | altered | no | rejected: history would change |
| 88 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 88 | duplicate_load | unit fix (divide by 100) on GW_A | -49.13% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.71% | altered | no | rejected: history would change |
| 88 | duplicate_load | unit fix (divide by 100) on GW_B | -36.07% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.78% | altered | no | rejected: history would change |
| 88 | duplicate_load | unit fix (divide by 100) on GW_C | -4.35% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.22% | altered | no | rejected: history would change |
| 88 | join_fanout | unit fix (divide by 100) on GW_A | -49.14% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.75% | altered | no | rejected: history would change |
| 88 | join_fanout | unit fix (divide by 100) on GW_B | -36.01% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -1.79% | altered | no | rejected: history would change |
| 88 | join_fanout | unit fix (divide by 100) on GW_C | -4.42% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.22% | altered | no | rejected: history would change |
| 88 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 88 | stale_fx | unit fix (divide by 100) on GW_A | -54.11% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -3.01% | altered | no | rejected: history would change |
| 88 | stale_fx | unit fix (divide by 100) on GW_B | -39.83% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.00% | altered | no | rejected: history would change |
| 88 | stale_fx | unit fix (divide by 100) on GW_C | -4.94% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.26% | altered | no | rejected: history would change |
| 88 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 88 | ist_utc | unit fix (divide by 100) on GW_A | -58.47% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.25% | altered | no | rejected: history would change |
| 88 | ist_utc | unit fix (divide by 100) on GW_B | -24.05% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | ist_utc | unit fix (divide by 100) on GW_C | -5.34% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.28% | altered | no | rejected: history would change |
| 88 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 88 | new_code | unit fix (divide by 100) on GW_A | -48.99% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.74% | altered | no | rejected: history would change |
| 88 | new_code | unit fix (divide by 100) on GW_B | -36.06% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.87% | altered | no | rejected: history would change |
| 88 | new_code | unit fix (divide by 100) on GW_C | -4.50% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.22% | altered | no | rejected: history would change |
| 88 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 88 | masked_pair | unit fix (divide by 100) on GW_A | -58.76% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.21% | altered | yes | rejected: history would change |
| 88 | masked_pair | unit fix (divide by 100) on GW_B | -23.92% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 88 | masked_pair | unit fix (divide by 100) on GW_C | -5.17% | unchanged | yes | ACCEPTED |
| 88 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.28% | altered | yes | rejected: history would change |
| 99 | unit_paise | divide GW_C by 10 instead of 100 | -74.44% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | unit_paise | divide GW_C by 1000 instead of 100 | -82.63% | unchanged | yes | ACCEPTED |
| 99 | unit_paise | divide GW_C by 100 on every day, not only tonight | -81.89% | altered | yes | rejected: history would change |
| 99 | unit_paise | unit fix (divide by 100) on GW_A | -8.90% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.50% | altered | no | rejected: history would change |
| 99 | unit_paise | unit fix (divide by 100) on GW_B | -6.56% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.36% | altered | no | rejected: history would change |
| 99 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -4.07% | altered | no | rejected: history would change |
| 99 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 99 | duplicate_load | unit fix (divide by 100) on GW_A | -49.03% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.78% | altered | no | rejected: history would change |
| 99 | duplicate_load | unit fix (divide by 100) on GW_B | -36.41% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -2.01% | altered | no | rejected: history would change |
| 99 | duplicate_load | unit fix (divide by 100) on GW_C | -4.59% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.24% | altered | no | rejected: history would change |
| 99 | join_fanout | unit fix (divide by 100) on GW_A | -49.51% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.71% | altered | no | rejected: history would change |
| 99 | join_fanout | unit fix (divide by 100) on GW_B | -35.91% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -1.92% | altered | no | rejected: history would change |
| 99 | join_fanout | unit fix (divide by 100) on GW_C | -4.40% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.25% | altered | no | rejected: history would change |
| 99 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 99 | stale_fx | unit fix (divide by 100) on GW_A | -54.08% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -3.01% | altered | no | rejected: history would change |
| 99 | stale_fx | unit fix (divide by 100) on GW_B | -39.83% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.18% | altered | no | rejected: history would change |
| 99 | stale_fx | unit fix (divide by 100) on GW_C | -4.97% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.25% | altered | no | rejected: history would change |
| 99 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 99 | ist_utc | unit fix (divide by 100) on GW_A | -58.62% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.26% | altered | no | rejected: history would change |
| 99 | ist_utc | unit fix (divide by 100) on GW_B | -24.14% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | ist_utc | unit fix (divide by 100) on GW_C | -5.39% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.27% | altered | no | rejected: history would change |
| 99 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 99 | new_code | unit fix (divide by 100) on GW_A | -49.26% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.72% | altered | no | rejected: history would change |
| 99 | new_code | unit fix (divide by 100) on GW_B | -36.10% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.98% | altered | no | rejected: history would change |
| 99 | new_code | unit fix (divide by 100) on GW_C | -4.54% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.16% | altered | no | rejected: history would change |
| 99 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 99 | masked_pair | unit fix (divide by 100) on GW_A | -58.55% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.31% | altered | yes | rejected: history would change |
| 99 | masked_pair | unit fix (divide by 100) on GW_B | -24.22% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 99 | masked_pair | unit fix (divide by 100) on GW_C | -5.38% | unchanged | yes | ACCEPTED |
| 99 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.29% | altered | yes | rejected: history would change |
| 110 | unit_paise | divide GW_C by 10 instead of 100 | -74.79% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | unit_paise | divide GW_C by 1000 instead of 100 | -83.01% | unchanged | yes | ACCEPTED |
| 110 | unit_paise | divide GW_C by 100 on every day, not only tonight | -82.27% | altered | yes | rejected: history would change |
| 110 | unit_paise | unit fix (divide by 100) on GW_A | -8.79% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.49% | altered | no | rejected: history would change |
| 110 | unit_paise | unit fix (divide by 100) on GW_B | -6.34% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.36% | altered | no | rejected: history would change |
| 110 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -3.13% | altered | no | rejected: history would change |
| 110 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 110 | duplicate_load | unit fix (divide by 100) on GW_A | -49.47% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.81% | altered | no | rejected: history would change |
| 110 | duplicate_load | unit fix (divide by 100) on GW_B | -35.90% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -2.16% | altered | no | rejected: history would change |
| 110 | duplicate_load | unit fix (divide by 100) on GW_C | -4.58% | unchanged | yes | ACCEPTED |
| 110 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.20% | altered | no | rejected: history would change |
| 110 | join_fanout | unit fix (divide by 100) on GW_A | -49.44% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.75% | altered | no | rejected: history would change |
| 110 | join_fanout | unit fix (divide by 100) on GW_B | -35.66% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -2.09% | altered | no | rejected: history would change |
| 110 | join_fanout | unit fix (divide by 100) on GW_C | -4.64% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.17% | altered | no | rejected: history would change |
| 110 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 110 | stale_fx | unit fix (divide by 100) on GW_A | -54.51% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -3.03% | altered | no | rejected: history would change |
| 110 | stale_fx | unit fix (divide by 100) on GW_B | -39.28% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.26% | altered | no | rejected: history would change |
| 110 | stale_fx | unit fix (divide by 100) on GW_C | -5.10% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.19% | altered | no | rejected: history would change |
| 110 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 110 | ist_utc | unit fix (divide by 100) on GW_A | -58.68% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.26% | altered | no | rejected: history would change |
| 110 | ist_utc | unit fix (divide by 100) on GW_B | -24.12% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | ist_utc | unit fix (divide by 100) on GW_C | -5.49% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.21% | altered | no | rejected: history would change |
| 110 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 110 | new_code | unit fix (divide by 100) on GW_A | -49.81% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.68% | altered | no | rejected: history would change |
| 110 | new_code | unit fix (divide by 100) on GW_B | -35.52% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.94% | altered | no | rejected: history would change |
| 110 | new_code | unit fix (divide by 100) on GW_C | -4.67% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.18% | altered | no | rejected: history would change |
| 110 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 110 | masked_pair | unit fix (divide by 100) on GW_A | -58.62% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.24% | altered | yes | rejected: history would change |
| 110 | masked_pair | unit fix (divide by 100) on GW_B | -24.07% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 110 | masked_pair | unit fix (divide by 100) on GW_C | -5.38% | unchanged | yes | ACCEPTED |
| 110 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.21% | altered | yes | rejected: history would change |
| 121 | unit_paise | divide GW_C by 10 instead of 100 | -73.81% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | unit_paise | divide GW_C by 1000 instead of 100 | -81.93% | unchanged | yes | ACCEPTED |
| 121 | unit_paise | divide GW_C by 100 on every day, not only tonight | -81.19% | altered | yes | rejected: history would change |
| 121 | unit_paise | unit fix (divide by 100) on GW_A | -9.32% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.51% | altered | no | rejected: history would change |
| 121 | unit_paise | unit fix (divide by 100) on GW_B | -6.72% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.38% | altered | no | rejected: history would change |
| 121 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -4.68% | altered | no | rejected: history would change |
| 121 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 121 | duplicate_load | unit fix (divide by 100) on GW_A | -49.48% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.68% | altered | no | rejected: history would change |
| 121 | duplicate_load | unit fix (divide by 100) on GW_B | -35.84% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.98% | altered | no | rejected: history would change |
| 121 | duplicate_load | unit fix (divide by 100) on GW_C | -4.21% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.23% | altered | no | rejected: history would change |
| 121 | join_fanout | unit fix (divide by 100) on GW_A | -49.52% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.66% | altered | no | rejected: history would change |
| 121 | join_fanout | unit fix (divide by 100) on GW_B | -35.70% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -1.93% | altered | no | rejected: history would change |
| 121 | join_fanout | unit fix (divide by 100) on GW_C | -4.38% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.23% | altered | no | rejected: history would change |
| 121 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 121 | stale_fx | unit fix (divide by 100) on GW_A | -54.69% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -2.97% | altered | no | rejected: history would change |
| 121 | stale_fx | unit fix (divide by 100) on GW_B | -39.43% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.21% | altered | no | rejected: history would change |
| 121 | stale_fx | unit fix (divide by 100) on GW_C | -4.76% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.27% | altered | no | rejected: history would change |
| 121 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 121 | ist_utc | unit fix (divide by 100) on GW_A | -58.87% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.20% | altered | no | rejected: history would change |
| 121 | ist_utc | unit fix (divide by 100) on GW_B | -23.86% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | ist_utc | unit fix (divide by 100) on GW_C | -5.13% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.30% | altered | no | rejected: history would change |
| 121 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 121 | new_code | unit fix (divide by 100) on GW_A | -49.34% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.83% | altered | no | rejected: history would change |
| 121 | new_code | unit fix (divide by 100) on GW_B | -35.90% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.95% | altered | no | rejected: history would change |
| 121 | new_code | unit fix (divide by 100) on GW_C | -4.38% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.24% | altered | no | rejected: history would change |
| 121 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 121 | masked_pair | unit fix (divide by 100) on GW_A | -58.58% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.14% | altered | yes | rejected: history would change |
| 121 | masked_pair | unit fix (divide by 100) on GW_B | -24.25% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 121 | masked_pair | unit fix (divide by 100) on GW_C | -5.02% | unchanged | yes | ACCEPTED |
| 121 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.25% | altered | no | rejected: history would change |
| 132 | unit_paise | divide GW_C by 10 instead of 100 | -75.07% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | unit_paise | divide GW_C by 1000 instead of 100 | -83.33% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | unit_paise | divide GW_C by 100 on every day, not only tonight | -82.57% | altered | yes | rejected: history would change |
| 132 | unit_paise | unit fix (divide by 100) on GW_A | -8.69% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.49% | altered | no | rejected: history would change |
| 132 | unit_paise | unit fix (divide by 100) on GW_B | -6.19% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.36% | altered | no | rejected: history would change |
| 132 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -4.04% | altered | no | rejected: history would change |
| 132 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 132 | duplicate_load | unit fix (divide by 100) on GW_A | -49.69% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.78% | altered | no | rejected: history would change |
| 132 | duplicate_load | unit fix (divide by 100) on GW_B | -35.80% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -2.08% | altered | no | rejected: history would change |
| 132 | duplicate_load | unit fix (divide by 100) on GW_C | -4.71% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.22% | altered | no | rejected: history would change |
| 132 | join_fanout | unit fix (divide by 100) on GW_A | -50.16% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.88% | altered | no | rejected: history would change |
| 132 | join_fanout | unit fix (divide by 100) on GW_B | -35.37% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -2.09% | altered | no | rejected: history would change |
| 132 | join_fanout | unit fix (divide by 100) on GW_C | -4.76% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.24% | altered | no | rejected: history would change |
| 132 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 132 | stale_fx | unit fix (divide by 100) on GW_A | -54.71% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -3.07% | altered | no | rejected: history would change |
| 132 | stale_fx | unit fix (divide by 100) on GW_B | -38.98% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.28% | altered | no | rejected: history would change |
| 132 | stale_fx | unit fix (divide by 100) on GW_C | -5.20% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.25% | altered | no | rejected: history would change |
| 132 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 132 | ist_utc | unit fix (divide by 100) on GW_A | -59.05% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.32% | altered | no | rejected: history would change |
| 132 | ist_utc | unit fix (divide by 100) on GW_B | -23.89% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | ist_utc | unit fix (divide by 100) on GW_C | -5.61% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.27% | altered | no | rejected: history would change |
| 132 | ist_utc | remove duplicate payments in tonight's batch | -0.00% | unchanged | no | rejected: moves today's number only -0.00% |
| 132 | new_code | unit fix (divide by 100) on GW_A | -49.69% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.68% | altered | no | rejected: history would change |
| 132 | new_code | unit fix (divide by 100) on GW_B | -35.52% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | new_code | clock fix (shift back 5.5 hours) on GW_B | -2.06% | altered | no | rejected: history would change |
| 132 | new_code | unit fix (divide by 100) on GW_C | -4.78% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.23% | altered | no | rejected: history would change |
| 132 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 132 | masked_pair | unit fix (divide by 100) on GW_A | -59.15% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.35% | altered | yes | rejected: history would change |
| 132 | masked_pair | unit fix (divide by 100) on GW_B | -23.79% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 132 | masked_pair | unit fix (divide by 100) on GW_C | -5.72% | unchanged | yes | ACCEPTED |
| 132 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.27% | altered | no | rejected: history would change |
| 143 | unit_paise | divide GW_C by 10 instead of 100 | -73.71% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | unit_paise | divide GW_C by 1000 instead of 100 | -81.82% | unchanged | yes | ACCEPTED |
| 143 | unit_paise | divide GW_C by 100 on every day, not only tonight | -81.08% | altered | yes | rejected: history would change |
| 143 | unit_paise | unit fix (divide by 100) on GW_A | -9.22% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.49% | altered | no | rejected: history would change |
| 143 | unit_paise | unit fix (divide by 100) on GW_B | -6.97% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.40% | altered | no | rejected: history would change |
| 143 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -2.92% | altered | no | rejected: history would change |
| 143 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 143 | duplicate_load | unit fix (divide by 100) on GW_A | -48.82% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.68% | altered | no | rejected: history would change |
| 143 | duplicate_load | unit fix (divide by 100) on GW_B | -36.67% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -2.09% | altered | no | rejected: history would change |
| 143 | duplicate_load | unit fix (divide by 100) on GW_C | -4.34% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.17% | altered | no | rejected: history would change |
| 143 | join_fanout | unit fix (divide by 100) on GW_A | -48.79% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.48% | altered | no | rejected: history would change |
| 143 | join_fanout | unit fix (divide by 100) on GW_B | -36.87% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -2.14% | altered | no | rejected: history would change |
| 143 | join_fanout | unit fix (divide by 100) on GW_C | -4.30% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.14% | altered | no | rejected: history would change |
| 143 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 143 | stale_fx | unit fix (divide by 100) on GW_A | -53.64% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -2.87% | altered | no | rejected: history would change |
| 143 | stale_fx | unit fix (divide by 100) on GW_B | -40.53% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.33% | altered | no | rejected: history would change |
| 143 | stale_fx | unit fix (divide by 100) on GW_C | -4.71% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.17% | altered | no | rejected: history would change |
| 143 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 143 | ist_utc | unit fix (divide by 100) on GW_A | -58.31% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.11% | altered | no | rejected: history would change |
| 143 | ist_utc | unit fix (divide by 100) on GW_B | -24.65% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | ist_utc | unit fix (divide by 100) on GW_C | -5.13% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.18% | altered | no | rejected: history would change |
| 143 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 143 | new_code | unit fix (divide by 100) on GW_A | -48.97% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.71% | altered | no | rejected: history would change |
| 143 | new_code | unit fix (divide by 100) on GW_B | -36.46% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | new_code | clock fix (shift back 5.5 hours) on GW_B | -2.12% | altered | no | rejected: history would change |
| 143 | new_code | unit fix (divide by 100) on GW_C | -4.29% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.14% | altered | no | rejected: history would change |
| 143 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 143 | masked_pair | unit fix (divide by 100) on GW_A | -58.35% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.18% | altered | no | rejected: history would change |
| 143 | masked_pair | unit fix (divide by 100) on GW_B | -24.47% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 143 | masked_pair | unit fix (divide by 100) on GW_C | -5.21% | unchanged | yes | ACCEPTED |
| 143 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.21% | altered | no | rejected: history would change |
| 154 | unit_paise | divide GW_C by 10 instead of 100 | -75.04% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | unit_paise | divide GW_C by 1000 instead of 100 | -83.30% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | unit_paise | divide GW_C by 100 on every day, not only tonight | -82.55% | altered | yes | rejected: history would change |
| 154 | unit_paise | unit fix (divide by 100) on GW_A | -8.64% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.51% | altered | no | rejected: history would change |
| 154 | unit_paise | unit fix (divide by 100) on GW_B | -6.26% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.32% | altered | no | rejected: history would change |
| 154 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -4.34% | altered | no | rejected: history would change |
| 154 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 154 | duplicate_load | unit fix (divide by 100) on GW_A | -49.49% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.97% | altered | no | rejected: history would change |
| 154 | duplicate_load | unit fix (divide by 100) on GW_B | -35.88% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.84% | altered | no | rejected: history would change |
| 154 | duplicate_load | unit fix (divide by 100) on GW_C | -4.68% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.25% | altered | no | rejected: history would change |
| 154 | join_fanout | unit fix (divide by 100) on GW_A | -49.36% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.93% | altered | no | rejected: history would change |
| 154 | join_fanout | unit fix (divide by 100) on GW_B | -35.79% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -1.83% | altered | no | rejected: history would change |
| 154 | join_fanout | unit fix (divide by 100) on GW_C | -4.71% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.26% | altered | no | rejected: history would change |
| 154 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 154 | stale_fx | unit fix (divide by 100) on GW_A | -54.33% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -3.18% | altered | no | rejected: history would change |
| 154 | stale_fx | unit fix (divide by 100) on GW_B | -39.36% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.02% | altered | no | rejected: history would change |
| 154 | stale_fx | unit fix (divide by 100) on GW_C | -5.19% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.27% | altered | no | rejected: history would change |
| 154 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 154 | ist_utc | unit fix (divide by 100) on GW_A | -59.07% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.46% | altered | no | rejected: history would change |
| 154 | ist_utc | unit fix (divide by 100) on GW_B | -23.66% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | ist_utc | unit fix (divide by 100) on GW_C | -5.64% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.30% | altered | no | rejected: history would change |
| 154 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 154 | new_code | unit fix (divide by 100) on GW_A | -49.94% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.81% | altered | no | rejected: history would change |
| 154 | new_code | unit fix (divide by 100) on GW_B | -35.70% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.81% | altered | no | rejected: history would change |
| 154 | new_code | unit fix (divide by 100) on GW_C | -4.54% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.24% | altered | no | rejected: history would change |
| 154 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 154 | masked_pair | unit fix (divide by 100) on GW_A | -58.97% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.56% | altered | yes | rejected: history would change |
| 154 | masked_pair | unit fix (divide by 100) on GW_B | -23.76% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 154 | masked_pair | unit fix (divide by 100) on GW_C | -5.67% | unchanged | yes | ACCEPTED |
| 154 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.29% | altered | no | rejected: history would change |
| 165 | unit_paise | divide GW_C by 10 instead of 100 | -74.75% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | unit_paise | divide GW_C by 1000 instead of 100 | -82.97% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | unit_paise | divide GW_C by 100 on every day, not only tonight | -82.22% | altered | yes | rejected: history would change |
| 165 | unit_paise | unit fix (divide by 100) on GW_A | -8.84% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.49% | altered | no | rejected: history would change |
| 165 | unit_paise | unit fix (divide by 100) on GW_B | -6.32% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.36% | altered | no | rejected: history would change |
| 165 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -5.68% | altered | no | rejected: history would change |
| 165 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 165 | duplicate_load | unit fix (divide by 100) on GW_A | -49.93% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.78% | altered | no | rejected: history would change |
| 165 | duplicate_load | unit fix (divide by 100) on GW_B | -35.61% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -2.07% | altered | no | rejected: history would change |
| 165 | duplicate_load | unit fix (divide by 100) on GW_C | -4.51% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.31% | altered | no | rejected: history would change |
| 165 | join_fanout | unit fix (divide by 100) on GW_A | -49.78% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.82% | altered | no | rejected: history would change |
| 165 | join_fanout | unit fix (divide by 100) on GW_B | -35.65% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -2.15% | altered | no | rejected: history would change |
| 165 | join_fanout | unit fix (divide by 100) on GW_C | -4.55% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.29% | altered | no | rejected: history would change |
| 165 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 165 | stale_fx | unit fix (divide by 100) on GW_A | -54.67% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -3.04% | altered | no | rejected: history would change |
| 165 | stale_fx | unit fix (divide by 100) on GW_B | -39.12% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.24% | altered | no | rejected: history would change |
| 165 | stale_fx | unit fix (divide by 100) on GW_C | -5.09% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.35% | altered | no | rejected: history would change |
| 165 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 165 | ist_utc | unit fix (divide by 100) on GW_A | -59.05% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.29% | altered | no | rejected: history would change |
| 165 | ist_utc | unit fix (divide by 100) on GW_B | -23.68% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | ist_utc | unit fix (divide by 100) on GW_C | -5.49% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.38% | altered | no | rejected: history would change |
| 165 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 165 | new_code | unit fix (divide by 100) on GW_A | -49.78% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.88% | altered | no | rejected: history would change |
| 165 | new_code | unit fix (divide by 100) on GW_B | -35.64% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | new_code | clock fix (shift back 5.5 hours) on GW_B | -2.04% | altered | no | rejected: history would change |
| 165 | new_code | unit fix (divide by 100) on GW_C | -4.77% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.31% | altered | no | rejected: history would change |
| 165 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 165 | masked_pair | unit fix (divide by 100) on GW_A | -59.17% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.31% | altered | yes | rejected: history would change |
| 165 | masked_pair | unit fix (divide by 100) on GW_B | -23.70% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 165 | masked_pair | unit fix (divide by 100) on GW_C | -5.43% | unchanged | yes | ACCEPTED |
| 165 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.38% | altered | yes | rejected: history would change |
| 176 | unit_paise | divide GW_C by 10 instead of 100 | -74.26% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | unit_paise | divide GW_C by 1000 instead of 100 | -82.42% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | unit_paise | divide GW_C by 100 on every day, not only tonight | -81.68% | altered | yes | rejected: history would change |
| 176 | unit_paise | unit fix (divide by 100) on GW_A | -9.21% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.52% | altered | no | rejected: history would change |
| 176 | unit_paise | unit fix (divide by 100) on GW_B | -6.55% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.32% | altered | no | rejected: history would change |
| 176 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -3.71% | altered | no | rejected: history would change |
| 176 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 176 | duplicate_load | unit fix (divide by 100) on GW_A | -50.09% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.80% | altered | no | rejected: history would change |
| 176 | duplicate_load | unit fix (divide by 100) on GW_B | -35.69% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.77% | altered | no | rejected: history would change |
| 176 | duplicate_load | unit fix (divide by 100) on GW_C | -4.59% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.19% | altered | no | rejected: history would change |
| 176 | join_fanout | unit fix (divide by 100) on GW_A | -49.97% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.83% | altered | no | rejected: history would change |
| 176 | join_fanout | unit fix (divide by 100) on GW_B | -35.96% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -1.72% | altered | no | rejected: history would change |
| 176 | join_fanout | unit fix (divide by 100) on GW_C | -4.39% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.22% | altered | no | rejected: history would change |
| 176 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 176 | stale_fx | unit fix (divide by 100) on GW_A | -54.94% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -3.09% | altered | no | rejected: history would change |
| 176 | stale_fx | unit fix (divide by 100) on GW_B | -39.08% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -1.92% | altered | no | rejected: history would change |
| 176 | stale_fx | unit fix (divide by 100) on GW_C | -4.87% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.22% | altered | no | rejected: history would change |
| 176 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 176 | ist_utc | unit fix (divide by 100) on GW_A | -60.23% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.39% | altered | no | rejected: history would change |
| 176 | ist_utc | unit fix (divide by 100) on GW_B | -23.18% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | ist_utc | unit fix (divide by 100) on GW_C | -5.34% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.24% | altered | no | rejected: history would change |
| 176 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 176 | new_code | unit fix (divide by 100) on GW_A | -50.11% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.78% | altered | no | rejected: history would change |
| 176 | new_code | unit fix (divide by 100) on GW_B | -36.08% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.70% | altered | no | rejected: history would change |
| 176 | new_code | unit fix (divide by 100) on GW_C | -4.31% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.22% | altered | no | rejected: history would change |
| 176 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 176 | masked_pair | unit fix (divide by 100) on GW_A | -60.50% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.40% | altered | yes | rejected: history would change |
| 176 | masked_pair | unit fix (divide by 100) on GW_B | -22.91% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 176 | masked_pair | unit fix (divide by 100) on GW_C | -5.38% | unchanged | yes | ACCEPTED |
| 176 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.22% | altered | yes | rejected: history would change |
| 187 | unit_paise | divide GW_C by 10 instead of 100 | -75.48% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | unit_paise | divide GW_C by 1000 instead of 100 | -83.78% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | unit_paise | divide GW_C by 100 on every day, not only tonight | -83.03% | altered | yes | rejected: history would change |
| 187 | unit_paise | unit fix (divide by 100) on GW_A | -8.37% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.44% | altered | no | rejected: history would change |
| 187 | unit_paise | unit fix (divide by 100) on GW_B | -6.09% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.33% | altered | no | rejected: history would change |
| 187 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -4.35% | altered | no | rejected: history would change |
| 187 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 187 | duplicate_load | unit fix (divide by 100) on GW_A | -49.19% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.58% | altered | no | rejected: history would change |
| 187 | duplicate_load | unit fix (divide by 100) on GW_B | -36.01% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.97% | altered | no | rejected: history would change |
| 187 | duplicate_load | unit fix (divide by 100) on GW_C | -4.88% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.29% | altered | no | rejected: history would change |
| 187 | join_fanout | unit fix (divide by 100) on GW_A | -49.31% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.48% | altered | no | rejected: history would change |
| 187 | join_fanout | unit fix (divide by 100) on GW_B | -36.01% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -1.91% | altered | no | rejected: history would change |
| 187 | join_fanout | unit fix (divide by 100) on GW_C | -4.73% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.23% | altered | no | rejected: history would change |
| 187 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 187 | stale_fx | unit fix (divide by 100) on GW_A | -54.13% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -2.82% | altered | no | rejected: history would change |
| 187 | stale_fx | unit fix (divide by 100) on GW_B | -39.38% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.13% | altered | no | rejected: history would change |
| 187 | stale_fx | unit fix (divide by 100) on GW_C | -5.37% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.28% | altered | no | rejected: history would change |
| 187 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 187 | ist_utc | unit fix (divide by 100) on GW_A | -58.62% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.06% | altered | no | rejected: history would change |
| 187 | ist_utc | unit fix (divide by 100) on GW_B | -24.00% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | ist_utc | unit fix (divide by 100) on GW_C | -5.81% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.30% | altered | no | rejected: history would change |
| 187 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 187 | new_code | unit fix (divide by 100) on GW_A | -49.07% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.58% | altered | no | rejected: history would change |
| 187 | new_code | unit fix (divide by 100) on GW_B | -36.42% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.92% | altered | no | rejected: history would change |
| 187 | new_code | unit fix (divide by 100) on GW_C | -4.70% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.29% | altered | no | rejected: history would change |
| 187 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 187 | masked_pair | unit fix (divide by 100) on GW_A | -58.54% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -2.98% | altered | yes | rejected: history would change |
| 187 | masked_pair | unit fix (divide by 100) on GW_B | -24.02% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 187 | masked_pair | unit fix (divide by 100) on GW_C | -5.85% | unchanged | yes | ACCEPTED |
| 187 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.33% | altered | no | rejected: history would change |
| 198 | unit_paise | divide GW_C by 10 instead of 100 | -74.29% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | unit_paise | divide GW_C by 1000 instead of 100 | -82.47% | unchanged | yes | ACCEPTED |
| 198 | unit_paise | divide GW_C by 100 on every day, not only tonight | -81.72% | altered | yes | rejected: history would change |
| 198 | unit_paise | unit fix (divide by 100) on GW_A | -9.17% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.47% | altered | no | rejected: history would change |
| 198 | unit_paise | unit fix (divide by 100) on GW_B | -6.51% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.33% | altered | no | rejected: history would change |
| 198 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -4.84% | altered | no | rejected: history would change |
| 198 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 198 | duplicate_load | unit fix (divide by 100) on GW_A | -50.16% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.53% | altered | no | rejected: history would change |
| 198 | duplicate_load | unit fix (divide by 100) on GW_B | -35.51% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.77% | altered | no | rejected: history would change |
| 198 | duplicate_load | unit fix (divide by 100) on GW_C | -4.54% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.28% | altered | no | rejected: history would change |
| 198 | join_fanout | unit fix (divide by 100) on GW_A | -49.98% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.50% | altered | no | rejected: history would change |
| 198 | join_fanout | unit fix (divide by 100) on GW_B | -35.90% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -1.82% | altered | no | rejected: history would change |
| 198 | join_fanout | unit fix (divide by 100) on GW_C | -4.43% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.26% | altered | no | rejected: history would change |
| 198 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 198 | stale_fx | unit fix (divide by 100) on GW_A | -54.97% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -2.82% | altered | no | rejected: history would change |
| 198 | stale_fx | unit fix (divide by 100) on GW_B | -39.02% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -1.99% | altered | no | rejected: history would change |
| 198 | stale_fx | unit fix (divide by 100) on GW_C | -4.90% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.29% | altered | no | rejected: history would change |
| 198 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 198 | ist_utc | unit fix (divide by 100) on GW_A | -59.35% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.05% | altered | no | rejected: history would change |
| 198 | ist_utc | unit fix (divide by 100) on GW_B | -23.99% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | ist_utc | unit fix (divide by 100) on GW_C | -5.29% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.31% | altered | no | rejected: history would change |
| 198 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 198 | new_code | unit fix (divide by 100) on GW_A | -50.35% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.50% | altered | no | rejected: history would change |
| 198 | new_code | unit fix (divide by 100) on GW_B | -35.35% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.79% | altered | no | rejected: history would change |
| 198 | new_code | unit fix (divide by 100) on GW_C | -4.36% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.29% | altered | no | rejected: history would change |
| 198 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 198 | masked_pair | unit fix (divide by 100) on GW_A | -59.40% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.02% | altered | no | rejected: history would change |
| 198 | masked_pair | unit fix (divide by 100) on GW_B | -23.82% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 198 | masked_pair | unit fix (divide by 100) on GW_C | -5.33% | unchanged | yes | ACCEPTED |
| 198 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.33% | altered | no | rejected: history would change |
| 209 | unit_paise | divide GW_C by 10 instead of 100 | -74.63% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | unit_paise | divide GW_C by 1000 instead of 100 | -82.84% | unchanged | yes | ACCEPTED |
| 209 | unit_paise | divide GW_C by 100 on every day, not only tonight | -82.09% | altered | yes | rejected: history would change |
| 209 | unit_paise | unit fix (divide by 100) on GW_A | -8.89% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.45% | altered | no | rejected: history would change |
| 209 | unit_paise | unit fix (divide by 100) on GW_B | -6.38% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.33% | altered | no | rejected: history would change |
| 209 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -4.15% | altered | no | rejected: history would change |
| 209 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 209 | duplicate_load | unit fix (divide by 100) on GW_A | -49.53% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.59% | altered | no | rejected: history would change |
| 209 | duplicate_load | unit fix (divide by 100) on GW_B | -35.83% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.87% | altered | no | rejected: history would change |
| 209 | duplicate_load | unit fix (divide by 100) on GW_C | -4.52% | unchanged | yes | ACCEPTED |
| 209 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.24% | altered | no | rejected: history would change |
| 209 | join_fanout | unit fix (divide by 100) on GW_A | -49.63% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.51% | altered | no | rejected: history would change |
| 209 | join_fanout | unit fix (divide by 100) on GW_B | -35.59% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -1.91% | altered | no | rejected: history would change |
| 209 | join_fanout | unit fix (divide by 100) on GW_C | -4.59% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.23% | altered | no | rejected: history would change |
| 209 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 209 | stale_fx | unit fix (divide by 100) on GW_A | -54.62% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -2.78% | altered | no | rejected: history would change |
| 209 | stale_fx | unit fix (divide by 100) on GW_B | -39.21% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.05% | altered | no | rejected: history would change |
| 209 | stale_fx | unit fix (divide by 100) on GW_C | -5.04% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.26% | altered | no | rejected: history would change |
| 209 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 209 | ist_utc | unit fix (divide by 100) on GW_A | -58.75% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -2.99% | altered | no | rejected: history would change |
| 209 | ist_utc | unit fix (divide by 100) on GW_B | -23.97% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | ist_utc | unit fix (divide by 100) on GW_C | -5.43% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.27% | altered | no | rejected: history would change |
| 209 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 209 | new_code | unit fix (divide by 100) on GW_A | -49.90% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.49% | altered | no | rejected: history would change |
| 209 | new_code | unit fix (divide by 100) on GW_B | -35.63% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.71% | altered | no | rejected: history would change |
| 209 | new_code | unit fix (divide by 100) on GW_C | -4.57% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.17% | altered | no | rejected: history would change |
| 209 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 209 | masked_pair | unit fix (divide by 100) on GW_A | -58.59% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.02% | altered | yes | rejected: history would change |
| 209 | masked_pair | unit fix (divide by 100) on GW_B | -24.23% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 209 | masked_pair | unit fix (divide by 100) on GW_C | -5.35% | unchanged | yes | ACCEPTED |
| 209 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.28% | altered | yes | rejected: history would change |
| 220 | unit_paise | divide GW_C by 10 instead of 100 | -74.57% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | unit_paise | divide GW_C by 1000 instead of 100 | -82.78% | unchanged | yes | ACCEPTED |
| 220 | unit_paise | divide GW_C by 100 on every day, not only tonight | -82.03% | altered | yes | rejected: history would change |
| 220 | unit_paise | unit fix (divide by 100) on GW_A | -8.81% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.49% | altered | no | rejected: history would change |
| 220 | unit_paise | unit fix (divide by 100) on GW_B | -6.59% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.34% | altered | no | rejected: history would change |
| 220 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -5.58% | altered | no | rejected: history would change |
| 220 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 220 | duplicate_load | unit fix (divide by 100) on GW_A | -48.94% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.69% | altered | no | rejected: history would change |
| 220 | duplicate_load | unit fix (divide by 100) on GW_B | -36.72% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.91% | altered | no | rejected: history would change |
| 220 | duplicate_load | unit fix (divide by 100) on GW_C | -4.59% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.30% | altered | no | rejected: history would change |
| 220 | join_fanout | unit fix (divide by 100) on GW_A | -48.84% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.73% | altered | no | rejected: history would change |
| 220 | join_fanout | unit fix (divide by 100) on GW_B | -36.95% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -1.92% | altered | no | rejected: history would change |
| 220 | join_fanout | unit fix (divide by 100) on GW_C | -4.53% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.31% | altered | no | rejected: history would change |
| 220 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 220 | stale_fx | unit fix (divide by 100) on GW_A | -53.69% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -2.98% | altered | no | rejected: history would change |
| 220 | stale_fx | unit fix (divide by 100) on GW_B | -40.20% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.09% | altered | no | rejected: history would change |
| 220 | stale_fx | unit fix (divide by 100) on GW_C | -5.00% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.34% | altered | no | rejected: history would change |
| 220 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | yes | rejected: moves today's number only +0.00% |
| 220 | ist_utc | unit fix (divide by 100) on GW_A | -58.81% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.27% | altered | no | rejected: history would change |
| 220 | ist_utc | unit fix (divide by 100) on GW_B | -24.25% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | ist_utc | unit fix (divide by 100) on GW_C | -5.48% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.37% | altered | no | rejected: history would change |
| 220 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 220 | new_code | unit fix (divide by 100) on GW_A | -49.31% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.76% | altered | no | rejected: history would change |
| 220 | new_code | unit fix (divide by 100) on GW_B | -36.43% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.97% | altered | no | rejected: history would change |
| 220 | new_code | unit fix (divide by 100) on GW_C | -4.65% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.35% | altered | no | rejected: history would change |
| 220 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 220 | masked_pair | unit fix (divide by 100) on GW_A | -58.82% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.26% | altered | yes | rejected: history would change |
| 220 | masked_pair | unit fix (divide by 100) on GW_B | -24.26% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 220 | masked_pair | unit fix (divide by 100) on GW_C | -5.51% | unchanged | yes | ACCEPTED |
| 220 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.36% | altered | no | rejected: history would change |
| 231 | unit_paise | divide GW_C by 10 instead of 100 | -75.75% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | unit_paise | divide GW_C by 1000 instead of 100 | -84.09% | unchanged | yes | ACCEPTED |
| 231 | unit_paise | divide GW_C by 100 on every day, not only tonight | -83.33% | altered | yes | rejected: history would change |
| 231 | unit_paise | unit fix (divide by 100) on GW_A | -8.35% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.46% | altered | no | rejected: history would change |
| 231 | unit_paise | unit fix (divide by 100) on GW_B | -5.86% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.27% | altered | no | rejected: history would change |
| 231 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -4.63% | altered | no | rejected: history would change |
| 231 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 231 | duplicate_load | unit fix (divide by 100) on GW_A | -50.14% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.77% | altered | no | rejected: history would change |
| 231 | duplicate_load | unit fix (divide by 100) on GW_B | -35.24% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.68% | altered | no | rejected: history would change |
| 231 | duplicate_load | unit fix (divide by 100) on GW_C | -4.95% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.30% | altered | no | rejected: history would change |
| 231 | join_fanout | unit fix (divide by 100) on GW_A | -49.78% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.77% | altered | no | rejected: history would change |
| 231 | join_fanout | unit fix (divide by 100) on GW_B | -35.49% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -1.59% | altered | no | rejected: history would change |
| 231 | join_fanout | unit fix (divide by 100) on GW_C | -4.99% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.29% | altered | no | rejected: history would change |
| 231 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 231 | stale_fx | unit fix (divide by 100) on GW_A | -54.87% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -3.01% | altered | no | rejected: history would change |
| 231 | stale_fx | unit fix (divide by 100) on GW_B | -38.53% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -1.78% | altered | no | rejected: history would change |
| 231 | stale_fx | unit fix (divide by 100) on GW_C | -5.48% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.30% | altered | no | rejected: history would change |
| 231 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 231 | ist_utc | unit fix (divide by 100) on GW_A | -59.13% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.24% | altered | no | rejected: history would change |
| 231 | ist_utc | unit fix (divide by 100) on GW_B | -23.60% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | ist_utc | unit fix (divide by 100) on GW_C | -5.90% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.33% | altered | no | rejected: history would change |
| 231 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 231 | new_code | unit fix (divide by 100) on GW_A | -49.97% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.66% | altered | no | rejected: history would change |
| 231 | new_code | unit fix (divide by 100) on GW_B | -35.02% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.67% | altered | no | rejected: history would change |
| 231 | new_code | unit fix (divide by 100) on GW_C | -5.00% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.24% | altered | no | rejected: history would change |
| 231 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 231 | masked_pair | unit fix (divide by 100) on GW_A | -59.17% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.14% | altered | no | rejected: history would change |
| 231 | masked_pair | unit fix (divide by 100) on GW_B | -23.55% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 231 | masked_pair | unit fix (divide by 100) on GW_C | -5.86% | unchanged | yes | ACCEPTED |
| 231 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.34% | altered | no | rejected: history would change |
| 242 | unit_paise | divide GW_C by 10 instead of 100 | -74.02% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | unit_paise | divide GW_C by 1000 instead of 100 | -82.17% | unchanged | yes | ACCEPTED |
| 242 | unit_paise | divide GW_C by 100 on every day, not only tonight | -81.43% | altered | yes | rejected: history would change |
| 242 | unit_paise | unit fix (divide by 100) on GW_A | -9.28% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.57% | altered | no | rejected: history would change |
| 242 | unit_paise | unit fix (divide by 100) on GW_B | -6.62% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.32% | altered | no | rejected: history would change |
| 242 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -4.97% | altered | no | rejected: history would change |
| 242 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 242 | duplicate_load | unit fix (divide by 100) on GW_A | -49.82% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -3.03% | altered | no | rejected: history would change |
| 242 | duplicate_load | unit fix (divide by 100) on GW_B | -35.74% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.71% | altered | no | rejected: history would change |
| 242 | duplicate_load | unit fix (divide by 100) on GW_C | -4.40% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.26% | altered | no | rejected: history would change |
| 242 | join_fanout | unit fix (divide by 100) on GW_A | -50.10% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -3.02% | altered | no | rejected: history would change |
| 242 | join_fanout | unit fix (divide by 100) on GW_B | -35.51% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -1.77% | altered | no | rejected: history would change |
| 242 | join_fanout | unit fix (divide by 100) on GW_C | -4.38% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.28% | altered | no | rejected: history would change |
| 242 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 242 | stale_fx | unit fix (divide by 100) on GW_A | -54.89% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -3.38% | altered | no | rejected: history would change |
| 242 | stale_fx | unit fix (divide by 100) on GW_B | -39.17% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -1.91% | altered | no | rejected: history would change |
| 242 | stale_fx | unit fix (divide by 100) on GW_C | -4.82% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.29% | altered | no | rejected: history would change |
| 242 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 242 | ist_utc | unit fix (divide by 100) on GW_A | -59.29% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.65% | altered | no | rejected: history would change |
| 242 | ist_utc | unit fix (divide by 100) on GW_B | -23.80% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | ist_utc | unit fix (divide by 100) on GW_C | -5.20% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.32% | altered | no | rejected: history would change |
| 242 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 242 | new_code | unit fix (divide by 100) on GW_A | -49.79% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.95% | altered | no | rejected: history would change |
| 242 | new_code | unit fix (divide by 100) on GW_B | -35.61% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.85% | altered | no | rejected: history would change |
| 242 | new_code | unit fix (divide by 100) on GW_C | -4.48% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.24% | altered | no | rejected: history would change |
| 242 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 242 | masked_pair | unit fix (divide by 100) on GW_A | -59.10% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.68% | altered | yes | rejected: history would change |
| 242 | masked_pair | unit fix (divide by 100) on GW_B | -24.18% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 242 | masked_pair | unit fix (divide by 100) on GW_C | -5.23% | unchanged | yes | ACCEPTED |
| 242 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.31% | altered | no | rejected: history would change |
| 253 | unit_paise | divide GW_C by 10 instead of 100 | -74.00% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | unit_paise | divide GW_C by 1000 instead of 100 | -82.14% | unchanged | yes | ACCEPTED |
| 253 | unit_paise | divide GW_C by 100 on every day, not only tonight | -81.40% | altered | yes | rejected: history would change |
| 253 | unit_paise | unit fix (divide by 100) on GW_A | -9.23% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.48% | altered | no | rejected: history would change |
| 253 | unit_paise | unit fix (divide by 100) on GW_B | -6.59% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.36% | altered | no | rejected: history would change |
| 253 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -5.07% | altered | no | rejected: history would change |
| 253 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 253 | duplicate_load | unit fix (divide by 100) on GW_A | -49.66% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.60% | altered | no | rejected: history would change |
| 253 | duplicate_load | unit fix (divide by 100) on GW_B | -35.51% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.97% | altered | no | rejected: history would change |
| 253 | duplicate_load | unit fix (divide by 100) on GW_C | -4.36% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.26% | altered | no | rejected: history would change |
| 253 | join_fanout | unit fix (divide by 100) on GW_A | -49.28% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.62% | altered | no | rejected: history would change |
| 253 | join_fanout | unit fix (divide by 100) on GW_B | -35.66% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -2.06% | altered | no | rejected: history would change |
| 253 | join_fanout | unit fix (divide by 100) on GW_C | -4.37% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.30% | altered | no | rejected: history would change |
| 253 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 253 | stale_fx | unit fix (divide by 100) on GW_A | -54.85% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -2.86% | altered | no | rejected: history would change |
| 253 | stale_fx | unit fix (divide by 100) on GW_B | -39.18% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.15% | altered | no | rejected: history would change |
| 253 | stale_fx | unit fix (divide by 100) on GW_C | -4.84% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.30% | altered | no | rejected: history would change |
| 253 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 253 | ist_utc | unit fix (divide by 100) on GW_A | -58.79% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.07% | altered | no | rejected: history would change |
| 253 | ist_utc | unit fix (divide by 100) on GW_B | -23.70% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | ist_utc | unit fix (divide by 100) on GW_C | -5.19% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.32% | altered | no | rejected: history would change |
| 253 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 253 | new_code | unit fix (divide by 100) on GW_A | -49.70% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.64% | altered | no | rejected: history would change |
| 253 | new_code | unit fix (divide by 100) on GW_B | -35.39% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | new_code | clock fix (shift back 5.5 hours) on GW_B | -2.06% | altered | no | rejected: history would change |
| 253 | new_code | unit fix (divide by 100) on GW_C | -4.56% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.28% | altered | no | rejected: history would change |
| 253 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 253 | masked_pair | unit fix (divide by 100) on GW_A | -58.91% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.08% | altered | yes | rejected: history would change |
| 253 | masked_pair | unit fix (divide by 100) on GW_B | -23.68% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 253 | masked_pair | unit fix (divide by 100) on GW_C | -5.06% | unchanged | yes | ACCEPTED |
| 253 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.29% | altered | no | rejected: history would change |
| 264 | unit_paise | divide GW_C by 10 instead of 100 | -74.29% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | unit_paise | divide GW_C by 1000 instead of 100 | -82.47% | unchanged | yes | ACCEPTED |
| 264 | unit_paise | divide GW_C by 100 on every day, not only tonight | -81.72% | altered | yes | rejected: history would change |
| 264 | unit_paise | unit fix (divide by 100) on GW_A | -9.05% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.50% | altered | no | rejected: history would change |
| 264 | unit_paise | unit fix (divide by 100) on GW_B | -6.55% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.34% | altered | no | rejected: history would change |
| 264 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -3.98% | altered | no | rejected: history would change |
| 264 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 264 | duplicate_load | unit fix (divide by 100) on GW_A | -49.65% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.79% | altered | no | rejected: history would change |
| 264 | duplicate_load | unit fix (divide by 100) on GW_B | -35.67% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.90% | altered | no | rejected: history would change |
| 264 | duplicate_load | unit fix (divide by 100) on GW_C | -4.46% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.20% | altered | no | rejected: history would change |
| 264 | join_fanout | unit fix (divide by 100) on GW_A | -49.29% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.68% | altered | no | rejected: history would change |
| 264 | join_fanout | unit fix (divide by 100) on GW_B | -36.08% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -1.99% | altered | no | rejected: history would change |
| 264 | join_fanout | unit fix (divide by 100) on GW_C | -4.44% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.24% | altered | no | rejected: history would change |
| 264 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 264 | stale_fx | unit fix (divide by 100) on GW_A | -54.51% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -2.99% | altered | no | rejected: history would change |
| 264 | stale_fx | unit fix (divide by 100) on GW_B | -39.44% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.05% | altered | no | rejected: history would change |
| 264 | stale_fx | unit fix (divide by 100) on GW_C | -4.92% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.24% | altered | no | rejected: history would change |
| 264 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 264 | ist_utc | unit fix (divide by 100) on GW_A | -58.79% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.22% | altered | no | rejected: history would change |
| 264 | ist_utc | unit fix (divide by 100) on GW_B | -23.99% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | ist_utc | unit fix (divide by 100) on GW_C | -5.31% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.26% | altered | no | rejected: history would change |
| 264 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 264 | new_code | unit fix (divide by 100) on GW_A | -49.59% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.92% | altered | no | rejected: history would change |
| 264 | new_code | unit fix (divide by 100) on GW_B | -35.89% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.95% | altered | no | rejected: history would change |
| 264 | new_code | unit fix (divide by 100) on GW_C | -4.57% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.20% | altered | no | rejected: history would change |
| 264 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 264 | masked_pair | unit fix (divide by 100) on GW_A | -58.76% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.25% | altered | yes | rejected: history would change |
| 264 | masked_pair | unit fix (divide by 100) on GW_B | -24.13% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 264 | masked_pair | unit fix (divide by 100) on GW_C | -5.28% | unchanged | yes | ACCEPTED |
| 264 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.23% | altered | no | rejected: history would change |
| 275 | unit_paise | divide GW_C by 10 instead of 100 | -75.64% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | unit_paise | divide GW_C by 1000 instead of 100 | -83.96% | unchanged | yes | ACCEPTED |
| 275 | unit_paise | divide GW_C by 100 on every day, not only tonight | -83.21% | altered | yes | rejected: history would change |
| 275 | unit_paise | unit fix (divide by 100) on GW_A | -8.26% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | unit_paise | clock fix (shift back 5.5 hours) on GW_A | -0.47% | altered | no | rejected: history would change |
| 275 | unit_paise | unit fix (divide by 100) on GW_B | -5.98% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | unit_paise | clock fix (shift back 5.5 hours) on GW_B | -0.31% | altered | no | rejected: history would change |
| 275 | unit_paise | clock fix (shift back 5.5 hours) on GW_C | -4.42% | altered | no | rejected: history would change |
| 275 | unit_paise | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 275 | duplicate_load | unit fix (divide by 100) on GW_A | -49.28% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | duplicate_load | clock fix (shift back 5.5 hours) on GW_A | -2.81% | altered | no | rejected: history would change |
| 275 | duplicate_load | unit fix (divide by 100) on GW_B | -35.55% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | duplicate_load | clock fix (shift back 5.5 hours) on GW_B | -1.80% | altered | no | rejected: history would change |
| 275 | duplicate_load | unit fix (divide by 100) on GW_C | -4.94% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | duplicate_load | clock fix (shift back 5.5 hours) on GW_C | -0.28% | altered | no | rejected: history would change |
| 275 | join_fanout | unit fix (divide by 100) on GW_A | -49.25% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | join_fanout | clock fix (shift back 5.5 hours) on GW_A | -2.78% | altered | no | rejected: history would change |
| 275 | join_fanout | unit fix (divide by 100) on GW_B | -35.44% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | join_fanout | clock fix (shift back 5.5 hours) on GW_B | -1.79% | altered | no | rejected: history would change |
| 275 | join_fanout | unit fix (divide by 100) on GW_C | -5.02% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | join_fanout | clock fix (shift back 5.5 hours) on GW_C | -0.26% | altered | no | rejected: history would change |
| 275 | join_fanout | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 275 | stale_fx | unit fix (divide by 100) on GW_A | -54.18% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | stale_fx | clock fix (shift back 5.5 hours) on GW_A | -3.10% | altered | no | rejected: history would change |
| 275 | stale_fx | unit fix (divide by 100) on GW_B | -39.24% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | stale_fx | clock fix (shift back 5.5 hours) on GW_B | -2.03% | altered | no | rejected: history would change |
| 275 | stale_fx | unit fix (divide by 100) on GW_C | -5.46% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | stale_fx | clock fix (shift back 5.5 hours) on GW_C | -0.29% | altered | no | rejected: history would change |
| 275 | stale_fx | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 275 | ist_utc | unit fix (divide by 100) on GW_A | -58.25% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | ist_utc | clock fix (shift back 5.5 hours) on GW_A | -3.33% | altered | no | rejected: history would change |
| 275 | ist_utc | unit fix (divide by 100) on GW_B | -23.88% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | ist_utc | unit fix (divide by 100) on GW_C | -5.87% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | ist_utc | clock fix (shift back 5.5 hours) on GW_C | -0.31% | altered | no | rejected: history would change |
| 275 | ist_utc | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 275 | new_code | unit fix (divide by 100) on GW_A | -49.12% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | new_code | clock fix (shift back 5.5 hours) on GW_A | -2.70% | altered | no | rejected: history would change |
| 275 | new_code | unit fix (divide by 100) on GW_B | -35.37% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | new_code | clock fix (shift back 5.5 hours) on GW_B | -1.83% | altered | no | rejected: history would change |
| 275 | new_code | unit fix (divide by 100) on GW_C | -5.04% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | new_code | clock fix (shift back 5.5 hours) on GW_C | -0.30% | altered | no | rejected: history would change |
| 275 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 275 | masked_pair | unit fix (divide by 100) on GW_A | -58.57% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -3.49% | altered | yes | rejected: history would change |
| 275 | masked_pair | unit fix (divide by 100) on GW_B | -23.83% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 275 | masked_pair | unit fix (divide by 100) on GW_C | -5.87% | unchanged | yes | ACCEPTED |
| 275 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.35% | altered | no | rejected: history would change |

## Every accepted wrong fix, by seed

| Seed | Scenario | Kind | Wrong fix | Move | History | Verdict of the run |
|---|---|---|---|---|---|---|
| 11 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.41% | UNCHANGED | PROVEN_FAULT |
| 22 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -83.06% | UNCHANGED | PROVEN_FAULT |
| 22 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.46% | UNCHANGED | PROVEN_FAULT |
| 33 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -82.88% | UNCHANGED | PROVEN_FAULT |
| 33 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.55% | UNCHANGED | PROVEN_FAULT |
| 44 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -83.76% | UNCHANGED | PROVEN_FAULT |
| 44 | duplicate_load | different_cause | unit fix (divide by 100) on GW_C | -4.92% | UNCHANGED | PROVEN_FAULT |
| 44 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.90% | UNCHANGED | PROVEN_FAULT |
| 55 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -82.98% | UNCHANGED | PROVEN_FAULT |
| 55 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.47% | UNCHANGED | PROVEN_FAULT |
| 66 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -83.23% | UNCHANGED | PROVEN_FAULT |
| 66 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.59% | UNCHANGED | PROVEN_FAULT |
| 77 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -81.68% | UNCHANGED | PROVEN_FAULT |
| 77 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -4.86% | UNCHANGED | PROVEN_FAULT |
| 88 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.17% | UNCHANGED | PROVEN_FAULT |
| 99 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -82.63% | UNCHANGED | PROVEN_FAULT |
| 99 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.38% | UNCHANGED | PROVEN_FAULT |
| 110 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -83.01% | UNCHANGED | PROVEN_FAULT |
| 110 | duplicate_load | different_cause | unit fix (divide by 100) on GW_C | -4.58% | UNCHANGED | PROVEN_FAULT |
| 110 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.38% | UNCHANGED | PROVEN_FAULT |
| 121 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -81.93% | UNCHANGED | PROVEN_FAULT |
| 121 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.02% | UNCHANGED | PROVEN_FAULT |
| 132 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.72% | UNCHANGED | PROVEN_FAULT |
| 143 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -81.82% | UNCHANGED | PROVEN_FAULT |
| 143 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.21% | UNCHANGED | PROVEN_FAULT |
| 154 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.67% | UNCHANGED | PROVEN_FAULT |
| 165 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.43% | UNCHANGED | PROVEN_FAULT |
| 176 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.38% | UNCHANGED | PROVEN_FAULT |
| 187 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.85% | UNCHANGED | PROVEN_FAULT |
| 198 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -82.47% | UNCHANGED | PROVEN_FAULT |
| 198 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.33% | UNCHANGED | PROVEN_FAULT |
| 209 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -82.84% | UNCHANGED | PROVEN_FAULT |
| 209 | duplicate_load | different_cause | unit fix (divide by 100) on GW_C | -4.52% | UNCHANGED | PROVEN_FAULT |
| 209 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.35% | UNCHANGED | PROVEN_FAULT |
| 220 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -82.78% | UNCHANGED | PROVEN_FAULT |
| 220 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.51% | UNCHANGED | PROVEN_FAULT |
| 231 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -84.09% | UNCHANGED | PROVEN_FAULT |
| 231 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.86% | UNCHANGED | PROVEN_FAULT |
| 242 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -82.17% | UNCHANGED | PROVEN_FAULT |
| 242 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.23% | UNCHANGED | PROVEN_FAULT |
| 253 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -82.14% | UNCHANGED | PROVEN_FAULT |
| 253 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.06% | UNCHANGED | PROVEN_FAULT |
| 264 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -82.47% | UNCHANGED | PROVEN_FAULT |
| 264 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.28% | UNCHANGED | PROVEN_FAULT |
| 275 | unit_paise | wrong_factor | divide GW_C by 1000 instead of 100 | -83.96% | UNCHANGED | PROVEN_FAULT |
| 275 | masked_pair | different_cause | unit fix (divide by 100) on GW_C | -5.87% | UNCHANGED | PROVEN_FAULT |
