from __future__ import annotations

"""Deterministic, bounded simulators built on calculator models.

This module provides small, explicit forward simulators that generate *time-indexed*
outputs from calculators that naturally support stepping over time (e.g., ISO 7933
Predicted Heat Strain, circadian performance envelopes).

Design goals
- Deterministic: identical inputs yield identical outputs.
- Bounded: every loop is explicitly bounded by max_points.
- Typed, explicit, analyzable: dataclasses with immutable tuples for results.

Notes on scientific validity
- The simulators here do **not** add new physiology beyond what the underlying
  calculator already encodes; they only sample it across time.
- For models that are *point estimators* (not time-series models), this module
  intentionally avoids inventing dynamics.
"""

from dataclasses import dataclass
from typing import Final

from .circadian import mitler_performance
from .phs import PredictedHeatStrainResult, predicted_heat_strain

__all__ = [
    "PHSTrajectory",
    "simulate_phs_trajectory",
    "MitlerTrajectory",
    "simulate_mitler_trajectory",
]


@dataclass(slots=True, frozen=True)
class PHSTrajectory:
    """Time-indexed outputs for Predicted Heat Strain (PHS).

    Attributes
    ----------
    times_minutes:
        Sample times in minutes (monotone increasing).
    core_temperature_C:
        Predicted core temperature at each time (°C).
    dehydration_percent_body_mass:
        Dehydration as percent body mass at each time (%).
    required_sweat_rate_L_per_h:
        Required sweat rate at each time (L/h).
    max_sustainable_sweat_rate_L_per_h:
        Max sustainable sweat rate at each time (L/h).
    actual_sweat_rate_L_per_h:
        Actual/effective sweat rate at each time (L/h).
    allowable_exposure_minutes:
        Allowable exposure time (minutes) at the final horizon.
    limiting_factor:
        Limiting factor (e.g., "Core temperature limit" or "Dehydration limit")
        at the final horizon.
    """

    times_minutes: tuple[float, ...]
    core_temperature_C: tuple[float, ...]
    dehydration_percent_body_mass: tuple[float, ...]
    required_sweat_rate_L_per_h: tuple[float, ...]
    max_sustainable_sweat_rate_L_per_h: tuple[float, ...]
    actual_sweat_rate_L_per_h: tuple[float, ...]
    allowable_exposure_minutes: float
    limiting_factor: str


_DEFAULT_MAX_POINTS: Final[int] = 720


