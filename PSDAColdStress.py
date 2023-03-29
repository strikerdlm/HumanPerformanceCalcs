# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 14:25:35 2023

@author: DiegoMalpica
"""

def calculate_wind_chill_temperature(temp_celsius, wind_speed_mps):
    temp_fahrenheit = temp_celsius * 9 / 5 + 32  # Convert to Fahrenheit
    wind_speed_mph = wind_speed_mps * 2.23694  # Convert to mph

    if temp_fahrenheit <= 50 and wind_speed_mph >= 3:
        wind_chill = 35.74 + 0.6215 * temp_fahrenheit - 35.75 * wind_speed_mph**0.16 + 0.4275 * temp_fahrenheit * wind_speed_mph**0.16
        return wind_chill
    else:
        return temp_fahrenheit

def probability_of_survival_and_survival_time(temp_celsius, wind_speed_mps, humidity_percent, exposure_level):
    wind_chill = calculate_wind_chill_temperature(temp_celsius, wind_speed_mps)
    survival_time_minutes = 0

    if exposure_level == "minimal":
        survival_time_minutes = 2 * wind_chill + humidity_percent - 55
    elif exposure_level == "moderate":
        survival_time_minutes = 1.5 * wind_chill + humidity_percent - 50
    elif exposure_level == "severe":
        survival_time_minutes = wind_chill + humidity_percent - 45
    else:
        raise ValueError("Invalid exposure level")

    probability_of_survival_percent = 100 - (survival_time_minutes / 6) * 10
    probability_of_survival_percent = max(0, min(probability_of_survival_percent, 100))
    return survival_time_minutes, probability_of_survival_percent

print("Exposure level explanation:")
print("- Minimal: minimal wind and precipitation exposure, appropriate clothing and shelter are available")
print("- Moderate: moderate wind and precipitation exposure, clothing provides some protection and shelter is partially available")
print("- Severe: severe wind and precipitation exposure, clothing provides little protection and shelter is not available")
temp_celsius = float(input("Enter temperature in Celsius: "))
wind_speed_mps = float(input("Enter wind speed in meters per second: "))
humidity_percent = float(input("Enter relative humidity in percent: "))
exposure_level = input("Enter exposure level (minimal, moderate, severe): ").lower()

if exposure_level not in ["minimal", "moderate", "severe"]:
    raise ValueError("Invalid exposure level")

survival_time_minutes, probability_of_survival_percent = probability_of_survival_and_survival_time(temp_celsius, wind_speed_mps, humidity_percent, exposure_level)
print(f"Survival Time: {survival_time_minutes:.1f} minutes")
print(f"Probability of Survival: {round(probability_of_survival_percent)}%")
