"""Anti-G Straining Maneuver (AGSM) effectiveness model.

This module provides a deterministic, parameterized estimate of +Gz tolerance
changes attributable to:
- anti-G suit (AGS)
- positive pressure breathing for G (PBG/PBfG)
- anti-G straining maneuver quality (AGSM)

Scientific grounding (defaults)
------------------------------
The default deltas are anchored to published experimental results comparing
configurations during rapid-onset +Gz profiles:

- G protection interaction of straining and pressure breathing:
  https://pubmed.ncbi.nlm.nih.gov/17484342/
  (Reports representative tolerance levels by condition: no protection, AGS,
  AGS+PBG, AGS+AGSM, AGS+PBG+AGSM.)

Important scope notes
---------------------
- This is **not** an operational flight safety tool.
- Individual tolerance depends on many factors (hydration, fatigue, illness,
  posture, onset rate, seat tilt, equipment fit, training status).
- The model is intentionally transparent and **parameterized** so assumptions
  are explicit and can be tuned to a validated local dataset if needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

__all__ = [
    "AgsmInputs",
    "AgsmResult",
    "estimate_gz_tolerance_with_agsm",
]


DEFAULT_BASELINE_RELAXED_GZ: Final[float] = 3.4
DEFAULT_MAX_SYSTEM_GZ: Final[float] = 9.0

# Default deltas (in +Gz) anchored to the published condition values in PubMed 17484342.
# Condition I (relaxed, no garment)  ~3.4 Gz
# Condition II (relaxed + anti-G suit) >=6.5 Gz  => delta_suit ≈ 3.1
# Condition III (suit + pressure breathing) >=8.0 Gz => delta_pbg ≈ 1.5 beyond suit
# Condition IV (suit + AGSM) >=8.9 Gz => delta_agsm ≈ 2.4 beyond suit (at full quality)
# Condition V (suit + PBG + AGSM) >=9.0 Gz (cap / saturation)
DEFAULT_SUIT_DELTA_GZ: Final[float] = 6.5 - 3.4  # 3.1
DEFAULT_PBG_DELTA_GZ: Final[float] = 8.0 - 6.5  # 1.5
DEFAULT_AGSM_DELTA_GZ: Final[float] = 8.9 - 6.5  # 2.4


@dataclass(frozen=True, slots=True)
class AgsmInputs:
    """Inputs for the AGSM effectiveness estimate.

    Units
    - All tolerance/deltas are expressed in +Gz units.
    """

    baseline_relaxed_gz: float = DEFAULT_BASELINE_RELAXED_GZ
    anti_g_suit: bool = True
    pressure_breathing_for_g: bool = False
    agsm_quality: float = 1.0
    suit_delta_gz: float = DEFAULT_SUIT_DELTA_GZ
    pbg_delta_gz: float = DEFAULT_PBG_DELTA_GZ
    agsm_delta_gz: float = DEFAULT_AGSM_DELTA_GZ
    max_system_gz: float = DEFAULT_MAX_SYSTEM_GZ


@dataclass(frozen=True, slots=True)
class AgsmResult:
    baseline_relaxed_gz: float
    suit_component_gz: float
    pbg_component_gz: float
    agsm_component_gz: float
    raw_estimated_gz: float
    capped_estimated_gz: float
    was_capped: bool


def estimate_gz_tolerance_with_agsm(inputs: AgsmInputs) -> AgsmResult:
    """Estimate +Gz tolerance with AGS/PBG/AGSM components.

    Parameters
    ----------
    inputs:
        Input bundle containing baseline tolerance and protection settings.

    Returns
    -------
    AgsmResult
        Component-wise breakdown and the final (possibly capped) estimate.

    Raises
    ------
    TypeError
        If input types are invalid.
    ValueError
        If numeric ranges are invalid (negative tolerances/deltas, etc.).
    """
    if not isinstance(inputs, AgsmInputs):
        raise TypeError("inputs must be an AgsmInputs instance")

    baseline = float(inputs.baseline_relaxed_gz)
    if baseline <= 0.0:
        raise ValueError("baseline_relaxed_gz must be > 0")

    suit_delta = float(inputs.suit_delta_gz)
    pbg_delta = float(inputs.pbg_delta_gz)
    agsm_delta = float(inputs.agsm_delta_gz)
    if suit_delta < 0.0 or pbg_delta < 0.0 or agsm_delta < 0.0:
        raise ValueError("Delta values must be >= 0")

    q = float(inputs.agsm_quality)
    if q < 0.0 or q > 1.0:
        raise ValueError("agsm_quality must be within [0, 1]")

    max_gz = float(inputs.max_system_gz)
    if max_gz <= 0.0:
        raise ValueError("max_system_gz must be > 0")

    suit_component = suit_delta if bool(inputs.anti_g_suit) else 0.0
    pbg_component = pbg_delta if (bool(inputs.anti_g_suit) and bool(inputs.pressure_breathing_for_g)) else 0.0
    agsm_component = (agsm_delta * q) if (bool(inputs.anti_g_suit) and q > 0.0) else 0.0

    raw = baseline + suit_component + pbg_component + agsm_component
    capped = min(raw, max_gz)
    return AgsmResult(
        baseline_relaxed_gz=baseline,
        suit_component_gz=suit_component,
        pbg_component_gz=pbg_component,
        agsm_component_gz=agsm_component,
        raw_estimated_gz=raw,
        capped_estimated_gz=capped,
        was_capped=(capped < raw),
    )


