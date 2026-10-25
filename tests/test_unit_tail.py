"""The unit detector's tail check: a unit change on a small share of a gateway, which leaves its median alone."""

import pytest

from receipts import detectors, gate
from receipts.faults import Scenario
from receipts.heldout import CASES, case_sql
from receipts.load import ingest, reset_raw

from .conftest import DAY


def _land(be, *sql):
    ingest(be, DAY, Scenario("t", "t", "", "PROVEN_FAULT", frozenset({"unit_scale"}), list(sql)))


def test_poisson_tail():
    assert detectors._poisson_sf(0, 3.0) == 1.0
    assert abs(detectors._poisson_sf(1, 0.5) - (1 - 2.718281828 ** -0.5)) < 1e-6
    # with no tail rows in the baseline (lambda floored at 0.5) it takes 8 rows to fire
    assert detectors._poisson_sf(8, 0.5) < detectors.TAIL_P < detectors._poisson_sf(7, 0.5)


def test_clean_batch_has_no_tail_hit(duck):
    _land(duck)
    f = detectors.run_all(duck, DAY, "local-shim")[0]
    assert not f.fired
    reset_raw(duck, DAY)


def test_two_percent_x100_on_the_small_gateway_is_proven(duck):
    _land(duck, case_sql("GW_C", 100, 0.02))
    c = gate.run(duck, DAY, write_back=False)
    reset_raw(duck, DAY)
    s = c["suspects"][0]
    assert s["fired"] and s["metrics"]["factor"] == 100 and s["slice"]["GATEWAY"] == "GW_C"
    assert "AMOUNT >" in s["correction_note"]  # only the rows in the far tail are divided
    assert c["verdict"] == "PROVEN_FAULT" and c["confirmed"] == ["unit_scale"]


@pytest.mark.parametrize("factor", [10, 1000])
def test_factor_is_recognised(duck, factor):
    _land(duck, case_sql("GW_A", factor, 0.05))
    f = detectors.run_all(duck, DAY, "local-shim")[0]
    reset_raw(duck, DAY)
    assert f.fired and f.metrics["factor"] == factor


def test_heldout_cases_are_frozen():
    # written before the fix: changing them would let the fix be tuned to them
    assert len(CASES) == 12 and {c[0] for c in CASES} == {"GW_A", "GW_B"}
    assert {c[1] for c in CASES} == {10, 1000} and {c[2] for c in CASES} == {0.02, 0.05, 0.10}
