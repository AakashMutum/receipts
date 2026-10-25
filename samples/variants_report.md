# Held-out fault variants

17 variants x 2 seeds, 8,000 orders a day, backend duckdb. Written after the detectors were fixed. See `receipts/variants.py`.

caught 30, held 2, small (published, under 4% error) 2, **published a wrong number 0** of 34 runs.

| Variant | Real error | Outcome | Verdict | Causes named |
|---|---|---|---|---|
| Unit change x10 on GW_B | +327.4% to +334.9% | caught | PROVEN_FAULT | unit_scale |
| Unit change x1000 on GW_C | +4390.5% to +4434.0% | caught | PROVEN_FAULT | unit_scale |
| Unit change x100 on GW_A (largest gateway) | +4967.9% to +5021.4% | caught | PROVEN_FAULT | unit_scale |
| Unit change x100 on 25% of GW_A rows | +1293.1% to +1310.2% | caught | PROVEN_FAULT | unit_scale |
| Unit change x100 on 5% of GW_A rows | +239.8% to +274.3% | caught | PROVEN_FAULT | unit_scale |
| Three payment files loaded twice | +37.9% to +38.4% | caught | PROVEN_FAULT | duplicate_key |
| Two other files loaded twice | +24.2% to +25.3% | caught | PROVEN_FAULT | duplicate_key |
| A quarter of one file loaded twice | +3.1% to +3.6% | caught | PROVEN_FAULT | duplicate_key |
| IST written as UTC on GW_A (largest gateway) | -22.5% to -22.2% | caught | PROVEN_FAULT | clock_shift |
| IST written as UTC on GW_C (smallest gateway) | -2.2% to -1.9% | caught | PROVEN_FAULT | clock_shift |
| One hour clock shift on GW_B | -1.5% to -1.4% | small | NO_INCIDENT | none |
| Twelve hour clock shift on GW_B | -29.2% to -28.6% | held | UNEXPLAINED | none |
| New code on 10% of Electronics orders | -3.6% to -3.4% | caught | PROVEN_FAULT | orphan_code |
| New code for all Fashion orders | -23.7% to -22.4% | caught | PROVEN_FAULT | orphan_code |
| Merchant table fans out for 5% of merchants | +3.9% to +4.0% | caught | PROVEN_FAULT | key_fanout |
| Merchant table fans out for 40% of merchants | +37.7% to +39.8% | caught | PROVEN_FAULT | key_fanout |
| Two faults at once: paise on GW_C and a file loaded twice | +497.6% to +524.3% | caught | PROVEN_FAULT | duplicate_key,unit_scale |
