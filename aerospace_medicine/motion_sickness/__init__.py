"""
Motion Sickness and Sensory Assessment Calculations

This module contains calculators for:
- Motion Sickness Susceptibility Questionnaire (MSSQ) processing
- Vestibular and sensory conflict analysis
"""

from .mssq_calc import main as mssq_calculator

__all__ = [
    "mssq_calculator"
] 