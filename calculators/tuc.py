"""
Time of Useful Consciousness (TUC) Estimator
Author: Diego Malpica

Usage:
    Estimates the median Time of Useful Consciousness (TUC) in seconds for a given altitude (ft).
    For educational and research use in aerospace medicine and aviation physiology.

Scientific Source:
    - USAF Flight Surgeon Handbook, 3rd Edition, 1991
    - Ernsting, J., Nicholson, A.N., Rainford, D. (2016). Aviation Medicine, 4th Edition.
    - Data compiled from multiple aerospace medicine sources.
"""
import numpy as np  # type: ignore

# Altitude (ft) → median Time of Useful Consciousness (s)
# Data compiled from USAF Flight Surgeon Handbook & other sources.
_TIME_TABLE = [
    (18_000, 1_500),  # 25 min
    (22_000,   600),  # 10 min
    (25_000,   240),  # 4 min
    (28_000,   150),  # 2.5 min
    (30_000,    90),  # 1.5 min
    (35_000,    45),
    (40_000,    18),
    (43_000,    10),
    (50_000,    10),
    (63_000,     0),  # Armstrong line – instantaneous
]


def estimate_tuc(altitude_ft: float | int) -> float:
    """Estimate Time of Useful Consciousness (seconds) for given altitude."""
    altitude_ft = float(altitude_ft)

    alts, times = zip(*_TIME_TABLE)
    if altitude_ft <= alts[0]:
        return times[0]
    if altitude_ft >= alts[-1]:
        return times[-1]

    return float(np.interp(altitude_ft, alts, times))