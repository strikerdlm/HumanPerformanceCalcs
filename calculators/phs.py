from __future__ import annotations

"""Lightweight Predicted Heat Strain (PHS) helper utilities.

This module implements an analytically transparent, fully typed approximation of
ISO 7933:2023 predicted heat strain guidance using a simplified heat balance.
It favors clarity and bounded behaviour over exhaustive fidelity so the
calculations remain explainable inside the Streamlit UI.

The implementation follows these modelling assumptions:

* The worker is represented by a 75 kg individual with 1.9 m² body surface area
  unless the caller specifies otherwise.
* A single mean skin temperature of 34.5 °C is used for dry heat exchanges.
* Clothing insulation and vapor resistance are captured through empirical
  multipliers derived from ISO 9920 approximations.
* Required sweat rate is computed from the dry heat deficit and limited by the
  environment's evaporative capacity; latent heat of vaporisation is assumed to
  be 675 W per L/h of sweat.

Even with these simplifications the function reproduces trends reported in the
PHS literature (core temperature rise when E_req>E_max, dehydration limits under
high sweat requirements) and is well suited for educational and screening use.
"""

from dataclasses import dataclass
from math import exp
from typing import Final

__all__ = ["PredictedHeatStrainResult", "predicted_heat_strain"]


@dataclass(slots=True, frozen=True)
class PredictedHeatStrainResult:
    """Structured output returned by :func:`predicted_heat_strain`.

    Attributes
    ----------
    predicted_core_temperature_C:
        Core temperature after the requested exposure (°C).
    required_sweat_rate_L_per_h:
        The evaporative sweat rate needed to achieve heat balance (L/h).
    max_sustainable_sweat_rate_L_per_h:
        Environment- and clothing-limited sweat rate (L/h).
    actual_sweat_rate_L_per_h:
        The effective sweat rate used in the heat balance (L/h).
    predicted_water_loss_L:
        Total sweat loss over the exposure assuming the calculated actual rate.
    dehydration_percent_body_mass:
        Resulting dehydration as % of body mass.
    allowable_exposure_minutes:
        Maximum recommended exposure time before violating either the core
        temperature (default 38.5 °C) or dehydration (default 5 % body mass)
        limits. When the requested exposure is shorter this equals the request.
    limiting_factor:
        Textual description of the most restrictive limit ("Input duration",
        "Core temperature limit", or "Dehydration limit").
    """

    predicted_core_temperature_C: float
    required_sweat_rate_L_per_h: float
    max_sustainable_sweat_rate_L_per_h: float
    actual_sweat_rate_L_per_h: float
    predicted_water_loss_L: float
    dehydration_percent_body_mass: float
    allowable_exposure_minutes: float
    limiting_factor: str


_BODY_SPECIFIC_HEAT_J_PER_KG_K: Final[float] = 3470.0
_LATENT_HEAT_W_PER_L_H: Final[float] = 675.0
_SIGMA: Final[float] = 5.670374419e-8
_DEFAULT_T_SKIN_C: Final[float] = 34.5


def _validate_positive(name: str, value: float) -> float:
    if value <= 0.0:
        raise ValueError(f"{name} must be > 0 (got {value}).")
    return value


def _sat_vapor_pressure_kpa(temp_c: float) -> float:
    """Return saturation vapour pressure (kPa) using Tetens approximation."""

    return 0.61078 * exp(17.27 * temp_c / (temp_c + 237.3))