def simulate_phs_trajectory(
    *,
    metabolic_rate_w_m2: float,
    air_temperature_C: float,
    mean_radiant_temperature_C: float,
    relative_humidity_percent: float,
    air_velocity_m_s: float,
    clothing_insulation_clo: float,
    exposure_minutes: float,
    step_minutes: float = 5.0,
    max_points: int = _DEFAULT_MAX_POINTS,
    mechanical_power_w_m2: float = 0.0,
    body_mass_kg: float = 75.0,
    body_surface_area_m2: float = 1.9,
    baseline_core_temp_C: float = 37.0,
    core_temp_limit_C: float = 38.5,
    dehydration_limit_percent: float = 5.0,
) -> PHSTrajectory:
    """Simulate PHS outputs across time up to ``exposure_minutes``.

    This function repeatedly calls :func:`calculators.phs.predicted_heat_strain`
    at bounded time steps. It does not introduce additional physiology.

    Raises
    ------
    ValueError
        If ``step_minutes`` is non-positive, the time grid would be empty, or
        the requested horizon would exceed the bounded ``max_points``.
    """

    if step_minutes <= 0.0:
        raise ValueError("step_minutes must be > 0")

    horizon = float(exposure_minutes)
    if horizon <= 0.0:
        raise ValueError("exposure_minutes must be > 0")

    max_n = int(max_points)
    if max_n < 2 or max_n > 50_000:
        raise ValueError("max_points must be between 2 and 50000")

    step = float(step_minutes)

    # Build a monotone time grid including the horizon.
    times: list[float] = []
    t = step
    for _ in range(max_n):
        if t >= horizon:
            break
        times.append(t)
        t += step

    times.append(horizon)

    if len(times) < 2:
        # This can happen if horizon < step; we still want 2 points for a chart.
        times = [horizon / 2.0, horizon]

    if len(times) > max_n:
        raise ValueError(
            "Requested horizon/step would exceed max_points; increase step_minutes or max_points"
        )

    core: list[float] = []
    dehyd: list[float] = []
    sw_req: list[float] = []
    sw_max: list[float] = []
    sw_act: list[float] = []

    last: PredictedHeatStrainResult | None = None
    for t_i in times:
        last = predicted_heat_strain(
            metabolic_rate_w_m2=float(metabolic_rate_w_m2),
            air_temperature_C=float(air_temperature_C),
            mean_radiant_temperature_C=float(mean_radiant_temperature_C),
            relative_humidity_percent=float(relative_humidity_percent),
            air_velocity_m_s=float(air_velocity_m_s),
            clothing_insulation_clo=float(clothing_insulation_clo),
            exposure_minutes=float(t_i),
            mechanical_power_w_m2=float(mechanical_power_w_m2),
            body_mass_kg=float(body_mass_kg),
            body_surface_area_m2=float(body_surface_area_m2),
            baseline_core_temp_C=float(baseline_core_temp_C),
            core_temp_limit_C=float(core_temp_limit_C),
            dehydration_limit_percent=float(dehydration_limit_percent),
        )
        core.append(float(last.predicted_core_temperature_C))
        dehyd.append(float(last.dehydration_percent_body_mass))
        sw_req.append(float(last.required_sweat_rate_L_per_h))
        sw_max.append(float(last.max_sustainable_sweat_rate_L_per_h))
        sw_act.append(float(last.actual_sweat_rate_L_per_h))

    if last is None:
        raise ValueError("Internal error: trajectory generation produced no points")

    return PHSTrajectory(
        times_minutes=tuple(times),
        core_temperature_C=tuple(core),
        dehydration_percent_body_mass=tuple(dehyd),
        required_sweat_rate_L_per_h=tuple(sw_req),
        max_sustainable_sweat_rate_L_per_h=tuple(sw_max),
        actual_sweat_rate_L_per_h=tuple(sw_act),
        allowable_exposure_minutes=float(last.allowable_exposure_minutes),
        limiting_factor=str(last.limiting_factor),
    )


@dataclass(slots=True, frozen=True)
class MitlerTrajectory:
    """Time-indexed circadian performance predictions (Mitler model)."""

    times_hours: tuple[float, ...]
    performance: tuple[float, ...]


def simulate_mitler_trajectory(
    *,
    phi_hours: float,
    SD: float,
    K: float,
    horizon_hours: float = 48.0,
    step_minutes: float = 10.0,
    max_points: int = 10_000,
) -> MitlerTrajectory:
    """Simulate Mitler performance over a bounded time grid."""

    if horizon_hours <= 0.0:
        raise ValueError("horizon_hours must be > 0")
    if step_minutes <= 0.0:
        raise ValueError("step_minutes must be > 0")

    max_n = int(max_points)
    if max_n < 2 or max_n > 200_000:
        raise ValueError("max_points must be between 2 and 200000")

    step_h = float(step_minutes) / 60.0
    horizon = float(horizon_hours)

    times: list[float] = []
    t = 0.0
    for _ in range(max_n):
        times.append(t)
        t += step_h
        if t > horizon:
            break

    if len(times) > max_n:
        raise ValueError("Time grid exceeded max_points")

    perf: list[float] = []
    for t_i in times:
        perf.append(float(mitler_performance(float(t_i), float(phi_hours), float(SD), float(K))))

    return MitlerTrajectory(times_hours=tuple(times), performance=tuple(perf))
