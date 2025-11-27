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
from dataclasses import dataclass
from typing import Literal

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


# --- HAPE risk model (Suona et al., BMJ Open 2023;13:e074161) -----------------
#
# This implementation uses the **point-based nomogram** approach, digitized
# directly from Figure 2A of the paper. Each predictor contributes a number of
# points; the total is converted to probability via a logistic function
# calibrated to match the nomogram's "Total Points → Risk" scale.
#
# Point values (digitized from Figure 2A):
#   Age:  <25 → 12 pts;  25–34 → 20 pts;  34–46 → 0 pts;  >46 → 10 pts
#   Transport:  Airplane → 0 pts;  Vehicle → 40 pts;  Train → 70 pts
#   Fatigue:  No → 0 pts;  Yes → 10 pts
#   Cough:  No → 0 pts;  Yes → 20 pts
#   Expectoration (sputum):  No → 0 pts;  Yes → 18 pts
#   SpO₂:  points = (100 − SpO₂%) × 1.185   (calibrated so 73% → 32 pts)
#
# Total Points → Risk conversion (logistic):
#   logit = −1.85 + 0.0675 × TotalPoints
#   probability = 1 / (1 + exp(−logit))
#
# Paper's worked example: 27 yo, plane, fatigue+, cough+, sputum−, SpO₂=73%
#   → 12 + 0 + 10 + 20 + 0 + 32 = 74 pts … but paper states 54 pts.  The paper
#   text appears to omit cough points (states "cough (0 points)" despite patient
#   having cough).  Using the paper's explicit total of 54 pts → ~90% risk.

TransportMode = Literal["plane", "train", "vehicle"]


@dataclass(slots=True, frozen=True)
class HAPERiskResult:
    """Result of the Suona 2023 HAPE risk model (model 1 with SpO₂).

    Attributes
    ----------
    probability:
        Predicted probability of HAPE (0–1).
    total_points:
        Nomogram total points before conversion to probability.
    model_used:
        Identifier of the underlying model implementation.
    """

    probability: float
    total_points: float
    model_used: Literal["with_spo2"]


# --- Point assignments digitized from Figure 2A ---

_AGE_POINTS = {
    "<25": 12.0,
    "25-34": 20.0,
    "34-46": 0.0,
    ">46": 10.0,
}

_TRANSPORT_POINTS = {
    "plane": 0.0,
    "vehicle": 40.0,
    "train": 70.0,
}

_FATIGUE_POINTS = {False: 0.0, True: 10.0}
_COUGH_POINTS = {False: 0.0, True: 20.0}
_SPUTUM_POINTS = {False: 0.0, True: 18.0}

# SpO₂ scale factor calibrated so that 73% → 32 pts (from paper example)
_SPO2_SCALE = 32.0 / (100.0 - 73.0)  # ≈ 1.185


def _spo2_to_points(spo2_percent: float) -> float:
    """Convert SpO₂ percentage to nomogram points."""
    return max(0.0, (100.0 - spo2_percent) * _SPO2_SCALE)


def _age_to_category(age_years: float) -> str:
    """Map age in years to the nomogram category."""
    if age_years < 25:
        return "<25"
    elif age_years < 34:
        return "25-34"
    elif age_years <= 46:
        return "34-46"
    else:
        return ">46"


# Logistic conversion from Total Points to probability
# Calibrated from Figure 2A bottom scale:
#   ~40 pts → 0.7 risk,  ~60 pts → 0.9 risk
#   logit(0.7) ≈ 0.847,  logit(0.9) ≈ 2.197
#   slope = (2.197 − 0.847) / 20 = 0.0675
#   intercept = 0.847 − 0.0675×40 = −1.85

_LOGIT_INTERCEPT = -1.85
_LOGIT_SLOPE = 0.0675


def _points_to_probability(total_points: float) -> float:
    """Convert nomogram total points to HAPE probability."""
    logit = _LOGIT_INTERCEPT + _LOGIT_SLOPE * total_points
    return 1.0 / (1.0 + math.exp(-logit))


def hape_risk_suona2023(
    age_years: float,
    spo2_percent: float,
    transport_mode: TransportMode,
    fatigue: bool,
    cough: bool,
    sputum: bool,
) -> HAPERiskResult:
    """Estimate HAPE risk using Suona et al. 2023 nomogram (with SpO₂).

    Parameters
    ----------
    age_years:
        Age in years (study population ≥14 years).
    spo2_percent:
        Peripheral oxygen saturation (SpO₂) in percent at altitude.
    transport_mode:
        Mode of travel to high altitude: "plane", "train" or "vehicle".
    fatigue:
        True if the patient reports fatigue.
    cough:
        True if the patient reports cough of any kind.
    sputum:
        True if the patient reports coughing sputum (white or pink, foamy).

    Returns
    -------
    HAPERiskResult
        Dataclass with probability in [0, 1], total nomogram points, and
        model identifier.

    Notes
    -----
    - Point values are digitized from Figure 2A of Suona et al. (BMJ Open
      2023;13:e074161).
    - The Total Points → probability conversion is calibrated to match the
      nomogram's risk scale.
    - This implementation is intended for educational and research use and
      should not be used for clinical decision-making without independent
      validation.
    """

    if age_years < 14.0:
        raise ValueError("age_years must be ≥ 14 (study inclusion criterion)")

    if not (0.0 < spo2_percent <= 100.0):
        raise ValueError("spo2_percent must be in the range (0, 100]")

    mode_norm = transport_mode.strip().lower()
    if mode_norm not in {"plane", "train", "vehicle"}:
        raise ValueError("transport_mode must be 'plane', 'train', or 'vehicle'")

    # If sputum is present, cough is implicitly present as well.
    if sputum and not cough:
        cough = True

    # Calculate points for each predictor
    age_cat = _age_to_category(age_years)
    pts_age = _AGE_POINTS[age_cat]
    pts_transport = _TRANSPORT_POINTS[mode_norm]
    pts_fatigue = _FATIGUE_POINTS[fatigue]
    pts_cough = _COUGH_POINTS[cough]
    pts_sputum = _SPUTUM_POINTS[sputum]
    pts_spo2 = _spo2_to_points(spo2_percent)

    total_points = (
        pts_age + pts_transport + pts_fatigue + pts_cough + pts_sputum + pts_spo2
    )

    prob = _points_to_probability(total_points)
    prob = max(0.0, min(1.0, prob))

    return HAPERiskResult(
        probability=prob, total_points=total_points, model_used="with_spo2"
    )


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
