"""
Cold Stress and Environmental Exposure Calculations

This module contains calculators for:
- Wind chill temperature assessment with frostbite risk
- Cold stress survival prediction
"""

# Import available calculators  
try:
    from .wind_chill import main as wind_chill_calculator
except ImportError:
    wind_chill_calculator = None

# Other calculators to be implemented
cold_survival_calculator = None

__all__ = [
    "wind_chill_calculator",
    "cold_survival_calculator"
] 