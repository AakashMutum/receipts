"""Exasol's own statement timings in the case: read when available, labelled when not."""

from receipts import gate
from receipts.db import DuckDBBackend

from .conftest import DAY


class FakeExasol(DuckDBBackend):
    """The stand-in, but with statement ids and a statistics table like Exasol's EXA_SQL_LAST_DAY."""

    is_standin = False

    def __init__(self, be, stats=True):
        self.__dict__.update(be.__dict__)
        self.n, self.stats = 0, stats

    def query(self, sql):
        self.n += 1
        return super().query(sql)

    def execute(self, sql):
        self.n += 1
        return super().execute(sql)

    def server_marker(self):
        self.n += 1
        return self.n

    def server_stats(self, first, last):
        if not self.stats:
            return None
        return "EXA_STATISTICS.EXA_SQL_LAST_DAY", [
            {"stmt_id": i, "command_name": "SELECT", "duration": 0.002, "cpu": 50.0, "temp_db_ram_peak": i,
             "row_count": 1} for i in range(first + 1, last)]


def test_standin_says_na(duck):
    from receipts.load import ingest
    ingest(duck, DAY, "ist_utc")
    c = gate.run(duck, DAY, write_back=False)
    assert c["exasol_measured"]["source"] == "n/a"


def test_measured_by_exasol_per_step(duck):
    from receipts.load import ingest
    ingest(duck, DAY, "ist_utc")
    fake = FakeExasol(duck)
    c = gate.run(fake, DAY, write_back=False)
    m = c["exasol_measured"]
    assert m["source"] == "EXA_STATISTICS.EXA_SQL_LAST_DAY"
    assert [s["step"] for s in m["steps"]] == [t["step"] for t in c["timings"]]
    assert m["statements"] == sum(s["statements"] for s in m["steps"]) > 20
    assert abs(m["db_ms"] - m["statements"] * 2.0) < 0.5 and m["temp_ram_peak_mib"] > 0


def test_unreadable_statistics_fall_back_to_client_timing(duck):
    from receipts.load import ingest
    ingest(duck, DAY, "ist_utc")
    c = gate.run(FakeExasol(duck, stats=False), DAY, write_back=False)
    assert c["exasol_measured"]["source"] == "client" and "client-side" in c["exasol_measured"]["note"]
