# -*- coding: utf-8 -*-
"""
Physiological Strain Index (PSI) Calculator
Created on Wed Mar 29 07:34:30 2023
Updated for accuracy and usability

@author: Diego Malpica

Based on:
Moran, D.S., et al. (1998). A physiological strain index to evaluate heat stress. 
American Journal of Physiology, 275(1), R129-R134.

Used in aerospace medicine for heat stress assessment.
"""

import math
from calculators.utils import get_float_input

def physiological_strain_index(
    initial_core_temp: float,
    initial_heart_rate: float,
    final_core_temp: float,
    final_heart_rate: float,
    max_heart_rate: float = None,
    age: int = None
) -> float:
    """
    Calculate the Physiological Strain Index (PSI).

    PSI = 5 × (Tct - Tc0)/(39 - Tc0) + 5 × (HRt - HR0)/(180 - HR0)

    Where:
    - Tct, Tc0 = final and initial core temperatures (°C)
    - HRt, HR0 = final and initial heart rates (bpm)
    - 39°C = assumed maximum sustainable core temperature
    - 180 bpm = assumed maximum heart rate (can be adjusted)

    Args:
        initial_core_temp (float): Initial core temperature in °C
        initial_heart_rate (float): Initial heart rate in bpm
        final_core_temp (float): Final core temperature in °C
        final_heart_rate (float): Final heart rate in bpm
        max_heart_rate (float, optional): Maximum heart rate (default: 180 bpm)
        age (int, optional): Age for age-adjusted max HR calculation

    Returns:
        float: Physiological Strain Index (0-10 scale)

    Raises:
        ValueError: If inputs are outside physiological ranges
    """
    # Validate inputs
    if initial_core_temp < 35 or initial_core_temp > 40:
        raise ValueError("Initial core temperature must be between 35-40°C")
    
    if final_core_temp < 35 or final_core_temp > 42:
        raise ValueError("Final core temperature must be between 35-42°C")
    
    if initial_heart_rate < 40 or initial_heart_rate > 200:
        raise ValueError("Initial heart rate must be between 40-200 bpm")
    
    if final_heart_rate < 40 or final_heart_rate > 220:
        raise ValueError("Final heart rate must be between 40-220 bpm")
    
    # Determine maximum heart rate
    if max_heart_rate is None:
        if age is not None:
            max_heart_rate = 220 - age
        else:
            max_heart_rate = 180  # Default value from original formula
    
    # Validate max heart rate
    if max_heart_rate <= initial_heart_rate:
        raise ValueError("Maximum heart rate must be greater than initial heart rate")
    
    # Calculate PSI components
    temp_component = 5 * (final_core_temp - initial_core_temp) / (39 - initial_core_temp)
    hr_component = 5 * (final_heart_rate - initial_heart_rate) / (max_heart_rate - initial_heart_rate)
    
    # Calculate total PSI
    psi = temp_component + hr_component
    
    # Ensure PSI is within valid range (0-10)
    psi = max(0, min(10, psi))
    
    return round(psi, 2)

def interpret_psi(psi: float) -> str:
    """
    Interpret the PSI value according to established guidelines.
    
    Args:
        psi (float): Physiological Strain Index value
    
    Returns:
        str: Interpretation of the PSI value
    """
    if psi < 2:
        return "No/little heat strain (PSI < 2)"
    elif psi < 4:
        return "Low heat strain (PSI 2-4)"
    elif psi < 6:
        return "Moderate heat strain (PSI 4-6)"
    elif psi < 8:
        return "High heat strain (PSI 6-8)"
    elif psi < 9:
        return "Very high heat strain (PSI 8-9)"
    else:
        return "Extremely high heat strain (PSI ≥ 9) - IMMEDIATE ACTION REQUIRED"

def calculate_heat_stress_risk(psi: float, duration_minutes: float = None) -> str:
    """
    Calculate overall heat stress risk based on PSI and exposure duration.
    
    Args:
        psi (float): Physiological Strain Index
        duration_minutes (float, optional): Exposure duration in minutes
    
    Returns:
        str: Risk assessment with recommendations
    """
    base_risk = interpret_psi(psi)
    
    if duration_minutes is None:
        return base_risk
    
    # Duration-based risk modification
    if psi >= 6:
        if duration_minutes > 60:
            return f"{base_risk} - EXTENDED EXPOSURE: Immediate cooling recommended"
        elif duration_minutes > 30:
            return f"{base_risk} - PROLONGED EXPOSURE: Enhanced monitoring required"
    
    return base_risk

