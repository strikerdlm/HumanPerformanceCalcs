"""
Noise Exposure & Daily Noise Dose Calculator
Author: Diego Malpica

Usage:
    Provides functions to calculate the percentage noise dose and permissible
    exposure durations according to the U.S. OSHA occupational noise standard
    (29 CFR §1910.95) and the NIOSH Recommended Exposure Limit (REL) for noise.
    The calculator is intended for occupational and industrial hygiene studies
    and *must not* be used as a legal compliance tool without proper sound-level
    measurements and professional judgement.

Scientific & Regulatory Basis (APA style):
    Occupational Safety and Health Administration. (2023). *29 CFR §1910.95 –
    Occupational noise exposure.* https://www.osha.gov/laws-regs/regulations/

    National Institute for Occupational Safety and Health. (1998). *Criteria for
    a recommended standard: Occupational noise exposure* (DHHS Publication
    No. 98-126). U.S. Department of Health and Human Services.

    Suter, A. H. (1991). *Noise and its effects.* Administrative Conference of
    the United States.
"""
from __future__ import annotations

__all__ = [
    "permissible_duration",
    "noise_dose_osha",
    "noise_dose_niosh",
]

# ----------------------------------------------------------------------------
# Core Functions
# ----------------------------------------------------------------------------

def permissible_duration(
    spl_dba: float,
    *,
    criterion_level: float = 90.0,
    exchange_rate: float = 5.0,
) -> float:
    """Return permissible exposure duration in *hours* at a given SPL.

    Parameters
    ----------
    spl_dba : float
        A-weighted sound pressure level, dB(A).
    criterion_level : float, default 90 dBA
        Criterion level (Lc). OSHA uses 90 dBA. NIOSH uses 85 dBA.
    exchange_rate : float, default 5 dB
        Exchange rate (q). OSHA uses 5 dB. NIOSH uses 3 dB.

    Notes
    -----
    Formula (OSHA, NIOSH):
        T = 8 h / 2^((SPL − Lc) / q)
    """
    exponent = (spl_dba - criterion_level) / exchange_rate
    T_hours = 8.0 / (2 ** exponent)
    return T_hours


def _dose_percent(spl_dba: float, duration_hours: float,
                  *, criterion_level: float, exchange_rate: float) -> float:
    """Internal helper that computes percent dose for a single SPL block."""
    T_allowed = permissible_duration(spl_dba,
                                     criterion_level=criterion_level,
                                     exchange_rate=exchange_rate)
    dose_pct = 100.0 * (duration_hours / T_allowed)
    return dose_pct


def noise_dose_osha(levels: list[float], durations_hours: list[float]) -> float:
    """Compute total OSHA noise dose (percent) for multiple exposure segments.

    Parameters
    ----------
    levels : list[float]
        List of A-weighted sound levels in dB(A).
    durations_hours : list[float]
        Corresponding exposure durations in hours.

    Returns
    -------
    float
        Total daily dose in percent. ≥100 % exceeds the permissible dose.
    """
    if len(levels) != len(durations_hours):
        raise ValueError("`levels` and `durations_hours` length mismatch.")

    total_dose = 0.0
    for L, t in zip(levels, durations_hours):
        total_dose += _dose_percent(L, t, criterion_level=90.0, exchange_rate=5.0)
    return total_dose


def noise_dose_niosh(levels: list[float], durations_hours: list[float]) -> float:
    """Compute total NIOSH REL noise dose (percent).

    NIOSH uses criterion level 85 dBA and 3-dB exchange rate.
    """
    if len(levels) != len(durations_hours):
        raise ValueError("`levels` and `durations_hours` length mismatch.")

    total_dose = 0.0
    for L, t in zip(levels, durations_hours):
        total_dose += _dose_percent(L, t, criterion_level=85.0, exchange_rate=3.0)
    return total_dose