"""Bühlmann ZH-L16 decompression model with Gradient Factors (GF).

This module implements a deterministic, bounded Bühlmann ZH-L16 decompression engine
with Erik Baker-style Gradient Factors.

Scientific basis
----------------
The model is neo-Haldanian, computing inert gas loading per compartment using the
Schreiner equation and computing ascent ceilings using Bühlmann M-value parameters
modified by gradient factors.

Coefficient sources used here
-----------------------------
The ZH-L16B-GF and ZH-L16C-GF coefficient tables and the exact equation forms used
in this implementation are cross-checked against the published documentation and
source listings in the DecoTengu project:
- https://wrobell.dcmod.org/decotengu/_modules/decotengu/model.html
- https://wrobell.dcmod.org/decotengu/cmd.html

Important notes
---------------
- This module is intended for **educational and research use** only.
- It does NOT model bubble dynamics, micro-bubbles, or individual susceptibility.
- Always validate against operational procedures and professional guidance.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final, Iterable, Literal, Sequence

__all__ = [
    "GasMix",
    "DecompressionStop",
    "BuhlmannPlan",
    "plan_zh_l16_gf",
]


ModelVariant = Literal["zh-l16b-gf", "zh-l16c-gf"]


LOG_2: Final[float] = math.log(2.0)

# Water vapour pressure and depth-to-pressure conversion constants used in the
# reference implementation cited above (OSTC-style settings).
WATER_VAPOUR_PRESSURE_BAR: Final[float] = 0.0627
METER_TO_BAR: Final[float] = 0.09985


# ZH-L16B coefficient set (N2/He A/B and half-times).
_ZHL16B_N2_A: Final[tuple[float, ...]] = (
    1.1696, 1.0000, 0.8618, 0.7562, 0.6667, 0.5600, 0.4947, 0.4500,
    0.4187, 0.3798, 0.3497, 0.3223, 0.2850, 0.2737, 0.2523, 0.2327,
)
_ZHL16B_N2_B: Final[tuple[float, ...]] = (
    0.5578, 0.6514, 0.7222, 0.7825, 0.8126, 0.8434, 0.8693, 0.8910,
    0.9092, 0.9222, 0.9319, 0.9403, 0.9477, 0.9544, 0.9602, 0.9653,
)
_ZHL16B_HE_A: Final[tuple[float, ...]] = (
    1.6189, 1.3830, 1.1919, 1.0458, 0.9220, 0.8205, 0.7305, 0.6502,
    0.5950, 0.5545, 0.5333, 0.5189, 0.5181, 0.5176, 0.5172, 0.5119,
)
_ZHL16B_HE_B: Final[tuple[float, ...]] = (
    0.4770, 0.5747, 0.6527, 0.7223, 0.7582, 0.7957, 0.8279, 0.8553,
    0.8757, 0.8903, 0.8997, 0.9073, 0.9122, 0.9171, 0.9217, 0.9267,
)
_ZHL16B_N2_HALF_MIN: Final[tuple[float, ...]] = (
    5.0, 8.0, 12.5, 18.5, 27.0, 38.3, 54.3, 77.0, 109.0, 146.0, 187.0, 239.0, 305.0, 390.0, 498.0, 635.0,
)
_ZHL16B_HE_HALF_MIN: Final[tuple[float, ...]] = (
    1.88, 3.02, 4.72, 6.99, 10.21, 14.48, 20.53, 29.11, 41.20, 55.19, 70.69, 90.34, 115.29, 147.42, 188.24, 240.03,
)


# ZH-L16C coefficient set (N2/He A/B and half-times).
_ZHL16C_N2_A: Final[tuple[float, ...]] = (
    1.2599, 1.0000, 0.8618, 0.7562, 0.6200, 0.5043, 0.4410, 0.4000,
    0.3750, 0.3500, 0.3295, 0.3065, 0.2835, 0.2610, 0.2480, 0.2327,
)
_ZHL16C_N2_B: Final[tuple[float, ...]] = _ZHL16B_N2_B
_ZHL16C_HE_A: Final[tuple[float, ...]] = (
    1.7424, 1.3830, 1.1919, 1.0458, 0.9220, 0.8205, 0.7305, 0.6502,
    0.5950, 0.5545, 0.5333, 0.5189, 0.5181, 0.5176, 0.5172, 0.5119,
)
_ZHL16C_HE_B: Final[tuple[float, ...]] = (
    0.4245, 0.5747, 0.6527, 0.7223, 0.7582, 0.7957, 0.8279, 0.8553,
    0.8757, 0.8903, 0.8997, 0.9073, 0.9122, 0.9171, 0.9217, 0.9267,
)
_ZHL16C_N2_HALF_MIN: Final[tuple[float, ...]] = (
    4.0, 8.0, 12.5, 18.5, 27.0, 38.3, 54.3, 77.0, 109.0, 146.0, 187.0, 239.0, 305.0, 390.0, 498.0, 635.0,
)
_ZHL16C_HE_HALF_MIN: Final[tuple[float, ...]] = (
    1.51, 3.02, 4.72, 6.99, 10.21, 14.48, 20.53, 29.11, 41.20, 55.19, 70.69, 90.34, 115.29, 147.42, 188.24, 240.03,
)


@dataclass(frozen=True, slots=True)
class GasMix:
    """Breathing gas mix as fractions (0–1)."""

    o2: float
    he: float = 0.0

    @property
    def n2(self) -> float:
        return 1.0 - self.o2 - self.he


@dataclass(frozen=True, slots=True)
class DecompressionStop:
    depth_m: float
    minutes: int


@dataclass(frozen=True, slots=True)
class BuhlmannPlan:
    model: ModelVariant
    max_depth_m: float
    bottom_time_min: float
    gf_low: float
    gf_high: float
    surface_pressure_bar: float
    stops: tuple[DecompressionStop, ...]

    @property
    def total_decompression_minutes(self) -> int:
        return int(sum(s.minutes for s in self.stops))


def _is_finite(x: float) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def _validate_gf(gf: float, name: str) -> float:
    if not _is_finite(gf):
        raise TypeError(f"{name} must be a finite float")
    g = float(gf)
    if not (0.0 < g <= 1.5):
        raise ValueError(f"{name} must be in (0, 1.5]")
    return g


def _validate_depth(depth_m: float, name: str) -> float:
    if not _is_finite(depth_m):
        raise TypeError(f"{name} must be a finite float")
    d = float(depth_m)
    if d < 0.0:
        raise ValueError(f"{name} must be >= 0")
    return d


def _validate_pressure_bar(p_bar: float, name: str) -> float:
    if not _is_finite(p_bar):
        raise TypeError(f"{name} must be a finite float")
    p = float(p_bar)
    if p <= 0.0:
        raise ValueError(f"{name} must be > 0")
    return p


def _abs_pressure_bar(depth_m: float, surface_pressure_bar: float) -> float:
    return float(surface_pressure_bar + (float(depth_m) * METER_TO_BAR))


def _schreiner(p_i: float, p_alv: float, r: float, k: float, time_min: float) -> float:
    # P = P_alv + R*(t - 1/k) - (P_alv - P_i - R/k) * exp(-k*t)
    t = float(time_min)
    return float(p_alv + r * (t - 1.0 / k) - (p_alv - p_i - r / k) * math.exp(-k * t))


def _eq_gf_limit(gf: float, p_n2: float, p_he: float, a_n2: float, b_n2: float, a_he: float, b_he: float) -> float:
    # P_l = (P - A*gf) / (gf/B + 1 - gf) with mixed-gas A,B.
    g = _validate_gf(gf, "gf")
    p = float(p_n2) + float(p_he)
    if p <= 0.0:
        # If there is no inert gas loading, ceiling is unconstrained (return 0 bar).
        return 0.0
    a = (float(a_n2) * float(p_n2) + float(a_he) * float(p_he)) / p
    b = (float(b_n2) * float(p_n2) + float(b_he) * float(p_he)) / p
    return float((p - a * g) / (g / b + 1.0 - g))


def _coeffs_for_model(model: ModelVariant) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[float, ...]]:
    if model == "zh-l16b-gf":
        return (
            _ZHL16B_N2_A,
            _ZHL16B_N2_B,
            _ZHL16B_HE_A,
            _ZHL16B_HE_B,
            _ZHL16B_N2_HALF_MIN,
            _ZHL16B_HE_HALF_MIN,
        )
    if model == "zh-l16c-gf":
        return (
            _ZHL16C_N2_A,
            _ZHL16C_N2_B,
            _ZHL16C_HE_A,
            _ZHL16C_HE_B,
            _ZHL16C_N2_HALF_MIN,
            _ZHL16C_HE_HALF_MIN,
        )
    raise ValueError("Unsupported model variant")


def _k_constants(half_times_min: Sequence[float]) -> tuple[float, ...]:
    return tuple(LOG_2 / float(v) for v in half_times_min)


def _tissue_load_step(
    *,
    abs_p_bar: float,
    duration_min: float,
    rate_bar_per_min: float,
    gas: GasMix,
    water_vapour_pressure_bar: float,
    k_n2: Sequence[float],
    k_he: Sequence[float],
    tissues: Sequence[tuple[float, float]],
) -> tuple[tuple[float, float], ...]:
    if duration_min <= 0.0:
        raise ValueError("duration_min must be > 0")

    f_n2 = float(gas.n2)
    f_he = float(gas.he)
    if f_n2 < 0.0 or f_he < 0.0 or float(gas.o2) < 0.0:
        raise ValueError("Gas fractions must be >= 0")
    if (float(gas.o2) + f_he) >= 1.0:
        raise ValueError("Invalid gas mix: o2 + he must be < 1")

    p_alv_n2 = f_n2 * (float(abs_p_bar) - float(water_vapour_pressure_bar))
    p_alv_he = f_he * (float(abs_p_bar) - float(water_vapour_pressure_bar))
    r_n2 = f_n2 * float(rate_bar_per_min)
    r_he = f_he * float(rate_bar_per_min)

    out: list[tuple[float, float]] = []
    # Bounded loop: fixed number of compartments (16).
    for i, (p_n2, p_he) in enumerate(tissues):
        kn2 = float(k_n2[i])
        khe = float(k_he[i])
        out.append(
            (
                _schreiner(float(p_n2), p_alv_n2, r_n2, kn2, float(duration_min)),
                _schreiner(float(p_he), p_alv_he, r_he, khe, float(duration_min)),
            )
        )
    return tuple(out)


def _ceiling_limit_bar(
    *,
    gf: float,
    tissues: Sequence[tuple[float, float]],
    n2_a: Sequence[float],
    n2_b: Sequence[float],
    he_a: Sequence[float],
    he_b: Sequence[float],
) -> float:
    g = _validate_gf(gf, "gf")
    ceiling = 0.0
    for (p_n2, p_he), a_n2, b_n2, a_he, b_he in zip(tissues, n2_a, n2_b, he_a, he_b):
        lim = _eq_gf_limit(g, float(p_n2), float(p_he), float(a_n2), float(b_n2), float(a_he), float(b_he))
        if lim > ceiling:
            ceiling = lim
    return float(ceiling)


def _gf_at_ambient(
    *,
    amb_bar: float,
    surface_bar: float,
    first_stop_bar: float,
    gf_low: float,
    gf_high: float,
) -> float:
    # Linear interpolation: gf_low at first stop, gf_high at surface.
    if first_stop_bar <= surface_bar:
        return _validate_gf(gf_high, "gf_high")
    frac = (float(first_stop_bar) - float(amb_bar)) / (float(first_stop_bar) - float(surface_bar))
    frac = max(0.0, min(1.0, frac))
    return float(gf_low + frac * (gf_high - gf_low))


def _round_up_to_step(depth_m: float, step_m: float) -> float:
    if step_m <= 0.0:
        raise ValueError("step_m must be > 0")
    d = max(0.0, float(depth_m))
    return float(math.ceil(d / step_m) * step_m)


def plan_zh_l16_gf(
    *,
    max_depth_m: float,
    bottom_time_min: float,
    gas: GasMix,
    include_descent_in_bottom_time: bool = True,
    gf_low: float = 0.30,
    gf_high: float = 0.85,
    model: ModelVariant = "zh-l16c-gf",
    surface_pressure_bar: float = 1.01325,
    descent_rate_m_per_min: float = 20.0,
    ascent_rate_m_per_min: float = 10.0,
    stop_step_m: float = 3.0,
    max_stop_minutes: int = 240,
    max_total_runtime_minutes: int = 12 * 60,
) -> BuhlmannPlan:
    """Plan decompression stops for a square-profile dive using ZH-L16-GF.

    The dive profile is:
    - descent from surface to max depth at constant descent rate
    - bottom at max depth for bottom_time_min
    - ascent with 3 m step stops (or other step) until surfacing is allowed

    Returns a list of stops (depth, minutes). Gas is assumed constant for all phases
    in this initial implementation (nitrox/trimix fractions supported in tissue model).
    """
    depth = _validate_depth(max_depth_m, "max_depth_m")
    if not _is_finite(bottom_time_min):
        raise TypeError("bottom_time_min must be a finite float")
    bt = float(bottom_time_min)
    if bt <= 0.0:
        raise ValueError("bottom_time_min must be > 0")

    sp = _validate_pressure_bar(surface_pressure_bar, "surface_pressure_bar")
    if not _is_finite(descent_rate_m_per_min) or float(descent_rate_m_per_min) <= 0.0:
        raise ValueError("descent_rate_m_per_min must be > 0")
    if not _is_finite(ascent_rate_m_per_min) or float(ascent_rate_m_per_min) <= 0.0:
        raise ValueError("ascent_rate_m_per_min must be > 0")
    if not isinstance(max_stop_minutes, int) or max_stop_minutes <= 0:
        raise ValueError("max_stop_minutes must be a positive int")
    if not isinstance(max_total_runtime_minutes, int) or max_total_runtime_minutes <= 0:
        raise ValueError("max_total_runtime_minutes must be a positive int")

    gf_l = _validate_gf(gf_low, "gf_low")
    gf_h = _validate_gf(gf_high, "gf_high")
    if gf_h < gf_l:
        raise ValueError("gf_high must be >= gf_low")

    n2_a, n2_b, he_a, he_b, n2_half, he_half = _coeffs_for_model(model)
    k_n2 = _k_constants(n2_half)
    k_he = _k_constants(he_half)

    # Initialize tissues at surface equilibrium.
    start_p_n2 = 0.7902 * (sp - WATER_VAPOUR_PRESSURE_BAR)
    tissues: tuple[tuple[float, float], ...] = tuple((start_p_n2, 0.0) for _ in range(16))

    runtime = 0.0

    # Descent to max depth.
    descent_time = 0.0
    if depth > 0.0:
        descent_time = depth / float(descent_rate_m_per_min)
        if descent_time > 0.0:
            rate_bar_per_min = (depth * METER_TO_BAR) / descent_time  # positive
            tissues = _tissue_load_step(
                abs_p_bar=_abs_pressure_bar(0.0, sp),
                duration_min=descent_time,
                rate_bar_per_min=rate_bar_per_min,
                gas=gas,
                water_vapour_pressure_bar=WATER_VAPOUR_PRESSURE_BAR,
                k_n2=k_n2,
                k_he=k_he,
                tissues=tissues,
            )
            runtime += descent_time

    # Bottom time at depth.
    # NOTE: For compatibility with the reference decotengu `dt-lint` tool, the
    # CLI-style "40m for 35min" convention interprets the given time as the
    # runtime at max depth INCLUDING descent time. That is, time at depth is:
    #   t_depth = max(0, bottom_time_min - descent_time)
    t_depth = bt
    if include_descent_in_bottom_time:
        t_depth = max(0.0, bt - descent_time)

    if t_depth > 0.0:
        tissues = _tissue_load_step(
            abs_p_bar=_abs_pressure_bar(depth, sp),
            duration_min=t_depth,
            rate_bar_per_min=0.0,
            gas=gas,
            water_vapour_pressure_bar=WATER_VAPOUR_PRESSURE_BAR,
            k_n2=k_n2,
            k_he=k_he,
            tissues=tissues,
        )
        runtime += t_depth

    # Determine first stop depth using gf_low.
    surface_bar = sp

    # Ascent and decompression stops.
    stops: list[DecompressionStop] = []
    current_depth = depth

    def _ascend_to(target_depth_m: float) -> None:
        nonlocal tissues, runtime, current_depth
        d0 = current_depth
        d1 = float(target_depth_m)
        if d1 > d0:
            raise ValueError("Target depth must be <= current depth for ascent")
        if d1 == d0:
            return
        travel = d0 - d1
        t = travel / float(ascent_rate_m_per_min)
        # Pressure rate is negative during ascent.
        rate_bar_per_min = -((travel * METER_TO_BAR) / t)
        tissues = _tissue_load_step(
            abs_p_bar=_abs_pressure_bar(d0, sp),
            duration_min=t,
            rate_bar_per_min=rate_bar_per_min,
            gas=gas,
            water_vapour_pressure_bar=WATER_VAPOUR_PRESSURE_BAR,
            k_n2=k_n2,
            k_he=k_he,
            tissues=tissues,
        )
        runtime += t
        current_depth = d1

    # Find first decompression stop in discrete `stop_step_m` increments.
    # This mirrors common planner behavior and matches decotengu's first-stop validation:
    # the first stop should be shallow enough that going one more step shallower would
    # violate the GF-low ceiling.
    first_stop_depth_m = 0.0
    first_stop_bar = surface_bar

    step_m = float(stop_step_m)
    if not _is_finite(step_m) or step_m <= 0.0:
        raise ValueError("stop_step_m must be a positive float")

    # Determine first stop by simulating ascent to candidate stop depths on a grid
    # anchored at 0m, without "committing" intermediate ascents. Once found, perform
    # a single ascent segment to that stop.
    bottom_depth = current_depth
    bottom_tissues = tissues

    candidate = math.floor(bottom_depth / step_m) * step_m
    # Ensure first candidate is shallower than bottom depth when bottom isn't on grid.
    if candidate >= bottom_depth - 1e-12:
        candidate = max(0.0, candidate - step_m)

    def _simulate_ascent(from_depth: float, to_depth: float, tissues0: tuple[tuple[float, float], ...]) -> tuple[tuple[float, float], ...]:
        if to_depth >= from_depth:
            return tissues0
        travel = from_depth - to_depth
        t = travel / float(ascent_rate_m_per_min)
        rate_bar_per_min = -((travel * METER_TO_BAR) / t)
        return _tissue_load_step(
            abs_p_bar=_abs_pressure_bar(from_depth, sp),
            duration_min=t,
            rate_bar_per_min=rate_bar_per_min,
            gas=gas,
            water_vapour_pressure_bar=WATER_VAPOUR_PRESSURE_BAR,
            k_n2=k_n2,
            k_he=k_he,
            tissues=tissues0,
        )

    while candidate > 0.0:
        tissues_at_candidate = _simulate_ascent(bottom_depth, candidate, bottom_tissues)
        ceiling_bar = _ceiling_limit_bar(
            gf=gf_l,
            tissues=tissues_at_candidate,
            n2_a=n2_a,
            n2_b=n2_b,
            he_a=he_a,
            he_b=he_b,
        )
        next_candidate = max(0.0, candidate - step_m)
        next_amb = _abs_pressure_bar(next_candidate, sp)

        if next_candidate > 0.0 and next_amb >= ceiling_bar - 1e-12:
            candidate = next_candidate
            continue

        # Found first stop.
        first_stop_depth_m = candidate
        first_stop_bar = _abs_pressure_bar(first_stop_depth_m, sp)
        tissues = tissues_at_candidate
        # Commit ascent time to first stop in one segment.
        travel = bottom_depth - first_stop_depth_m
        runtime += travel / float(ascent_rate_m_per_min)
        current_depth = first_stop_depth_m
        break

    if first_stop_depth_m <= 0.0:
        # No stop found; check surfacing is allowed at GF-low.
        ceiling_at_surface = _ceiling_limit_bar(
            gf=gf_l,
            tissues=bottom_tissues,
            n2_a=n2_a,
            n2_b=n2_b,
            he_a=he_a,
            he_b=he_b,
        )
        if ceiling_at_surface <= surface_bar + 1e-12:
            return BuhlmannPlan(
                model=model,
                max_depth_m=depth,
                bottom_time_min=bt,
                gf_low=gf_l,
                gf_high=gf_h,
                surface_pressure_bar=sp,
                stops=tuple(),
            )
        # Conservative fallback: stop at the first grid depth above surface.
        first_stop_depth_m = step_m
        first_stop_bar = _abs_pressure_bar(first_stop_depth_m, sp)
        tissues = _simulate_ascent(bottom_depth, first_stop_depth_m, bottom_tissues)
        runtime += (bottom_depth - first_stop_depth_m) / float(ascent_rate_m_per_min)
        current_depth = first_stop_depth_m

    # Iterate decompression stops using a decotengu-style schedule:
    # - Each stop is guarded by the GF value of the *next* stop (or surface).
    # - We check if ascent is possible after 1 minute first, otherwise keep waiting.
    total_stop_minutes = 0

    p_step = step_m * METER_TO_BAR
    n_stops = int(round((first_stop_bar - surface_bar) / p_step))
    if n_stops <= 0:
        # Should not happen if first_stop_depth_m > 0, but keep safe.
        n_stops = 1
    gf_step = (gf_h - gf_l) / float(n_stops)

    safety_iterations = 0

    for stop_index in range(n_stops):
        safety_iterations += 1
        if safety_iterations > 500:
            raise RuntimeError("Decompression planning exceeded iteration budget")
        if runtime > float(max_total_runtime_minutes):
            raise RuntimeError("Decompression planning exceeded max_total_runtime_minutes")

        next_depth = max(0.0, current_depth - step_m)
        # GF for the *next* stop (or surface) using a stable formula (no accumulation).
        gf_next = gf_l + gf_step * float(stop_index + 1)
        if next_depth <= 0.0:
            gf_next = gf_h
        gf_next = max(gf_l, min(gf_h, float(gf_next)))

        # Required time to ascend by one stop step.
        travel = current_depth - next_depth
        time_to_next = 0.0 if travel <= 0.0 else (travel / float(ascent_rate_m_per_min))

        # Always wait at least 1 minute at the stop (discrete planner behavior).
        stop_minutes = 0
        while True:
            if stop_minutes >= max_stop_minutes:
                raise RuntimeError("Exceeded max_stop_minutes at decompression stops")
            if runtime > float(max_total_runtime_minutes):
                raise RuntimeError("Decompression planning exceeded max_total_runtime_minutes")

            tissues = _tissue_load_step(
                abs_p_bar=_abs_pressure_bar(current_depth, sp),
                duration_min=1.0,
                rate_bar_per_min=0.0,
                gas=gas,
                water_vapour_pressure_bar=WATER_VAPOUR_PRESSURE_BAR,
                k_n2=k_n2,
                k_he=k_he,
                tissues=tissues,
            )
            runtime += 1.0
            stop_minutes += 1
            total_stop_minutes += 1

            # Check ascent to next stop after 1+ minutes.
            next_amb = _abs_pressure_bar(next_depth, sp)
            ceiling_bar = _ceiling_limit_bar(
                gf=gf_next,
                tissues=tissues,
                n2_a=n2_a,
                n2_b=n2_b,
                he_a=he_a,
                he_b=he_b,
            )
            if next_amb >= ceiling_bar - 1e-12:
                break

        stops.append(DecompressionStop(depth_m=current_depth, minutes=stop_minutes))

        if next_depth <= 0.0:
            current_depth = 0.0
            break

        # Ascend one stop step and update tissues with Schreiner ascent.
        _ascend_to(next_depth)

    return BuhlmannPlan(
        model=model,
        max_depth_m=depth,
        bottom_time_min=bt,
        gf_low=gf_l,
        gf_high=gf_h,
        surface_pressure_bar=sp,
        stops=tuple(stops),
    )


