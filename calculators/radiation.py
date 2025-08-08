"""
Cosmic Radiation Dose Rate Calculator
Author: Diego Malpica

Usage:
    Estimates cosmic radiation dose rate (µSv/h) at cruise altitude, with
    adjustment for polar routes. For educational and research use in aerospace
    medicine and aviation physiology.

Scientific Source:
    - Friedberg, W. et al. (1992). Radiation exposure of aircrews.
      Occupational Medicine, 7(2), 285-301.
    - ICRP Publication 132 (2016). Radiation Dose to Aircrew.
    - Model is a simplified educational approximation, not for operational use.
"""
def dose_rate(altitude_ft: float | int, polar: bool = False) -> float:
    """Return approximate cosmic-radiation dose rate at cruise altitude.

    Units: micro-Sieverts per hour (µSv/h).

    Calibrated piecewise-linear approximation based on published ranges:
      - ~2-3 µSv/h at 30,000 ft (mid-latitudes)
      - ~4-6 µSv/h at 40,000 ft (mid-latitudes)
    Reference ranges: ICRP 132; FAA CARI examples (order-of-magnitude only).

    This simplified model is for education only. Use route/solar-activity tools
    (e.g., CARI, EPCARD, SIEVERT) for operational estimates.
    """
    h = float(altitude_ft)

    # Clamp to reasonable flight levels
    h = max(0.0, min(h, 50_000.0))

    # Base mid-latitude model
    if h <= 30_000.0:
        base = 0.5 + 2.5 * (h / 30_000.0)  # 0.5 -> 3.0 µSv/h
    elif h <= 40_000.0:
        # 3.0 -> 5.0 µSv/h between 30k-40k
        base = 3.0 + 2.0 * ((h - 30_000.0) / 10_000.0)
    else:
        # 5.0 -> 6.5 µSv/h between 40k-50k (flattening)
        base = 5.0 + 1.5 * ((h - 40_000.0) / 10_000.0)

    # Polar enhancement factor (typical 20-40%); use 30% here
    if polar:
        base *= 1.3

    return base
