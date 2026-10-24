"""Record the demo tour GIF for the top of the README, from the running command center in lab mode.

Needs `pip install playwright` and `playwright install chromium` (as capture_screenshots.py), and
`receipts serve --lab` running. No image library: the browser decodes and scales each screenshot on a
canvas, and the GIF is written here with numpy (one shared palette, only the changed area per frame).

    python scripts/capture_tour.py --url http://127.0.0.1:8000

The tour: tonight's batch is waiting, a clean batch lands and is published, then Break the pipeline plants
IST written as UTC, the gate runs step by step, the number is HELD, the receipt, Approve, and the agent.
"""

from __future__ import annotations

import argparse
import base64
from pathlib import Path

import numpy as np
from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "tour.gif"
W, H = 1280, 800          # browser viewport
SCALE = 0.625             # GIF is 800 x 500


# ---- frames ----------------------------------------------------------------------------------------
def grab(page: Page) -> np.ndarray:
    """Screenshot the viewport, decode and downscale it in the browser, return an RGB array."""
    png = base64.b64encode(page.screenshot(type="png")).decode()
    w, h = int(W * SCALE), int(H * SCALE)
    data = page.evaluate("""async ([src, w, h]) => {
        const img = new Image(); img.src = 'data:image/png;base64,' + src; await img.decode();
        const c = document.createElement('canvas'); c.width = w; c.height = h;
        const x = c.getContext('2d'); x.imageSmoothingQuality = 'high'; x.drawImage(img, 0, 0, w, h);
        const d = x.getImageData(0, 0, w, h).data; let s = '';
        for (let i = 0; i < d.length; i += 32768) s += String.fromCharCode.apply(null, d.subarray(i, i + 32768));
        return btoa(s); }""", [png, w, h])
    return np.frombuffer(base64.b64decode(data), np.uint8).reshape(h, w, 4)[:, :, :3]


# ---- GIF writing -----------------------------------------------------------------------------------
def palette(frames: list[np.ndarray]) -> np.ndarray:
    """The 256 most used colours after rounding to 5 bits per channel: the UI has few colours."""
    px = np.concatenate([f.reshape(-1, 3)[::7] for f in frames]) & 0xF8
    keys, counts = np.unique(px.astype(np.uint32) @ np.array([65536, 256, 1], np.uint32), return_counts=True)
    top = keys[np.argsort(-counts)[:256]]
    pal = np.stack([(top >> 16) & 255, (top >> 8) & 255, top & 255], 1).astype(np.uint8) | 4
    return np.vstack([pal, np.zeros((256 - len(pal), 3), np.uint8)])


def index(frame: np.ndarray, pal: np.ndarray) -> np.ndarray:
    p = pal.astype(np.int32)
    flat = frame.reshape(-1, 3).astype(np.int32)
    out = np.empty(len(flat), np.uint8)
    for i in range(0, len(flat), 65536):  # nearest palette colour, in chunks to bound memory
        d = ((flat[i:i + 65536, None, :] - p[None]) ** 2).sum(-1)
        out[i:i + 65536] = d.argmin(1)
    return out.reshape(frame.shape[:2])


def lzw(px: bytes) -> bytes:
    """GIF LZW with 8-bit codes, variable code width, clear when the table is full."""
    clear, end = 256, 257
    out, buf, nbits = bytearray(), 0, 0
    width, table, nxt = 9, {bytes([i]): i for i in range(256)}, 258

    def emit(code):
        nonlocal buf, nbits
        buf |= code << nbits
        nbits += width
        while nbits >= 8:
            out.append(buf & 255)
            buf >>= 8
            nbits -= 8
    emit(clear)
    w = b""
    for b in px:
        wb = w + bytes([b])
        if wb in table:
            w = wb
            continue
        emit(table[w])
        if nxt < 4096:
            table[wb] = nxt
            nxt += 1
            if nxt > (1 << width) and width < 12:
                width += 1
        else:
            emit(clear)
            table, nxt, width = {bytes([i]): i for i in range(256)}, 258, 9
        w = bytes([b])
    if w:
        emit(table[w])
    emit(end)
    if nbits:
        out.append(buf & 255)
    return bytes(out)


