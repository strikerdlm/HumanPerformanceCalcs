"""
G-Force Tolerance Calculator
Author: Diego Malpica

Usage:
    Estimates maximum exposure time before G-LOC (G-induced Loss Of Consciousness)
    for a given +Gz acceleration.

Scientific Source:
    - Stoll, A.M. (1956). Human tolerance to positive G as determined by the
      physiological end-point. USAF School of Aerospace Medicine.
    - DeHart, R.L., Davis, J.R. (2002). Fundamentals of Aerospace Medicine,
      3rd Edition.

Disclaimer: Educational approximation; large inter-individual variability and
effects of training/equipment apply.
"""


def _base_time_at_Gz(Gz: float) -> float:
    if Gz < 5.0:
        return float("inf")

    table = {6.0: 60.0, 7.0: 30.0, 8.0: 15.0, 9.0: 5.0}
    if Gz >= 9.0:
        return table[9.0]

    lower_key = max(k for k in table if k <= Gz)
    upper_key = min(k for k in table if k >= Gz)
    if lower_key == upper_key:
        return table[lower_key]

    t_low = table[lower_key]
    t_high = table[upper_key]
    return t_low + (t_high - t_low) * (Gz - lower_key) / (upper_key - lower_key)


def g_loc_time(
    Gz: float | int,
    *,
    anti_g_suit: bool = False,
    agsm: bool = False,
    reclined: bool = False,
) -> float:
    """Estimate max exposure time (s) before G-LOC under +Gz.

    Parameters
    ----------
    Gz : float | int
        +Gz acceleration (seated unless modifiers applied)
    anti_g_suit : bool, optional
        If wearing anti-G suit; increases tolerance (coarse factor ~1.5x)
    agsm : bool, optional
        If performing anti-G straining maneuvers; increases tolerance (~1.3x)
    reclined : bool, optional
        Semi-reclined seat posture; increases tolerance (~1.2x)
    """
    Gz = float(Gz)
    base = _base_time_at_Gz(Gz)
    if base == float("inf"):
        return base

    factor = 1.0
    if anti_g_suit:
        factor *= 1.5
    if agsm:
        factor *= 1.3
    if reclined:
        factor *= 1.2

    return base * factor
