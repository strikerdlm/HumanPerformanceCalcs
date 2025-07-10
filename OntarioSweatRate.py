# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 18:45:26 2023

@author: Diego Malpica
"""

import math

def body_surface_area(height: float, weight: float) -> float:
    """
    Calculate body surface area (BSA) using the Du Bois formula.

    Args:
        height (float): Height in centimeters.
        weight (float): Weight in kilograms.

    Returns:
        float: Body surface area in square meters (m^2).
    """
    return math.sqrt(height * weight / 3600)

def ontario_sweat_estimator(bsa: float, hr_rest: float, hr_exercise: float, t_rest: float, t_exercise: float) -> float:
    """
    Estimate sweat rate using the Ontario Sweat Rate formula.

    Args:
        bsa (float): Body surface area in square meters (m^2).
        hr_rest (float): Resting heart rate in beats per minute (bpm).
        hr_exercise (float): Exercise heart rate in beats per minute (bpm).
        t_rest (float): Resting ambient temperature in degrees Celsius (°C).
        t_exercise (float): Exercise ambient temperature in degrees Celsius (°C).

    Returns:
        float: Estimated sweat rate in milliliters per hour (mL/h).
    """
    delta_hr = hr_exercise - hr_rest
    delta_t = t_exercise - t_rest
    sweat_rate = 0.019 * bsa * (delta_hr * delta_t) / (hr_rest * t_rest)
    return sweat_rate

if __name__ == "__main__":
    height = float(input("Enter height (cm): "))
    weight = float(input("Enter weight (kg): "))
    hr_rest = float(input("Enter resting heart rate (bpm): "))
    hr_exercise = float(input("Enter exercise heart rate (bpm): "))
    t_rest = float(input("Enter resting ambient temperature (°C): "))
    t_exercise = float(input("Enter exercise ambient temperature (°C): "))

    bsa = body_surface_area(height, weight)
    sweat_rate = ontario_sweat_estimator(bsa, hr_rest, hr_exercise, t_rest, t_exercise) * 1000

    print("\nSweat Rate: {:.2f} mL/h".format(sweat_rate))
