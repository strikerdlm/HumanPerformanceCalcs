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
    
    # Calculate maximum heart rate
    if max_heart_rate is None:
        if age is not None:
            max_heart_rate = 220 - age  # Age-adjusted max HR
        else:
            max_heart_rate = 180  # Standard PSI formula value
    
    # Validate maximum heart rate
    if max_heart_rate < final_heart_rate:
        print(f"Warning: Final heart rate ({final_heart_rate}) exceeds maximum ({max_heart_rate})")
    
    # PSI calculation
    temperature_component = 5 * (final_core_temp - initial_core_temp) / (39 - initial_core_temp)
    heart_rate_component = 5 * (final_heart_rate - initial_heart_rate) / (max_heart_rate - initial_heart_rate)
    
    psi = temperature_component + heart_rate_component
    
    # Ensure PSI is within expected range
    psi = max(0, min(10, psi))
    
    return psi

def interpret_psi(psi_value):
    """
    Interpret PSI value for heat stress assessment.
    
    Args:
        psi_value (float): PSI value (0-10 scale)
    
    Returns:
        str: Interpretation and recommendations
    """
    if psi_value < 2:
        return "Low heat stress - minimal physiological strain"
    elif psi_value <= 4:
        return "Moderate heat stress - monitor for signs of heat strain"
    elif psi_value <= 6:
        return "High heat stress - implement cooling measures"
    elif psi_value <= 8:
        return "Very high heat stress - immediate cooling required"
    else:
        return "Extreme heat stress - stop activity, immediate medical attention may be needed"

def calculate_heat_stress_risk(psi_value, duration_minutes=None):
    """
    Calculate heat stress risk based on PSI and exposure duration.
    
    Args:
        psi_value (float): PSI value
        duration_minutes (int, optional): Exposure duration in minutes
    
    Returns:
        str: Risk assessment
    """
    base_risk = interpret_psi(psi_value)
    
    if duration_minutes is None:
        return base_risk
    
    # Adjust risk based on duration
    if duration_minutes > 60 and psi_value > 4:
        return base_risk + " - Extended exposure increases risk"
    elif duration_minutes > 120 and psi_value > 2:
        return base_risk + " - Prolonged exposure, monitor closely"
    else:
        return base_risk

def get_user_input() -> tuple:
    """
    Get user input with validation.
    
    Returns:
        tuple: All validated input values
    """
    print("Physiological Strain Index (PSI) Calculator")
    print("Based on Moran et al. (1998) heat stress assessment")
    print("-" * 50)
    
    while True:
        try:
            initial_temp = float(input("Initial core temperature (°C): "))
            if initial_temp < 35 or initial_temp > 40:
                print("Please enter a realistic core temperature (35-40°C)")
                continue
            break
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            final_temp = float(input("Final core temperature (°C): "))
            if final_temp < 35 or final_temp > 42:
                print("Please enter a realistic core temperature (35-42°C)")
                continue
            if final_temp < initial_temp - 1:
                print("Final temperature significantly lower than initial - please verify")
                continue
            break
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            initial_hr = float(input("Initial heart rate (bpm): "))
            if initial_hr < 40 or initial_hr > 200:
                print("Please enter a realistic heart rate (40-200 bpm)")
                continue
            break
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            final_hr = float(input("Final heart rate (bpm): "))
            if final_hr < 40 or final_hr > 220:
                print("Please enter a realistic heart rate (40-220 bpm)")
                continue
            break
        except ValueError:
            print("Please enter a valid number")
    
    # Optional age for age-adjusted max HR
    while True:
        try:
            age_input = input("Age (optional, for age-adjusted max HR): ")
            if age_input.strip() == "":
                age = None
                break
            age = int(age_input)
            if age < 18 or age > 80:
                print("Please enter a realistic age (18-80)")
                continue
            break
        except ValueError:
            print("Please enter a valid number or leave blank")
    
    # Optional duration
    while True:
        try:
            duration_input = input("Exposure duration in minutes (optional): ")
            if duration_input.strip() == "":
                duration = None
                break
            duration = int(duration_input)
            if duration < 0 or duration > 480:
                print("Please enter a realistic duration (0-480 minutes)")
                continue
            break
        except ValueError:
            print("Please enter a valid number or leave blank")
    
    return initial_temp, final_temp, initial_hr, final_hr, age, duration

def main() -> None:
    """
    Main function to run the PSI calculator.
    """
    try:
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
        if hr_change > 50:
            print(f"⚠️  WARNING: Large heart rate increase may indicate heat stress")
        
        print(f"\nNote: PSI based on Moran et al. (1998) heat stress assessment model.")
        print(f"For operational decisions, consult qualified professionals.")
        
    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nCalculation cancelled by user.")

if __name__ == "__main__":
    main()
