"""Unit tests for the predicted_heat_strain helper."""

from __future__ import annotations

import pytest

from calculators import PredictedHeatStrainResult, predicted_heat_strain


def test_predicted_heat_strain_trends() -> None:
    """Higher metabolic rates should demand more sweat and heat storage."""

    moderate = predicted_heat_strain(
        metabolic_rate_w_m2=350.0,
        air_temperature_C=32.0,
        mean_radiant_temperature_C=36.0,
        relative_humidity_percent=45.0,
        air_velocity_m_s=0.3,
        clothing_insulation_clo=0.8,
        exposure_minutes=60.0,
    )
    heavy = predicted_heat_strain(
        metabolic_rate_w_m2=500.0,
        air_temperature_C=32.0,
        mean_radiant_temperature_C=36.0,
        relative_humidity_percent=45.0,
        air_velocity_m_s=0.3,
        clothing_insulation_clo=0.8,
        exposure_minutes=60.0,
    )

    assert isinstance(moderate, PredictedHeatStrainResult)
    assert heavy.required_sweat_rate_L_per_h > moderate.required_sweat_rate_L_per_h
    assert heavy.predicted_core_temperature_C > moderate.predicted_core_temperature_C


def test_predicted_heat_strain_detects_limits() -> None:
    """Extremely hot/humid settings should cap allowable exposure."""

    result = predicted_heat_strain(
        metabolic_rate_w_m2=480.0,
        air_temperature_C=36.0,
        mean_radiant_temperature_C=45.0,
        relative_humidity_percent=70.0,
        air_velocity_m_s=0.2,
        clothing_insulation_clo=1.0,
        exposure_minutes=180.0,
    )

    assert result.allowable_exposure_minutes < 180.0
    assert result.limiting_factor in {"Core temperature limit", "Dehydration limit"}


def test_predicted_heat_strain_validates_inputs() -> None:
    """Relative humidity outside physical bounds must raise ValueError."""

    with pytest.raises(ValueError):
        predicted_heat_strain(
            metabolic_rate_w_m2=300.0,
            air_temperature_C=30.0,
            mean_radiant_temperature_C=30.0,
            relative_humidity_percent=120.0,
            air_velocity_m_s=0.5,
            clothing_insulation_clo=0.5,
            exposure_minutes=60.0,
        )
