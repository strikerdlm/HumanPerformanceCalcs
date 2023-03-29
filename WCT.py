# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 14:46:58 2023

@author: Diego Malpica
"""

def wind_chill_temperature(Ta, V):
    """Calculate wind chill temperature in °C

    Args:
        Ta (float): Air temperature in °C
        V (float): Wind speed in m/s

    Returns:
        float: Wind chill temperature in °C
    """
    return 13.12 + 0.6215 * Ta - 11.37 * V**0.16 + 0.3965 * Ta * V**0.16

# Example usage:
Ta = float(input("Enter air temperature in °C: "))
V = float(input("Enter wind speed in m/s: "))
wind_chill = wind_chill_temperature(Ta, V)
print(f"Wind chill temperature: {wind_chill:.1f} °C")