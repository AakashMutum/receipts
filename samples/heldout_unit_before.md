# Held-out partial unit errors, before the fix

Partial unit errors written before the fix and frozen: factors x10 and x1000, gateways GW_A and GW_B, 2, 5 and 10 percent of the gateway's payments, seeds 21 and 22. Run on synthetic data only.

On the DuckDB stand-in, 20,000 orders a day. Generated 2026-10-26 01:27:01 in 1 minutes. Reproduce: `receipts heldout --backend duckdb --seeds 21 22 --orders-per-day 20000`.

**24 cases: caught 0, held without a proven cause 24, published under 4% off 0, wrong cause named 0, published a number more than 4% off 0.**

| Seed | Gateway | Factor | Share | Outcome | Verdict | Causes named | Error |
|---|---|---|---|---|---|---|---|
| 21 | GW_A | x10 | 2% | held | UNEXPLAINED | none | +8.68% |
| 21 | GW_A | x10 | 5% | held | UNEXPLAINED | none | +21.89% |
| 21 | GW_A | x10 | 10% | held | UNEXPLAINED | none | +42.74% |
| 21 | GW_A | x1000 | 2% | held | UNEXPLAINED | none | +962.97% |
| 21 | GW_A | x1000 | 5% | held | UNEXPLAINED | none | +2429.97% |
| 21 | GW_A | x1000 | 10% | held | UNEXPLAINED | none | +4743.92% |
| 21 | GW_B | x10 | 2% | held | UNEXPLAINED | none | +7.41% |
| 21 | GW_B | x10 | 5% | held | UNEXPLAINED | none | +17.27% |
| 21 | GW_B | x10 | 10% | held | UNEXPLAINED | none | +30.78% |
| 21 | GW_B | x1000 | 2% | held | UNEXPLAINED | none | +822.31% |
| 21 | GW_B | x1000 | 5% | held | UNEXPLAINED | none | +1917.18% |
| 21 | GW_B | x1000 | 10% | held | UNEXPLAINED | none | +3416.32% |
| 22 | GW_A | x10 | 2% | held | UNEXPLAINED | none | +8.36% |
| 22 | GW_A | x10 | 5% | held | UNEXPLAINED | none | +21.91% |
| 22 | GW_A | x10 | 10% | held | UNEXPLAINED | none | +45.12% |
| 22 | GW_A | x1000 | 2% | held | UNEXPLAINED | none | +928.46% |
| 22 | GW_A | x1000 | 5% | held | UNEXPLAINED | none | +2431.48% |
| 22 | GW_A | x1000 | 10% | held | UNEXPLAINED | none | +5008.66% |
| 22 | GW_B | x10 | 2% | held | UNEXPLAINED | none | +6.69% |
| 22 | GW_B | x10 | 5% | held | UNEXPLAINED | none | +16.13% |
| 22 | GW_B | x10 | 10% | held | UNEXPLAINED | none | +31.24% |
| 22 | GW_B | x1000 | 2% | held | UNEXPLAINED | none | +742.30% |
| 22 | GW_B | x1000 | 5% | held | UNEXPLAINED | none | +1790.13% |
| 22 | GW_B | x1000 | 10% | held | UNEXPLAINED | none | +3468.03% |

Outcomes: `caught` proven, right cause; `held` held, nothing proven; `held_partial` held, part of the cause proven; `wrong_cause` a cause that was not planted was named; `small` published, under 4% off; `WRONG` published a number more than 4% off.
