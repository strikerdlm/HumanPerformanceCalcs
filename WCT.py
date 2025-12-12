"""Wind Chill Temperature (WCT) using NOAA/NWS 2001 formula.

This provides a small, import-safe API for wind chill calculations in the same
shape expected by the existing unit tests.

Scientific basis
- National Weather Service (NWS) Wind Chill Temperature Index (2001).
  The NWS formula is defined in °F with wind speed in mph and uses exponent 0.16.

Applicability (NWS)
- Air temperature <= 10°C (50°F)
- Wind speed >= 1.34 m/s (3 mph)

Notes
- Inputs are temperature in °C and wind speed in m/s.
- output_unit controls the output units ('celsius' or 'fahrenheit').
"""

from __future__ import annotations

from typing import Final


_MIN_WIND_SPEED_M_S: Final[float] = 1.34
_MAX_TEMP_C_FOR_FORMULA: Final[float] = 10.0


def wind_chill_temperature(temp_celsius: float, wind_speed_ms: float, output_unit: str = "celsius") -> float:
    """Calculate wind chill temperature.

    Args:
        temp_celsius: Air temperature in °C.
        wind_speed_ms: Wind speed in m/s.
        output_unit: 'celsius' or 'fahrenheit'.

    Returns:
        Wind chill temperature in the requested units.

    Raises:
        ValueError: If outside formula applicability or output_unit invalid.
    """

    tc = float(temp_celsius)
    v_ms = float(wind_speed_ms)
    unit = str(output_unit).strip().lower()

    if tc > _MAX_TEMP_C_FOR_FORMULA:
        raise ValueError("Wind chill valid only for temperatures <= 10°C")
    if v_ms < _MIN_WIND_SPEED_M_S:
        raise ValueError("Wind chill valid only for wind speeds >= 1.34 m/s (3 mph)")
    if unit not in {"celsius", "fahrenheit"}:
        raise ValueError("Output unit must be 'celsius' or 'fahrenheit'")

    # Convert inputs to NWS formula units
    tf = tc * 9.0 / 5.0 + 32.0
    v_mph = v_ms * 2.237

    v_term = v_mph ** 0.16
    wct_f = 35.74 + 0.6215 * tf - 35.75 * v_term + 0.4275 * tf * v_term

    if unit == "fahrenheit":
        return float(wct_f)

    # Fahrenheit -> Celsius
    return float((wct_f - 32.0) * 5.0 / 9.0)


def interpret_wind_chill(wind_chill_c: float) -> str:
    """Interpret wind chill (°C) into a qualitative frostbite risk category."""

    wc = float(wind_chill_c)
    if wc > -10.0:
        return "Low risk: Dress warmly"
    if wc > -20.0:
        return "Moderate risk: Exposed skin may freeze in 10-30 minutes"
    if wc > -35.0:
        return "High risk: Exposed skin may freeze in 5-10 minutes"
    return "Extreme risk: Exposed skin may freeze in less than 2 minutes"
