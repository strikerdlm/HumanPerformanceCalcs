"""
Circadian and Sleep-Homeostatic Utilities
- Mitler performance model
- Two-Process model components (S and C)
- Jet lag recovery estimator
"""
from __future__ import annotations

import math

__all__ = [
    "mitler_performance",
    "homeostatic_waking",
    "homeostatic_sleep",
    "circadian_component",
    "jet_lag_days_to_adjust",
]


def mitler_performance(t_hours: float, phi_hours: float, SD: float, K: float) -> float:
    """Mitler's circadian performance model.

    P = 1/K [ K - cos^2(theta) * (1 - cos(theta)/SD)^2 ]
    where theta = 2π (t + φ) / 24

    Returns unitless performance (higher is better).
    """
    theta = 2.0 * math.pi * (float(t_hours) + float(phi_hours)) / 24.0
    c = math.cos(theta)
    denom = float(K) if K != 0 else 1.0
    value = (denom - (c ** 2) * (1.0 - c / float(SD)) ** 2) / denom
    return value


def homeostatic_waking(Sa: float, L: float, t_hours: float) -> float:
    """Homeostatic (waking) component: S = (Sa - L) e^{-0.0343 t} + L"""
    return (float(Sa) - float(L)) * math.exp(-0.0343 * float(t_hours)) + float(L)


def homeostatic_sleep(U: float, Sr: float, t_hours: float) -> float:
    """Homeostatic (sleep) component: S' = U - (U - Sr) e^{-0.381 t}"""
    return float(U) - (float(U) - float(Sr)) * math.exp(-0.381 * float(t_hours))


def circadian_component(M: float, t_hours: float, p_hours: float) -> float:
    """Circadian component: C = M · cos((t - p) · π/12)"""
    return float(M) * math.cos((float(t_hours) - float(p_hours)) * math.pi / 12.0)


def jet_lag_days_to_adjust(time_zones: int, direction: str) -> float:
    """Estimate days to adjust from jet lag by travel direction.

    Westward: ~90 minutes/day; Eastward: ~60 minutes/day.
    """
    tz = max(0, int(time_zones))
    direction_norm = (direction or "").strip().lower()
    minutes_per_day = 90.0 if "west" in direction_norm else 60.0
    total_minutes = tz * 60.0
    return total_minutes / minutes_per_day