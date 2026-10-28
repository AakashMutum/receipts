# Evaluation card

One page on what Receipts was tested on, what came out, and what is not claimed. Every number links to an
unedited report in `samples/`. Platform: Exasol Personal 2026.2.0-nano.3 on a Windows 11 laptop (Intel
Core 5, Podman on WSL2, about 7.7 GiB visible to the VM), unless a line says the DuckDB stand-in.

## Scope

* **One metric:** daily revenue, built by a chain of six views from raw payments, orders and three reference
  tables. **Six fault classes** with a detector each: unit change, duplicate rows, join fan-out, stale FX
  feed, clock shift (a Python UDF inside Exasol) and unmapped codes.
* **The decision:** hold or publish tonight's number, and name the cause only if undoing it in a sandbox puts
  the number back in range with published history unchanged. Verdicts: NO_INCIDENT, REAL_CHANGE (published),
  PROVEN_FAULT, UNEXPLAINED (held).
* No thresholds were changed for any test on this page. One detector was extended after the red team found a
  hole (the unit tail check, below); every test was re-run after it on Exasol, the real-data backtest
  included.

## Data

| Data | What it is |
|---|---|
| Synthetic marketplace | Seeded generator: 8 cities, 6 categories, 4 gateways, a USD slice with daily FX, evening-heavy shopping in IST, background payment retries; 42 days of history plus the incoming day. Faults are SQL in `receipts/faults.py`, which the engine never imports |
| NYC TLC yellow taxi trips | Public, Jan to Mar 2024, 9,554,757 trips, mapped onto the same tables by an adapter (`receipts/backtest.py`) |

## Results

| Test | Result | Report |
|---|---|---|
| Scored evaluation, 10 scenarios x 5 seeds, 20,000 orders a day | 50 of 50; cause precision and recall 100%, 0 wrong causes. Ablation without the undo test: 5 wrong causes. Threshold alert: 0% of causes; on the masked pair it held 4 of 5 seeds without naming a cause and stayed silent on the fifth (+4.0%, inside the range). Corrected values within 0.017% of the clean value | [`samples/exasol/eval_report.md`](../samples/exasol/eval_report.md) |
| Held-out variants, 17, written after the detectors were fixed | caught 15, held 1, published under 4% off 1, published wrong 0 (before the tail check: caught 13, held 3) | [`samples/exasol/variants_report.md`](../samples/exasol/variants_report.md) |
| Real data, 56 days judged, after the tail check | 0 held, 54 NO_INCIDENT, 2 REAL_CHANGE (real change, no fault found); 6 of 6 planted faults caught; 62 of 62 runs agree with the DuckDB stand-in; the same verdicts as before the tail check | [`samples/exasol/real_backtest.md`](../samples/exasol/real_backtest.md) |
| Newest checks on live Exasol | 10 of 10 pass: blast radius, audit-log reader, `DOWNSTREAM_*` columns, metric history, `connect --check`, both new metrics, badge | [`samples/exasol/live_checks.md`](../samples/exasol/live_checks.md) |
| Red team, seed 11, 20,000 orders a day | Floors: unit 2%, duplicates 2%, fan-out 2%, new codes 5%, clock faults 100%, stale FX caught. 0 holes (1 before the tail check). 8 of 9 opposite-direction pairs caught, 1 held with one cause |
| Held-out partial unit changes, 24, frozen before the tail check | before: caught 0, held 24; after: caught 12 (all x1000), held 12 (all x10); published 0 both times | [`samples/exasol/heldout_unit_after.md`](../samples/exasol/heldout_unit_after.md) | [`samples/exasol/redteam_report.md`](../samples/exasol/redteam_report.md) |
| Scaling, IST case (29 Oct, after the unit tail check) | Right verdict at 20k, 100k, 200k and 400k orders a day; at 400k (17,346,085 payment rows) the gate takes 15.8 s, 15.1 s measured by Exasol, peak temporary memory 344 MiB | [`samples/exasol/scaling.md`](../samples/exasol/scaling.md) |
| Live demo, click to HELD | median 8.4 s over 5 runs (6.8 to 20.5 s) | [`samples/exasol/timings.md`](../samples/exasol/timings.md) |
| IST case, `receipts run ist_utc`, one session on an idle laptop | median 5.6 s end to end over 4 repeats, 4.6 s measured by Exasol, 63 to 69 MiB peak temporary memory | [`samples/exasol/timings.md`](../samples/exasol/timings.md) |
| Read-only agent user | reads PUB; refused on RAW, PIPE, RECEIPTS, insert, update, delete, create schema | [`docs/MCP_DEMO.md`](MCP_DEMO.md) |

## The unit-change hole: before and after the tail check

The red team found that a x100 unit change on 2% of one small gateway's payments was published (REAL_CHANGE on
seed 11, +6.47%): the unit check compared medians, which 2% of rows do not move. A tail check was
added: per gateway and currency, today's count of amounts above 20 times the
baseline median against the baseline share (Poisson test, false-alarm budget 1e-6 per slice and night). A stricter
real-change test was also proposed; it was not needed and is not applied. The held-out cases were committed before
the fix was written and were not used to tune it.

