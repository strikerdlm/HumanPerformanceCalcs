"""
Atmospheric Properties Calculator (ISA Model)
Author: Diego Malpica

Usage:
    Provides functions to compute standard atmospheric properties (temperature,
    pressure, density, pO2) and alveolar oxygen pressure at a given altitude.
    For educational and research use in aerospace medicine and physiology.

Scientific Source:
    - International Standard Atmosphere (ISA), ICAO Doc 7488-CD, 1993
    - Alveolar Gas Equation: West, J.B. (2012). Respiratory Physiology: The Essentials. 9th Edition.
"""
import math

# Physical constants
T0 = 288.15  # Sea-level standard temperature (K)
P0 = 101_325  # Sea-level standard pressure (Pa)
L = 0.0065  # Temperature lapse rate in the troposphere (K/m)
R = 8.31447  # Universal gas constant (J/(mol·K))
g = 9.80665  # Acceleration due to gravity (m/s²)
M = 0.0289644  # Molar mass of dry air (kg/mol)
FIO2_STANDARD = 0.2095  # Fraction of oxygen in dry air


def _to_meters(altitude_ft: float) -> float:
    """Convert feet to metres."""
    return altitude_ft * 0.3048


def standard_atmosphere(altitude_m: float | int) -> dict:
    """Return ISA properties up to ~32 km altitude.

    Segments implemented:
      - 0–11 km: Troposphere, lapse rate L = 0.0065 K/m
      - 11–20 km: Isothermal at T = 216.65 K
      - 20–32 km: Stratosphere, lapse rate L_s = -0.001 K/m (warming)
    """
    h = max(0.0, float(altitude_m))

    # Segment 0–11 km
    if h <= 11_000.0:
        T = T0 - L * h
        P = P0 * (T / T0) ** (g * M / (R * L))
    else:
        # Precompute values at 11 km
        T11 = T0 - L * 11_000.0
        P11 = P0 * (T11 / T0) ** (g * M / (R * L))
        if h <= 20_000.0:
            # 11–20 km: isothermal
            T = T11
            P = P11 * math.exp(-g * M * (h - 11_000.0) / (R * T11))
        else:
            # 20–32 km: warming layer (L_s negative for increasing T with height)
            L_s = -0.001  # K/m
            # Conditions at 20 km
            T20 = T11
            P20 = P11 * math.exp(-g * M * (20_000.0 - 11_000.0) / (R * T11))
            # Temperature increases with altitude: T = T20 - L_s * (h - 20 km)
            T = T20 - L_s * (h - 20_000.0)
            P = P20 * (T / T20) ** (g * M / (R * L_s))

    rho = P * M / (R * T)
    pO2 = FIO2_STANDARD * P

    return {
        "temperature_C": T - 273.15,
        "pressure_Pa": P,
        "density_kg_m3": rho,
        "pO2_Pa": pO2,
    }


def alveolar_PO2(
    altitude_m: float | int,
    FiO2: float = 0.21,
    PaCO2: float = 40.0,
    RQ: float = 0.8,
) -> float:
    r"""Compute alveolar PAO₂ via the alveolar gas equation.

    All pressures in mmHg here for pedagogical familiarity.
    """
    # Barometric pressure from ISA
    Pb = standard_atmosphere(altitude_m)["pressure_Pa"] / 133.322  # Pa → mmHg
    PH2O = 47.0  # Water-vapour pressure at 37 °C (mmHg)
    PAO2 = FiO2 * (Pb - PH2O) - PaCO2 / RQ
    return PAO2


def spo2_unacclimatized(altitude_m: float) -> float:
    """Estimate oxygen saturation (SpO₂ %) for unacclimatized individuals vs altitude.

    Formula validated up to ~4164 m (Spanish mountaineers):
        SpO₂ = 98.8183 - 0.0001·h - 0.000001·h²
    where h is altitude in meters.

    Returns SpO₂ in percent, clamped to [50, 100].
    """
    h = max(0.0, float(altitude_m))
    spo2 = 98.8183 - 0.0001 * h - 0.000001 * (h ** 2)
    return max(50.0, min(100.0, spo2))


def spo2_acclimatized(altitude_m: float) -> float:
    """Estimate oxygen saturation (SpO₂ %) for acclimatized mountain dwellers vs altitude.

    Formula:
        SpO₂ = 98.2171 + 0.0012·h - 0.0000008·h²
    where h is altitude in meters.

    Returns SpO₂ in percent, clamped to [50, 100].
    """
    h = max(0.0, float(altitude_m))
    spo2 = 98.2171 + 0.0012 * h - 0.0000008 * (h ** 2)
    return max(50.0, min(100.0, spo2))


def pao2_at_altitude(PaO2_ground_mmHg: float, FEV1_percent: float) -> float:
    """Predict arterial oxygen pressure (PaO₂) at altitude from ground PaO₂ and FEV₁%.

    Best-performing regression:
        PaO₂_alt = 0.453·PaO₂_ground + 0.386·FEV₁(%) + 2.44

    Parameters use mmHg for PaO₂ and percent for FEV₁.
    """
    return 0.453 * float(PaO2_ground_mmHg) + 0.386 * float(FEV1_percent) + 2.44


def ams_probability(AAE_km_days: float) -> float:
    """Probability of Acute Mountain Sickness from Accumulated Altitude Exposure (AAE).

    Logistic model:
        logit = 2.188 - 0.5335·AAE
        p = 1 / (1 + e^{-logit})

    Returns probability in [0, 1].
    """
    import math

    logit = 2.188 - 0.5335 * float(AAE_km_days)
    p = 1.0 / (1.0 + math.exp(-logit))
    return max(0.0, min(1.0, p))


def ambient_pressure_mmHg_at_altitude(altitude_m: float) -> float:
    """Compute ambient barometric pressure (mmHg) at altitude using ISA segments."""
    return standard_atmosphere(altitude_m)["pressure_Pa"] / 133.322


def inspired_PO2(altitude_m: float, FiO2: float = 0.21, PH2O_mmHg: float = 47.0) -> float:
    """Inspired oxygen partial pressure PiO₂ (mmHg): PiO₂ = (Pb - PH₂O)·FiO₂.

    Pb is computed from ISA at given altitude.
    """
    Pb = ambient_pressure_mmHg_at_altitude(altitude_m)
    return max(0.0, (Pb - float(PH2O_mmHg)) * float(FiO2))


def oxygen_content(Hb_g_dL: float, SaO2: float, PaO2_mmHg: float) -> float:
    """Arterial oxygen content CaO₂ (mL O₂/dL blood).

    CaO₂ = (Hb × 1.34 × SaO₂) + (0.0031 × PaO₂)
    SaO₂ may be given as a fraction (0–1) or percent (0–100). This function
    accepts either; values > 1 are interpreted as percent.
    """
    hb = max(0.0, float(Hb_g_dL))
    sao2_in = float(SaO2)
    sao2_frac = sao2_in / 100.0 if sao2_in > 1.0 else max(0.0, min(1.0, sao2_in))
    pao2 = max(0.0, float(PaO2_mmHg))
    return hb * 1.34 * sao2_frac + 0.0031 * pao2
