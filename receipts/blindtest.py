"""`receipts blindtest`: someone other than the author plants a fault, the gate judges it, the result is logged.

Lab mode and synthetic data only. The tester picks the fault class (or no fault at all), the share of rows and
the gateway in a short prompt, or passes them as flags. The gate runs without write-back, tonight's batch is
removed again afterwards, and one line per run is appended to a Markdown results file that can be pasted into
a report as it is, misses included.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .db import Backend
from .faults import FAULT_CLASSES
from .redteam import OUTCOMES, attack, clean_value

HEADER = ("| When | Tester | Planted | Share | Gateway | Verdict | Cause named | Outcome | Correct | Error | Note |\n"
          "|---|---|---|---|---|---|---|---|---|---|---|\n")
CORRECT = {"caught": "yes", "held": "safe miss (held, no cause)", "held_partial": "partly (held, one cause)",
           "small": "safe miss (published, under 4% off)", "wrong_cause": "NO (wrong cause)",
           "WRONG": "NO (published wrong)"}


def judge(be: Backend, day, fault: str | None, share: float, gateway: str | None) -> dict:
    """Plant the chosen fault (or none), run the gate without write-back, restore tonight. Returns the outcome."""
    truth = clean_value(be, day)
    if fault is None:  # a clean night: the right answer is to publish it
        from .gate import run
        from .load import ingest, reset_raw
        ingest(be, day, "healthy")
        try:
            c = run(be, day, {"id": "blind_none"}, write_back=False)
        finally:
            reset_raw(be, day)
        ok = c["trust_status"] != "HELD" and not c["confirmed"]
        return {"verdict": c["verdict"], "confirmed": c["confirmed"], "error_pct": 0.0,
                "outcome": "clean, published" if ok else "clean, held (false alarm)",
                "correct": "yes" if ok else "NO (false alarm)"}
    r = attack(be, day, [(fault, share, gateway)], truth)
    return r | {"correct": CORRECT[r["outcome"]], "outcome": OUTCOMES[r["outcome"]]}


def row(tester: str, fault: str | None, share: float, gateway: str | None, r: dict, note: str = "") -> str:
    clean = lambda s: str(s).replace("|", "/").replace("\n", " ")
    return (f"| {datetime.now():%Y-%m-%d %H:%M} | {clean(tester) or '-'} | {fault or 'none'} | "
            f"{'-' if fault in (None, 'stale_feed') else f'{share:.0%}'} | {gateway or '-'} | {r['verdict']} | "
            f"{', '.join(r['confirmed']) or 'none'} | {r['outcome']} | {r['correct']} | {r['error_pct']:+.2f}% | "
            f"{clean(note) or '-'} |\n")


def append(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with path.open("a", encoding="utf-8") as f:
        if new:
            f.write("# Blind test results\n\nAppended by `receipts blindtest`, one line per run, unedited.\n\n" + HEADER)
        f.write(line)


def ask(prompt_fn=input) -> tuple[str | None, float, str | None, str, str]:
    """The guided prompt. Returns fault (None for a clean night), share, gateway, tester, note."""
    kinds = list(FAULT_CLASSES)
    print("Pick a fault to plant (the author should not know which):")
    for i, k in enumerate(kinds, 1):
        print(f"  {i}. {FAULT_CLASSES[k][0]}")
    print(f"  {len(kinds) + 1}. No fault (a clean night)")
    while True:
        a = prompt_fn("Number: ").strip()
        if a.isdigit() and 1 <= int(a) <= len(kinds) + 1:
            break
        print("Type one of the numbers above.")
    fault = None if int(a) == len(kinds) + 1 else kinds[int(a) - 1]
    share, gw = 1.0, None
    if fault and FAULT_CLASSES[fault][1]:
        while True:
            s = prompt_fn(f"Share of {FAULT_CLASSES[fault][1]} to affect, 1 to 100 percent: ").strip().rstrip("%")
            try:
                if 1 <= float(s) <= 100:
                    share = float(s) / 100
                    break
            except ValueError:
                pass
            print("Type a number from 1 to 100.")
    if fault and FAULT_CLASSES[fault][2]:
        opts = FAULT_CLASSES[fault][2]
        while True:
            g = prompt_fn(f"Gateway ({', '.join(opts)}): ").strip().upper()
            if g in opts:
                gw = g
                break
            print(f"Type one of {', '.join(opts)}.")
    tester = prompt_fn("Your name or initials (for the results file): ").strip()
    note = prompt_fn("Note (optional): ").strip()
    return fault, share, gw, tester, note
