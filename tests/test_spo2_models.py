import pytest

from calculators.spo2_models import (
    SpO2Result,
    alt_var_spo2,
    compare_spo2_models,
    niermeyer_spo2,
    tushaus_cascade_spo2,
)


def test_niermeyer_reference_value_male() -> None:
    result = niermeyer_spo2(altitude_m=4000.0, sex="male")
    assert result.predicted_spo2 == pytest.approx(85.2, abs=1e-9)


def test_niermeyer_female_offset() -> None:
    male = niermeyer_spo2(altitude_m=4000.0, sex="male")
    female = niermeyer_spo2(altitude_m=4000.0, sex="female")
    assert female.predicted_spo2 - male.predicted_spo2 == pytest.approx(0.7, abs=1e-9)


def test_niermeyer_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        _ = niermeyer_spo2(altitude_m=-1.0, sex="male")
    with pytest.raises(ValueError):
        _ = niermeyer_spo2(altitude_m=1000.0, sex="other")  # type: ignore[arg-type]


def test_alt_var_reference_value() -> None:
    result = alt_var_spo2(
        altitude_m=4000.0,
        spo2_12h=88.0,
        spo2_24h=86.0,
        hr_12h=85.0,
        hr_24h=82.0,
    )
    assert result.predicted_spo2 == pytest.approx(78.4, abs=1e-9)


def test_alt_var_rejects_out_of_range_inputs() -> None:
    with pytest.raises(ValueError):
        _ = alt_var_spo2(
            altitude_m=9000.0,
            spo2_12h=88.0,
            spo2_24h=86.0,
            hr_12h=85.0,
            hr_24h=82.0,
        )
    with pytest.raises(ValueError):
        _ = alt_var_spo2(
            altitude_m=4000.0,
            spo2_12h=49.0,
            spo2_24h=86.0,
            hr_12h=85.0,
            hr_24h=82.0,
        )


def test_tushaus_monotonic_with_altitude() -> None:
    sea_level = tushaus_cascade_spo2(altitude_m=0.0)
    high_alt = tushaus_cascade_spo2(altitude_m=6000.0)
    assert sea_level.predicted_spo2 > high_alt.predicted_spo2


def test_tushaus_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        _ = tushaus_cascade_spo2(altitude_m=1000.0, fi_o2=0.05)
    with pytest.raises(ValueError):
        _ = tushaus_cascade_spo2(altitude_m=1000.0, temp_c=50.0)


def test_compare_spo2_models_returns_expected_structure() -> None:
    result = compare_spo2_models(altitude_m=3500.0, sex="female")
    assert set(result.keys()) == {"Niermeyer", "Tüshaus"}
    assert isinstance(result["Niermeyer"], SpO2Result)
    assert isinstance(result["Tüshaus"], SpO2Result)