| Test on Exasol | Before | After |
|---|---|---|
| Red team, seed 11 | unit floor 100%, 1 hole | unit floor 2%, 0 holes |
| Held-out partial unit changes, 24 | caught 0, held 24, published 0 | caught 12, held 12, published 0 |
| Variants, 17 | caught 13, held 3, small 1, wrong 0 | caught 15, held 1, small 1, wrong 0 |
| Scored evaluation, 50 runs | 50 of 50 | 50 of 50, same precision, recall and ablation numbers, festival control published as REAL_CHANGE on all 5 seeds |
| Real-data backtest | 0 held, REAL_CHANGE on 13 Feb and 27 Feb, 6 of 6 | the same: 0 held, REAL_CHANGE on 13 Feb and 27 Feb, 6 of 6, all 62 verdicts and causes unchanged |

Reports: `samples/exasol/*_before.md` and the files without the suffix. The DuckDB stand-in gives the same
held-out counts and the same red team floors.

On the masked pair the total stayed inside the normal range in 1 of 5 seeds (seed 44, +4.0%), and Receipts proved both causes in all 5.

## Wrong-fix control: is the undo test circular?

For every scenario with a planted fault, the gate's own rules (moves today by at least 1.5%, keeps history as
published, lands in the normal range) were shown deliberately wrong corrections: the right fix on the wrong
gateway, the wrong factor, the right fix on every day instead of tonight, or the fix for a cause that was not
planted. Run on Exasol, 5 seeds, 20,000 orders a day
([`samples/exasol/wrongfix_report.md`](../samples/exasol/wrongfix_report.md), `receipts wrongfix --backend exasol`); the
stand-in gives the same table ([`samples/wrongfix_report.md`](../samples/wrongfix_report.md)).

| Wrong fixes | Tried | Rejected | Accepted |
|---|---|---|---|
| Wrong gateway | 30 | 30 | 0 |
| Applied to every day, not tonight | 5 | 5 | 0 |
| Wrong factor | 10 | 6 | 4 |
| Fix for a cause that was not planted | 190 | 184 | 6 |
| **All** | **235** | **225** | **10** |

The 10 accepted, on Exasol and on the stand-in alike, all act on GW_C, the smallest gateway, which carries about
5% of revenue:

| Runs | Wrong fix | Why the rules accepted it |
|---|---|---|
| masked pair, all 5 seeds | divide GW_C by 100, although GW_C was not touched | The two faults partly cancel, so the total moved only +4.0% to +7.9%, about the size of the smallest gateway; it was inside the normal range in 1 of 5 seeds. Taking about 5.5% off brings it inside the range on every seed, moves today by more than 1.5% and keeps history. |
| unit change, seeds 22, 33, 44, 55 | divide GW_C by 1000 where x100 was planted | The right cause with the wrong size. Over-correcting a 5% slice leaves revenue about 4% under the clean value, inside the range. |
| file loaded twice, seed 44 | divide GW_C by 100 | The planted duplicates moved revenue +11.2%; taking 4.9% off happens to land inside the range. |

None of these is the same cause under another name, and none is below the 1.5% line: each passes because the
normal range is wider than the smallest gateway's share. That is a real limit of the undo test on its own: for a
slice smaller than the band, "lands in range" cannot tell a right correction from a wrong one. In all 10 runs the
gate's verdict was still right, because no detector nominated these corrections (the unit check fits the factor
from the data, and it did not fire on GW_C in the masked pair). The history rule rejected every fix applied to
past days, and every wrong-gateway fix was rejected.

## Known limits and holes

* **Not closed:** a x10 unit change on 2% to 10% of a gateway is held without a proven cause (12 of 24 held-out
  cases): those amounts mostly stay below the 20x cut. Held, not published, but a person has to look.
* Partial clock shifts (25% to 50%) are held without a proven cause. Safe, but a person has to investigate.
* A fault without a detector is held as UNEXPLAINED when it leaves the normal range, and published when it
  does not. On real taxi data the normal range is about plus or minus 22%.
* The undo test alone cannot tell a right from a wrong correction on a slice smaller than the normal range:
  10 of 235 wrong corrections, all on the smallest gateway, pass the rules (above). Detector nomination covers it.
* Configured metrics: the detectors are bound to the payments layout. On the stand-in's 16 held-out faults, two orphan-code faults of -3.7% and -4.0% on order count were held although they sit just
  under the 4% line ([`samples/metrics_heldout_after.md`](../samples/metrics_heldout_after.md)).
* No holiday calendar; a real change with no fault found becomes part of the baseline.
* Red team and scaling ran on one seed and one laptop. The eval ran on 5 seeds.

Where each result was verified, and what was not run here, is in one place:
[README, Verified and not covered](../README.md#verified-and-not-covered).
