# Jury questions, with short answers

Q&A is 30% of the demo-day score. Answer in one or two sentences, then offer to show it.

**Why Exasol and not Postgres or DuckDB?**
The method is "test every slice, then rebuild the pipeline and re-run it for each suspect". That is many wide aggregations over the full fact table per incident. Exasol runs them in memory and in parallel, runs the Python UDF next to the data per group, and keeps view text we can parse for lineage. Our claim is the measured time on Exasol shown in every receipt, not a guess about other databases. We use DuckDB only as a stand-in so anyone can reproduce the results without installing a database, and the same SQL templates render for both.

**What stops the LLM from hallucinating a cause?**
It is not in the loop. Detectors nominate, the undo test proves, and deterministic rules decide. The LLM only rewrites a finished verdict, sees only aggregates, and its text is discarded if it mentions a check that never fired. With no API key the whole system still works.

**What if a detector is wrong?**
That is expected. On the festival day the duplicate check fires on payment retries. Undoing it moves revenue by 0.00%, so it is ruled out. The ablation in the eval shows a detectors-only system names 5 wrong causes over 50 runs; Receipts names none.

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
A holiday calendar for the baseline, fault classes beyond six, detectors for raw layouts other than the sample payments, and the upstream fix itself. All listed in the README under Verified and not covered.

**Is any of this real data?**
The scenarios, the eval, the variants and the red team use synthetic data generated from a seed, so we know the true clean value. The backtest uses real public data: 9,554,757 NYC yellow taxi trips, January to March 2024. On Exasol (before the unit tail check) 56 real days were judged, 0 held, and 6 of 6 planted faults were caught; the DuckDB re-run after the tail check matched every verdict and cause.

**Isn't the undo test circular? The same detector nominates the cause and writes the fix.**
Partly, and we say so. For fixes limited to today's batch, rule 4 (history unchanged) holds by construction, so the rule that really discriminates is rule 3: undoing the cause must bring the number back into its normal range. That is a real test, because a wrong suspect's fix does not move the number (the festival retry burst is the example). Rule 4 matters for fixes that touch shared tables, like the merchant fan-out, where it passes only if history returns to exactly what was published.

**You wrote the faults and the detectors. Is 100% meaningful?**
On the ten scripted scenarios it shows consistency, not generality, and we say that. So there is a second test, `receipts variants`: 17 held-out variants (other gateways, other factors, partial row coverage, two faults at once). On Exasol, after the unit tail check: 15 caught, 1 held for a person with no cause named, 1 published because the real error was under 4%, and 0 published wrong. Writing it found a real bug: the unit check only recognised a factor of 100.

**Real revenue has weekly cycles. Does the baseline break?**
A flat 14-day baseline would. The gate now learns each weekday's index from five weeks of trusted history, but only when a statistical test says the weekly pattern is real. On the real taxi data the weekday baseline was used on 56 of 56 judged days, and no real day was held.

**Is it fast on big data? Your demo is small.**
On Exasol Personal on a laptop, the IST case gave the right verdict at every size up to 400,000 orders a day (17,346,085 payment rows): 27.5 seconds end to end, 26.3 measured by Exasol, the CUBE over 5.95 million rows in 5.9. Each run was the first after a fresh load, measured before the unit tail check. That is the largest size we have measured, and we claim nothing beyond it.

**Your red team found a hole. What was it, and is it closed?**
A x100 unit change on 2% of one small gateway's payments moved revenue up 6.5% and was published as a verified real change, because the unit check compared medians and 2% of rows do not move a median. We added a tail check: per gateway, count today's amounts above 20 times the baseline median and compare with the baseline share. Re-run on the same seed, the unit floor went from 100% to 2% and the holes from 1 to 0. Held-out cases written before the fix were not used to tune it.

**Why is the normal range on the taxi data about plus or minus 22%?**
Because real daily revenue is noisy. Weather, holidays and events move taxi revenue a lot from one day to the next, so the band learned from five weeks of history is wide (21.7% at the median, from 12.9% to 31.9%). A fault without a detector that moves the total less than that would be published. The detectors do not depend on the band: a payment file loaded twice (+8%, inside the range) was caught on all three days it was planted.

**What happens today with a x10 unit error on 2% to 10% of one gateway?**
It is held, not proven. Those amounts mostly stay below the 20x cut, so the tail check does not see them, but the total leaves the normal range, so the number is held as UNEXPLAINED and a person looks. In the 24 held-out cases all 12 x10 cases ended like this, and none was published.

**Why is there a DuckDB stand-in if Exasol is the platform?**
So CI and anyone without Exasol can run the tests and the demo. It runs the same SQL templates. The results we quote come from Exasol unless a line says the stand-in, and the stand-in gives the same verdicts where both were run.

**What have you not tested?**
The newest parts (the blast radius views and audit-log query, the order-count metric, the wrong-fix control, the badge) are written for Exasol and pass the Exasol grammar test and the stand-in, but have not run on a live Exasol yet. Also: the Mac and Linux run scripts on a real Mac or Linux machine (only under Git Bash on Windows), the Exasol MCP server with a real AI agent (only the read-only database user was verified), posting to a real Slack workspace (only that a failing webhook does not stop the watcher), and building the Docker image.

**How is this different from tools that estimate or replay the effect of a change?**
They tell you how much a change probably contributed. Receipts proves a cause by undoing it: it rebuilds the pipeline in a sandbox schema inside Exasol with one source corrected, re-runs the metric, and accepts the cause only if the number comes back into range and published history is unchanged. Until then the number is held, and dashboards and agents see the last trusted value.

**How do you know a wrong fix would not pass the undo test?**
We tried. `receipts wrongfix` feeds the gate's rules deliberately wrong corrections for every planted fault: the wrong gateway, the wrong factor, the right fix on every day, or the fix for another cause. On the stand-in, 5 seeds: 235 tried, 225 rejected, 10 accepted. All 10 are on the smallest gateway, and in every one the gate's real verdict named only the planted cause, because no detector nominated the wrong fix. So the undo test does most of the work, and on a small slice the detector's nomination carries the rest. The list is in `samples/wrongfix_report.md`.

**How would a company connect its own metric?**
Edit `receipts.yaml`: the daily view, its value and day columns, the raw tables, and the amount, ID and time columns. `receipts connect --check` says in plain English what is missing or the wrong type. The band, weekday baseline, lineage, undo test and blast radius then follow that metric. The six detectors are written for the payments layout, so a different raw layout gets the band and lineage but needs its own detectors for causes.
