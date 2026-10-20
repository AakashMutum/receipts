"""Runtime configuration, read from environment variables.

RECEIPTS_BACKEND   exasol (default when EXA_DSN is set) or duckdb (local stand-in)
EXA_DSN            Exasol host:port, for example localhost:8563 (see `exasol info`)
EXA_USER           default sys
EXA_PASSWORD       default exasol (Exasol Personal local default)
EXA_INSECURE       1 to skip TLS certificate checks (self-signed local deployments)
RECEIPTS_DUCKDB    path of the DuckDB file in stand-in mode
RECEIPTS_DATA      directory for generated CSV files
ANTHROPIC_API_KEY  optional, enables the LLM explanation layer
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Settings:
    backend: str = field(default_factory=lambda: os.environ.get(
        "RECEIPTS_BACKEND", "exasol" if os.environ.get("EXA_DSN") else "duckdb").lower())
    exa_dsn: str = field(default_factory=lambda: os.environ.get("EXA_DSN", "localhost:8563"))
    exa_user: str = field(default_factory=lambda: os.environ.get("EXA_USER", "sys"))
    exa_password: str = field(default_factory=lambda: os.environ.get("EXA_PASSWORD", "exasol"))
    exa_insecure: bool = field(default_factory=lambda: os.environ.get("EXA_INSECURE", "1") == "1")
    duckdb_path: str = field(default_factory=lambda: os.environ.get(
        "RECEIPTS_DUCKDB", str(ROOT / "data" / "standin.duckdb")))
    data_dir: Path = field(default_factory=lambda: Path(os.environ.get("RECEIPTS_DATA", str(ROOT / "data"))))
    llm_key: str | None = field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY"))
    llm_model: str = field(default_factory=lambda: os.environ.get("RECEIPTS_LLM_MODEL", "claude-sonnet-5-5"))


def settings() -> Settings:
    return Settings()
