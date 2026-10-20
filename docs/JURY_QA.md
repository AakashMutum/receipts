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
