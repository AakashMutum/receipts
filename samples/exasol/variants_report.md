# Held-out fault variants

17 variants x 1 seeds, 8,000 orders a day, backend exasol. Written after the detectors were fixed. See `receipts/variants.py`.

caught 15, held 1, small (published, under 4% error) 1, **published a wrong number 0** of 17 runs.

| Variant | Real error | Outcome | Verdict | Causes named |
|---|---|---|---|---|
| Unit change x10 on GW_B | +334.9% | caught | PROVEN_FAULT | unit_scale |
| Unit change x1000 on GW_C | +4434.0% | caught | PROVEN_FAULT | unit_scale |
| Unit change x100 on GW_A (largest gateway) | +4967.9% | caught | PROVEN_FAULT | unit_scale |
| Unit change x100 on 25% of GW_A rows | +1310.2% | caught | PROVEN_FAULT | unit_scale |
| Unit change x100 on 5% of GW_A rows | +274.3% | caught | PROVEN_FAULT | unit_scale |
| Three payment files loaded twice | +38.4% | caught | PROVEN_FAULT | duplicate_key |
| Two other files loaded twice | +25.3% | caught | PROVEN_FAULT | duplicate_key |
| A quarter of one file loaded twice | +3.6% | caught | PROVEN_FAULT | duplicate_key |
| IST written as UTC on GW_A (largest gateway) | -22.2% | caught | PROVEN_FAULT | clock_shift |
| IST written as UTC on GW_C (smallest gateway) | -1.9% | caught | PROVEN_FAULT | clock_shift |
| One hour clock shift on GW_B | -1.5% | small | NO_INCIDENT | none |
| Twelve hour clock shift on GW_B | -29.2% | held | UNEXPLAINED | none |
| New code on 10% of Electronics orders | -3.6% | caught | PROVEN_FAULT | orphan_code |
| New code for all Fashion orders | -23.7% | caught | PROVEN_FAULT | orphan_code |
| Merchant table fans out for 5% of merchants | +3.9% | caught | PROVEN_FAULT | key_fanout |
| Merchant table fans out for 40% of merchants | +37.7% | caught | PROVEN_FAULT | key_fanout |
| Two faults at once: paise on GW_C and a file loaded twice | +524.3% | caught | PROVEN_FAULT | duplicate_key,unit_scale |