def get_user_input() -> tuple:
    """
    Get user input with validation and error handling.
    
    Returns:
        tuple: (initial_temp, final_temp, initial_hr, final_hr, age, duration)
    """
    print("Physiological Strain Index (PSI) Calculator")
    print("For research and educational use only. Not for operational or clinical decision-making.")
    print("Enter physiological measurements:")
    print("-" * 40)
    
    initial_temp = get_float_input("Initial core temperature (°C): ", min_value=35.0, max_value=40.0)
    final_temp = get_float_input("Final core temperature (°C): ", min_value=35.0, max_value=42.0)
    
    if final_temp < initial_temp:
        print("Warning: Final temperature is lower than initial temperature")
    
    initial_hr = get_float_input("Initial heart rate (bpm): ", min_value=40, max_value=200)
    final_hr = get_float_input("Final heart rate (bpm): ", min_value=40, max_value=220)
    
    if final_hr < initial_hr:
        print("Warning: Final heart rate is lower than initial heart rate")
    
    # Optional age for age-adjusted max HR
    age = get_float_input("Age (years, optional, press Enter to skip): ", 
                         min_value=16, max_value=80, allow_blank=True, default=None)
    if age is not None:
        age = int(age)
    
    # Optional duration
    duration = get_float_input("Exposure duration (minutes, optional, press Enter to skip): ",
                              min_value=1, max_value=480, allow_blank=True, default=None)
    
    return initial_temp, final_temp, initial_hr, final_hr, age, duration

def main() -> None:
    """
    Main function to run the PSI calculator.
    """
    try:
        print("\nPhysiological Strain Index (PSI) Calculator")
        print("For research and educational use only. Not for operational or clinical decision-making.")
        print("-" * 70)
        
        initial_temp, final_temp, initial_hr, final_hr, age, duration = get_user_input()
        
        # Calculate PSI
        psi = physiological_strain_index(initial_temp, initial_hr, final_temp, final_hr, age=age)
        
        # Calculate components for detailed analysis
        temp_change = final_temp - initial_temp
        hr_change = final_hr - initial_hr
        max_hr = 220 - age if age else 180
        
        temp_component = 5 * temp_change / (39 - initial_temp)
        hr_component = 5 * hr_change / (max_hr - initial_hr)
        
        # Display results
        print(f"\n{'='*50}")
        print(f"PHYSIOLOGICAL STRAIN INDEX RESULTS")
        print(f"{'='*50}")
        
        print(f"\nInput Values:")
        print(f"Initial core temperature: {initial_temp:.1f}°C")
        print(f"Final core temperature: {final_temp:.1f}°C")
        print(f"Initial heart rate: {initial_hr:.0f} bpm")
        print(f"Final heart rate: {final_hr:.0f} bpm")
        if age:
            print(f"Age: {age} years")
        
        print(f"\nCalculated Values:")
        print(f"Temperature change: {temp_change:.1f}°C")
        print(f"Heart rate change: {hr_change:.0f} bpm")
        print(f"Maximum heart rate used: {max_hr:.0f} bpm")
        
        print(f"\nPSI Components:")
        print(f"Temperature component: {temp_component:.2f}")
        print(f"Heart rate component: {hr_component:.2f}")
        
        print(f"\nPhysiological Strain Index: {psi:.2f}")
        print(f"Interpretation: {interpret_psi(psi)}")
        
        if duration:
            print(f"Risk assessment: {calculate_heat_stress_risk(psi, duration)}")
        
        # Safety warnings
        if psi > 6:
            print(f"\n⚠️  WARNING: High PSI indicates significant heat stress")
        if final_temp > 38.5:
            print(f"⚠️  WARNING: Core temperature > 38.5°C indicates heat strain")
        if hr_change > 60:
            print(f"⚠️  WARNING: Large heart rate increase indicates cardiovascular strain")
        
        print(f"\nNote: PSI calculation based on Moran et al. (1998).")
        print(f"For medical decisions, consult qualified healthcare professionals.")
        
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