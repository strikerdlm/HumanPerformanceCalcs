# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 15:29:03 2023

@author: Diego Malpica
"""
import math
from calculators.utils import get_float_input

def altitude_from_pressure(pressure, sea_level_pressure=1013.25):
    altitude_feet = (1 - (pressure / sea_level_pressure) ** (1/5.255)) * 145366.45
    altitude_meters = altitude_feet * 0.3048
    return altitude_meters

def meters_to_feet(meters):
    return meters * 3.28084

def calculate_parameters(barometric_pressure, FiO2=0.21, PACO2=40, PH2O=47, A_a_gradient=5, sea_level_pressure=1013.25, V_initial=1):
    # Calculate PAO2
    PAO2 = FiO2 * (barometric_pressure - PH2O) - (PACO2 / 0.8)

    # Calculate equivalent FiO2 at altitude
    FiO2_eq = FiO2 / (barometric_pressure / sea_level_pressure)

    # Calculate PaO2
    PaO2 = PAO2 - A_a_gradient

    # Calculate SpO2 using a model or lookup table
    # Replace this function with an actual model or lookup table
# =============================================================================
# def SpO2_from_PaO2(PaO2):
#     return 95  # Placeholder value, should be replaced with an actual calculation
# 
# SpO2 = SpO2_from_PaO2(PaO2)
# =============================================================================

# Calculate wet bubble volume expansion
    P_initial = sea_level_pressure
    P_final = barometric_pressure
    V_exp = V_initial * (P_initial / P_final)

    return PAO2, FiO2_eq, PaO2, V_exp

def main():
    print("\nAltitude Calculator (Barometric Method)")
    print("For research and educational use only. Not for operational or clinical decision-making.")
    print("-" * 60)
    try:
        barometric_pressure_mmHg = get_float_input("Please enter the barometric pressure in mmHg: ", min_value=100, max_value=800)
        barometric_pressure_hPa = barometric_pressure_mmHg * 1.33322
        altitude_meters = altitude_from_pressure(barometric_pressure_hPa)
        altitude_feet = meters_to_feet(altitude_meters)
        PAO2, FiO2_eq, PaO2, V_exp = calculate_parameters(barometric_pressure_hPa)
        print(f"Altitude: {altitude_meters:.2f} meters ({altitude_feet:.2f} feet)")
        print(f"PAO2: {PAO2:.2f} mmHg")
        print(f"Equivalent FiO2 at altitude: {FiO2_eq:.2f}")
        print(f"PaO2: {PaO2:.2f} mmHg")
        print(f"Expected volume expansion in a wet bubble at given altitude: {V_exp:.2f} L")
        print("\nNote: For research/educational use only. Consult qualified professionals for operational guidance.")
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()

