"""Measure the time from clicking "Break the pipeline" to the HELD banner, in a real browser.

Needs `pip install playwright` and `playwright install chromium`, and a command center started in lab mode:

    receipts serve --lab --watch
    python scripts/measure_break.py --url http://127.0.0.1:8000 --runs 5

Each run presses Reset, picks the fault, clicks Break the pipeline and stops the clock when the page's status
flag reads HELD. Prints every run and the median, and writes them to logs/break_timing.json.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--fault", default="clock_shift")
    a = ap.parse_args()
    runs = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        page.goto(a.url)
        page.wait_for_selector("#lab-fault option", state="attached", timeout=30_000)
        backend = page.inner_text("#chips")
        for i in range(a.runs):
            with page.expect_response(lambda r: r.url.endswith("/api/lab/reset")):
                page.click("#lab-reset")
            page.wait_for_function("document.querySelector('#status .flag').textContent === 'WAITING'")
            page.select_option("#lab-fault", a.fault)
            t0 = time.perf_counter()
            page.click("#lab-break")
            page.wait_for_function("document.querySelector('#status .flag') && "
                                   "document.querySelector('#status .flag').textContent === 'HELD'", timeout=120_000)
            ms = (time.perf_counter() - t0) * 1000
            steps = page.eval_on_selector_all("#lab-timeline li", "els => els.length")
            page.wait_for_function("!document.querySelector('#lab-break').disabled")
            runs.append(round(ms))
            print(f"run {i + 1}: click to HELD {ms:,.0f} ms ({steps} steps shown live)")
        browser.close()
    out = {"backend": " ".join(backend.split()), "fault": a.fault, "runs_ms": runs, "median_ms": statistics.median(runs)}
    (ROOT / "logs").mkdir(exist_ok=True)
    (ROOT / "logs" / "break_timing.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"median {out['median_ms']:,.0f} ms over {len(runs)} runs on {out['backend']}")


if __name__ == "__main__":
    main()
