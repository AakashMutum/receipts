#!/usr/bin/env bash
# Receipts one-click demo for macOS: double-click this file in Finder.
# It runs run.sh in this folder and keeps the window open if anything goes wrong.
cd "$(dirname "$0")" || exit 1
bash ./run.sh
status=$?
if [ $status -ne 0 ]; then
    read -r -p "  Press Enter to close this window. " _
fi
exit $status
