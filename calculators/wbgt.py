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
from typing import Dict, Any

__all__ = [
    "psychrometric_wet_bulb",
    "wbgt_indoor",
    "wbgt_outdoor",
    "heat_stress_index",
]

# -----------------------------------------------------------------------------
# Helper – Estimate natural/psychrometric wet-bulb temperature (°C)
# -----------------------------------------------------------------------------


def psychrometric_wet_bulb(T_db: float, RH: float, *, strict: bool = False) -> float:
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
    RH = float(RH)
    T_db = float(T_db)

    # Validity per Stull (2011)
    if strict:
        if not (0.0 <= T_db <= 50.0):
            raise ValueError("Stull wet-bulb valid for 0–50 °C dry-bulb only")
        if not (5.0 <= RH <= 99.0):
            raise ValueError("Stull wet-bulb valid for 5–99 % RH only")

    # Clamp to physical range when not strict
    RH = max(0.0, min(RH, 100.0))

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

def wbgt_indoor(
    T_nwb: float | None = None,
    T_g: float | None = None,
    *,
    T_db: float | None = None,
    RH: float | None = None,
    strict: bool = False,
    return_details: bool = False,
) -> float | Dict[str, Any]:
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
    estimated = False
    notes: list[str] = []

    if T_nwb is None:
        if T_db is None or RH is None:
            raise ValueError("T_nwb missing – provide T_db and RH for estimation.")
        T_nwb = psychrometric_wet_bulb(T_db, RH, strict=strict)
        estimated = True
        notes.append("T_nwb estimated via Stull (2011)")

    # Handle missing globe temperature
    if T_g is None:
        if T_db is None:
            raise ValueError("T_g missing – provide T_db as conservative proxy.")
        T_g = T_db  # Conservative assumption (ISO 7243 guidance)
        notes.append("T_g proxied by T_db (conservative)")

    wbgt = 0.7 * T_nwb + 0.3 * T_g
    if return_details:
        return {
            "wbgt_C": wbgt,
            "used_T_nwb": T_nwb,
            "used_T_g": T_g,
            "estimated_T_nwb": estimated,
            "notes": notes,
        }
    return wbgt



def wbgt_outdoor(
    T_nwb: float | None = None,
    T_g: float | None = None,
    *,
    T_db: float,
    RH: float | None = None,
    strict: bool = False,
    return_details: bool = False,
) -> float | Dict[str, Any]:
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
    estimated = False
    notes: list[str] = []

    if T_nwb is None:
        if RH is None:
            raise ValueError("T_nwb missing – provide RH for estimation.")
        T_nwb = psychrometric_wet_bulb(T_db, RH, strict=strict)
        estimated = True
        notes.append("T_nwb estimated via Stull (2011)")

    if T_g is None:
        T_g = T_db  # Conservative fallback
        notes.append("T_g proxied by T_db (conservative)")

    wbgt = 0.7 * T_nwb + 0.2 * T_g + 0.1 * T_db
    if return_details:
        return {
            "wbgt_C": wbgt,
            "used_T_nwb": T_nwb,
            "used_T_g": T_g,
            "estimated_T_nwb": estimated,
            "notes": notes,
        }
    return wbgt


# -----------------------------------------------------------------------------
# Heat Stress Index (HSI)
# -----------------------------------------------------------------------------

def _sat_vapor_pressure_kPa(T_C: float) -> float:
    """Saturation vapor pressure (kPa) via Tetens formula."""
    return 0.61078 * math.exp(17.27 * T_C / (T_C + 237.3))


def heat_stress_index(
    M_W_m2: float,
    T_db_C: float,
    RH_percent: float,
    air_speed_m_s: float,
    Wext_W_m2: float = 0.0,
    T_g_C: float | None = None,
) -> float:
    """Compute Heat Stress Index (HSI) as percentage.

    HSI = (Required Evaporation / Maximum Evaporation) × 100
    Required Evaporation ≈ max(0, M - W - (C + R))
    Maximum Evaporation ≈ h_e · (p_sat(T_skin) − p_air)

    Simplified heat balance with typical assumptions for educational use.
    """
    # Assumptions
    T_skin_C = 35.0
    emissivity = 0.95
    sigma = 5.670374419e-8
    T_r_C = T_g_C if T_g_C is not None else T_db_C

    # Convert to Kelvin
    TskK = T_skin_C + 273.15
    TrK = T_r_C + 273.15

    # Heat transfer coefficients
    v = max(0.0, float(air_speed_m_s))
    hc = max(2.5, 8.3 * (v ** 0.6))  # W/m²/K
    # Radiative coefficient around mean temp
    TmK = (TskK + TrK) / 2.0
    hr = 4.0 * emissivity * sigma * (TmK ** 3)  # W/m²/K

    # Convective and radiative heat exchange (positive = loss)
    C = hc * (T_skin_C - T_db_C)
    R = hr * (T_skin_C - T_r_C)

    # Required evaporation to balance
    M = float(M_W_m2)
    W = float(Wext_W_m2)
    E_req = max(0.0, M - W - (C + R))

    # Maximum evaporative capacity
    he = 16.5 * hc  # W/m²/kPa
    p_sk = _sat_vapor_pressure_kPa(T_skin_C)
    p_air = max(0.0, min(100.0, float(RH_percent))) / 100.0 * _sat_vapor_pressure_kPa(T_db_C)
    delta_p = max(0.0, p_sk - p_air)
    E_max = max(1e-6, he * delta_p)

    HSI = (E_req / E_max) * 100.0
    return HSI