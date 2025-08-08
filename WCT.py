# -*- coding: utf-8 -*-
"""
Wind Chill Temperature Calculator
Created on Tue Mar 28 14:46:58 2023
Updated for accuracy and usability

Author: Diego Malpica
Updated by: AI Assistant

Uses the current NOAA Wind Chill Index formula (2001)
Reference: https://www.weather.gov/media/epz/wxcalc/windChill.pdf
"""

from calculators.utils import get_float_input, get_choice_input


def wind_chill_temperature(temp_celsius, wind_speed_ms, output_unit='celsius'):
    """Calculate wind chill temperature using the NOAA formula (2001).

    Valid for:
    - Air temperatures <= 10°C (50°F)
    - Wind speeds >= 1.34 m/s (3 mph)
    """
    if temp_celsius > 10:
        raise ValueError("Wind chill valid only for temperatures <= 10°C")

    if wind_speed_ms < 1.34:
        raise ValueError(
            "Wind chill valid only for wind speeds >= 1.34 m/s (3 mph)"
        )

    # Convert to imperial units for NOAA formula
    temp_fahrenheit = temp_celsius * 9 / 5 + 32
    wind_speed_mph = wind_speed_ms * 2.237

    # National Weather Service (2001) uses exponent 0.16 for wind speed in mph
    exponent = 0.16

    # NOAA Wind Chill Formula (2001) in °F
    wind_chill_f = (
        35.74
        + 0.6215 * temp_fahrenheit
        - 35.75 * (wind_speed_mph ** exponent)
        + 0.4275 * temp_fahrenheit * (wind_speed_mph ** exponent)
    )

    if output_unit.lower() == 'celsius':
        return (wind_chill_f - 32) * 5 / 9
    if output_unit.lower() == 'fahrenheit':
        return wind_chill_f
    raise ValueError("Output unit must be 'celsius' or 'fahrenheit'")


def interpret_wind_chill(wind_chill_c):
    """Provide interpretation of wind chill temperature for safety."""
    if wind_chill_c > -10:
        return "Low risk: Dress warmly"
    if wind_chill_c > -20:
        return "Moderate risk: Exposed skin may freeze in 10-30 minutes"
    if wind_chill_c > -35:
        return "High risk: Exposed skin may freeze in 5-10 minutes"
    return "Extreme risk: Exposed skin may freeze in less than 2 minutes"


def main():
    print("\nWind Chill Temperature Calculator")
    print("Using NOAA Wind Chill Index Formula (2001)")
    print(
        "For research/education only. Not for operational or clinical use."
    )
    print("-" * 60)
    try:
        temp_c = get_float_input(
            "Enter air temperature in °C: ", max_value=10
        )
        wind_ms = get_float_input(
            "Enter wind speed in m/s: ", min_value=0
        )
        if wind_ms < 1.34:
            print(
                "Warning: Most accurate for wind speeds >= 1.34 m/s (3 mph)"
            )
            cont = get_choice_input(
                "Continue anyway?", ["y", "n"], case_sensitive=False
            )
            if cont != "y":
                return

        unit = get_choice_input(
            "Output unit",
            ["celsius", "fahrenheit"],
            case_sensitive=False,
            allow_blank=True,
            default="celsius",
        )

        wind_chill = wind_chill_temperature(temp_c, wind_ms, unit)
        print("\nResults:")
        print(f"Air temperature: {temp_c:.1f}°C")
        print(f"Wind speed: {wind_ms:.1f} m/s")
        if unit == 'celsius':
            print(f"Wind chill temperature: {wind_chill:.1f}°C")
            print(
                f"Safety assessment: {interpret_wind_chill(wind_chill)}"
            )
        else:
            print(f"Wind chill temperature: {wind_chill:.1f}°F")
            wind_chill_c = (wind_chill - 32) * 5 / 9
            print(
                f"Safety assessment: {interpret_wind_chill(wind_chill_c)}"
            )
        print("\nNote: This uses the current NOAA Wind Chill Index (2001)")
        print("Most accurate for temps <= 10°C and wind >= 1.34 m/s")
    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nCalculation cancelled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()