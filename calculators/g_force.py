def g_loc_time(Gz: float | int) -> float:
    """Return estimated maximum exposure time in seconds before G-LOC.

    Based on a simplified interpretation of the Stoll curve (USAF, 1956).
    Works for +G\_z accelerations in the seated position, no anti-G suit.
    """
    Gz = float(Gz)

    if Gz < 5.0:
        return float("inf")  # Below ~5 g most subjects tolerate indefinitely

    _TABLE = {
        6.0: 60.0,
        7.0: 30.0,
        8.0: 15.0,
        9.0:  5.0,
    }

    if Gz >= 9.0:
        return _TABLE[9.0]

    # Linear interpolation between available points
    lower_key = max(k for k in _TABLE if k <= Gz)
    upper_key = min(k for k in _TABLE if k >= Gz)
    if lower_key == upper_key:
        return _TABLE[lower_key]

    t_low = _TABLE[lower_key]
    t_high = _TABLE[upper_key]
    return t_low + (t_high - t_low) * (Gz - lower_key) / (upper_key - lower_key)