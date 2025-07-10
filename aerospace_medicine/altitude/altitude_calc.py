# -*- coding: utf-8 -*-
"""
Altitude Calculator (Barometric Method)
Updated for scientific accuracy and usability

@author: Diego Malpica

Calculates altitude from barometric pressure using the standard atmosphere model.
Used in aerospace medicine for altitude-related physiological assessments.
"""

import math
from calculators.utils import get_float_input

def altitude_from_pressure(pressure_hPa: float) -> float:
    """
    Calculate altitude from barometric pressure using the barometric formula.
    
    Args:
        pressure_hPa (float): Barometric pressure in hectopascals (hPa)
    
    Returns:
        float: Altitude in meters
    """
    # Standard atmosphere constants
    P0 = 1013.25  # Sea level pressure (hPa)
    T0 = 288.15   # Sea level temperature (K)
    L = 0.0065    # Temperature lapse rate (K/m)
    g = 9.80665   # Gravity (m/s²)
    R = 287.053   # Specific gas constant for dry air (J/(kg·K))
    
    # Barometric formula for troposphere (0-11 km)
    altitude_m = (T0 / L) * (1 - (pressure_hPa / P0) ** (R * L / g))
    
    return altitude_m

def meters_to_feet(meters: float) -> float:
    """Convert meters to feet."""
    return meters * 3.28084

def calculate_parameters(pressure_hPa: float) -> tuple:
    """
    Calculate physiological parameters at altitude.
    
    Args:
        pressure_hPa (float): Barometric pressure in hPa
    
    Returns:
        tuple: (PAO2, FiO2_equivalent, PaO2_estimate, volume_expansion)
    """
    # Alveolar oxygen partial pressure (simplified)
    # PAO2 = FiO2 * (Pb - PH2O) - PaCO2/R
    PH2O = 47  # Water vapor pressure at body temperature (mmHg)
    PaCO2 = 40  # Typical arterial CO2 (mmHg)
    R = 0.8    # Respiratory quotient
    FiO2 = 0.21  # Fraction of inspired oxygen
    
    # Convert pressure to mmHg
    pressure_mmHg = pressure_hPa * 0.750062
    
    # Calculate alveolar oxygen pressure
    PAO2 = FiO2 * (pressure_mmHg - PH2O) - (PaCO2 / R)
    
    # Equivalent FiO2 at sea level for same PAO2
    P_sea_level = 760  # mmHg
    FiO2_equivalent = (PAO2 + (PaCO2 / R)) / (P_sea_level - PH2O)
    
    # Estimate arterial oxygen (simplified)
    PaO2 = PAO2 - 10  # Approximate A-a gradient
    
    # Volume expansion factor (Boyle's law)
    volume_expansion = 1013.25 / pressure_hPa
    
    return PAO2, FiO2_equivalent, PaO2, volume_expansion

def interpret_altitude_effects(altitude_m: float, PAO2: float) -> str:
    """
    Interpret physiological effects of altitude.
    
    Args:
        altitude_m (float): Altitude in meters
        PAO2 (float): Alveolar oxygen pressure in mmHg
    
    Returns:
        str: Interpretation of altitude effects
    """
    altitude_ft = meters_to_feet(altitude_m)
    
    if altitude_ft < 8000:
        return "Sea level to moderate altitude - minimal physiological effects"
    elif altitude_ft < 12000:
        return "Moderate altitude - mild hypoxia, possible performance decrease"
    elif altitude_ft < 18000:
        return "High altitude - significant hypoxia, supplemental oxygen recommended"
    elif altitude_ft < 25000:
        return "Very high altitude - severe hypoxia, oxygen required"
    else:
        return "Extreme altitude - life-threatening hypoxia, pressurization required"

def main():
    """Main function to run the altitude calculator."""
    try:
        print("\nAltitude Calculator (Barometric Method)")
        print("For research and educational use only. Not for operational or clinical decision-making.")
        print("-" * 70)
        
        # Get barometric pressure input
        pressure_mmHg = get_float_input(
            "Barometric pressure (mmHg): ", 
            min_value=100, 
            max_value=800
        )
        
        # Convert to hPa for calculations
        pressure_hPa = pressure_mmHg * 1.33322
        
        # Calculate altitude
        altitude_m = altitude_from_pressure(pressure_hPa)
        altitude_ft = meters_to_feet(altitude_m)
        
        # Calculate physiological parameters
        PAO2, FiO2_eq, PaO2, V_exp = calculate_parameters(pressure_hPa)
        
        # Display results
        print(f"\n{'='*50}")
        print(f"ALTITUDE CALCULATION RESULTS")
        print(f"{'='*50}")
        
        print(f"\nInput:")
        print(f"Barometric pressure: {pressure_mmHg:.1f} mmHg ({pressure_hPa:.1f} hPa)")
        
        print(f"\nCalculated Altitude:")
        print(f"{altitude_m:.0f} meters ({altitude_ft:.0f} feet)")
        
        print(f"\nPhysiological Parameters:")
        print(f"Alveolar oxygen pressure (PAO2): {PAO2:.1f} mmHg")
        print(f"Equivalent FiO2 at sea level: {FiO2_eq:.3f} ({FiO2_eq*100:.1f}%)")
        print(f"Estimated arterial oxygen (PaO2): {PaO2:.1f} mmHg")
        print(f"Gas volume expansion factor: {V_exp:.2f}x")
        
        print(f"\nPhysiological Effects:")
        print(f"{interpret_altitude_effects(altitude_m, PAO2)}")
        
        # Safety warnings
        if altitude_ft > 12000:
            print(f"\n⚠️  WARNING: Altitude > 12,000 ft - hypoxia risk")
        if PAO2 < 60:
            print(f"⚠️  WARNING: Low alveolar oxygen - supplemental oxygen recommended")
        if V_exp > 2.0:
            print(f"⚠️  WARNING: Significant gas expansion - barotrauma risk")
        
        print(f"\nNote: Calculations based on standard atmosphere model.")
        print(f"For operational guidance, consult qualified aerospace medicine professionals.")
        
    except ValueError as e:
        print(f"Input error: {e}")
        return
    except KeyboardInterrupt:
        print("\nCalculation interrupted by user.")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return

if __name__ == "__main__":
    main() 