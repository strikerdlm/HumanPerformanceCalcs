"""Spatial Disorientation (SD) risk assessment (deterministic, physiology-grounded).

This module intentionally avoids "black-box" probability claims. Instead it:
- Computes **physically meaningful metrics** (e.g., gravito-inertial tilt angle).
- Applies **explicit, cited thresholds** from aviation physiology references.
- Produces a bounded **SD Risk Index (0–100)** for relative comparison across scenarios.

Key quantitative anchors used
-----------------------------
1) Semicircular canal perceptual threshold (leans risk):
   FAA states an approximate threshold of ~2°/s below which gradual rotation may go unnoticed.
   - https://www.faa.gov/pilots/training/airman_education/topics_of_interest/spatial_disorientation

   An FAA physiology PDF (also circulated via NTSB docket) similarly notes detection around ~2°/s.
   - https://data.ntsb.gov/Docket/Document/docBLOB?ID=40482287&FileExtension=.PDF&FileName=FAA+Aviation+Physiology+--+Spatial+Disorientation-Master.PDF

2) Canal "adaptation" / entrainment window:
   Constant-rate turns can become less perceptible after ~10–20 s (endolymph catches up).
   - StatPearls: Physiology of Spatial Orientation (NCBI Bookshelf)
     https://www.ncbi.nlm.nih.gov/books/NBK518976/

3) Coriolis illusion threshold (modern quantified study):
   Coriolis illusion perceived at yaw rates exceeding ~10°/s given a representative head motion.
   - Houben et al. (2022). "The perception threshold of the vestibular Coriolis illusion."
     Abstract via PubMed: https://pubmed.ncbi.nlm.nih.gov/34924407/

4) Somatogravic tilt from gravito-inertial acceleration (GIA):
   The perceived "tilt" is often explained as the direction of the resultant gravito-inertial vector.
   We therefore compute pitch error from forward linear acceleration as:
       tilt_deg = atan(a_forward / g) * 180/pi
   This is consistent with experimental paradigms where ~0.58 g corresponds to ~30°.
   - PubMed: https://pubmed.ncbi.nlm.nih.gov/9491247/
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final, Literal

__all__ = [
    "SpatialDisorientationInputs",
    "SpatialDisorientationResult",
    "spatial_disorientation_risk",
]


RiskLevel = Literal["Low", "Moderate", "High", "Very High"]

G_M_S2: Final[float] = 9.80665

# Quantitative anchors (see module docstring for citations).
LEANS_DETECTION_THRESHOLD_DEG_S: Final[float] = 2.0
CANAL_ENTRAINMENT_SECONDS_MIN: Final[float] = 10.0
CANAL_ENTRAINMENT_SECONDS_MAX: Final[float] = 20.0
CORIOLIS_YAW_THRESHOLD_DEG_S: Final[float] = 10.0


@dataclass(frozen=True, slots=True)
class SpatialDisorientationInputs:
    """Inputs for SD assessment.

    Notes
    - This is a scenario-level estimator: it does not model individual physiology.
    - All inputs are expected to be **current** and representative of the event window.
    """

    # Flight environment / cues
    imc: bool
    night: bool
    nvg: bool
    time_since_horizon_reference_s: float

    # Motion / maneuver (simplified)
    yaw_rate_deg_s: float
    sustained_turn_duration_s: float
    head_movement_during_turn: bool

    # Linear acceleration along aircraft forward axis (+ = accelerating)
    forward_accel_m_s2: float

    # Workload / task saturation proxy (0..1)
    workload: float = 0.5


@dataclass(frozen=True, slots=True)
class SpatialDisorientationResult:
    risk_index_0_100: float
    risk_level: RiskLevel
    likely_illusions: tuple[str, ...]
    somatogravic_tilt_deg: float
    leans_risk_component_0_1: float
    canal_entraintment_component_0_1: float
    coriolis_component_0_1: float
    somatogravic_component_0_1: float
    cue_deprivation_component_0_1: float


def _clamp(x: float, lo: float, hi: float) -> float:
    return float(max(lo, min(hi, x)))


def _smoothstep01(x: float) -> float:
    """Cubic smoothstep for x in [0,1]."""
    v = _clamp(x, 0.0, 1.0)
    return float(v * v * (3.0 - 2.0 * v))


def _validate_finite(name: str, x: float) -> float:
    if not isinstance(x, (int, float)):
        raise TypeError(f"{name} must be a number")
    v = float(x)
    if not math.isfinite(v):
        raise ValueError(f"{name} must be finite")
    return v


def _cue_deprivation(imc: bool, night: bool, nvg: bool, time_since_horizon_s: float) -> float:
    # Deterministic cue deprivation proxy in [0,1].
    # Rationale: loss of external horizon cues is a primary amplifier of vestibular illusions
    # and instrument misinterpretation risk in SD training materials (FAA).
    base = 0.0
    if imc:
        base += 0.55
    if night:
        base += 0.25
    if nvg:
        base += 0.20
    # Time without horizon reference increases risk; saturate beyond ~60 s.
    t = _clamp(float(time_since_horizon_s), 0.0, 120.0)
    time_factor = _smoothstep01(t / 60.0) * 0.35
    return _clamp(base + time_factor, 0.0, 1.0)


def _leans_component(yaw_rate_deg_s: float, turn_duration_s: float) -> float:
    # "Leans" risk is elevated when rotation rate is below detection threshold (~2°/s)
    # and sustained long enough that a slow bank can go unnoticed (FAA).
    r = abs(float(yaw_rate_deg_s))
    d = float(turn_duration_s)
    if d <= 0.0:
        return 0.0
    below = _clamp((LEANS_DETECTION_THRESHOLD_DEG_S - r) / LEANS_DETECTION_THRESHOLD_DEG_S, 0.0, 1.0)
    # Saturate after ~20 s (consistent with canal dynamics discussions).
    dur = _smoothstep01(_clamp(d / CANAL_ENTRAINMENT_SECONDS_MAX, 0.0, 1.0))
    return float(below * dur)


def _canal_entrainment_component(yaw_rate_deg_s: float, turn_duration_s: float) -> float:
    # Sustained constant-rate turn beyond ~10–20 s risks "adaptation" (endolymph catches up),
    # setting up post-turn illusions (e.g., graveyard spiral) if cues are poor.
    r = abs(float(yaw_rate_deg_s))
    d = float(turn_duration_s)
    if d <= 0.0 or r < LEANS_DETECTION_THRESHOLD_DEG_S:
        return 0.0
    # Ramp between 10 and 20 seconds.
    x = (d - CANAL_ENTRAINMENT_SECONDS_MIN) / (CANAL_ENTRAINMENT_SECONDS_MAX - CANAL_ENTRAINMENT_SECONDS_MIN)
    return _smoothstep01(x)


def _coriolis_component(yaw_rate_deg_s: float, head_movement: bool) -> float:
    # Quantitative anchor: Coriolis illusion perceived at yaw rates exceeding ~10°/s with head motion.
    if not head_movement:
        return 0.0
    r = abs(float(yaw_rate_deg_s))
    if r <= CORIOLIS_YAW_THRESHOLD_DEG_S:
        return 0.0
    # Saturate by ~30°/s (heuristic scaling; threshold itself is cited).
    return _smoothstep01((r - CORIOLIS_YAW_THRESHOLD_DEG_S) / 20.0)


def _somatogravic_tilt_deg(forward_accel_m_s2: float) -> float:
    # Resultant gravito-inertial vector tilt in pitch plane: atan(a_forward / g).
    a = float(forward_accel_m_s2)
    return float(math.degrees(math.atan2(a, G_M_S2)))


def _somatogravic_component(tilt_deg: float) -> float:
    # A 30° equivalent tilt is commonly used in experimental demonstrations (e.g., ~0.58 g ≈ 30°).
    # We scale tilt magnitude into [0,1] with saturation by 30°.
    t = abs(float(tilt_deg))
    return _smoothstep01(_clamp(t / 30.0, 0.0, 1.0))


def spatial_disorientation_risk(inputs: SpatialDisorientationInputs) -> SpatialDisorientationResult:
    """Compute SD Risk Index (0–100) and likely illusion flags.

    The index is a bounded monotone mapping of component scores, intended for
    *relative* comparison across scenarios. It is not a calibrated mishap probability.
    """
    if not isinstance(inputs, SpatialDisorientationInputs):
        raise TypeError("inputs must be a SpatialDisorientationInputs instance")

    t_hz = _validate_finite("time_since_horizon_reference_s", inputs.time_since_horizon_reference_s)
    yaw = _validate_finite("yaw_rate_deg_s", inputs.yaw_rate_deg_s)
    turn_t = _validate_finite("sustained_turn_duration_s", inputs.sustained_turn_duration_s)
    acc = _validate_finite("forward_accel_m_s2", inputs.forward_accel_m_s2)
    workload = _validate_finite("workload", inputs.workload)
    if t_hz < 0.0:
        raise ValueError("time_since_horizon_reference_s must be >= 0")
    if turn_t < 0.0:
        raise ValueError("sustained_turn_duration_s must be >= 0")
    if workload < 0.0 or workload > 1.0:
        raise ValueError("workload must be within [0, 1]")

    cue = _cue_deprivation(bool(inputs.imc), bool(inputs.night), bool(inputs.nvg), t_hz)
    leans = _leans_component(yaw, turn_t)
    entrain = _canal_entrainment_component(yaw, turn_t)
    coriolis = _coriolis_component(yaw, bool(inputs.head_movement_during_turn))
    tilt = _somatogravic_tilt_deg(acc)
    somato = _somatogravic_component(tilt)

    # Combine components.
    #
    # Hard reasoning: SD severity rises when vestibular illusion drivers are present AND
    # when visual/horizon cues are degraded AND when workload is high (reduced capacity
    # for cross-checking instruments).
    #
    # We therefore:
    # - weight vestibular drivers (leans/entrainment/coriolis/somatogravic)
    # - amplify by cue deprivation and workload in a bounded way
    vestibular_sum = (1.0 * leans) + (1.0 * entrain) + (1.2 * coriolis) + (1.1 * somato)
    vestibular_sum = _clamp(vestibular_sum / 4.3, 0.0, 1.0)  # normalize to [0,1]
    amplifier = _clamp(0.55 + 0.45 * cue, 0.0, 1.0) * _clamp(0.70 + 0.30 * workload, 0.0, 1.0)
    combined = _clamp(vestibular_sum * amplifier, 0.0, 1.0)

    # Map to 0–100 with a mild exponential saturation for readability.
    risk_index = 100.0 * (1.0 - math.exp(-2.2 * combined))

    if risk_index < 25.0:
        level: RiskLevel = "Low"
    elif risk_index < 50.0:
        level = "Moderate"
    elif risk_index < 75.0:
        level = "High"
    else:
        level = "Very High"

    illusions: list[str] = []
    if leans >= 0.45:
        illusions.append("Leans (slow unnoticed bank)")
    if entrain >= 0.45:
        illusions.append("Post-turn canal entrainment risk (graveyard spiral/spin)")
    if coriolis >= 0.35:
        illusions.append("Coriolis illusion (head movement during turn)")
    if somato >= 0.35 and cue >= 0.35:
        illusions.append("Somatogravic illusion (GIA tilt / pitch misperception)")

    return SpatialDisorientationResult(
        risk_index_0_100=float(_clamp(risk_index, 0.0, 100.0)),
        risk_level=level,
        likely_illusions=tuple(illusions),
        somatogravic_tilt_deg=float(tilt),
        leans_risk_component_0_1=float(_clamp(leans, 0.0, 1.0)),
        canal_entraintment_component_0_1=float(_clamp(entrain, 0.0, 1.0)),
        coriolis_component_0_1=float(_clamp(coriolis, 0.0, 1.0)),
        somatogravic_component_0_1=float(_clamp(somato, 0.0, 1.0)),
        cue_deprivation_component_0_1=float(_clamp(cue, 0.0, 1.0)),
    )


