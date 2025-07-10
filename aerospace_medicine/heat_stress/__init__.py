"""
Heat Stress Assessment Calculations

This module contains calculators for:
- Predicted Heat Strain using Heart Rate (PHS-HR) model
- Physiological Strain Index (PSI)
- Sweat rate and dehydration risk assessment
- Regional sweat rate calculations
"""

# Import available calculators
try:
    from .strain_index import main as strain_index_calculator
except ImportError:
    strain_index_calculator = None

# Other calculators to be implemented
phs_hr_calculator = None
sweat_rate_calculator = None
ontario_sweat_calculator = None

__all__ = [
    "phs_hr_calculator",
    "strain_index_calculator",
    "sweat_rate_calculator", 
    "ontario_sweat_calculator"
] 