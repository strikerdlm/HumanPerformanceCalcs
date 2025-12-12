"""Simple sweat rate and dehydration estimators.

These functions implement a basic mass-balance approach commonly used in field
hydration monitoring.

Assumptions
- 1 kg body mass change is approximated as 1 L water change.
- Inputs represent a single session; extremely large acute mass losses are
  treated as likely measurement/unit errors.

This module is intentionally small and import-safe.
"""

from __future__ import annotations

from typing import Final


_MAX_ACUTE_BODY_MASS_LOSS_FRACTION: Final[float] = 0.05  # 5% in a single session is treated as suspicious


def calculate_sweat_rate(
    initial_weight_kg: float,
    final_weight_kg: float,
    fluid_intake_l: float,
    urine_output_l: float,
    duration_hours: float,
) -> float:
    """Estimate sweat rate in L/h from session measurements.

    Sweat loss (L) is approximated as:
        (initial_weight - final_weight) + fluid_intake - urine_output

    Args:
        initial_weight_kg: Body mass at start (kg).
        final_weight_kg: Body mass at end (kg).
        fluid_intake_l: Fluid intake during session (L).
        urine_output_l: Urine output during session (L).
        duration_hours: Session duration (h).

    Returns:
        Estimated sweat rate (L/h). Can be negative if weight increased.

    Raises:
        ValueError: For invalid ranges or suspiciously large acute mass losses.
    """

    wi = float(initial_weight_kg)
    wf = float(final_weight_kg)
    intake = float(fluid_intake_l)
    urine = float(urine_output_l)
    hours = float(duration_hours)

    if wi <= 0.0:
        raise ValueError("initial_weight_kg must be > 0")
    if wf <= 0.0:
        raise ValueError("final_weight_kg must be > 0")
    if intake < 0.0:
        raise ValueError("fluid_intake_l must be >= 0")
    if urine < 0.0:
        raise ValueError("urine_output_l must be >= 0")
    if hours <= 0.0:
        raise ValueError("duration_hours must be > 0")

    weight_loss_kg = wi - wf
    if weight_loss_kg > _MAX_ACUTE_BODY_MASS_LOSS_FRACTION * wi:
        raise ValueError("Unrealistic acute weight loss for a single session")

    sweat_loss_l = weight_loss_kg + intake - urine
    return sweat_loss_l / hours


def get_dehydration_percentage(initial_weight_kg: float, final_weight_kg: float) -> float:
    """Compute dehydration percentage as percent body mass change.

    Returns negative values if final_weight_kg > initial_weight_kg.
    """

    wi = float(initial_weight_kg)
    wf = float(final_weight_kg)

    if wi <= 0.0:
        raise ValueError("initial_weight_kg must be > 0")
    if wf <= 0.0:
        raise ValueError("final_weight_kg must be > 0")

    return ((wi - wf) / wi) * 100.0


def interpret_sweat_rate(sweat_rate_l_per_h: float) -> str:
    """Interpret sweat rate (L/h) into practical hydration categories."""

    x = float(sweat_rate_l_per_h)
    if x < 0.75:
        return "Low sweat rate"
    if x < 1.5:
        return "Moderate sweat rate"
    if x < 2.5:
        return "High sweat rate"
    return "Very high sweat rate"


def interpret_dehydration(dehydration_percent: float) -> str:
    """Interpret dehydration (% body mass loss) into severity categories."""

    x = float(dehydration_percent)
    if x < 1.0:
        return "Minimal dehydration"
    if x < 2.0:
        return "Mild dehydration"
    if x < 3.5:
        return "Moderate dehydration"
    return "Severe dehydration"


def calculate_replacement_fluid_needed(
    sweat_rate_l_per_h: float,
    duration_hours: float,
    *,
    replacement_fraction: float = 1.0,
) -> tuple[float, float]:
    """Estimate recommended fluid replacement rate and total volume.

    This helper is commonly used in field hydration planning: replace some
    fraction of estimated sweat losses to limit dehydration.

    Args:
        sweat_rate_l_per_h: Estimated sweat rate (L/h).
        duration_hours: Planned duration (h).
        replacement_fraction: Fraction of sweat losses to replace (0–1.5).
            Values slightly above 1.0 can be used for planned rehydration.

    Returns:
        (recommended_rate_l_per_h, recommended_total_l)

    Raises:
        ValueError: If duration is not positive or replacement_fraction invalid.
    """

    rate = float(sweat_rate_l_per_h)
    hours = float(duration_hours)
    frac = float(replacement_fraction)

    if hours <= 0.0:
        raise ValueError("duration_hours must be > 0")
    if frac < 0.0 or frac > 1.5:
        raise ValueError("replacement_fraction must be between 0 and 1.5")

    if rate <= 0.0:
        return 0.0, 0.0

    recommended_rate = rate * frac
    return recommended_rate, recommended_rate * hours
