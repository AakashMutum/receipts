#!/usr/bin/env bash
# Receipts on Exasol Personal for macOS: double-click this file in Finder.
# Exasol Personal runs locally only on Apple Silicon Macs. Intel Macs are not supported.
# It runs run-exasol.sh in this folder and keeps the window open if anything goes wrong.
cd "$(dirname "$0")" || exit 1
bash ./run-exasol.sh
status=$?
if [ $status -ne 0 ]; then
    read -r -p "  Press Enter to close this window. " _
fi
exit $status
