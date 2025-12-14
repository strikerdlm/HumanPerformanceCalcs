"""Cold water immersion survival time (hypothermia-limited guidance).

This module provides deterministic, transparent estimates of survival time during
cold water immersion based on published *survival time prediction* curves/equations.

Scope
-----
These estimates address **hypothermia-limited survival** only and do not replace
the earlier risks of:
- cold shock (first ~3–5 minutes)
- swimming failure (often < 30 minutes)
- drowning risk due to waves, exhaustion, panic, or loss of airway protection

Models implemented
------------------
1) **Hayward et al. (1975)** (water temperature only):
   A commonly-cited equation for survival time (minutes) vs water temperature.
   See PubMed record "Thermal balance and survival time prediction of man in cold water".

2) **Golden (1996) summary values** (fully clothed + lifejacket):
   Transport Canada TP 13822 (Survival in Cold Waters, 2003) cites:
   - 1 hour at 5°C
   - 2 hours at 10°C
   - 6 hours at 15°C
   We provide a simple piecewise-linear interpolation between these points.

References
----------
- Hayward, J. S., Eckerson, J. D., & Collis, M. L. (1975).
  Thermal balance and survival time prediction of man in cold water.
  Journal of Applied Physiology. PubMed ID: 1139445.
- Transport Canada (2003). TP 13822 – Survival in Cold Waters.
  (Quotes Golden, 1996 survival times for fully clothed men wearing lifejackets.)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final, Literal

__all__ = [
    "ColdWaterSurvivalEstimate",
    "cold_water_survival_hayward_1975_minutes",
    "cold_water_survival_golden_lifejacket_hours",
    "cold_water_survival",
]


ModelName = Literal["hayward_1975", "golden_lifejacket_tp13822"]


@dataclass(frozen=True, slots=True)
class ColdWaterSurvivalEstimate:
    """A survival time estimate for cold water immersion."""

    model: ModelName
    water_temperature_c: float
    survival_time_minutes: float
    notes: tuple[str, ...]

    @property
    def survival_time_hours(self) -> float:
        return self.survival_time_minutes / 60.0


def _is_finite_number(x: float) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


_HAYWARD_A: Final[float] = 15.0
_HAYWARD_B: Final[float] = 7.2
_HAYWARD_C: Final[float] = 0.0785
_HAYWARD_D: Final[float] = 0.0034


def cold_water_survival_hayward_1975_minutes(
    water_temperature_c: float,
    *,
    strict: bool = False,
) -> float:
    """Estimate survival time (minutes) from water temperature using Hayward et al. (1975).

    Equation
    --------
    \(t_s = 15 + 7.2 / (0.0785 - 0.0034 T_w)\)

    Validity / cautions
    -------------------
    The equation becomes singular at \(T_w = 0.0785 / 0.0034 ≈ 23.1°C\).
    In practice, interpret this model only for *cold* water. If `strict=True`,
    the function enforces 0–20°C as a conservative validity range.
    """
    if not _is_finite_number(water_temperature_c):
        raise TypeError("water_temperature_c must be a finite float")
    tw = float(water_temperature_c)

    if strict and not (0.0 <= tw <= 20.0):
        raise ValueError("Hayward (1975) equation should be used for 0–20°C water only")

    denom = _HAYWARD_C - _HAYWARD_D * tw
    if denom <= 0.0:
        raise ValueError("Hayward (1975) equation undefined for this water temperature (denominator <= 0)")
    minutes = _HAYWARD_A + (_HAYWARD_B / denom)
    if minutes <= 0.0:
        raise ValueError("Computed survival time is non-physical (<= 0 minutes)")
    return float(minutes)


_GOLDEN_POINTS: Final[tuple[tuple[float, float], ...]] = (
    (5.0, 1.0),
    (10.0, 2.0),
    (15.0, 6.0),
)


def cold_water_survival_golden_lifejacket_hours(
    water_temperature_c: float,
    *,
    strict: bool = False,
) -> float:
    """Estimate survival time (hours) for fully clothed persons wearing lifejackets.

    Source
    ------
    Transport Canada TP 13822 (2003) cites Golden (1996) with survival times:
    1h at 5°C, 2h at 10°C, 6h at 15°C.

    Method
    ------
    Piecewise-linear interpolation between the cited points.

    Notes
    -----
    This is a coarse guidance curve and does **not** include sea state, waves, wind,
    swimming activity, suit leakage, or individual physiology.
    """
    if not _is_finite_number(water_temperature_c):
        raise TypeError("water_temperature_c must be a finite float")
    tw = float(water_temperature_c)

    t_min, h_min = _GOLDEN_POINTS[0]
    t_mid, h_mid = _GOLDEN_POINTS[1]
    t_max, h_max = _GOLDEN_POINTS[2]

    if strict and not (t_min <= tw <= t_max):
        raise ValueError("Golden lifejacket curve supported for 5–15°C only")

    # Clamp outside range when not strict.
    if tw <= t_min:
        return float(h_min)
    if tw >= t_max:
        return float(h_max)

    if tw <= t_mid:
        # Interpolate between 5 and 10.
        frac = (tw - t_min) / (t_mid - t_min)
        return float(h_min + frac * (h_mid - h_min))

    # Interpolate between 10 and 15.
    frac = (tw - t_mid) / (t_max - t_mid)
    return float(h_mid + frac * (h_max - h_mid))


def cold_water_survival(
    water_temperature_c: float,
    *,
    model: ModelName = "hayward_1975",
    strict: bool = False,
) -> ColdWaterSurvivalEstimate:
    """Compute a survival time estimate for cold water immersion."""
    if model not in ("hayward_1975", "golden_lifejacket_tp13822"):
        raise ValueError("Unsupported model")
    tw = float(water_temperature_c)

    notes: list[str] = []
    notes.append("Hypothermia-limited guidance only (does not model cold shock/swim failure/drowning risk).")

    if model == "hayward_1975":
        minutes = cold_water_survival_hayward_1975_minutes(tw, strict=strict)
        notes.append("Hayward et al. (1975) temperature-only equation.")
        return ColdWaterSurvivalEstimate(
            model=model,
            water_temperature_c=tw,
            survival_time_minutes=float(minutes),
            notes=tuple(notes),
        )

    hours = cold_water_survival_golden_lifejacket_hours(tw, strict=strict)
    notes.append("Transport Canada TP 13822 (2003) cites Golden (1996): 1h@5°C, 2h@10°C, 6h@15°C (linear interp).")
    return ColdWaterSurvivalEstimate(
        model=model,
        water_temperature_c=tw,
        survival_time_minutes=float(hours * 60.0),
        notes=tuple(notes),
    )


