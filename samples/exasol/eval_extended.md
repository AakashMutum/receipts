# Receipts evaluation, extended to 25 seeds

250 runs: 10 scenarios x 25 seeds (20,000 orders a day, 42 days of history, backend exasol). Generated 2026-10-31 02:42:26.

**Receipts passed 250 of 250 runs** (right verdict and exactly the right causes).

| System | Hold decision right | Cause precision | Cause recall | Wrong causes named | Causes missed |
|---|---|---|---|---|---|
| Receipts | 100% | 100% | 100% | 0 | 0 |
| Detectors only (ablation, no undo test) | 80% | 89% | 100% | 25 | 0 |
| Threshold alert (typical monitor) | 87% | 100% | 0% | 0 | 200 |

Corrected value after the proven fix, against the true clean value: mean error 0.001%, max 0.017%.
Gate latency per run: median 2835 ms, max 6891 ms.

## Extended run

Seeds 11, 22, 33, 44, 55, 66, 77, 88, 99, 110, 121, 132, 143, 154, 165, 176, 187, 198, 209, 220, 231, 242, 253, 264, 275: the five seeds of [`eval_report.md`](eval_report.md) (11 to 55) and 20 more, with the same generator settings (20,000 orders a day, 42 days of history), the same scenarios and the same scoring. Each seed was run on its own and saved as it finished ([`scripts/evidence_seeds.py`](../../scripts/evidence_seeds.py)). Time on Exasol: 46 minutes in all.

Runs that did not pass: none.

## The same runs on the DuckDB stand-in

* Seeds run on the stand-in: 25 of 25; runs passed there: 250 of 250.
* Runs compared one by one: 250; same verdict and same causes: **250 of 250**.
* Runs that differ: none.
* The stand-in seeds ran on 30 October at version 1.0.0; the Exasol seeds ran on 31 October after the fix for a weekday with no trading history. That fix changes no number here: the five seeds of `eval_report.md`, run again before and after it on both backends, gave the published numbers each time.

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
| healthy | 33 | +3.2% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 33 | +26.7% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 33 | +477.9% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 33 | +16.2% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 33 | +24.1% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 33 | -6.2% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 33 | -14.1% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 33 | -14.1% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 33 | +7.9% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 33 | -7.6% | UNEXPLAINED | UNEXPLAINED | - | yes |
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
| healthy | 66 | -0.1% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 66 | +22.7% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 66 | +470.1% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 66 | +12.5% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 66 | +20.8% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 66 | -8.9% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 66 | -15.7% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 66 | -17.3% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 66 | +5.6% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 66 | -10.4% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 77 | -0.0% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 77 | +22.8% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 77 | +424.7% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 77 | +12.9% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 77 | +29.1% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 77 | -8.7% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 77 | -16.0% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 77 | -16.9% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 77 | +5.6% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 77 | -10.4% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 88 | -2.8% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 88 | +20.1% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 88 | +432.4% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 88 | +9.5% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 88 | +17.7% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 88 | -11.9% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 88 | -18.4% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 88 | -19.4% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 88 | +1.4% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 88 | -13.2% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 99 | +0.9% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 99 | +23.7% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 99 | +457.4% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 99 | +13.0% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 99 | +21.0% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 99 | -8.2% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 99 | -15.3% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 99 | -16.6% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 99 | +5.2% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 99 | -9.4% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 110 | -1.5% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 110 | +21.2% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 110 | +455.6% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 110 | +10.8% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 110 | +11.2% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 110 | -10.3% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 110 | -16.7% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 110 | -19.2% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 110 | +4.4% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 110 | -11.6% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 121 | +0.9% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 121 | +23.8% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 121 | +436.6% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 121 | +13.6% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 121 | +29.4% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 121 | -8.5% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 121 | -15.0% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 121 | -16.7% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 121 | +6.2% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 121 | -10.0% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 132 | -0.1% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 132 | +22.9% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 132 | +473.6% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 132 | +12.1% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 132 | +16.0% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 132 | -8.9% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 132 | -15.6% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 132 | -17.0% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 132 | +5.1% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 132 | -10.1% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 143 | +4.4% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 143 | +27.4% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 143 | +451.8% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 143 | +17.6% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 143 | +25.1% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 143 | -5.1% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 143 | -12.7% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 143 | -13.9% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 143 | +9.2% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 143 | -6.4% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 154 | -0.4% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 154 | +22.2% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 154 | +470.9% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 154 | +12.3% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 154 | +19.0% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 154 | -9.2% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 154 | -16.5% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 154 | -17.2% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 154 | +4.8% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 154 | -10.8% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 165 | -0.7% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 165 | +22.5% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 165 | +458.4% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 165 | +11.7% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 165 | +19.5% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 165 | -9.7% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 165 | -16.4% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 165 | -18.5% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 165 | +4.2% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 165 | -10.8% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 176 | -0.7% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 176 | +22.2% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 176 | +441.9% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 176 | +11.7% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 176 | +18.5% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 176 | -9.2% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 176 | -17.2% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 176 | -17.2% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 176 | +3.7% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 176 | -10.8% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 187 | +0.1% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 187 | +23.4% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 187 | +489.4% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 187 | +12.4% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 187 | +20.8% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 187 | -8.8% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 187 | -15.8% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 187 | -17.3% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 187 | +5.5% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 187 | -10.6% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 198 | +2.6% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 198 | +25.9% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 198 | +461.4% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 198 | +16.0% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 198 | +27.6% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 198 | -6.4% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 198 | -13.3% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 198 | -15.2% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 198 | +9.0% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 198 | -7.8% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 209 | -1.2% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 209 | +21.8% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 209 | +451.8% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 209 | +11.3% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 209 | +19.6% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 209 | -10.2% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 209 | -16.5% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 209 | -18.3% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 209 | +4.5% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 209 | -11.6% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 220 | +3.6% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 220 | +27.0% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 220 | +476.5% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 220 | +16.8% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 220 | +23.8% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 220 | -5.4% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 220 | -13.7% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 220 | -13.0% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 220 | +8.1% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 220 | -6.8% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 231 | +3.9% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 231 | +26.5% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 231 | +523.4% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 231 | +17.0% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 231 | +28.1% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 231 | -5.2% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 231 | -12.0% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 231 | -14.3% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 231 | +9.9% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 231 | -6.8% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 242 | +1.2% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 242 | +24.0% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 242 | +444.7% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 242 | +13.4% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 242 | +18.6% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 242 | -7.9% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 242 | -14.8% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 242 | -16.1% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 242 | +6.5% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 242 | -8.8% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 253 | +0.4% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 253 | +23.2% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 253 | +440.1% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 253 | +13.5% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 253 | +32.2% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 253 | -9.1% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 253 | -15.2% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 253 | -17.1% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 253 | +5.9% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 253 | -9.8% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 264 | +1.3% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 264 | +24.3% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 264 | +454.1% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 264 | +13.5% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 264 | +22.1% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 264 | -8.0% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 264 | -14.7% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 264 | -15.8% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 264 | +5.9% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 264 | -9.0% | UNEXPLAINED | UNEXPLAINED | - | yes |
| healthy | 275 | +1.2% | NO_INCIDENT | NO_INCIDENT | - | yes |
| festival | 275 | +24.8% | REAL_CHANGE | REAL_CHANGE | - | yes |
| unit_paise | 275 | +502.6% | PROVEN_FAULT | PROVEN_FAULT | unit_scale | yes |
| duplicate_load | 275 | +13.7% | PROVEN_FAULT | PROVEN_FAULT | duplicate_key | yes |
| join_fanout | 275 | +18.1% | PROVEN_FAULT | PROVEN_FAULT | key_fanout | yes |
| stale_fx | 275 | -8.2% | PROVEN_FAULT | PROVEN_FAULT | stale_feed | yes |
| ist_utc | 275 | -14.6% | PROVEN_FAULT | PROVEN_FAULT | clock_shift | yes |
| new_code | 275 | -16.3% | PROVEN_FAULT | PROVEN_FAULT | orphan_code | yes |
| masked_pair | 275 | +7.0% | PROVEN_FAULT | PROVEN_FAULT | clock_shift, duplicate_key | yes |
| unknown_discount | 275 | -9.3% | UNEXPLAINED | UNEXPLAINED | - | yes |

