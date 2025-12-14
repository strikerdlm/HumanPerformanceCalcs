from __future__ import annotations

import math

import pytest

from calculators import (
    simulate_mitler_trajectory,
    simulate_phs_trajectory,
)


def test_simulate_phs_trajectory_is_bounded_and_monotone_time() -> None:
    traj = simulate_phs_trajectory(
        metabolic_rate_w_m2=420.0,
        air_temperature_C=32.0,
        mean_radiant_temperature_C=38.0,
        relative_humidity_percent=55.0,
        air_velocity_m_s=0.6,
        clothing_insulation_clo=0.9,
        exposure_minutes=60.0,
        step_minutes=10.0,
        max_points=30,
    )

    assert len(traj.times_minutes) == len(traj.core_temperature_C)
    assert len(traj.times_minutes) >= 2
    assert traj.times_minutes[-1] == pytest.approx(60.0)
    assert all(b > a for a, b in zip(traj.times_minutes, traj.times_minutes[1:]))


def test_simulate_phs_trajectory_core_temperature_trend_in_heat_storage_case() -> None:
    # Choose parameters likely to yield positive heat storage.
    traj = simulate_phs_trajectory(
        metabolic_rate_w_m2=500.0,
        air_temperature_C=36.0,
        mean_radiant_temperature_C=45.0,
        relative_humidity_percent=70.0,
        air_velocity_m_s=0.2,
        clothing_insulation_clo=1.0,
        exposure_minutes=90.0,
        step_minutes=15.0,
        max_points=20,
    )

    # Core temperature should not decrease over time for this case.
    assert all(
        b >= a for a, b in zip(traj.core_temperature_C, traj.core_temperature_C[1:])
    )

    # In a stressful case, the model should report a finite allowable exposure.
    assert math.isfinite(traj.allowable_exposure_minutes)


def test_simulate_mitler_trajectory_returns_expected_grid() -> None:
    traj = simulate_mitler_trajectory(phi_hours=0.0, SD=2.0, K=2.0, horizon_hours=24.0, step_minutes=30.0)
    assert len(traj.times_hours) == len(traj.performance)
    assert traj.times_hours[0] == pytest.approx(0.0)
    assert traj.times_hours[-1] <= 24.0 + 1e-9
    assert all(b > a for a, b in zip(traj.times_hours, traj.times_hours[1:]))

    # The model should produce finite values.
    assert all(math.isfinite(v) for v in traj.performance)


def test_simulate_mitler_trajectory_validates_inputs() -> None:
    with pytest.raises(ValueError):
        _ = simulate_mitler_trajectory(phi_hours=0.0, SD=2.0, K=2.0, horizon_hours=0.0)

    with pytest.raises(ValueError):
        _ = simulate_mitler_trajectory(phi_hours=0.0, SD=2.0, K=2.0, step_minutes=0.0)

    with pytest.raises(ValueError):
        _ = simulate_mitler_trajectory(phi_hours=0.0, SD=0.0, K=2.0)

    with pytest.raises(ValueError):
        _ = simulate_mitler_trajectory(phi_hours=0.0, SD=2.0, K=0.0)
