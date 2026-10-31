"""The one-click setup scripts, and the demo command they call."""

import shutil
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

from receipts import cli

ROOT = Path(__file__).resolve().parent.parent
WINDOWS = ["run.bat", "run-exasol.bat"]
UNIX = ["run.sh", "run-exasol.sh", "run.command", "run-exasol.command"]


@pytest.mark.parametrize("name", WINDOWS + UNIX)
def test_script_exists_without_em_dashes(name):
    text = (ROOT / name).read_text(encoding="utf-8")
    assert chr(0x2014) not in text
    assert "demo" in text or "run" in text


@pytest.mark.parametrize("name", UNIX)
def test_unix_scripts_have_shebang_and_lf(name):
    raw = (ROOT / name).read_bytes()
    assert raw.startswith(b"#!/usr/bin/env bash\n") and b"\r" not in raw


@pytest.mark.skipif(shutil.which("git") is None or not (ROOT / ".git").exists(), reason="needs a git checkout")
@pytest.mark.parametrize("name", UNIX)
def test_unix_scripts_are_executable_in_git(name):
    mode = subprocess.run(["git", "ls-files", "-s", name], cwd=ROOT, capture_output=True, text=True).stdout.split()
    assert mode and mode[0] == "100755", f"{name} is not marked executable in git"


@pytest.mark.parametrize("name", ["run-exasol.bat", "run-exasol.sh"])
def test_exasol_scripts_never_install_exasol(name):
    text = (ROOT / name).read_text(encoding="utf-8").lower()
    assert "exasol is not running. run: exasol start" in text
    for forbidden in ("winget install", "exasol install", "podman machine init", "apt install podman", "brew install podman"):
        assert forbidden not in text


@pytest.mark.parametrize("proxied", [False, True])
def test_demo_opens_the_browser_only_once_the_server_answers(monkeypatch, proxied):
    if proxied:  # a proxy that does not exist must not stop the check of the local server
        for var in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
            monkeypatch.setenv(var, "http://127.0.0.1:9")
        for var in ("NO_PROXY", "no_proxy"):
            monkeypatch.delenv(var, raising=False)
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"{}")

        def log_message(self, *a):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    url = f"http://127.0.0.1:{server.server_port}/"
    opened = threading.Event()
    monkeypatch.setattr("webbrowser.open", lambda u: opened.set() if u == url else None)
    cli._open_browser_when_up(url, timeout=10)
    assert not opened.wait(1.0)  # nothing answers yet
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        assert opened.wait(5.0)
    finally:
        server.shutdown()


@pytest.mark.parametrize("name", ["run.bat", "run-exasol.bat", "run.sh", "run-exasol.sh"])
def test_judge_facing_scripts_start_in_lab_mode(name):
    text = (ROOT / name).read_text(encoding="utf-8")
    assert "demo --lab" in text or "demo --watch --lab" in text