## What the rows mean

* **Hold decision right**: faulty batches held, healthy and genuinely changed batches published.
* **Detectors only** is the ablation. It names every check that fired. On the festival day the retry burst trips the duplicate check, so it blames a fault that is not there. The undo test removes it.
* **Threshold alert** never names a cause and holds the real festival surge. On the masked pair it holds the number without a cause when the net move leaves the normal range, and stays silent when it does not.
* The unknown fault has no detector by design. The right answer is UNEXPLAINED (held, no cause named), and that is what is scored.

## Wrong-fix control

Deliberately wrong corrections for every planted fault (wrong gateway, wrong factor, every day instead of tonight, or the fix for another cause), judged by the gate's own rules: tried 1175, rejected 1129, accepted 46.

* Accepted: unit fix (divide by 100) on GW_C (-5.41%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-83.06%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-5.46%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-82.88%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-5.55%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-83.76%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-4.92%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_C (-5.90%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-82.98%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-5.47%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-83.23%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-5.59%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-81.68%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-4.86%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: unit fix (divide by 100) on GW_C (-5.17%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-82.63%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-5.38%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-83.01%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-4.58%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_C (-5.38%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-81.93%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-5.02%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: unit fix (divide by 100) on GW_C (-5.72%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-81.82%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-5.21%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: unit fix (divide by 100) on GW_C (-5.67%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: unit fix (divide by 100) on GW_C (-5.43%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: unit fix (divide by 100) on GW_C (-5.38%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: unit fix (divide by 100) on GW_C (-5.85%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-82.47%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-5.33%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-82.84%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-4.52%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed duplicate_key.
* Accepted: unit fix (divide by 100) on GW_C (-5.35%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-82.78%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-5.51%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-84.09%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-5.86%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-82.17%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-5.23%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-82.14%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-5.06%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-82.47%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-5.28%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
* Accepted: divide GW_C by 1000 instead of 100 (-83.96%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed unit_scale.
* Accepted: unit fix (divide by 100) on GW_C (-5.87%, history unchanged, in range); gate verdict PROVEN_FAULT, confirmed clock_shift, duplicate_key.
