"""
Atmospheric Properties Calculator (ISA Model)
Author: Diego Malpica

Usage:
    Provides functions to compute standard atmospheric properties (temperature, pressure, density, pO2) and alveolar oxygen pressure at a given altitude.
    For educational and research use in aerospace medicine and physiology.

Scientific Source:
    - International Standard Atmosphere (ISA), ICAO Doc 7488-CD, 1993
    - Alveolar Gas Equation: West, J.B. (2012). Respiratory Physiology: The Essentials. 9th Edition.
"""
import math

# Physical constants
T0 = 288.15  # Sea-level standard temperature (K)
P0 = 101_325  # Sea-level standard pressure (Pa)
L  = 0.0065   # Temperature lapse rate in the troposphere (K/m)
R  = 8.31447  # Universal gas constant (J/(mol·K))
g  = 9.80665  # Acceleration due to gravity (m/s²)
M  = 0.0289644  # Molar mass of dry air (kg/mol)
FIO2_STANDARD = 0.2095  # Fraction of oxygen in dry air


def _to_meters(altitude_ft: float) -> float:
    """Convert feet to metres."""
    return altitude_ft * 0.3048


def standard_atmosphere(altitude_m: float | int) -> dict:
    """Return ISA properties up to ~32 km altitude.

    Parameters
    ----------
    altitude_m : float | int
        Geometric height above sea level in metres.

    Returns
    -------
    dict
        temperature_C : Ambient temperature in °C
        pressure_Pa   : Ambient pressure in pascals
        density_kg_m3 : Air density in kg/m³
        pO2_Pa        : Partial pressure of oxygen in pascals
    """
    altitude_m = max(0.0, float(altitude_m))

    # Troposphere (0–11 km): linear temperature lapse rate
    if altitude_m <= 11_000:
        T = T0 - L * altitude_m
        P = P0 * (T / T0) ** (g * M / (R * L))
    else:
        # Lower stratosphere isothermal layer (11–20 km)
        T11 = T0 - L * 11_000
        P11 = P0 * (T11 / T0) ** (g * M / (R * L))
        P = P11 * math.exp(-g * M * (altitude_m - 11_000) / (R * T11))
        T = T11  # remains constant in this layer

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
    """Compute alveolar \(\text{PAO₂}\) via the alveolar gas equation.

    All pressures in mmHg here for pedagogical familiarity.
    """
    # Barometric pressure from ISA
    Pb = standard_atmosphere(altitude_m)["pressure_Pa"] / 133.322  # Pa → mmHg
    PH2O = 47.0  # Water-vapour pressure at 37 °C (mmHg)
    PAO2 = FiO2 * (Pb - PH2O) - PaCO2 / RQ
    return PAO2