def write_gif(path: Path, frames: list[tuple[np.ndarray, int]]) -> None:
    pal = palette([f for f, _ in frames])
    h, w = frames[0][0].shape[:2]
    g = bytearray(b"GIF89a" + w.to_bytes(2, "little") + h.to_bytes(2, "little") + bytes([0xF7, 0, 0]))
    g += pal.tobytes()
    g += b"\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00"  # loop forever
    prev = None
    for f, ms in frames:
        idx = index(f, pal)
        if prev is None:
            y0, y1, x0, x1 = 0, h, 0, w
        else:  # only the part that changed
            ch = np.argwhere(idx != prev)
            if not len(ch):
                ch = np.array([[0, 0]])
            (y0, x0), (y1, x1) = ch.min(0), ch.max(0) + 1
        prev = idx
        g += b"\x21\xF9\x04\x04" + max(2, ms // 10).to_bytes(2, "little") + b"\x00\x00"
        g += b"\x2C" + int(x0).to_bytes(2, "little") + int(y0).to_bytes(2, "little")
        g += int(x1 - x0).to_bytes(2, "little") + int(y1 - y0).to_bytes(2, "little") + b"\x00\x08"
        data = lzw(idx[y0:y1, x0:x1].tobytes())
        for i in range(0, len(data), 255):
            g += bytes([len(data[i:i + 255])]) + data[i:i + 255]
        g += b"\x00"
    g += b"\x3B"
    path.write_bytes(bytes(g))


# ---- the tour --------------------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    url = ap.parse_args().url
    frames: list[tuple[np.ndarray, int]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H}, reduced_motion="reduce")
        page.goto(url)
        page.wait_for_selector("#lab-fault option", state="attached", timeout=30_000)
        with page.expect_response(lambda r: r.url.endswith("/api/lab/reset")):
            page.click("#lab-reset")
        page.wait_for_function("document.querySelector('#status .flag').textContent === 'WAITING'")
        page.evaluate("window.scrollTo(0, 0)")
        frames.append((grab(page), 2200))                                   # 1. tonight's batch is waiting
        page.click('#scenarios button[data-id="healthy"]')
        with page.expect_response(lambda r: r.url.endswith("/api/run"), timeout=120_000):
            page.click("#go")
        page.wait_for_function("document.querySelector('#status .flag').textContent === 'PUBLISHED'")
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(600)
        frames.append((grab(page), 2200))                                   # 2. a clean batch lands, published
        page.locator("#lab").scroll_into_view_if_needed()
        page.select_option("#lab-fault", "clock_shift")
        page.evaluate("document.querySelector('#lab').scrollIntoView({block: 'start'})")
        frames.append((grab(page), 1600))                                   # 3. pick a fault
        page.click("#lab-break")
        seen = 0
        while True:                                                         # 4. the gate, step by step
            n = page.eval_on_selector_all("#lab-timeline li:not(.running)", "e => e.length")
            if n > seen:
                seen = n
                frames.append((grab(page), 500))
            if not page.evaluate("document.querySelector('#lab-break').disabled") and \
                    page.inner_text("#lab-result"):
                break
            page.wait_for_timeout(150)
        frames.append((grab(page), 1800))
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(400)
        frames.append((grab(page), 2600))                                   # 5. HELD banner
        page.evaluate("document.querySelector('#case').scrollIntoView({block: 'start'})")
        page.wait_for_timeout(600)
        frames.append((grab(page), 2600))                                   # 6. the receipt
        page.evaluate("document.querySelector('#fix-card').scrollIntoView({block: 'center'})")
        page.wait_for_timeout(300)
        frames.append((grab(page), 1600))
        with page.expect_response(lambda r: "/approve" in r.url):
            page.click("#approve")
        page.wait_for_timeout(500)
        frames.append((grab(page), 1800))                                   # 7. approved
        page.evaluate("document.querySelector('section.agents').scrollIntoView({block: 'start'})")
        with page.expect_response(lambda r: r.url.endswith("/api/agent")):
            page.click("#ask")
        page.wait_for_function("document.querySelector('#question').textContent.length > 0")
        page.wait_for_timeout(300)
        frames.append((grab(page), 3200))                                   # 8. the agent answers
        browser.close()
    write_gif(OUT, frames)
    print(f"{OUT.name}: {len(frames)} frames, {OUT.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
