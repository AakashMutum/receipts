"""Capture the README screenshots from the running command center.

Needs `pip install playwright` and `playwright install chromium`, a database built with
`receipts init`, and `receipts serve --lab` running (lab mode, because it lands planted scenarios).
Between scenarios it rebuilds the database with `receipts init --fresh --day DAY`, so each scenario
starts clean. DAY defaults to the server's incoming day (yesterday in India), so the screenshots show
a current date. Run with the same RECEIPTS_* / EXA_* variables as the server:

    python scripts/capture_screenshots.py --url http://127.0.0.1:8000

`--only redteam` retakes just 09_redteam.png (no rebuild; the tab reads the committed red team report).
`--only blast` lands the IST case and takes 11_who_saw.png; `--only badges` takes 12_badges.png from /badge.svg
after a healthy night, the IST case, its approval and the festival (lab mode, no rebuild). `--only connect` needs
no server (stop it first: the stand-in allows one process): it lands the IST case with `receipts run` and takes
13_connect.png of `receipts connect`.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "screenshots"
DAY = ""


def rebuild() -> None:
    subprocess.run([sys.executable, "-m", "receipts.cli", "init", "--fresh", "--day", DAY], check=True,
                   cwd=ROOT, stdout=subprocess.DEVNULL)


def open_page(page: Page, url: str) -> None:
    page.goto(url)
    page.wait_for_selector("#chips .chip, #chips span", timeout=30_000)
    page.wait_for_selector("#status .flag", timeout=30_000)


def run(page: Page, scenario: str) -> None:
    page.click(f'#scenarios button[data-id="{scenario}"]')
    with page.expect_response(lambda r: r.url.endswith("/api/run"), timeout=120_000) as r:
        page.click("#go")
    assert r.value.ok, f"{scenario}: /api/run returned {r.value.status}"
    page.wait_for_function("!document.querySelector('#go').disabled && !document.querySelector('#case').hidden")
    page.wait_for_timeout(1500)  # let the charts settle


def shot(target, name: str) -> None:
    path = OUT / name
    target.screenshot(path=str(path))
    print(f"{name}: {path.stat().st_size // 1024} KB")


def redteam(page: Page) -> None:
    page.click("#tab-redteam")
    page.wait_for_selector("#rt-chart svg")
    page.evaluate("document.querySelector('#lab').scrollIntoView({block: 'start'})")
    page.wait_for_timeout(500)
    shot(page.locator("#lab"), "09_redteam.png")


def blast(page: Page, url: str) -> None:
    open_page(page, url)
    run(page, "ist_utc")
    card = page.locator("section.card:has(#blast-title)")
    card.scroll_into_view_if_needed()
    page.wait_for_timeout(300)
    shot(card, "11_who_saw.png")


def badges(page: Page, url: str) -> None:
    import html as _html
    base = url.rstrip("/")
    got = []

    def land(scenario):
        r = page.request.post(base + "/api/run", data={"scenario": scenario}, timeout=120_000)
        assert r.ok, f"{scenario}: {r.status}"
        return r.json()["case"]

    def badge(label):
        r = page.request.get(base + "/badge.svg")
        assert r.ok
        got.append((label, r.text()))

    land("healthy")
    badge("A clean night")
    c = land("ist_utc")
    badge("IST written as UTC, held")
    r = page.request.post(base + f"/api/case/{c['case_id']}/approve", data={"note": "screenshot"})
    assert r.ok, r.status
    badge("The proven correction approved by a person")
    land("festival")
    badge("A real festival surge")
    rows = "".join(f"<tr><td>{_html.escape(l)}</td><td>{svg}</td></tr>" for l, svg in got)
    page.set_content("<html><body style='margin:0'><div id='w' style='display:inline-block;padding:24px;background:#fff;font:15px system-ui,sans-serif;color:#222'>"
                     "<h3 style='margin:0 0 12px'>GET /badge.svg after each night</h3><table id='b' "
                     "style='border-collapse:collapse'>" + rows.replace("<td>", "<td style='padding:8px 16px 8px 0'>")
                     + "</table></div></body></html>")
    shot(page.locator("#w"), "12_badges.png")


def connect_shot(page: Page) -> None:
    import html as _html
    env = {**__import__("os").environ, "PYTHONIOENCODING": "utf-8"}
    subprocess.run([sys.executable, "-m", "receipts.cli", "run", "ist_utc"], cwd=ROOT, env=env, check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out = subprocess.run([sys.executable, "-m", "receipts.cli", "connect"], cwd=ROOT, env=env, capture_output=True,
                         text=True, encoding="utf-8").stdout
    lines = [l for l in out.splitlines() if not l.lstrip().startswith("ok ")]
    page.set_content("<html><body style='margin:0;background:#0f1720'><pre id='t' style='margin:0;padding:20px 24px;"
                     "color:#e6edf3;font:13px Consolas,monospace;white-space:pre'>$ receipts connect\n"
                     + _html.escape("\n".join(lines)) + "</pre></body></html>")
    shot(page.locator("#t"), "13_connect.png")


def main() -> None:
    ap = argparse.ArgumentParser()
    global DAY
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    ap.add_argument("--day", help="incoming day, YYYY-MM-DD (default: the one the server holds)")
    ap.add_argument("--only", choices=["redteam", "blast", "badges", "connect"], help="take one screenshot only")
    a = ap.parse_args()
    url = a.url
    import json
    import urllib.request
    if a.only == "connect":
        with sync_playwright() as p:
            browser = p.chromium.launch()
            connect_shot(browser.new_page(viewport={"width": 1500, "height": 400}))
            browser.close()
        return
    with urllib.request.urlopen(url.rstrip("/") + "/api/overview", timeout=60) as r:
        DAY = a.day or json.load(r)["incoming_day"]
    print(f"incoming day {DAY}")
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")

        if a.only == "redteam":
            open_page(page, url)
            redteam(page)
            browser.close()
            return
        if a.only in ("blast", "badges"):
            (blast if a.only == "blast" else badges)(page, url)
            browser.close()
            return

        rebuild()
        open_page(page, url)
        assert "WAITING" in page.inner_text("#status")
        shot(page, "01_waiting.png")

        run(page, "ist_utc")
        page.evaluate("window.scrollTo(0, 0)")
        shot(page, "02_held_ist.png")
        shot(page.locator("#case"), "03_receipt_ist.png")
        with page.expect_response(lambda r: r.url.endswith("/api/agent")):
            page.click("#ask")
        page.wait_for_function("document.querySelector('#question').textContent.length > 0")
        shot(page.locator("section.agents"), "04_agents_held.png")
        shot(page.locator(".ev-grid > div:nth-child(2)"), "10_measured_by_exasol.png")

        rebuild()
        open_page(page, url)
        run(page, "masked_pair")
        where = page.inner_text("#where")
        assert "against its usual level" in where and "of the total change" not in where, where
        shot(page.locator("#case"), "05_masked_pair.png")

        rebuild()
        open_page(page, url)
        run(page, "festival")
        assert "PUBLISHED" in page.inner_text("#status")
        page.evaluate("window.scrollTo(0, 0)")
        top = page.locator("section.hero").bounding_box()
        paper = page.locator("#paper").bounding_box()
        page.screenshot(path=str(OUT / "06_festival_published.png"), full_page=True,
                        clip={"x": 0, "y": top["y"], "width": 1440, "height": paper["y"] + paper["height"] - top["y"] + 24})
        print(f"06_festival_published.png: {(OUT / '06_festival_published.png').stat().st_size // 1024} KB")

        # lab: break the pipeline, then the red team tab
        with page.expect_response(lambda r: r.url.endswith("/api/lab/reset")):
            page.click("#lab-reset")
        page.select_option("#lab-fault", "clock_shift")
        page.click("#lab-break")
        page.wait_for_function("document.querySelector('#lab-result').textContent.includes('HELD')", timeout=120_000)
        page.evaluate("document.querySelector('#lab').scrollIntoView({block: 'start'})")
        page.wait_for_timeout(800)
        shot(page.locator("#lab"), "08_break_it.png")
        redteam(page)
        browser.close()


if __name__ == "__main__":
    main()
