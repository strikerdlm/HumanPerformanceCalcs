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
import math
from typing import Final

from .circadian import mitler_performance
from .phs import PredictedHeatStrainResult, predicted_heat_strain

__all__ = [
    "PHSTrajectory",
    "simulate_phs_trajectory",
    "MitlerTrajectory",
    "simulate_mitler_trajectory",
    "PHSSweep1D",
    "PHSSweep2D",
    "sweep_phs_metric_1d",
    "sweep_phs_metric_2d",
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
        Allowable exposure time (minutes) under the selected guardrails.

        Notes
        -----
        - This value is derived from the underlying model's limit calculations.
        - When no limit is reached within the simplified PHS model (e.g., zero
          heat storage and negligible sweat), this may be ``float('inf')``.
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

    allowable, limiting_factor = _phs_allowable_exposure_minutes(
        metabolic_rate_w_m2=float(metabolic_rate_w_m2),
        air_temperature_C=float(air_temperature_C),
        mean_radiant_temperature_C=float(mean_radiant_temperature_C),
        relative_humidity_percent=float(relative_humidity_percent),
        air_velocity_m_s=float(air_velocity_m_s),
        clothing_insulation_clo=float(clothing_insulation_clo),
        mechanical_power_w_m2=float(mechanical_power_w_m2),
        body_mass_kg=float(body_mass_kg),
        body_surface_area_m2=float(body_surface_area_m2),
        baseline_core_temp_C=float(baseline_core_temp_C),
        core_temp_limit_C=float(core_temp_limit_C),
        dehydration_limit_percent=float(dehydration_limit_percent),
    )

    return PHSTrajectory(
        times_minutes=tuple(times),
        core_temperature_C=tuple(core),
        dehydration_percent_body_mass=tuple(dehyd),
        required_sweat_rate_L_per_h=tuple(sw_req),
        max_sustainable_sweat_rate_L_per_h=tuple(sw_max),
        actual_sweat_rate_L_per_h=tuple(sw_act),
        allowable_exposure_minutes=float(allowable),
        limiting_factor=str(limiting_factor),
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
    if float(SD) <= 0.0:
        raise ValueError("SD must be > 0")
    if float(K) <= 0.0:
        raise ValueError("K must be > 0")

    max_n = int(max_points)
    if max_n < 2 or max_n > 200_000:
        raise ValueError("max_points must be between 2 and 200000")

    step_h = float(step_minutes) / 60.0
    horizon = float(horizon_hours)

    # Build a grid that always includes the horizon; do not silently truncate.
    n_full_steps = int(math.floor(horizon / step_h))
    times: list[float] = [i * step_h for i in range(n_full_steps + 1)]
    if times[-1] < horizon:
        times.append(horizon)
    if len(times) > max_n:
        raise ValueError(
            "Requested horizon/step would exceed max_points; increase step_minutes or max_points"
        )

    perf: list[float] = []
    for t_i in times:
        perf.append(float(mitler_performance(float(t_i), float(phi_hours), float(SD), float(K))))

    return MitlerTrajectory(times_hours=tuple(times), performance=tuple(perf))


@dataclass(slots=True, frozen=True)
class PHSSweep1D:
    """One-dimensional sweep for a chosen PHS-derived metric."""

    parameter_name: str
    parameter_unit: str
    parameter_values: tuple[float, ...]
    metric_name: str
    metric_unit: str
    metric_values: tuple[float, ...]


@dataclass(slots=True, frozen=True)
class PHSSweep2D:
    """Two-dimensional sweep (grid) for a chosen PHS-derived metric."""

    x_name: str
    x_unit: str
    x_values: tuple[float, ...]
    y_name: str
    y_unit: str
    y_values: tuple[float, ...]
    metric_name: str
    metric_unit: str
    z_values: tuple[tuple[float, ...], ...]  # shape: (len(y_values), len(x_values))


_PHS_PARAMETER_UNITS: Final[dict[str, str]] = {
    "metabolic_rate_w_m2": "W/m²",
    "air_temperature_C": "°C",
    "mean_radiant_temperature_C": "°C",
    "relative_humidity_percent": "%",
    "air_velocity_m_s": "m/s",
    "clothing_insulation_clo": "clo",
}

_PHS_METRIC_UNITS: Final[dict[str, str]] = {
    "allowable_exposure_minutes": "min",
    "core_temperature_C_at_horizon": "°C",
    "dehydration_percent_body_mass_at_horizon": "% body mass",
}


def _phs_allowable_exposure_minutes(
    *,
    metabolic_rate_w_m2: float,
    air_temperature_C: float,
    mean_radiant_temperature_C: float,
    relative_humidity_percent: float,
    air_velocity_m_s: float,
    clothing_insulation_clo: float,
    mechanical_power_w_m2: float,
    body_mass_kg: float,
    body_surface_area_m2: float,
    baseline_core_temp_C: float,
    core_temp_limit_C: float,
    dehydration_limit_percent: float,
    probe_minutes: float = 1_000_000.0,
    max_probe_minutes: float = 1_000_000_000.0,
    max_probe_steps: int = 6,
) -> tuple[float, str]:
    """Compute PHS allowable exposure with an unbounded/safe-case probe.

    Notes
    -----
    ``predicted_heat_strain`` caps allowable exposure to the requested duration when
    no limits are reached. To avoid reporting "allowable == horizon" for safe cases,
    this function probes a very large duration and interprets the model's "Input duration"
    limiting factor as effectively unbounded within the simplified model.
    """
    if probe_minutes <= 0.0:
        raise ValueError("probe_minutes must be > 0")
    if max_probe_minutes <= 0.0:
        raise ValueError("max_probe_minutes must be > 0")
    steps = int(max_probe_steps)
    if steps < 1 or steps > 20:
        raise ValueError("max_probe_steps must be between 1 and 20")

    # Bounded multi-probe to reduce the chance of incorrectly reporting "inf"
    # when the true limiting time is finite but very large.
    #
    # Strategy: probe at increasing durations until a non-"Input duration" limiting
    # factor is observed, or until max_probe_minutes/steps are exhausted.
    duration = float(min(float(probe_minutes), float(max_probe_minutes)))
    last_limiting = "Input duration"
    for _ in range(steps):
        probe = predicted_heat_strain(
            metabolic_rate_w_m2=float(metabolic_rate_w_m2),
            air_temperature_C=float(air_temperature_C),
            mean_radiant_temperature_C=float(mean_radiant_temperature_C),
            relative_humidity_percent=float(relative_humidity_percent),
            air_velocity_m_s=float(air_velocity_m_s),
            clothing_insulation_clo=float(clothing_insulation_clo),
            exposure_minutes=float(duration),
            mechanical_power_w_m2=float(mechanical_power_w_m2),
            body_mass_kg=float(body_mass_kg),
            body_surface_area_m2=float(body_surface_area_m2),
            baseline_core_temp_C=float(baseline_core_temp_C),
            core_temp_limit_C=float(core_temp_limit_C),
            dehydration_limit_percent=float(dehydration_limit_percent),
        )
        last_limiting = str(probe.limiting_factor)
        if last_limiting != "Input duration":
            return (float(probe.allowable_exposure_minutes), last_limiting)

        if duration >= float(max_probe_minutes):
            break
        duration = float(min(duration * 10.0, float(max_probe_minutes)))

    return (float("inf"), "No limit reached (model)")


def sweep_phs_metric_1d(
    *,
    sweep_parameter: str,
    start: float,
    stop: float,
    n_points: int,
    metric: str,
    # Base scenario (held constant during sweep)
    exposure_minutes: float,
    metabolic_rate_w_m2: float,
    air_temperature_C: float,
    mean_radiant_temperature_C: float,
    relative_humidity_percent: float,
    air_velocity_m_s: float,
    clothing_insulation_clo: float,
    mechanical_power_w_m2: float = 0.0,
    body_mass_kg: float = 75.0,
    body_surface_area_m2: float = 1.9,
    baseline_core_temp_C: float = 37.0,
    core_temp_limit_C: float = 38.5,
    dehydration_limit_percent: float = 5.0,
    max_evaluations: int = 2_500,
) -> PHSSweep1D:
    """Sweep a single PHS input parameter and compute a chosen metric.

    Parameters
    ----------
    sweep_parameter:
        One of: ``metabolic_rate_w_m2``, ``air_temperature_C``,
        ``mean_radiant_temperature_C``, ``relative_humidity_percent``,
        ``air_velocity_m_s``, ``clothing_insulation_clo``.
    metric:
        One of: ``allowable_exposure_minutes``, ``core_temperature_C_at_horizon``,
        ``dehydration_percent_body_mass_at_horizon``.

    Raises
    ------
    ValueError
        On unsupported parameter/metric, invalid ranges, or if the requested sweep
        would exceed ``max_evaluations``.
    """
    if sweep_parameter not in _PHS_PARAMETER_UNITS:
        raise ValueError(f"Unsupported sweep_parameter: {sweep_parameter}")
    if metric not in _PHS_METRIC_UNITS:
        raise ValueError(f"Unsupported metric: {metric}")

    n = int(n_points)
    if n < 2 or n > 2_000:
        raise ValueError("n_points must be between 2 and 2000")

    if float(exposure_minutes) <= 0.0:
        raise ValueError("exposure_minutes must be > 0")

    max_eval = int(max_evaluations)
    if max_eval < 1 or max_eval > 250_000:
        raise ValueError("max_evaluations must be between 1 and 250000")
    if n > max_eval:
        raise ValueError("Requested sweep exceeds max_evaluations")

    a = float(start)
    b = float(stop)
    if not (math.isfinite(a) and math.isfinite(b)):
        raise ValueError("start/stop must be finite")

    # Build inclusive grid.
    if n == 2:
        xs = (a, b)
    else:
        step = (b - a) / float(n - 1)
        xs_list: list[float] = []
        v = a
        for i in range(n):
            xs_list.append(float(v))
            v = a + float(i + 1) * step
        xs = tuple(xs_list)

    results: list[float] = []
    for x in xs:
        kwargs = {
            "metabolic_rate_w_m2": float(metabolic_rate_w_m2),
            "air_temperature_C": float(air_temperature_C),
            "mean_radiant_temperature_C": float(mean_radiant_temperature_C),
            "relative_humidity_percent": float(relative_humidity_percent),
            "air_velocity_m_s": float(air_velocity_m_s),
            "clothing_insulation_clo": float(clothing_insulation_clo),
        }
        kwargs[sweep_parameter] = float(x)

        if metric == "allowable_exposure_minutes":
            m, _ = _phs_allowable_exposure_minutes(
                metabolic_rate_w_m2=float(kwargs["metabolic_rate_w_m2"]),
                air_temperature_C=float(kwargs["air_temperature_C"]),
                mean_radiant_temperature_C=float(kwargs["mean_radiant_temperature_C"]),
                relative_humidity_percent=float(kwargs["relative_humidity_percent"]),
                air_velocity_m_s=float(kwargs["air_velocity_m_s"]),
                clothing_insulation_clo=float(kwargs["clothing_insulation_clo"]),
                mechanical_power_w_m2=float(mechanical_power_w_m2),
                body_mass_kg=float(body_mass_kg),
                body_surface_area_m2=float(body_surface_area_m2),
                baseline_core_temp_C=float(baseline_core_temp_C),
                core_temp_limit_C=float(core_temp_limit_C),
                dehydration_limit_percent=float(dehydration_limit_percent),
            )
            results.append(float(m))
            continue

        point = predicted_heat_strain(
            metabolic_rate_w_m2=float(kwargs["metabolic_rate_w_m2"]),
            air_temperature_C=float(kwargs["air_temperature_C"]),
            mean_radiant_temperature_C=float(kwargs["mean_radiant_temperature_C"]),
            relative_humidity_percent=float(kwargs["relative_humidity_percent"]),
            air_velocity_m_s=float(kwargs["air_velocity_m_s"]),
            clothing_insulation_clo=float(kwargs["clothing_insulation_clo"]),
            exposure_minutes=float(exposure_minutes),
            mechanical_power_w_m2=float(mechanical_power_w_m2),
            body_mass_kg=float(body_mass_kg),
            body_surface_area_m2=float(body_surface_area_m2),
            baseline_core_temp_C=float(baseline_core_temp_C),
            core_temp_limit_C=float(core_temp_limit_C),
            dehydration_limit_percent=float(dehydration_limit_percent),
        )
        if metric == "core_temperature_C_at_horizon":
            results.append(float(point.predicted_core_temperature_C))
        elif metric == "dehydration_percent_body_mass_at_horizon":
            results.append(float(point.dehydration_percent_body_mass))
        else:
            raise ValueError(f"Unsupported metric: {metric}")

    return PHSSweep1D(
        parameter_name=sweep_parameter,
        parameter_unit=_PHS_PARAMETER_UNITS[sweep_parameter],
        parameter_values=tuple(xs),
        metric_name=metric,
        metric_unit=_PHS_METRIC_UNITS[metric],
        metric_values=tuple(results),
    )


def sweep_phs_metric_2d(
    *,
    x_parameter: str,
    x_start: float,
    x_stop: float,
    x_points: int,
    y_parameter: str,
    y_start: float,
    y_stop: float,
    y_points: int,
    metric: str,
    # Base scenario (held constant during sweep)
    exposure_minutes: float,
    metabolic_rate_w_m2: float,
    air_temperature_C: float,
    mean_radiant_temperature_C: float,
    relative_humidity_percent: float,
    air_velocity_m_s: float,
    clothing_insulation_clo: float,
    mechanical_power_w_m2: float = 0.0,
    body_mass_kg: float = 75.0,
    body_surface_area_m2: float = 1.9,
    baseline_core_temp_C: float = 37.0,
    core_temp_limit_C: float = 38.5,
    dehydration_limit_percent: float = 5.0,
    max_evaluations: int = 2_500,
) -> PHSSweep2D:
    """Compute a bounded 2D sweep grid for a chosen PHS-derived metric."""
    if x_parameter not in _PHS_PARAMETER_UNITS:
        raise ValueError(f"Unsupported x_parameter: {x_parameter}")
    if y_parameter not in _PHS_PARAMETER_UNITS:
        raise ValueError(f"Unsupported y_parameter: {y_parameter}")
    if x_parameter == y_parameter:
        raise ValueError("x_parameter and y_parameter must be different")
    if metric not in _PHS_METRIC_UNITS:
        raise ValueError(f"Unsupported metric: {metric}")

    nx = int(x_points)
    ny = int(y_points)
    if nx < 2 or nx > 500 or ny < 2 or ny > 500:
        raise ValueError("x_points/y_points must be between 2 and 500")

    if float(exposure_minutes) <= 0.0:
        raise ValueError("exposure_minutes must be > 0")

    max_eval = int(max_evaluations)
    if max_eval < 1 or max_eval > 250_000:
        raise ValueError("max_evaluations must be between 1 and 250000")
    if nx * ny > max_eval:
        raise ValueError("Requested grid exceeds max_evaluations")

    xa = float(x_start)
    xb = float(x_stop)
    ya = float(y_start)
    yb = float(y_stop)
    if not all(math.isfinite(v) for v in (xa, xb, ya, yb)):
        raise ValueError("start/stop must be finite")

    def _linspace(a: float, b: float, n: int) -> tuple[float, ...]:
        if n == 2:
            return (float(a), float(b))
        step = (b - a) / float(n - 1)
        out: list[float] = []
        for i in range(n):
            out.append(float(a + float(i) * step))
        return tuple(out)

    xs = _linspace(xa, xb, nx)
    ys = _linspace(ya, yb, ny)

    base_kwargs = {
        "metabolic_rate_w_m2": float(metabolic_rate_w_m2),
        "air_temperature_C": float(air_temperature_C),
        "mean_radiant_temperature_C": float(mean_radiant_temperature_C),
        "relative_humidity_percent": float(relative_humidity_percent),
        "air_velocity_m_s": float(air_velocity_m_s),
        "clothing_insulation_clo": float(clothing_insulation_clo),
    }

    rows: list[tuple[float, ...]] = []
    for y in ys:
        row: list[float] = []
        for x in xs:
            kwargs = dict(base_kwargs)
            kwargs[x_parameter] = float(x)
            kwargs[y_parameter] = float(y)

            if metric == "allowable_exposure_minutes":
                m, _ = _phs_allowable_exposure_minutes(
                    metabolic_rate_w_m2=float(kwargs["metabolic_rate_w_m2"]),
                    air_temperature_C=float(kwargs["air_temperature_C"]),
                    mean_radiant_temperature_C=float(kwargs["mean_radiant_temperature_C"]),
                    relative_humidity_percent=float(kwargs["relative_humidity_percent"]),
                    air_velocity_m_s=float(kwargs["air_velocity_m_s"]),
                    clothing_insulation_clo=float(kwargs["clothing_insulation_clo"]),
                    mechanical_power_w_m2=float(mechanical_power_w_m2),
                    body_mass_kg=float(body_mass_kg),
                    body_surface_area_m2=float(body_surface_area_m2),
                    baseline_core_temp_C=float(baseline_core_temp_C),
                    core_temp_limit_C=float(core_temp_limit_C),
                    dehydration_limit_percent=float(dehydration_limit_percent),
                )
                row.append(float(m))
                continue

            point = predicted_heat_strain(
                metabolic_rate_w_m2=float(kwargs["metabolic_rate_w_m2"]),
                air_temperature_C=float(kwargs["air_temperature_C"]),
                mean_radiant_temperature_C=float(kwargs["mean_radiant_temperature_C"]),
                relative_humidity_percent=float(kwargs["relative_humidity_percent"]),
                air_velocity_m_s=float(kwargs["air_velocity_m_s"]),
                clothing_insulation_clo=float(kwargs["clothing_insulation_clo"]),
                exposure_minutes=float(exposure_minutes),
                mechanical_power_w_m2=float(mechanical_power_w_m2),
                body_mass_kg=float(body_mass_kg),
                body_surface_area_m2=float(body_surface_area_m2),
                baseline_core_temp_C=float(baseline_core_temp_C),
                core_temp_limit_C=float(core_temp_limit_C),
                dehydration_limit_percent=float(dehydration_limit_percent),
            )
            if metric == "core_temperature_C_at_horizon":
                row.append(float(point.predicted_core_temperature_C))
            elif metric == "dehydration_percent_body_mass_at_horizon":
                row.append(float(point.dehydration_percent_body_mass))
            else:
                raise ValueError(f"Unsupported metric: {metric}")

        rows.append(tuple(row))

    return PHSSweep2D(
        x_name=x_parameter,
        x_unit=_PHS_PARAMETER_UNITS[x_parameter],
        x_values=tuple(xs),
        y_name=y_parameter,
        y_unit=_PHS_PARAMETER_UNITS[y_parameter],
        y_values=tuple(ys),
        metric_name=metric,
        metric_unit=_PHS_METRIC_UNITS[metric],
        z_values=tuple(rows),
    )
