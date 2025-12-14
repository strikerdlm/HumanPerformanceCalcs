from datetime import datetime

import pytest

from calculators.safte import (
    SafteInputs,
    SafteParameters,
    SleepEpisode,
    simulate_safte,
)


def test_awake_depletes_reservoir_linearly() -> None:
    p = SafteParameters()
    inputs = SafteInputs(
        start_datetime_local=datetime(2025, 1, 1, 8, 0, 0),
        horizon_minutes=60,
        step_minutes=10,
        sleep_episodes=tuple(),
        initial_reservoir_units=p.reservoir_capacity_rc,
        params=p,
    )
    series = simulate_safte(inputs)
    # 60 minutes awake at K=0.5 units/min => 30 units depleted.
    end = series.points[-1].reservoir_units
    assert end == pytest.approx(p.reservoir_capacity_rc - 30.0, abs=1e-9)


def test_sleep_has_fill_delay_then_fills() -> None:
    p = SafteParameters()
    # Sleep from t=0 to t=60 minutes.
    inputs = SafteInputs(
        start_datetime_local=datetime(2025, 1, 1, 23, 0, 0),
        horizon_minutes=60,
        step_minutes=5,
        sleep_episodes=(SleepEpisode(0.0, 60.0),),
        initial_reservoir_units=p.reservoir_capacity_rc - 200.0,
        params=p,
    )
    series = simulate_safte(inputs)
    # First 5 minutes: no change
    assert series.points[0].reservoir_units == pytest.approx(p.reservoir_capacity_rc - 200.0)
    assert series.points[1].reservoir_units == pytest.approx(p.reservoir_capacity_rc - 200.0)
    # After 10 minutes, reservoir should have increased (SI likely positive due to sleep debt term)
    assert series.points[2].reservoir_units > (p.reservoir_capacity_rc - 200.0)


def test_invalid_episode_order_raises() -> None:
    inputs = SafteInputs(
        start_datetime_local=datetime(2025, 1, 1, 0, 0, 0),
        horizon_minutes=120,
        step_minutes=10,
        sleep_episodes=(SleepEpisode(50.0, 60.0), SleepEpisode(40.0, 45.0)),
    )
    with pytest.raises(ValueError):
        _ = simulate_safte(inputs)


def test_horizon_must_be_divisible_by_step() -> None:
    inputs = SafteInputs(
        start_datetime_local=datetime(2025, 1, 1, 0, 0, 0),
        horizon_minutes=61,
        step_minutes=10,
        sleep_episodes=tuple(),
    )
    with pytest.raises(ValueError):
        _ = simulate_safte(inputs)


