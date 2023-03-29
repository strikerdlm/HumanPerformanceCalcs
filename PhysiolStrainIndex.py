# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 07:34:30 2023

@author: Diego Malpica
"""

import math

def physiological_strain_index(Tc0, HR0, Tct, HRt):
    """Calculate the physiological strain index.

    Args:
        Tc0 (float): Initial core temperature in Celsius
        HR0 (float): Initial heart rate relative to the maximum heart rate
        Tct (float): Core temperature at the end of the exposure period in Celsius
        HRt (float): Heart rate relative to the maximum heart rate at the end of the exposure period

    Returns:
        float: Physiological strain index
    """
    return 5 * ((Tct - Tc0) / (39 - Tc0)) + 5 * ((HRt - HR0) / (180 - HR0))

# Get user input
Tc0 = float(input("Enter initial core temperature in Celsius: "))
HR0 = float(input("Enter initial heart rate relative to the maximum heart rate: "))
Tct = float(input("Enter core temperature at the end of the exposure period in Celsius: "))
HRt = float(input("Enter heart rate relative to the maximum heart rate at the end of the exposure period: "))

# Calculate physiological strain index
PSI = physiological_strain_index(Tc0, HR0, Tct, HRt)

# Print physiological strain index to two decimal places
print(f"Physiological strain index: {PSI:.2f}")
