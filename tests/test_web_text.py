"""Wording in the command center that is easy to get wrong. Runs web/app.js helpers under Node."""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

APP_JS = Path(__file__).resolve().parent.parent / "web" / "app.js"

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")


def pair_text(pair: dict, total_change: float) -> str:
    src = APP_JS.read_text(encoding="utf-8").replace("\r\n", "\n")
    parts = [re.search(p, src).group(0) for p in
             (r"const esc = [^\n]*\n", r"const DIM_NAMES = [^\n]*\n", r"function pairText\([\s\S]*?\n  \}\n")]
    js = "".join(parts) + f"process.stdout.write(pairText({json.dumps(pair)}, {json.dumps(total_change)}));"
    out = subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout
    return re.sub(r"</?b>", "", out)


PAIR = {"dims": {"GATEWAY": "GW_B", "CURRENCY_CODE": "INR"}, "share": -6.2, "pct_change": -0.309}


def test_small_total_uses_the_slices_own_change():
    # masked pair on Exasol: total +1.8%, so a share of the total would read -620%
    assert pair_text(PAIR, 0.018) == \
        "Largest two-way slice: gateway GW_B and currency INR, down 31% against its usual level."
    assert pair_text({**PAIR, "pct_change": 0.42}, -0.01).endswith("up 42% against its usual level.")
    assert pair_text({**PAIR, "pct_change": None}, 0.02).endswith("new today with no usual level.")


def test_large_total_keeps_share_wording():
    pair = {**PAIR, "share": 0.87}
    assert pair_text(pair, -0.192) == "Largest two-way slice: gateway GW_B and currency INR, 87% of the total change."
    assert pair_text(pair, 0.05).endswith("87% of the total change.")
