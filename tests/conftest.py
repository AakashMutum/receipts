from datetime import date
from pathlib import Path

import pytest

from receipts.datagen import GenConfig, generate
from receipts.db import DuckDBBackend, ExasolShadowBackend
from receipts.load import init_database

DAY = date(2026, 10, 20)


@pytest.fixture(scope="session")
def data_dir(tmp_path_factory) -> Path:
    d = tmp_path_factory.mktemp("data")
    generate(d, GenConfig(seed=5, orders_per_day=8000))
    return d


@pytest.fixture(scope="session")
def duck(data_dir):
    be = DuckDBBackend(":memory:")
    init_database(be, data_dir, log=lambda *a: None)
    return be


@pytest.fixture(scope="session")
def shadow(data_dir):
    be = ExasolShadowBackend(":memory:")
    init_database(be, data_dir, log=lambda *a: None)
    return be
