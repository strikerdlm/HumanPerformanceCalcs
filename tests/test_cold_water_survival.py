import math

import pytest

from calculators.cold_water_survival import (
    cold_water_survival,
    cold_water_survival_golden_lifejacket_hours,
    cold_water_survival_hayward_1975_minutes,
)


def test_hayward_1975_reference_values() -> None:
    # Values pinned to our implementation of the published equation:
    # ts = 15 + 7.2 / (0.0785 - 0.0034 * Tw)
    v5 = cold_water_survival_hayward_1975_minutes(5.0, strict=True)
    v10 = cold_water_survival_hayward_1975_minutes(10.0, strict=True)
    assert v5 == pytest.approx(132.0731707317073, rel=0.0, abs=1e-12)
    assert v10 == pytest.approx(176.79775280898875, rel=0.0, abs=1e-12)


def test_hayward_strict_range_and_singularity() -> None:
    with pytest.raises(ValueError):
        _ = cold_water_survival_hayward_1975_minutes(-1.0, strict=True)
    with pytest.raises(ValueError):
        _ = cold_water_survival_hayward_1975_minutes(21.0, strict=True)
    # Denominator becomes non-positive near ~23.1°C.
    with pytest.raises(ValueError):
        _ = cold_water_survival_hayward_1975_minutes(23.2, strict=False)


def test_golden_lifejacket_interpolation() -> None:
    # TP 13822 cites Golden (1996): 1h@5°C, 2h@10°C, 6h@15°C.
    assert cold_water_survival_golden_lifejacket_hours(5.0) == pytest.approx(1.0, abs=0.0)
    assert cold_water_survival_golden_lifejacket_hours(10.0) == pytest.approx(2.0, abs=0.0)
    assert cold_water_survival_golden_lifejacket_hours(15.0) == pytest.approx(6.0, abs=0.0)
    assert cold_water_survival_golden_lifejacket_hours(7.5) == pytest.approx(1.5, abs=0.0)
    assert cold_water_survival_golden_lifejacket_hours(12.5) == pytest.approx(4.0, abs=0.0)


def test_cold_water_survival_wrapper() -> None:
    r1 = cold_water_survival(10.0, model="hayward_1975", strict=True)
    assert math.isfinite(r1.survival_time_minutes)
    assert r1.survival_time_minutes > 0

    r2 = cold_water_survival(10.0, model="golden_lifejacket_tp13822", strict=True)
    assert r2.survival_time_minutes == pytest.approx(120.0, abs=0.0)


