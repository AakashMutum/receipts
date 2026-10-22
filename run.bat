@echo off
rem Receipts one-click demo for Windows. Needs only Python 3.10 or newer, no database to install.
setlocal EnableExtensions
cd /d "%~dp0"
title Receipts
echo.
echo   Receipts demo, using the local stand-in database
echo.

rem 1. Find Python 3.10 or newer
set "PY="
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1 && set "PY=py -3"
if not defined PY python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1 && set "PY=python"
if not defined PY (
  echo   Python 3.10 or newer was not found.
  echo   Install it from https://www.python.org/downloads/
  echo   and tick "Add python.exe to PATH" in the installer, then double-click run.bat again.
  goto :fail
)

rem 2. A private Python environment in .venv, installed once
if not exist ".venv\Scripts\python.exe" (
  echo   Creating a private Python environment in .venv
  %PY% -m venv .venv || goto :fail_venv
)
if not exist ".venv\Scripts\receipts.exe" (
  echo   Installing Receipts and its packages. On a slow connection this takes a few minutes.
  ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -e . || goto :fail_install
)

rem 3. Build the demo database if needed, start the command center and open the browser
set "RECEIPTS_BACKEND=duckdb"
echo.
echo   Starting the command center. Your browser opens when it is ready.
echo   Keep this window open while you use it. Press Ctrl+C here to stop.
echo.
".venv\Scripts\receipts.exe" demo || goto :fail_run
goto :end

:fail_venv
echo   Could not create the .venv folder. Check that this folder is not read-only.
goto :fail

:fail_install
echo   The install did not finish. Check your internet connection and double-click run.bat again.
goto :fail

:fail_run
echo   Receipts stopped with an error. The messages above say why.
goto :fail

:fail
echo.
echo   Setup did not finish.
pause
exit /b 1

:end
endlocal
