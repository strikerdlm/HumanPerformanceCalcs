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