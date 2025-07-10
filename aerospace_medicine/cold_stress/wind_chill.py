# -*- coding: utf-8 -*-
"""
Wind Chill Temperature (WCT) Calculator
Updated for scientific accuracy and usability

@author: Diego Malpica

Based on the National Weather Service Wind Chill Index (2001)
Formula: WCT = 35.74 + 0.6215*T - 35.75*V^0.16 + 0.4275*T*V^0.16 (°F)

Used in aerospace medicine for cold exposure assessment.
"""

import math
from calculators.utils import get_float_input

def wind_chill_index(temperature_f: float, wind_speed_mph: float) -> float:
    """
    Calculate Wind Chill Temperature using the NWS formula (2001).
    
    Args:
        temperature_f (float): Air temperature in Fahrenheit
        wind_speed_mph (float): Wind speed in miles per hour
    
    Returns:
        float: Wind chill temperature in Fahrenheit
    
    Raises:
        ValueError: If inputs are outside valid ranges
    """
    # Validate input ranges for formula applicability
    if temperature_f > 50:
        raise ValueError("Wind chill formula applies only to temperatures ≤ 50°F (10°C)")
    
    if wind_speed_mph < 3:
        # Below 3 mph, wind chill equals air temperature
        return temperature_f
    
    # Calculate wind chill using NWS formula
    wc = (35.74 + 0.6215 * temperature_f - 
          35.75 * (wind_speed_mph ** 0.16) + 
          0.4275 * temperature_f * (wind_speed_mph ** 0.16))
    
    return round(wc, 1)

def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5/9

def mph_to_kmh(mph: float) -> float:
    """Convert miles per hour to kilometers per hour."""
    return mph * 1.609344

def kmh_to_mph(kmh: float) -> float:
    """Convert kilometers per hour to miles per hour."""
    return kmh / 1.609344

def interpret_wind_chill(wc_f: float) -> str:
    """
    Interpret wind chill temperature for frostbite risk.
    
    Args:
        wc_f (float): Wind chill temperature in Fahrenheit
    
    Returns:
        str: Risk interpretation with exposure time warnings
    """
    if wc_f >= 16:
        return "Low risk - Normal outdoor activities safe"
    elif wc_f >= 0:
        return "Moderate risk - Dress warmly, limit time outdoors"
    elif wc_f >= -18:
        return "High risk - Frostbite possible in 30 minutes with prolonged exposure"
    elif wc_f >= -35:
        return "Very high risk - Frostbite possible in 10 minutes"
    elif wc_f >= -60:
        return "Extreme risk - Frostbite possible in 5 minutes"
    else:
        return "Extreme danger - Frostbite possible in 2 minutes or less"

def get_temperature_input() -> tuple:
    """Get temperature input in user's preferred units."""
    print("\nTemperature Input:")
    print("1. Celsius")
    print("2. Fahrenheit")
    
    while True:
        choice = input("Choose temperature unit (1 or 2): ").strip()
        if choice in ['1', '2']:
            break
        print("Please enter 1 for Celsius or 2 for Fahrenheit")
    
    if choice == '1':
        temp_c = get_float_input("Temperature (°C): ", min_value=-60, max_value=10)
        temp_f = celsius_to_fahrenheit(temp_c)
        return temp_f, temp_c, 'C'
    else:
        temp_f = get_float_input("Temperature (°F): ", min_value=-76, max_value=50)
        temp_c = fahrenheit_to_celsius(temp_f)
        return temp_f, temp_c, 'F'

def get_wind_speed_input() -> tuple:
    """Get wind speed input in user's preferred units."""
    print("\nWind Speed Input:")
    print("1. Miles per hour (mph)")
    print("2. Kilometers per hour (km/h)")
    
    while True:
        choice = input("Choose wind speed unit (1 or 2): ").strip()
        if choice in ['1', '2']:
            break
        print("Please enter 1 for mph or 2 for km/h")
    
    if choice == '1':
        wind_mph = get_float_input("Wind speed (mph): ", min_value=0, max_value=200)
        wind_kmh = mph_to_kmh(wind_mph)
        return wind_mph, wind_kmh, 'mph'
    else:
        wind_kmh = get_float_input("Wind speed (km/h): ", min_value=0, max_value=320)
        wind_mph = kmh_to_mph(wind_kmh)
        return wind_mph, wind_kmh, 'kmh'

def main():
    """Main function to run the wind chill calculator."""
    try:
        print("\nWind Chill Temperature Calculator")
        print("For research and educational use only. Not for operational or clinical decision-making.")
        print("-" * 70)
        print("Based on National Weather Service Wind Chill Index (2001)")
        
        # Get temperature input
        temp_f, temp_c, temp_unit = get_temperature_input()
        
        # Get wind speed input
        wind_mph, wind_kmh, wind_unit = get_wind_speed_input()
        
        # Validate temperature range for wind chill formula
        if temp_f > 50:
            print(f"\nNote: Wind chill formula applies only to temperatures ≤ 50°F (10°C)")
            print(f"At {temp_f:.1f}°F ({temp_c:.1f}°C), wind chill equals air temperature.")
            return
        
        # Calculate wind chill
        if wind_mph < 3:
            wc_f = temp_f
            print(f"\nNote: At wind speeds < 3 mph (4.8 km/h), wind chill equals air temperature.")
        else:
            wc_f = wind_chill_index(temp_f, wind_mph)
        
        wc_c = fahrenheit_to_celsius(wc_f)
        
        # Display results
        print(f"\n{'='*50}")
        print(f"WIND CHILL CALCULATION RESULTS")
        print(f"{'='*50}")
        
        print(f"\nInput Values:")
        if temp_unit == 'C':
            print(f"Air temperature: {temp_c:.1f}°C ({temp_f:.1f}°F)")
        else:
            print(f"Air temperature: {temp_f:.1f}°F ({temp_c:.1f}°C)")
            
        if wind_unit == 'mph':
            print(f"Wind speed: {wind_mph:.1f} mph ({wind_kmh:.1f} km/h)")
        else:
            print(f"Wind speed: {wind_kmh:.1f} km/h ({wind_mph:.1f} mph)")
        
        print(f"\nWind Chill Temperature:")
        print(f"{wc_f:.1f}°F ({wc_c:.1f}°C)")
        
        print(f"\nRisk Assessment:")
        print(f"{interpret_wind_chill(wc_f)}")
        
        # Additional safety warnings
        if wc_f < -18:
            print(f"\n⚠️  WARNING: Dangerous wind chill conditions")
            print(f"   - Cover all exposed skin")
            print(f"   - Limit outdoor exposure time")
            print(f"   - Watch for signs of frostbite and hypothermia")
        
        if wind_mph > 40:
            print(f"\n⚠️  WARNING: High wind speeds increase heat loss")
        
        print(f"\nNote: Based on NWS Wind Chill Index for research/educational use.")
        print(f"For operational decisions, consult qualified meteorologists.")
        
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