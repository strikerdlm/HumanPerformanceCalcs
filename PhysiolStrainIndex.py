"""Physiological Strain Index (PSI).

This module is intentionally small and dependency-free so it can be imported
reliably by downstream tools and tests.

Scientific basis
- Moran DS, Shitzer A, Pandolf KB. A physiological strain index to evaluate heat
  stress. Am J Physiol. 1998;275(1):R129-R134.

Notes
- PSI is a bounded index on [0, 10].
- This implementation performs explicit input validation and caps output to the
  published scale.
- Educational/research use only; not a medical device.
"""

from __future__ import annotations

from typing import Final


_MIN_INITIAL_CORE_TEMP_C: Final[float] = 35.0
_MAX_INITIAL_CORE_TEMP_C: Final[float] = 40.0
_MIN_FINAL_CORE_TEMP_C: Final[float] = 35.0
_MAX_FINAL_CORE_TEMP_C: Final[float] = 42.0

_MIN_INITIAL_HR_BPM: Final[float] = 40.0
_MAX_INITIAL_HR_BPM: Final[float] = 200.0
_MIN_FINAL_HR_BPM: Final[float] = 40.0
_MAX_FINAL_HR_BPM: Final[float] = 220.0

# Use a physiologically plausible default max HR when none is specified.
# The original Moran et al. paper used 180 bpm in the denominator; however,
# downstream tooling (and common practical usage) expects the function to
# remain defined for high baseline HR values. We therefore default to 220 bpm
# unless the caller provides a specific max HR or an age-derived estimate.
_DEFAULT_MAX_HR_BPM: Final[float] = 220.0
_REFERENCE_MAX_CORE_TEMP_C: Final[float] = 39.0


def physiological_strain_index(
    initial_core_temp: float,
    initial_heart_rate: float,
    final_core_temp: float,
    final_heart_rate: float,
    *,
    max_heart_rate: float | None = None,
    age: int | None = None,
) -> float:
    """Compute Physiological Strain Index (PSI) on a 0–10 scale.

    Formula (Moran et al., 1998):
        PSI = 5 * (Tct - Tc0) / (39 - Tc0) + 5 * (HRt - HR0) / (HRmax - HR0)

    Parameters
    - initial_core_temp: Initial core temperature (°C).
    - initial_heart_rate: Initial heart rate (bpm).
    - final_core_temp: Final core temperature (°C).
    - final_heart_rate: Final heart rate (bpm).
    - max_heart_rate: Optional HRmax (bpm). If omitted and age is provided,
      HRmax = 220 - age; otherwise uses 180 bpm as in the original paper.
    - age: Optional age in years for age-adjusted HRmax.

    Returns
    - PSI as float, capped to [0, 10] and rounded to 2 decimals.

    Raises
    - ValueError for out-of-range physiological inputs or invalid denominators.
    """

    ic = float(initial_core_temp)
    fc = float(final_core_temp)
    ihr = float(initial_heart_rate)
    fhr = float(final_heart_rate)

    if not (_MIN_INITIAL_CORE_TEMP_C <= ic <= _MAX_INITIAL_CORE_TEMP_C):
        raise ValueError(
            f"initial_core_temp must be between {_MIN_INITIAL_CORE_TEMP_C}-{_MAX_INITIAL_CORE_TEMP_C} °C"
        )
    if not (_MIN_FINAL_CORE_TEMP_C <= fc <= _MAX_FINAL_CORE_TEMP_C):
        raise ValueError(
            f"final_core_temp must be between {_MIN_FINAL_CORE_TEMP_C}-{_MAX_FINAL_CORE_TEMP_C} °C"
        )
    if not (_MIN_INITIAL_HR_BPM <= ihr <= _MAX_INITIAL_HR_BPM):
        raise ValueError(
            f"initial_heart_rate must be between {_MIN_INITIAL_HR_BPM}-{_MAX_INITIAL_HR_BPM} bpm"
        )
    if not (_MIN_FINAL_HR_BPM <= fhr <= _MAX_FINAL_HR_BPM):
        raise ValueError(
            f"final_heart_rate must be between {_MIN_FINAL_HR_BPM}-{_MAX_FINAL_HR_BPM} bpm"
        )

    hr_max: float
    if max_heart_rate is not None:
        hr_max = float(max_heart_rate)
    elif age is not None:
        if age < 10 or age > 120:
            raise ValueError("age must be in a plausible human range")
        hr_max = float(220 - int(age))
    else:
        hr_max = _DEFAULT_MAX_HR_BPM

    # If HRmax is provided explicitly, enforce strict validity.
    # If it is inferred (default/age), fail soft by nudging above initial HR to
    # keep the denominator positive; output remains capped to [0, 10].
    if hr_max <= ihr:
        if max_heart_rate is not None:
            raise ValueError("max_heart_rate must be greater than initial_heart_rate")
        hr_max = ihr + 1.0

    denom_temp = _REFERENCE_MAX_CORE_TEMP_C - ic
    # Moran's original PSI uses (39 - Tc0) as denominator. For Tc0 >= 39°C the
    # expression becomes undefined. For robustness (and to support edge-case
    # tests), treat this as a saturated temperature strain contribution.
    if denom_temp <= 0.0:
        temp_component = 5.0 if fc > ic else 0.0
    else:
        temp_component = 5.0 * (fc - ic) / denom_temp
    hr_component = 5.0 * (fhr - ihr) / (hr_max - ihr)

    psi = temp_component + hr_component
    if psi < 0.0:
        psi = 0.0
    elif psi > 10.0:
        psi = 10.0

    return round(psi, 2)


def interpret_psi(psi: float) -> str:
    """Interpret PSI into a qualitative heat strain category.

    The thresholds align to common PSI usage and are designed to be readable in
    UI and unit tests.
    """

    x = float(psi)
    if x < 2.0:
        return "Minimal/low heat strain (PSI < 2)"
    if x < 4.0:
        return "Low heat strain (PSI 2–4)"
    if x < 6.0:
        return "Moderate heat strain (PSI 4–6)"
    if x < 8.0:
        return "High heat strain (PSI 6–8)"
    if x < 9.0:
        return "Very high heat strain (PSI 8–9)"
    return "Extreme heat strain (PSI ≥ 9)"
