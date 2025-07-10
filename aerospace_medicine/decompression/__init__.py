"""
Decompression Sickness (DCS) and Barotrauma Calculations

This module contains calculators for:
- DCS risk prediction using machine learning models
- Barotrauma treatment modeling
- Confidence interval calculations for barometric treatment
"""

# Import available calculators
try:
    from .dcs_risk import main as dcs_risk_calculator
except ImportError:
    dcs_risk_calculator = None

# Other calculators to be implemented
dcs_ensemble_calculator = None
barotrauma_mcmc_calculator = None  
barotrauma_ci_calculator = None

__all__ = [
    "dcs_risk_calculator",
    "dcs_ensemble_calculator", 
    "barotrauma_mcmc_calculator",
    "barotrauma_ci_calculator"
] 