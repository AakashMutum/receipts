# Demo script (3 minutes) and deck outline

Rehearse with the command center already open on the healthy batch, started in lab mode (`receipts demo --lab`, which the run scripts do). Record at 1440 x 900. Speak over the screen; no slides in the video except the first and last five seconds.

## Video, 3:00

**0:00 to 0:20. The problem, no technology.**
"Every Monday a finance analyst gets asked why revenue moved. Is it real, or is it a data bug? Every check is green. It usually takes two days and three people to answer. Receipts answers in seconds, with proof."

**0:20 to 0:40. Healthy batch.**
Show the big number and PUBLISHED. "Tonight's batch landed. Six checks ran on the raw rows before the dashboard saw anything. All clean, so it is published."

**0:40 to 1:30. Break it: IST written as UTC.**
In the Break the pipeline panel pick "IST written as UTC" and press the button. Each step of the gate ticks off live, then the HELD banner and the receipt (about 7 seconds on Exasol).
"Revenue dropped 19%. The dashboard did not show it: it is holding Monday's trusted value." Point at HELD.
"The clock check is a Python UDF running inside Exasol. It found gateway B's day sits exactly five and a half hours late. That's IST."
Point at the four rules. "A detector only nominates a suspect. Then we prove it: rebuild the whole pipeline in a sandbox schema with the fault undone, and re-run. Revenue comes back to normal and history does not change. That's the receipt."
Point at Where it moved: "11,000 slices tested in one GROUP BY CUBE." Point at lineage: "Lineage comes from Exasol's own view definitions."

**1:30 to 1:55. Ask an agent.**
Press "Ask both agents". "An agent reading the pipeline states the broken number as fact. An agent that checks METRIC_TRUST through the Exasol MCP server says it's held, why, and gives the last trusted value."

**1:55 to 2:25. The hard ones.**
Run "Two faults that cancel out": "The total looks normal. A threshold alert stays silent. Receipts proves both faults."
Run "Real festival surge": "The duplicate check fires on payment retries, but undoing it changes nothing, so it is ruled out. Published as a verified real change."

**2:25 to 2:50. Proof it works.**
Scroll to the scoreboard. "50 runs on fresh data. 100% right calls, zero wrong causes. Without the undo test, a wrong cause gets named five times. Corrected values within 0.02% of the truth."

**2:50 to 3:00. Close.**
"Receipts. Hold the number, prove why, tell people and agents whether to trust it. Open source, runs on Exasol Personal."

## Deck, 8 slides

1. **The problem sentence**, alone on the slide.
2. **Why today fails:** every check is green; the faults are unit changes, double loads, fan-outs, stale feeds, clock shifts, new codes. One line each.
3. **Three layers:** gate, investigate, explain. The LLM never decides.
4. **Prove by undoing:** the four rules and the undo chart from the IST case.
5. **Exasol at the centre:** CUBE over 11,000 slices, Python SET UDF, lineage from `EXA_ALL_VIEWS`, sandbox schemas, write-back, MCP. Real timings from Exasol Personal: the IST incident is proven in a median of 5.6 s end to end, with the CUBE over 11,074 slices in 1.3 s and the sandbox undo in 1.4 s (one session, `samples/exasol/timings.md`); at 17.3 million payment rows the gate took 27.5 s (scaling run, before the unit tail check).
6. **Agents:** the two answers side by side.
7. **Results:** the three-row scoreboard from the Exasol evaluation (50 of 50 runs, median gate latency 3.4 s) and the masked-pair and festival examples.
8. **Limitations and next steps:** the seven honest bullets from the README, then: more detector classes, seasonality-aware baseline, a second metric.

The timings on slides 5 and 7 come from `receipts run ist_utc` and `receipts eval --backend exasol` on Exasol Personal; see the README Results section.
