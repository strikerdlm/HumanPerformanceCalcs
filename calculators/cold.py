"""
Cold Exposure Calculators
- Peak Shivering Intensity prediction
"""
from __future__ import annotations

__all__ = ["peak_shivering_intensity"]


def peak_shivering_intensity(vo2max_mlkgmin: float, bmi: float, age_years: int) -> float:
    """Predict peak shivering intensity (ml O₂·kg⁻¹·min⁻¹).

    Shiv_peak = 30.5 + 0.348·VO₂max - 0.909·BMI - 0.233·Age
    """
    return (
        30.5
        + 0.348 * float(vo2max_mlkgmin)
        - 0.909 * float(bmi)
        - 0.233 * float(age_years)
    )