# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 15:29:03 2023

@author: Diego Malpica
"""
from calculators.utils import get_float_input

def altitude_from_pressure(
    pressure_hPa: float, sea_level_pressure_hPa: float = 1013.25
) -> float:
    """Altitude from barometric pressure using ISA tropospheric formula (0-11 km)."""
    altitude_feet = (
        1 - (pressure_hPa / sea_level_pressure_hPa) ** (1 / 5.255)
    ) * 145_366.45
    altitude_meters = altitude_feet * 0.3048
    return altitude_meters

def meters_to_feet(meters: float) -> float:
    return meters * 3.28084

def calculate_parameters(
    barometric_pressure_hPa: float,
    FiO2: float = 0.21,
    PaCO2_mmHg: float = 40.0,
    PH2O_mmHg: float = 47.0,
    A_a_gradient_mmHg: float = 5.0,
    sea_level_pressure_hPa: float = 1013.25,
    V_initial_L: float = 1.0,
    RQ: float = 0.8,
):
    """
    Calculate alveolar oxygen (PAO2), equivalent FiO2 at sea level, arterial PaO2,
    estimated SpO2, and Boyle's-law gas expansion.

    Inputs use SI for pressures (hPa), except gas equation terms in mmHg per
    clinical convention.
    """
    # Unit conversions
    hPa_per_mmHg = 1.33322
    Pb_mmHg = barometric_pressure_hPa / hPa_per_mmHg
    P0_mmHg = sea_level_pressure_hPa / hPa_per_mmHg

    # Alveolar gas equation (West)
    PAO2_mmHg = FiO2 * (Pb_mmHg - PH2O_mmHg) - (PaCO2_mmHg / RQ)

    # Equivalent FiO2 at SEA LEVEL to achieve the same PAO2 (accounting for PaCO2 term)
    # FiO2_eq = (PAO2 + PaCO2/RQ) / (P0 - PH2O)
    FiO2_eq_sea = max(0.0, min(1.0, (PAO2_mmHg + PaCO2_mmHg / RQ) / (P0_mmHg - PH2O_mmHg)))

    # Approximate arterial oxygen (simple A–a gradient subtraction)
    PaO2_mmHg = max(0.0, PAO2_mmHg - A_a_gradient_mmHg)

    # Estimate SpO2 (%) via Hill equation (simplified Severinghaus-like curve)
    def estimate_SpO2_from_PaO2(
        pao2_mmHg: float, P50: float = 26.8, n: float = 2.7
    ) -> float:
        if pao2_mmHg <= 0:
            return 0.0
        ratio = (pao2_mmHg ** n) / (pao2_mmHg ** n + P50 ** n)
        return max(0.0, min(100.0, 100.0 * ratio))

    SpO2_pct = estimate_SpO2_from_PaO2(PaO2_mmHg)

    # Boyle's law volume expansion for a trapped/wet bubble
    V_expansion_L = V_initial_L * (sea_level_pressure_hPa / barometric_pressure_hPa)

    return PAO2_mmHg, FiO2_eq_sea, PaO2_mmHg, SpO2_pct, V_expansion_L

def main():
    print("\nAltitude Calculator (Barometric Method)")
    print(
        "For research and educational use only. Not for operational or clinical "
        "decision-making."
    )
    print("-" * 60)
    try:
        barometric_pressure_mmHg = get_float_input(
            "Please enter the barometric pressure in mmHg: ", min_value=100, max_value=800
        )
        barometric_pressure_hPa = barometric_pressure_mmHg * 1.33322
        altitude_meters = altitude_from_pressure(barometric_pressure_hPa)
        altitude_feet = meters_to_feet(altitude_meters)
        PAO2, FiO2_eq, PaO2, SpO2, V_exp = calculate_parameters(barometric_pressure_hPa)
        print(f"Altitude: {altitude_meters:.2f} meters ({altitude_feet:.2f} feet)")
        print(f"PAO2: {PAO2:.2f} mmHg")
        print(f"Equivalent FiO2 at sea level for same PAO2: {FiO2_eq:.3f}")
        print(f"PaO2 (estimated): {PaO2:.2f} mmHg")
        print(f"Estimated SpO2: {SpO2:.0f}%")
        print(f"Expected volume expansion in a wet bubble at given altitude: {V_exp:.2f} L")
        print(
            "\nNote: For research/educational use only. Consult qualified professionals "
            "for operational guidance."
        )
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()