"""Altitude / hypoxia effects on visual acuity (empirical dynamic visual acuity model).

This module implements a small, transparent, empirical model for **dynamic visual acuity (DVA)**
under short-term hypobaric exposure using published group means (LogMAR) from:

- Wang, Y., et al. (2024). *Influence of short-term hypoxia exposure on dynamic visual acuity*.
  Frontiers in Neuroscience, 18:1428987. https://doi.org/10.3389/fnins.2024.1428987

The paper reports DVA LogMAR (mean ± SD) at multiple simulated altitudes and angular velocities
using a hypobaric chamber profile.

Scope and limitations (important)
---------------------------------
- This is an **empirical lookup/interpolation** based on one study’s cohort (healthy adults 20–24y).
- It is **not** a mechanistic oxygenation model (no PAO2/SpO2 curve), and it should not be used
  to predict clinical outcomes.
- The study uses a specific altitude-time protocol; outside the studied ranges we clamp inputs.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

__all__ = [
    "DvaEstimate",
    "estimate_dva_logmar_wang2024",
    "logmar_to_snellen_denominator",
]


@dataclass(frozen=True, slots=True)
class DvaEstimate:
    altitude_m: float
    time_at_altitude_min: float
    angular_velocity_deg_s: float
    logmar: float
    snellen_denominator_20ft: int


def _is_finite(x: float) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def _clamp(x: float, lo: float, hi: float) -> float:
    return float(max(lo, min(hi, x)))


def logmar_to_snellen_denominator(logmar: float) -> int:
    """Convert logMAR to an approximate Snellen denominator at 20 ft.

    MAR = 10^logMAR. Snellen is 20 / (20 * MAR).
    """
    lm = float(logmar)
    if not _is_finite(lm):
        raise TypeError("logmar must be a finite number")
    mar = 10.0 ** lm
    denom = int(round(20.0 * mar))
    return max(1, denom)


# Data extracted from Table 3 in Wang et al. (2024).
# Rows: altitude_m, time_at_altitude_min (0 or 30), Columns: angular velocity {20,40,60,80}
_VELS: Final[list[float]] = [20.0, 40.0, 60.0, 80.0]

_ROWS: Final[list[tuple[float, float, list[float]]]] = [
    (0.0, 0.0, [0.14, 0.13, 0.19, 0.18]),  # ground
    (3500.0, 0.0, [0.12, 0.16, 0.15, 0.13]),
    (3500.0, 30.0, [0.13, 0.14, 0.13, 0.16]),
    (4000.0, 0.0, [0.09, 0.15, 0.15, 0.16]),
    (4000.0, 30.0, [0.11, 0.12, 0.08, 0.13]),
    (4500.0, 0.0, [0.14, 0.16, 0.15, 0.13]),
    (4500.0, 30.0, [0.14, 0.17, 0.13, 0.15]),
]


def _interp_1d(x: float, x0: float, y0: float, x1: float, y1: float) -> float:
    if x1 == x0:
        return float(y0)
    t = (x - x0) / (x1 - x0)
    return float(y0 + t * (y1 - y0))


def _interp_velocity(values: list[float], vel: float) -> float:
    v = _clamp(float(vel), _VELS[0], _VELS[-1])
    for i in range(len(_VELS) - 1):
        v0 = _VELS[i]
        v1 = _VELS[i + 1]
        if v0 <= v <= v1:
            return _interp_1d(v, v0, float(values[i]), v1, float(values[i + 1]))
    return float(values[-1])


def _lookup_alt_time_points() -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for alt, tmin, _ in _ROWS:
        pts.append((alt, tmin))
    return pts


def estimate_dva_logmar_wang2024(
    *,
    altitude_m: float,
    time_at_altitude_min: float,
    angular_velocity_deg_s: float,
) -> DvaEstimate:
    """Estimate DVA (logMAR) using bilinear interpolation over (altitude, time) and linear over velocity.

    - altitude_m is clamped to [0, 4500]
    - time_at_altitude_min is clamped to [0, 30]
    - angular_velocity_deg_s is clamped to [20, 80]
    """
    alt = float(altitude_m)
    tmin = float(time_at_altitude_min)
    vel = float(angular_velocity_deg_s)
    if not (_is_finite(alt) and _is_finite(tmin) and _is_finite(vel)):
        raise TypeError("altitude_m, time_at_altitude_min, and angular_velocity_deg_s must be finite numbers")
    if alt < 0.0:
        raise ValueError("altitude_m must be >= 0")
    if tmin < 0.0:
        raise ValueError("time_at_altitude_min must be >= 0")
    if vel <= 0.0:
        raise ValueError("angular_velocity_deg_s must be > 0")

    alt = _clamp(alt, 0.0, 4500.0)
    tmin = _clamp(tmin, 0.0, 30.0)
    vel = _clamp(vel, 20.0, 80.0)

    # Build two time slices: 0 min and 30 min at each altitude (missing at 0m for 30 min; reuse ground).
    # Interpolate across altitude separately for t=0 and t=30, then interpolate across time.
    def slice_at_time(target_t: float) -> list[tuple[float, list[float]]]:
        alts: dict[float, list[float]] = {}
        for a, tm, vals in _ROWS:
            if tm == target_t:
                alts[a] = vals
        if target_t == 30.0 and 0.0 not in alts:
            # Not reported; treat ground as time-invariant for this empirical model.
            for a, tm, vals in _ROWS:
                if a == 0.0 and tm == 0.0:
                    alts[0.0] = vals
                    break
        return sorted(alts.items(), key=lambda kv: kv[0])

    def interp_over_alt(alt_m: float, rows: list[tuple[float, list[float]]]) -> float:
        # rows is sorted by altitude
        if alt_m <= rows[0][0]:
            return _interp_velocity(rows[0][1], vel)
        if alt_m >= rows[-1][0]:
            return _interp_velocity(rows[-1][1], vel)
        for i in range(len(rows) - 1):
            a0, v0 = rows[i]
            a1, v1 = rows[i + 1]
            if a0 <= alt_m <= a1:
                y0 = _interp_velocity(v0, vel)
                y1 = _interp_velocity(v1, vel)
                return _interp_1d(alt_m, a0, y0, a1, y1)
        return _interp_velocity(rows[-1][1], vel)

    row0 = slice_at_time(0.0)
    row30 = slice_at_time(30.0)
    y0 = interp_over_alt(alt, row0)
    y30 = interp_over_alt(alt, row30)
    y = _interp_1d(tmin, 0.0, y0, 30.0, y30)

    return DvaEstimate(
        altitude_m=float(alt),
        time_at_altitude_min=float(tmin),
        angular_velocity_deg_s=float(vel),
        logmar=float(y),
        snellen_denominator_20ft=logmar_to_snellen_denominator(float(y)),
    )


