"""
Cosmic Radiation Dose Rate Calculator
Author: Diego Malpica

Usage:
    Estimates cosmic radiation dose rate (µSv/h) at cruise altitude, with adjustment for polar routes.
    For educational and research use in aerospace medicine and aviation physiology.

Scientific Source:
    - Friedberg, W. et al. (1992). Radiation exposure of aircrews. Occupational Medicine, 7(2), 285-301.
    - ICRP Publication 132 (2016). Radiation Dose to Aircrew.
    - Model is a simplified educational approximation, not for operational use.
"""
def dose_rate(altitude_ft: float | int, polar: bool = False) -> float:
    """Return approximate cosmic-radiation dose rate at cruise altitude.

    The result is in micro-Sieverts per hour (µSv/h). A very coarse linear
    model is used for educational demonstration only:

        dose = 0.1 + 0.14 × (altitude\_ft / 10 000)

    with a 20 % increase applied on polar routes (>60° latitude).
    """
    altitude_ft = float(altitude_ft)
    dose = 0.1 + 0.14 * (altitude_ft / 10_000)
    if polar:
        dose *= 1.2
    return dose