import math

import pytest

from calculators.utci import utci, utci_category


def test_utci_reference_cases() -> None:
    # Reference outputs are locked to the UTCI_approx polynomial implementation (Oct 2009).
    # Values were computed once and pinned to prevent regressions.
    cases = [
        ((30.0, 30.0, 0.5, 50.0), 30.409353008727415),
        ((0.0, 0.0, 1.0, 50.0), -0.8200674401509809),
        ((-10.0, -10.0, 5.0, 80.0), -27.47301349442383),
        ((35.0, 50.0, 2.0, 30.0), 37.95777127028817),
    ]
    for (ta, tr, v, rh), expected in cases:
        got = utci(ta, tr, v, rh)
        assert math.isfinite(got)
        assert got == pytest.approx(expected, rel=0.0, abs=1e-10)


def test_utci_category_thresholds() -> None:
    assert utci_category(47.0) == "Extreme heat stress"
    assert utci_category(46.0) == "Very strong heat stress"
    assert utci_category(38.1) == "Very strong heat stress"
    assert utci_category(38.0) == "Strong heat stress"
    assert utci_category(32.1) == "Strong heat stress"
    assert utci_category(32.0) == "Moderate heat stress"
    assert utci_category(26.1) == "Moderate heat stress"
    assert utci_category(26.0) == "No thermal stress"
    assert utci_category(9.1) == "No thermal stress"
    assert utci_category(9.0) == "Slight cold stress"
    assert utci_category(0.1) == "Slight cold stress"
    assert utci_category(0.0) == "Moderate cold stress"
    assert utci_category(-12.9) == "Moderate cold stress"
    assert utci_category(-13.0) == "Strong cold stress"
    assert utci_category(-26.9) == "Strong cold stress"
    assert utci_category(-27.0) == "Very strong cold stress"
    assert utci_category(-39.9) == "Very strong cold stress"
    assert utci_category(-40.0) == "Extreme cold stress"


def test_utci_strict_validation() -> None:
    with pytest.raises(ValueError):
        _ = utci(air_temperature_c=60.0, mean_radiant_temperature_c=60.0, wind_speed_10m_m_s=1.0, relative_humidity_percent=50.0, strict=True)
    with pytest.raises(ValueError):
        _ = utci(air_temperature_c=20.0, mean_radiant_temperature_c=200.0, wind_speed_10m_m_s=1.0, relative_humidity_percent=50.0, strict=True)
    with pytest.raises(ValueError):
        _ = utci(air_temperature_c=20.0, mean_radiant_temperature_c=20.0, wind_speed_10m_m_s=0.1, relative_humidity_percent=50.0, strict=True)
    with pytest.raises(ValueError):
        _ = utci(air_temperature_c=20.0, mean_radiant_temperature_c=20.0, wind_speed_10m_m_s=1.0, relative_humidity_percent=150.0, strict=True)


