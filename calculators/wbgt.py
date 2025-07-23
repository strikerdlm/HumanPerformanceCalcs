"""
Wet Bulb Globe Temperature (WBGT) Calculator
Author: Diego Malpica

Usage:
    Provides functions to compute the WBGT index for indoor (no solar load) and outdoor
    (solar load) environments. Accepts measured natural wet-bulb temperature (T_nwb),
    globe temperature (T_g), and dry-bulb (ambient) temperature (T_db). If T_nwb is
    not available, a psychrometric wet-bulb temperature is estimated from dry-bulb
    temperature and relative humidity using the empirical formulation proposed by
    Stull (2011). This approximation is suitable for quick occupational screening
    but **should not** replace direct measurement for compliance purposes.

Scientific Basis:
    WBGT is defined in ISO 7243:2017 for the assessment of heat stress on humans.
    For indoor environments or outdoor settings without solar radiation:
        WBGT_in = 0.7·T_nwb + 0.3·T_g
    For outdoor environments with solar radiation:
        WBGT_out = 0.7·T_nwb + 0.2·T_g + 0.1·T_db

    Where:
        T_nwb : Natural wet-bulb temperature (°C)
        T_g   : Globe temperature (°C)
        T_db  : Dry-bulb (air) temperature (°C)

    Estimation of T_nwb (when not measured) follows:
        Stull, R. (2011). Wet-Bulb Temperature from Relative Humidity and Air
        Temperature. *Journal of Applied Meteorology and Climatology*, 50(11),
        2267–2269. https://doi.org/10.1175/JAMC-D-11-0143.1

    ⚠️  **Disclaimer**: The estimation of T_nwb introduces uncertainty. For legal
    or regulatory compliance (ISO 7243, ACGIH TLV®), direct instrument readings
    are required.
"""
from __future__ import annotations

import math

__all__ = [
    "psychrometric_wet_bulb",
    "wbgt_indoor",
    "wbgt_outdoor",
]

# -----------------------------------------------------------------------------
# Helper – Estimate natural/psychrometric wet-bulb temperature (°C)
# -----------------------------------------------------------------------------

def psychrometric_wet_bulb(T_db: float, RH: float) -> float:
    """Estimate the psychrometric wet-bulb temperature (°C).

    Parameters
    ----------
    T_db : float
        Dry-bulb temperature in degrees Celsius.
    RH : float
        Relative humidity in percent (0-100).

    Returns
    -------
    float
        Wet-bulb temperature (°C) estimated via Stull (2011).

    Notes
    -----
    Valid for 0 ≤ T_db ≤ 50 °C and 5 ≤ RH ≤ 99 %. Accuracy ±0.3 °C under typical
    conditions.
    """
    RH = max(0.0, min(float(RH), 100.0))
    T_db = float(T_db)

    # Convert RH to a fraction for the equation
    rh_frac = RH / 100.0

    # Stull (2011) empirical approximation
    T_wb = (
        T_db
        * math.atan(0.151977 * math.sqrt(rh_frac + 8.313659))
        + math.atan(T_db + rh_frac)
        - math.atan(rh_frac - 1.676331)
        + 0.00391838 * rh_frac ** 1.5 * math.atan(0.023101 * rh_frac)
        - 4.686035
    )
    return T_wb


# -----------------------------------------------------------------------------
# WBGT Calculations
# -----------------------------------------------------------------------------

def wbgt_indoor(T_nwb: float | None = None, T_g: float | None = None, *,
                T_db: float | None = None, RH: float | None = None) -> float:
    """Compute indoor WBGT (no solar load).

    Supply measured natural wet-bulb temperature (`T_nwb`) and globe
    temperature (`T_g`) when possible. If `T_nwb` is *None* but dry-bulb
    temperature (`T_db`) and relative humidity (`RH`) are provided, `T_nwb` will
    be estimated.

    Parameters
    ----------
    T_nwb : float | None
        Natural wet-bulb temperature (°C).
    T_g : float | None
        Globe temperature (°C). If *None*, `T_db` is used as a fallback (ISO
        7243 allows this conservative approximation).
    T_db : float | None, keyword-only
        Dry-bulb temperature (°C). Required when estimating `T_nwb` or when `T_g`
        is missing.
    RH : float | None, keyword-only
        Relative humidity (%) required for `T_nwb` estimation.

    Returns
    -------
    float
        WBGT in degrees Celsius.
    """
    # Derive T_nwb if absent and possible
    if T_nwb is None:
        if T_db is None or RH is None:
            raise ValueError("T_nwb missing – provide T_db and RH for estimation.")
        T_nwb = psychrometric_wet_bulb(T_db, RH)

    # Handle missing globe temperature
    if T_g is None:
        if T_db is None:
            raise ValueError("T_g missing – provide T_db as conservative proxy.")
        T_g = T_db  # Conservative assumption (ISO 7243 guidance)

    wbgt = 0.7 * T_nwb + 0.3 * T_g
    return wbgt


def wbgt_outdoor(T_nwb: float | None = None, T_g: float | None = None, *,
                 T_db: float, RH: float | None = None) -> float:
    """Compute outdoor WBGT (solar load).

    Same logic as :pyfunc:`wbgt_indoor`, but includes dry-bulb temperature term.

    Parameters
    ----------
    T_nwb : float | None
        Natural wet-bulb temperature (°C).
    T_g : float | None
        Globe temperature (°C).
    T_db : float (required)
        Dry-bulb temperature (°C).
    RH : float | None, keyword-only
        Relative humidity (%) required if `T_nwb` is to be estimated.

    Returns
    -------
    float
        WBGT in degrees Celsius.
    """
    if T_nwb is None:
        if RH is None:
            raise ValueError("T_nwb missing – provide RH for estimation.")
        T_nwb = psychrometric_wet_bulb(T_db, RH)

    if T_g is None:
        T_g = T_db  # Conservative fallback

    wbgt = 0.7 * T_nwb + 0.2 * T_g + 0.1 * T_db
    return wbgt