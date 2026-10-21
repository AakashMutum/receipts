# Jury questions, with short answers

Q&A is 30% of the demo-day score. Answer in one or two sentences, then offer to show it.

**Why Exasol and not Postgres or DuckDB?**
The method is "test every slice, then rebuild the pipeline and re-run it for each suspect". That is many wide aggregations over the full fact table per incident. Exasol runs them in memory and in parallel, runs the Python UDF next to the data per group, and keeps view text we can parse for lineage. Our claim is the measured time on Exasol shown in every receipt, not a guess about other databases. We use DuckDB only as a stand-in so anyone can reproduce the results without installing a database, and the same SQL templates render for both.

**What stops the LLM from hallucinating a cause?**
It is not in the loop. Detectors nominate, the undo test proves, and deterministic rules decide. The LLM only rewrites a finished verdict, sees only aggregates, and its text is discarded if it mentions a check that never fired. With no API key the whole system still works.

**What if a detector is wrong?**
That is expected. On the festival day the duplicate check fires on payment retries. Undoing it moves revenue by 0.00%, so it is ruled out. The ablation in the eval shows a detectors-only system names a wrong cause in 5 of 50 runs; Receipts names none.

**What if lineage is incomplete?**
Rule 2 fails and the suspect cannot be confirmed, so the batch is held as unexplained rather than blamed on the wrong thing. Failing safe means more human review, never a wrong answer.

**What about a fault you have no detector for?**
That is scenario ten. Receipts holds the value, names no cause, and points at the slice that moved most. If such a fault is small enough to stay inside the normal range it gets published; we show that case in the quick eval instead of hiding it.

**How does it scale?**
Detectors and the CUBE run on the incoming batch and a 15-day window, so cost grows with daily volume, not total history. The undo test rebuilds views, not tables. Each extra metric adds one pipeline and one set of detector bindings.

**Is the corrected value safe to publish automatically?**
No, and we do not. Proven faults stay held until a person approves. Approval is logged in `RECEIPTS.APPROVALS` and the value is published as `CORRECTED`, which agents can see.

**How do you know the numbers are right?**
Ground truth: we know what the clean value should be because we generated the data. Corrected values land within 0.017% of it. Run `make judge-check` on a clean clone.

**What does the analyst do differently on Monday?**
She opens the case instead of a Slack thread. It already says which upstream feed broke, which rows, by how much, the corrected number, and the one-line fix to send the gateway team.

**What did you not solve?**
Seasonality in the baseline, fault classes beyond six, metrics beyond one, and the upstream fix itself. All listed in the README.

**Is any of this real data?**
No. All data is synthetic and generated from a seed. The queries, timings, UDF and evaluation are real.

**Isn't the undo test circular? The same detector nominates the cause and writes the fix.**
Partly, and we say so. For fixes limited to today's batch, rule 4 (history unchanged) holds by construction, so the rule that really discriminates is rule 3: undoing the cause must bring the number back into its normal range. That is a real test, because a wrong suspect's fix does not move the number (the festival retry burst is the example). Rule 4 matters for fixes that touch shared tables, like the merchant fan-out, where it passes only if history returns to exactly what was published.

**You wrote the faults and the detectors. Is 100% meaningful?**
On the ten scripted scenarios it shows consistency, not generality, and we say that. So there is a second test, `receipts variants`: 17 held-out variants (other gateways, other factors, partial row coverage, two faults at once) across two seeds. Result: 26 caught, 6 held for a person with no cause named, 2 published because the real error was under 2%, and 0 published wrong. Writing it found a real bug: the unit check only recognised a factor of 100.

**Real revenue has weekly cycles. Does the baseline break?**
A flat 14-day baseline would. The gate now learns each weekday's index from five weeks of trusted history, but only when a statistical test says the weekly pattern is real. On data with a weekday pattern it gave 63 of 63 correct verdicts across all seven weekdays. With the flat baseline the same data hid an undetected 9% fault on every weekday.

**Is it fast on big data? Your demo is small.**
At 100,000 orders a day (4.2 million payment rows) on Exasol Personal on a laptop, the IST case takes 6.8 seconds (5.9 in the database, the CUBE over 1.48 million rows in 1.9) and the two-fault case 9.7 seconds, both with the right verdict. The DuckDB stand-in at the same size takes 7 to 10 seconds per case. That is the largest size we have measured, and we have not claimed anything about billion-row scale.
