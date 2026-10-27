# Wrong-fix control

Is the undo test circular? For every scenario with a planted fault, the gate's own rules are shown corrections that are deliberately wrong: the right fix on the wrong gateway, the wrong factor, the right fix applied to every day instead of tonight, or the fix for a cause that was not planted. A wrong fix is **accepted** if it moves today's number by at least 1.5%, keeps history as published and lands inside the normal range, which is what the gate needs to confirm a cause.

On Exasol 2026.2.0-nano.3, 20,000 orders a day, seeds 11, 22, 33, 44, 55. Generated 2026-10-27 21:52:37 in 615 s. Reproduce: `receipts wrongfix --backend exasol --seeds 11 22 33 44 55 --orders-per-day 20000`.

**Wrong fixes tried 235, rejected 225, accepted 10.**

| Kind of wrong fix | Tried | Rejected | Accepted |
|---|---|---|---|
| wrong factor | 10 | 6 | 4 |
| every day | 5 | 5 | 0 |
| wrong gateway | 30 | 30 | 0 |
| different cause | 190 | 184 | 6 |

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
| 55 | new_code | remove duplicate payments in tonight's batch | +0.00% | unchanged | no | rejected: moves today's number only +0.00% |
| 55 | masked_pair | unit fix (divide by 100) on GW_A | -59.64% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | masked_pair | clock fix (shift back 5.5 hours) on GW_A | -2.99% | altered | yes | rejected: history would change |
| 55 | masked_pair | unit fix (divide by 100) on GW_B | -23.66% | unchanged | no | rejected: the corrected number is still outside the normal range |
| 55 | masked_pair | unit fix (divide by 100) on GW_C | -5.47% | unchanged | yes | ACCEPTED |
| 55 | masked_pair | clock fix (shift back 5.5 hours) on GW_C | -0.27% | altered | no | rejected: history would change |
