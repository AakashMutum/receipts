@echo off
rem Receipts on Exasol Personal, for Windows. Exasol must already be installed and running.
rem This script never installs anything for Exasol (no Podman, no Exasol).
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title Receipts on Exasol
echo.
echo   Receipts on Exasol Personal
echo.

rem 1. Find Python 3.10 or newer
set "PY="
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1 && set "PY=py -3"
if not defined PY python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1 && set "PY=python"
if not defined PY (
  echo   Python 3.10 or newer was not found.
  echo   Install it from https://www.python.org/downloads/
  echo   and tick "Add python.exe to PATH" in the installer, then double-click this file again.
  goto :fail
)

rem 2. Find the exasol launcher: PATH, then EXASOL_HOME, then Downloads
set "EXASOL="
for /f "delims=" %%i in ('where exasol 2^>nul') do if not defined EXASOL set "EXASOL=%%i"
if not defined EXASOL if defined EXASOL_HOME if exist "%EXASOL_HOME%\exasol.exe" set "EXASOL=%EXASOL_HOME%\exasol.exe"
if not defined EXASOL if exist "%USERPROFILE%\Downloads\exasol.exe" set "EXASOL=%USERPROFILE%\Downloads\exasol.exe"
if not defined EXASOL (
  echo   The exasol launcher was not found on PATH, in EXASOL_HOME or in your Downloads folder.
  echo   Get it from https://downloads.exasol.com/exasol-personal
  echo   then install and start the database as described in docs\RUN_GUIDE.md.
  goto :fail
)
echo   Using the launcher at !EXASOL!

rem 3. Is the database running? Read host and port when the launcher prints them.
set "INFO=%TEMP%\receipts_exasol_info.txt"
"!EXASOL!" info > "%INFO%" 2>&1
findstr /i /c:"State: running" "%INFO%" >nul || goto :not_running
rem info can still say running after the machine stopped, so ask status too
"!EXASOL!" status 2>&1 | findstr /i /c:"Status: stopped" >nul && goto :not_running
rem right after `exasol start` the port opens before logins work, so wait up to 3 minutes for ready
set /a TRIES=0
:wait_ready
"!EXASOL!" status 2>&1 | findstr /i /c:"database_ready" >nul && goto :ready
set /a TRIES+=1
if !TRIES! EQU 1 echo   Exasol is still starting. Waiting until it accepts connections.
if !TRIES! GEQ 36 (
  echo   Exasol did not report ready after 3 minutes. Trying anyway.
  goto :ready
)
ping -n 6 127.0.0.1 >nul
goto :wait_ready
:ready
set "EXA_HOST=127.0.0.1"
set "EXA_PORT=8563"
for /f "tokens=1,* delims=:" %%a in ('findstr /i /r /c:"^ *- *Server:" /c:"^ *Host:" "%INFO%"') do for /f "tokens=*" %%v in ("%%b") do set "EXA_HOST=%%v"
for /f "tokens=1,* delims=:" %%a in ('findstr /i /r /c:"^ *- *Port:" /c:"^ *Port:" "%INFO%"') do for /f "tokens=*" %%v in ("%%b") do set "EXA_PORT=%%v"
set "RECEIPTS_BACKEND=exasol"
set "EXA_DSN=!EXA_HOST!:!EXA_PORT!"
if not defined EXA_USER set "EXA_USER=sys"
if not defined EXA_PASSWORD set "EXA_PASSWORD=exasol"
echo   Exasol is running at !EXA_DSN!

rem 4. A private Python environment in .venv, installed once
if not exist ".venv\Scripts\python.exe" (
  echo   Creating a private Python environment in .venv
  %PY% -m venv .venv || goto :fail_venv
)
if not exist ".venv\Scripts\receipts.exe" (
  echo   Installing Receipts and its packages. On a slow connection this takes a few minutes.
  ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -e . || goto :fail_install
)

rem 5. Build inside Exasol, check it, then start the command center
echo.
echo   Building the data inside Exasol
".venv\Scripts\receipts.exe" init || goto :fail_run
".venv\Scripts\receipts.exe" doctor || goto :fail_doctor
echo.
echo   Starting the command center. Your browser opens when it is ready.
echo   Keep this window open while you use it. Press Ctrl+C here to stop.
echo.
".venv\Scripts\receipts.exe" demo || goto :fail_run
goto :end

:not_running
echo   Exasol is not running. Run: exasol start
echo   Then double-click run-exasol.bat again.
goto :fail

:fail_venv
echo   Could not create the .venv folder. Check that this folder is not read-only.
goto :fail

:fail_install
echo   The install did not finish. Check your internet connection and try again.
goto :fail

:fail_doctor
echo   receipts doctor found a problem. The lines marked above say what to fix.
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
