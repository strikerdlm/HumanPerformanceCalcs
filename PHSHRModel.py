# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 07:54:25 2023

@author: User
"""

import math

# Input variables (replace these with your actual data)
ta = 34.8  # Air temperature (°C)
tr = 35.5  # Radiation temperature (°C)
Pa = 2.5541  # Water vapor pressure (Kpa)
va = 1.5  # Air velocity (m/s)
HR = 94  # Heart rate (bpm)
Icl = 0.4  # Clothing insulation (clo)
ti = 80  # Time (min)

# Constants and given values
Age = 30  # Age (yr)
Weight = 75  # Weight (kg)
Tsk_0 = 34.16  # Original skin temperature (°C)

def mi(M0, HRi, HR0, Ag):
    return M0 + (HRi - HR0) * (180 - 0.65 * Ag - HR0) / ((41.7 - 0.22 * Ag) * Weight ** 0.666 - (180 - 0.65 * Ag - HR0))

def evaporative_heat_flow(M, R, C, E, dSeq, delta_Hv):
    return (M - R - C - E - dSeq) / delta_Hv

def required_heat_flow(M, R, C, dSeq, delta_Hv):
    return (M - R - C - dSeq) / delta_Hv

def convective_heat_transfer_coefficient(va):
    return 8.3 * (va ** 0.6)

def evaporative_heat_transfer_coefficient(hc):
    return 16.5 * hc

def metabolic_rate(Ag, HRi, HR0, M0):
    return M0 + (HRi - HR0) * (180 - 0.65 * Ag - HR0) / ((41.7 - 0.22 * Ag) * Weight ** 0.666 - (180 - 0.65 * Ag - HR0))

def heat_exchange_coefficient(ta, tr, Pa, va, Icl, M, R, C, E, dSeq, delta_Hv):
    hc = convective_heat_transfer_coefficient(va)
    he = evaporative_heat_transfer_coefficient(hc)
    # Add other heat exchange coefficients as needed
    return hc, he

# Calculate initial metabolic rate (M0) based on HR0
HR0 = 85  # Initial heart rate (bpm)
Ag = Age
M0 = metabolic_rate(Ag, HR0, HR0, M0=230)  # Initial metabolic rate (W/m2)

# Calculate metabolic rate (M) and heat exchange coefficients (hc, he)
M = metabolic_rate(Ag, HR, HR0, M0)
hc, he = heat_exchange_coefficient(ta, tr, Pa, va, Icl, M, R=0, C=0, E=0, dSeq=0, delta_Hv=2454)

# Calculate R, C, E, dSeq, and delta_Hv using the given input variables and heat_exchange_coefficient values (hc, he)
# You may need to refer to the original research paper for detailed equations and relationships.

# Calculate the required evaporative heat flow
Ereq = required_heat_flow(M, R=0, C=0, dSeq=0, delta_Hv=2454)

# Calculate Tsk and




