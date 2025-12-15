from __future__ import annotations

import math

import pytest

from calculators import (
    simulate_mitler_trajectory,
    simulate_phs_trajectory,
    sweep_phs_metric_1d,
    sweep_phs_metric_2d,
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


def test_sweep_phs_metric_1d_returns_expected_shapes() -> None:
    sweep = sweep_phs_metric_1d(
        sweep_parameter="air_temperature_C",
        start=28.0,
        stop=40.0,
        n_points=7,
        metric="core_temperature_C_at_horizon",
        exposure_minutes=60.0,
        metabolic_rate_w_m2=420.0,
        air_temperature_C=32.0,
        mean_radiant_temperature_C=38.0,
        relative_humidity_percent=55.0,
        air_velocity_m_s=0.6,
        clothing_insulation_clo=0.9,
        max_evaluations=100,
    )
    assert len(sweep.parameter_values) == 7
    assert len(sweep.metric_values) == 7
    assert sweep.parameter_values[0] == pytest.approx(28.0)
    assert sweep.parameter_values[-1] == pytest.approx(40.0)
    assert all(math.isfinite(v) for v in sweep.metric_values)


def test_sweep_phs_metric_2d_returns_expected_grid_shape() -> None:
    grid = sweep_phs_metric_2d(
        x_parameter="air_temperature_C",
        x_start=28.0,
        x_stop=36.0,
        x_points=6,
        y_parameter="relative_humidity_percent",
        y_start=30.0,
        y_stop=70.0,
        y_points=5,
        metric="dehydration_percent_body_mass_at_horizon",
        exposure_minutes=60.0,
        metabolic_rate_w_m2=420.0,
        air_temperature_C=32.0,
        mean_radiant_temperature_C=38.0,
        relative_humidity_percent=55.0,
        air_velocity_m_s=0.6,
        clothing_insulation_clo=0.9,
        max_evaluations=1000,
    )
    assert len(grid.x_values) == 6
    assert len(grid.y_values) == 5
    assert len(grid.z_values) == 5
    assert all(len(row) == 6 for row in grid.z_values)


def test_sweep_phs_metric_enforces_max_evaluations() -> None:
    with pytest.raises(ValueError):
        _ = sweep_phs_metric_2d(
            x_parameter="air_temperature_C",
            x_start=20.0,
            x_stop=50.0,
            x_points=60,
            y_parameter="relative_humidity_percent",
            y_start=10.0,
            y_stop=100.0,
            y_points=60,
            metric="core_temperature_C_at_horizon",
            exposure_minutes=60.0,
            metabolic_rate_w_m2=420.0,
            air_temperature_C=32.0,
            mean_radiant_temperature_C=38.0,
            relative_humidity_percent=55.0,
            air_velocity_m_s=0.6,
            clothing_insulation_clo=0.9,
            max_evaluations=1000,
        )