def predicted_heat_strain(
    metabolic_rate_w_m2: float,
    air_temperature_C: float,
    mean_radiant_temperature_C: float,
    relative_humidity_percent: float,
    air_velocity_m_s: float,
    clothing_insulation_clo: float,
    exposure_minutes: float,
    *,
    mechanical_power_w_m2: float = 0.0,
    body_mass_kg: float = 75.0,
    body_surface_area_m2: float = 1.9,
    baseline_core_temp_C: float = 37.0,
    core_temp_limit_C: float = 38.5,
    dehydration_limit_percent: float = 5.0,
) -> PredictedHeatStrainResult:
    """Estimate core temperature rise and sweat requirements (ISO 7933 style).

    The function performs a simplified steady-state heat balance and then checks
    core-temperature and dehydration constraints to produce conservative
    screening guidance. All loops are bounded and every parameter is validated
    so that the function can be safely exposed in interactive UIs.
    """

    _validate_positive("metabolic_rate_w_m2", metabolic_rate_w_m2)
    if mechanical_power_w_m2 < 0.0:
        raise ValueError("mechanical_power_w_m2 cannot be negative.")
    _validate_positive("air_velocity_m_s", air_velocity_m_s + 1e-9)
    _validate_positive("clothing_insulation_clo", clothing_insulation_clo + 1e-9)
    _validate_positive("exposure_minutes", exposure_minutes)
    _validate_positive("body_mass_kg", body_mass_kg)
    _validate_positive("body_surface_area_m2", body_surface_area_m2)
    _validate_positive("core_temp_limit_C", core_temp_limit_C)
    _validate_positive("dehydration_limit_percent", dehydration_limit_percent)

    if relative_humidity_percent < 0.0 or relative_humidity_percent > 100.0:
        raise ValueError("relative_humidity_percent must be between 0 and 100.")
    if baseline_core_temp_C >= core_temp_limit_C:
        raise ValueError("baseline_core_temp_C must be below core_temp_limit_C.")

    metabolic_rate = metabolic_rate_w_m2 - mechanical_power_w_m2
    if metabolic_rate <= 0.0:
        raise ValueError("Net metabolic rate must be positive after mechanics.")

    # Clothing modifiers per ISO 9920 approximations
    clo = max(0.0, clothing_insulation_clo)
    r_cl = 0.155 * clo  # m²·K/W
    if clo <= 0.5:
        f_cl = 1.0 + 0.2 * clo
    else:
        f_cl = 1.05 + 0.1 * clo

    t_skin = _DEFAULT_T_SKIN_C
    v = max(0.1, air_velocity_m_s)
    h_c = max(3.0, 8.3 * v ** 0.6)
    t_r_k = mean_radiant_temperature_C + 273.15
    t_skin_k = t_skin + 273.15
    t_m = (t_r_k + t_skin_k) / 2.0
    h_r = 4.0 * 0.95 * _SIGMA * (t_m ** 3)
    h_total = h_c + h_r
    series_resistance = r_cl / max(1.0, f_cl) + 1.0 / max(h_total, 1e-6)
    dry_heat_loss = max(
        0.0,
        (t_skin - (0.55 * air_temperature_C + 0.45 * mean_radiant_temperature_C))
        / series_resistance,
    )

    metabolic_deficit = max(0.0, metabolic_rate - dry_heat_loss)

    rh_frac = relative_humidity_percent / 100.0
    p_skin = _sat_vapor_pressure_kpa(t_skin)
    p_air = rh_frac * _sat_vapor_pressure_kpa(air_temperature_C)
    h_e = 16.5 * h_c
    vapor_penalty = 1.0 + 2.22 * clo
    h_e_eff = h_e / vapor_penalty
    evaporative_capacity = max(0.0, h_e_eff * max(0.0, p_skin - p_air))

    required_sweat_rate = metabolic_deficit / _LATENT_HEAT_W_PER_L_H
    max_sweat_rate = evaporative_capacity / _LATENT_HEAT_W_PER_L_H
    actual_sweat_rate = min(required_sweat_rate, max_sweat_rate)

    evaporative_heat_removed = actual_sweat_rate * _LATENT_HEAT_W_PER_L_H
    heat_storage_w_m2 = max(0.0, metabolic_rate - dry_heat_loss - evaporative_heat_removed)
    net_heat_storage_w = heat_storage_w_m2 * body_surface_area_m2

    heat_capacity = body_mass_kg * _BODY_SPECIFIC_HEAT_J_PER_KG_K
    temp_rate_C_per_min = (
        net_heat_storage_w * 60.0 / heat_capacity if net_heat_storage_w > 0.0 else 0.0
    )
    predicted_core_temp = baseline_core_temp_C + temp_rate_C_per_min * exposure_minutes

    allowable_minutes = exposure_minutes
    limiting_factor = "Input duration"

    if temp_rate_C_per_min > 0.0:
        minutes_to_core_limit = (core_temp_limit_C - baseline_core_temp_C) / temp_rate_C_per_min
        if minutes_to_core_limit < allowable_minutes:
            allowable_minutes = max(minutes_to_core_limit, 0.0)
            limiting_factor = "Core temperature limit"
    else:
        minutes_to_core_limit = float("inf")

    if actual_sweat_rate > 0.0:
        water_limit_L = (dehydration_limit_percent / 100.0) * body_mass_kg
        minutes_to_water_limit = (water_limit_L / actual_sweat_rate) * 60.0
        if minutes_to_water_limit < allowable_minutes:
            allowable_minutes = max(minutes_to_water_limit, 0.0)
            limiting_factor = "Dehydration limit"
    else:
        minutes_to_water_limit = float("inf")

    actual_exposure_hours = exposure_minutes / 60.0
    predicted_water_loss = actual_sweat_rate * actual_exposure_hours
    dehydration_pct = (predicted_water_loss / body_mass_kg) * 100.0

    return PredictedHeatStrainResult(
        predicted_core_temperature_C=predicted_core_temp,
        required_sweat_rate_L_per_h=required_sweat_rate,
        max_sustainable_sweat_rate_L_per_h=max_sweat_rate,
        actual_sweat_rate_L_per_h=actual_sweat_rate,
        predicted_water_loss_L=predicted_water_loss,
        dehydration_percent_body_mass=dehydration_pct,
        allowable_exposure_minutes=allowable_minutes,
        limiting_factor=limiting_factor,
    )
