"""
Aerospace Medicine Calculators

This package contains domain-organized calculators for aerospace medicine and human performance assessment.
All tools are designed for research and educational purposes only.

Domains:
- decompression: DCS risk assessment and barotrauma calculations
- heat_stress: Heat strain, PSI, and sweat rate calculations  
- cold_stress: Wind chill and cold exposure assessments
- altitude: Altitude effects and TUC calculations
- fatigue: Cognitive performance and fatigue modeling
- motion_sickness: Motion sickness susceptibility tools
"""

__version__ = "1.0.0"
__author__ = "Diego Malpica"

# Import domain modules for easy access
from . import decompression
from . import heat_stress
from . import cold_stress
from . import altitude
from . import fatigue
from . import motion_sickness

__all__ = [
    "decompression",
    "heat_stress", 
    "cold_stress",
    "altitude",
    "fatigue",
    "motion_sickness"
] 