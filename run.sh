#!/usr/bin/env bash
# Receipts one-click demo for Linux, and for macOS through run.command.
# Needs only Python 3.10 or newer, no database to install.
set -u
cd "$(dirname "$0")" || exit 1

fail() {
    echo
    echo "  $1"
    echo "  Setup did not finish."
    if [ -t 0 ]; then read -r -p "  Press Enter to close. " _; fi
    exit 1
}

echo
echo "  Receipts demo, using the local stand-in database"
echo

# 1. Find Python 3.10 or newer
PY=""
for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' </dev/null >/dev/null 2>&1; then
        PY="$c"
        break
    fi
done
if [ -z "$PY" ]; then
    if [ "$(uname -s)" = "Darwin" ]; then
        fail "Python 3.10 or newer was not found. Install it from https://www.python.org/downloads/ or run: brew install python"
    fi
    fail "Python 3.10 or newer was not found. Install it from https://www.python.org/downloads/ or your package manager, for example: sudo apt install python3 python3-venv"
fi

# 2. A private Python environment in .venv, installed once
if [ ! -d .venv ]; then
    echo "  Creating a private Python environment in .venv"
    "$PY" -m venv .venv || fail "Could not create .venv. On Debian or Ubuntu install it first: sudo apt install python3-venv"
fi
if [ -d .venv/bin ]; then VBIN=.venv/bin; else VBIN=.venv/Scripts; fi
if [ ! -x "$VBIN/python" ] && [ ! -x "$VBIN/python.exe" ]; then
    fail "The .venv folder is incomplete (it may come from another computer or Python version). Delete the .venv folder and run this again."
fi
if [ ! -x "$VBIN/receipts" ] && [ ! -x "$VBIN/receipts.exe" ]; then
    echo "  Installing Receipts and its packages. On a slow connection this takes a few minutes."
    "$VBIN/python" -m pip install --disable-pip-version-check -e . || fail "The install did not finish. Check your internet connection and run this again."
fi

# 3. Build the demo database if needed, start the command center and open the browser
export RECEIPTS_BACKEND=duckdb
echo
echo "  Starting the command center. Your browser opens when it is ready."
echo "  Keep this window open while you use it. Press Ctrl+C here to stop."
echo
"$VBIN/receipts" demo --lab || fail "Receipts stopped with an error. The messages above say why."
