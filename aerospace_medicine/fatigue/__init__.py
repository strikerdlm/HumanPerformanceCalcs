"""
Fatigue and Cognitive Performance Calculations

This module contains calculators for:
- Comprehensive fatigue modeling using homeostatic and circadian processes
- Sleep quality and chronotype analysis
- Workload factor assessment
"""

from .fatigue_model import main as fatigue_calculator

__all__ = [
    "fatigue_calculator"
] 