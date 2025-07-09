# -*- coding: utf-8 -*-
"""
Wind Chill Temperature Calculator
Created on Tue Mar 28 14:46:58 2023
Updated for accuracy and usability

@author: Diego Malpica
Updated by: AI Assistant

Uses the current NOAA Wind Chill Index formula (2001)
Reference: https://www.weather.gov/media/epz/wxcalc/windChill.pdf
"""

import math

def wind_chill_temperature(temp_celsius, wind_speed_ms, output_unit='celsius'):
    """
    Calculate wind chill temperature using the current NOAA formula (2001).
    
    The formula is valid for:
    - Air temperatures ≤ 10°C (50°F)
    - Wind speeds ≥ 4.8 km/h (3 mph or 1.34 m/s)
    
    Args:
        temp_celsius (float): Air temperature in °C
        wind_speed_ms (float): Wind speed in m/s
        output_unit (str): Output unit ('celsius' or 'fahrenheit')
    
    Returns:
        float: Wind chill temperature in specified unit
        
    Raises:
        ValueError: If inputs are outside valid ranges
    """
    # Validate inputs
    if temp_celsius > 10:
        raise ValueError("Wind chill calculation is only valid for temperatures ≤ 10°C")
    
    if wind_speed_ms < 1.34:
        raise ValueError("Wind chill calculation is only valid for wind speeds ≥ 1.34 m/s (3 mph)")
    
    # Convert to imperial units for NOAA formula
    temp_fahrenheit = temp_celsius * 9/5 + 32
    wind_speed_mph = wind_speed_ms * 2.237
    
    # NOAA Wind Chill Formula (2001)
    wind_chill_f = (35.74 + 0.6215 * temp_fahrenheit - 
                   35.75 * (wind_speed_mph ** 0.16) + 
                   0.4275 * temp_fahrenheit * (wind_speed_mph ** 0.16))
    
    # Convert output based on requested unit
    if output_unit.lower() == 'celsius':
        return (wind_chill_f - 32) * 5/9
    elif output_unit.lower() == 'fahrenheit':
        return wind_chill_f
    else:
        raise ValueError("Output unit must be 'celsius' or 'fahrenheit'")

def get_user_input():
    """
    Get user input with validation and error handling.
    
    Returns:
        tuple: (temperature in °C, wind speed in m/s, output unit)
    """
    while True:
        try:
            temp_c = float(input("Enter air temperature in °C: "))
            if temp_c > 10:
                print("Warning: Wind chill is only meaningful for temperatures ≤ 10°C")
                if input("Continue anyway? (y/n): ").lower() != 'y':
                    continue
            break
        except ValueError:
            print("Please enter a valid number for temperature.")
    
    while True:
        try:
            wind_ms = float(input("Enter wind speed in m/s: "))
            if wind_ms < 0:
                print("Wind speed cannot be negative.")
                continue
            if wind_ms < 1.34:
                print("Warning: Wind chill formula is most accurate for wind speeds ≥ 1.34 m/s (3 mph)")
                if input("Continue anyway? (y/n): ").lower() != 'y':
                    continue
            break
        except ValueError:
            print("Please enter a valid number for wind speed.")
    
    while True:
        unit = input("Output unit (celsius/fahrenheit) [celsius]: ").lower()
        if unit == "":
            unit = "celsius"
        if unit in ['celsius', 'fahrenheit']:
            break
        print("Please enter 'celsius' or 'fahrenheit'.")
    
    return temp_c, wind_ms, unit

def interpret_wind_chill(wind_chill_c):
    """
    Provide interpretation of wind chill temperature for safety.
    
    Args:
        wind_chill_c (float): Wind chill temperature in Celsius
    
    Returns:
        str: Safety interpretation
    """
    if wind_chill_c > -10:
        return "Low risk: Dress warmly"
    elif wind_chill_c > -28:
        return "Moderate risk: Exposed skin may freeze in 10-30 minutes"
    elif wind_chill_c > -40:
        return "High risk: Exposed skin may freeze in 5-10 minutes"
    elif wind_chill_c > -48:
        return "Very high risk: Exposed skin may freeze in 2-5 minutes"
    else:
        return "Extreme risk: Exposed skin may freeze in less than 2 minutes"

def main():
    """Main function to run the wind chill calculator."""
    print("Wind Chill Temperature Calculator")
    print("Using NOAA Wind Chill Index Formula (2001)")
    print("-" * 45)
    
    try:
        temp_c, wind_ms, output_unit = get_user_input()
        
        # Calculate wind chill
        wind_chill = wind_chill_temperature(temp_c, wind_ms, output_unit)
        
        # Display results
        print(f"\nResults:")
        print(f"Air temperature: {temp_c:.1f}°C")
        print(f"Wind speed: {wind_ms:.1f} m/s")
        
        if output_unit == 'celsius':
            print(f"Wind chill temperature: {wind_chill:.1f}°C")
            print(f"Safety assessment: {interpret_wind_chill(wind_chill)}")
        else:
            print(f"Wind chill temperature: {wind_chill:.1f}°F")
            wind_chill_c = (wind_chill - 32) * 5/9
            print(f"Safety assessment: {interpret_wind_chill(wind_chill_c)}")
        
        # Additional information
        print(f"\nNote: This calculation uses the current NOAA Wind Chill Index formula (2001)")
        print(f"Most accurate for temperatures ≤ 10°C and wind speeds ≥ 1.34 m/s")
        
    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nCalculation cancelled by user.")

if __name__ == "__main__":
    main()