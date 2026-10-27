# Blind test: plant 10 faults without telling the author

Every result in this repository was produced by the person who wrote the detectors. A blind test removes that
advantage: someone else picks the faults, the gate judges them, and the results are reported as they come out,
misses included. No blind test has been run yet; this page is the kit for one.

## What the tester needs

* Python 3.10 or newer and this repository. No Exasol needed: the DuckDB stand-in is enough.
* About 15 minutes. Each run takes a few seconds.

## Steps

1. Set up once: `pip install -e .`, then `receipts init --fresh` (builds the synthetic data and the stand-in).
2. Without telling the author, write down 10 faults. Mix them: different fault classes, small and large shares
   (1 to 100 percent), different gateways, and at least one clean night with no fault.
3. For each one run `receipts blindtest --lab` and answer the prompts: the fault, the share of rows, the gateway,
   your initials and an optional note. Or pass the same as flags, for example
   `receipts blindtest --lab --fault clock_shift --share 30 --gateway GW_A --tester AB`.
4. Each run plants the fault into tonight's synthetic batch, runs the gate without write-back, removes the batch
   again and appends one line to `data/blindtest_results.md`. If it says tonight is already judged, run
   `receipts init --fresh` and continue.
5. Send `data/blindtest_results.md` unedited. Do not delete runs that look wrong; those are the point.

The faults to choose from: unit change (amounts x100), payment rows loaded twice, merchant table fans out, FX feed
misses today, IST written as UTC, new category code, or no fault. A fault class Receipts has no detector for cannot
be planted with this command; that case is covered by the `unknown_discount` scenario and would need a custom
SQL statement.

## How to read a line

| Column | Meaning |
|---|---|
| Planted, Share, Gateway | what the tester chose |
| Verdict | the gate's verdict: NO_INCIDENT, REAL_CHANGE, PROVEN_FAULT or UNEXPLAINED |
| Cause named | the cause the undo test confirmed, if any |
| Correct | `yes`; `safe miss` (held with no cause, or published less than 4% off); `partly`; `NO (wrong cause)`; `NO (published wrong)`; `NO (false alarm)` for a clean night that was held |
| Error | the published candidate against the same night without the fault |

## Report template

Copy this into the report and fill it in from the results file. Keep every run.

```markdown
## Blind test

Tester: <name or initials>, not an author. Date: <date>. Machine: <OS, CPU>. Backend: DuckDB stand-in.
Commit: <git rev-parse --short HEAD>.

| Runs | Correct | Safe misses | Partly | Wrong cause | Published wrong | False alarms |
|---|---|---|---|---|---|---|
| 10 | | | | | | |

Results file, unedited:

<paste data/blindtest_results.md here>

What the tester expected Receipts to miss, written before running:

<one or two lines>
```
