"""Guards for a public demo of lab mode on the stand-in (RECEIPTS_PUBLIC_DEMO=1).

A public lab demo lets strangers press Break, Reset and Run one attack. On top of the usual lab rules (synthetic
data only, normal mode keeps its write protection) this adds:

  rate limits   per client and for the whole server, on every action that writes to the database
  auto reset    tonight's batch is removed again after a few idle minutes, so the next visitor starts clean

Settings: RECEIPTS_DEMO_PER_MIN (per client, default 6), RECEIPTS_DEMO_GLOBAL_PER_MIN (default 30),
RECEIPTS_DEMO_RESET_MIN (default 10). The client is the first X-Forwarded-For address when a proxy sets it,
else the socket address; behind a proxy that does not set it, every visitor counts as one client.
"""

from __future__ import annotations

import os
import threading
import time
from collections import deque


def enabled() -> bool:
    return os.environ.get("RECEIPTS_PUBLIC_DEMO", "0") == "1"


class RateLimiter:
    def __init__(self, per_client: int, total: int, window: float = 60.0, clock=time.monotonic):
        self.per_client, self.total, self.window, self.clock = per_client, total, window, clock
        self.hits: dict[str, deque] = {}
        self.all: deque = deque()
        self.lock = threading.Lock()

    def _trim(self, q: deque, now: float) -> None:
        while q and now - q[0] >= self.window:
            q.popleft()

    def allow(self, client: str) -> tuple[bool, float]:
        """True if the client may act now; else False and the seconds until it may."""
        with self.lock:
            now = self.clock()
            q = self.hits.setdefault(client, deque())
            self._trim(q, now)
            self._trim(self.all, now)
            if len(q) >= self.per_client:
                return False, self.window - (now - q[0])
            if len(self.all) >= self.total:
                return False, self.window - (now - self.all[0])
            q.append(now)
            self.all.append(now)
            return True, 0.0


def limiter() -> RateLimiter:
    return RateLimiter(int(os.environ.get("RECEIPTS_DEMO_PER_MIN", "6")),
                       int(os.environ.get("RECEIPTS_DEMO_GLOBAL_PER_MIN", "30")))


def client_of(request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    return fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "unknown")


class AutoReset:
    """Calls `reset()` once the demo has been idle for `idle_min` minutes after an action."""

    def __init__(self, reset, idle_min: float, clock=time.monotonic):
        self.reset, self.idle, self.clock = reset, idle_min * 60, clock
        self.last_action: float | None = None

    def touched(self) -> None:
        self.last_action = self.clock()

    def tick(self) -> bool:
        if self.last_action is not None and self.clock() - self.last_action >= self.idle:
            self.last_action = None
            self.reset()
            return True
        return False

    def start(self, every: float = 30.0) -> threading.Thread:
        def loop():
            while True:
                time.sleep(every)
                try:
                    self.tick()
                except Exception:  # a failed reset is retried at the next action; the demo stays up
                    pass
        t = threading.Thread(target=loop, daemon=True)
        t.start()
        return t
