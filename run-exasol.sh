#!/usr/bin/env bash
# Receipts on Exasol Personal, for Linux, and for macOS through run-exasol.command.
# Exasol must already be installed and running. This script never installs anything for Exasol.
# Exasol Personal runs locally on Apple Silicon Macs and on Linux with Podman. Intel Macs are not supported.
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
echo "  Receipts on Exasol Personal"
echo

case "$(uname -s)" in
    Darwin)
        if [ "$(uname -m)" != "arm64" ]; then
            fail "Exasol Personal runs locally only on Apple Silicon Macs. Intel Macs are not supported. Use run.command for the stand-in demo instead."
        fi ;;
    Linux)
        command -v podman >/dev/null 2>&1 || fail "Exasol Personal on Linux runs in Podman, which was not found. Install Podman and Exasol Personal first (see docs/RUN_GUIDE.md), or use run.sh for the stand-in demo." ;;
esac

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

# 2. Find the exasol launcher: PATH, then EXASOL_HOME, then Downloads
EXASOL=""
if command -v exasol >/dev/null 2>&1; then
    EXASOL="$(command -v exasol)"
elif [ -n "${EXASOL_HOME:-}" ] && [ -x "$EXASOL_HOME/exasol" ]; then
    EXASOL="$EXASOL_HOME/exasol"
elif [ -x "$HOME/Downloads/exasol" ]; then
    EXASOL="$HOME/Downloads/exasol"
fi
[ -n "$EXASOL" ] || fail "The exasol launcher was not found on PATH, in EXASOL_HOME or in ~/Downloads. Install it with: curl https://downloads.exasol.com/exasol-personal/installer.sh | sh"
echo "  Using the launcher at $EXASOL"

# 3. Is the database running? Read host and port when the launcher prints them.
INFO="$("$EXASOL" info 2>&1)"
echo "$INFO" | grep -qi "State: running" || fail "Exasol is not running. Run: exasol start"
# info can still say running after the machine stopped, so ask status too
if "$EXASOL" status 2>&1 | grep -qi "Status: stopped"; then fail "Exasol is not running. Run: exasol start"; fi
# right after `exasol start` the port opens before logins work, so wait up to 3 minutes for ready
for i in $(seq 1 36); do
    "$EXASOL" status 2>&1 | grep -qi "database_ready" && break
    [ "$i" -eq 1 ] && echo "  Exasol is still starting. Waiting until it accepts connections."
    [ "$i" -eq 36 ] && echo "  Exasol did not report ready after 3 minutes. Trying anyway." && break
    sleep 5
done
EXA_HOST="$(echo "$INFO" | tr -d '\r' | grep -iE '^[ -]*(server|host):' | head -n 1 | sed 's/^[^:]*:[ ]*//')"
EXA_PORT="$(echo "$INFO" | tr -d '\r' | grep -iE '^[ -]*port:' | head -n 1 | sed 's/^[^:]*:[ ]*//')"
export RECEIPTS_BACKEND=exasol
export EXA_DSN="${EXA_HOST:-127.0.0.1}:${EXA_PORT:-8563}"
export EXA_USER="${EXA_USER:-sys}"
export EXA_PASSWORD="${EXA_PASSWORD:-exasol}"
echo "  Exasol is running at $EXA_DSN"

# 4. A private Python environment in .venv, installed once
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

# 5. Build inside Exasol, check it, then start the command center
echo
echo "  Building the data inside Exasol"
"$VBIN/receipts" init || fail "Receipts stopped with an error. The messages above say why."
"$VBIN/receipts" doctor || fail "receipts doctor found a problem. The lines marked above say what to fix."
echo
echo "  Starting the command center. Your browser opens when it is ready."
echo "  Keep this window open while you use it. Press Ctrl+C here to stop."
echo
"$VBIN/receipts" demo --watch --lab || fail "Receipts stopped with an error. The messages above say why."
