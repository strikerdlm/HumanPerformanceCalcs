"""Whole-body vibration (WBV) exposure metrics (ISO 2631-1 style A(8) and VDV).

This module implements **exposure scaling** and **classification** for whole-body
vibration using common ISO 2631-1 style metrics:

- Frequency-weighted root-mean-square acceleration (r.m.s., often written a_w)
- 8-hour equivalent acceleration A(8)
- Vibration Dose Value (VDV) and 8-hour VDV(8)

References (open / citable)
---------------------------
- Mansfield, N. J., Newell, G. S., & Notini, L. (2009). Earth moving machine
  whole-body vibration and the contribution of sub-1Hz components to ISO 2631-1
  metrics. *Industrial Health*, 47(4), 402–410. DOI: 10.2486/INDHEALTH.47.402
  (Defines the r.m.s. and VDV equations and discusses ISO 2631-1 metrology.)

- Orelaja, O. A., Wang, X., Ibrahim, D. S., & Sharif, U. (2019). Evaluation of
  health risk level of hand-arm and whole-body vibrations... *Journal of
  Healthcare Engineering*, 2019. DOI: 10.1155/2019/5723830
  (Provides commonly-used Health Guidance Caution Zone numbers, quoting
  A(8) bounds 0.47–0.93 m/s^2 and VDV bounds 8.5–17 m/s^1.75.)

Notes on standards and scope
----------------------------
- ISO standards are copyrighted; this code implements **generic exposure math**
  and uses widely cited threshold values as reported in published literature.
- Frequency weighting filters (Wk/Wd) are **not** implemented here. Inputs are
  assumed to already be frequency-weighted axis accelerations (a_wx, a_wy, a_wz)
  and/or a precomputed VDV.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final, Literal, Optional

__all__ = [
    "WbvAxisWeightedRms",
    "WbvExposureInputs",
    "WbvExposureResult",
    "WbvZone",
    "combine_axes_iso2631",
    "a8_from_aw",
    "vdv8_from_vdv",
    "time_to_reach_a8",
    "time_to_reach_vdv8",
    "classify_hgcz_a8",
    "classify_hgcz_vdv8",
    "compute_wbv_exposure",
]

WbvZone = Literal["below_lower", "within_hgcz", "above_upper"]

_HOURS_8_S: Final[float] = 8.0 * 3600.0

# HGCZ bounds (as commonly quoted in literature, e.g., Orelaja et al. 2019).
_A8_LOWER: Final[float] = 0.47
_A8_UPPER: Final[float] = 0.93
_VDV_LOWER: Final[float] = 8.5
_VDV_UPPER: Final[float] = 17.0

# Multiplying factors for x/y axes when combining axes (commonly cited ISO approach).
_KX: Final[float] = 1.4
_KY: Final[float] = 1.4
_KZ: Final[float] = 1.0


def _is_finite(x: float) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def _validate_positive_finite(name: str, value: float) -> float:
    v = float(value)
    if not _is_finite(v):
        raise TypeError(f"{name} must be a finite number")
    if v <= 0.0:
        raise ValueError(f"{name} must be > 0")
    return v


def _validate_nonnegative_finite(name: str, value: float) -> float:
    v = float(value)
    if not _is_finite(v):
        raise TypeError(f"{name} must be a finite number")
    if v < 0.0:
        raise ValueError(f"{name} must be >= 0")
    return v


@dataclass(frozen=True, slots=True)
class WbvAxisWeightedRms:
    """Frequency-weighted r.m.s. acceleration per axis (m/s^2)."""

    awx_m_s2: float
    awy_m_s2: float
    awz_m_s2: float


@dataclass(frozen=True, slots=True)
class WbvExposureInputs:
    """Inputs for exposure scaling.

    - `axis_aw`: already frequency-weighted r.m.s. accelerations.
    - `exposure_duration_s`: duration of the exposure being assessed.
    - `vdv_m_s1_75`: optional VDV computed over `vdv_reference_duration_s`.
      If provided, it will be scaled to VDV(8).
    """

    axis_aw: WbvAxisWeightedRms
    exposure_duration_s: float
    vdv_m_s1_75: Optional[float] = None
    vdv_reference_duration_s: Optional[float] = None


@dataclass(frozen=True, slots=True)
class WbvExposureResult:
    aw_combined_m_s2: float
    a8_m_s2: float
    a8_zone: WbvZone
    a8_lower_bound_m_s2: float
    a8_upper_bound_m_s2: float
    vdv8_m_s1_75: Optional[float]
    vdv8_zone: Optional[WbvZone]
    vdv8_lower_bound_m_s1_75: float
    vdv8_upper_bound_m_s1_75: float
    time_to_a8_lower_s: Optional[float]
    time_to_a8_upper_s: Optional[float]
    time_to_vdv8_lower_s: Optional[float]
    time_to_vdv8_upper_s: Optional[float]


def combine_axes_iso2631(axis_aw: WbvAxisWeightedRms) -> float:
    """Combine axis frequency-weighted accelerations into a single value.

    Uses multiplying factors (kx=ky=1.4, kz=1.0) commonly used with ISO 2631-1.
    """
    if not isinstance(axis_aw, WbvAxisWeightedRms):
        raise TypeError("axis_aw must be a WbvAxisWeightedRms")

    awx = _validate_nonnegative_finite("awx_m_s2", axis_aw.awx_m_s2)
    awy = _validate_nonnegative_finite("awy_m_s2", axis_aw.awy_m_s2)
    awz = _validate_nonnegative_finite("awz_m_s2", axis_aw.awz_m_s2)

    return float(math.sqrt((_KX * awx) ** 2 + (_KY * awy) ** 2 + (_KZ * awz) ** 2))


def a8_from_aw(*, aw_m_s2: float, exposure_duration_s: float) -> float:
    """Compute A(8) from frequency-weighted r.m.s. and exposure duration.

    A(8) scales as sqrt(T / 8h) assuming stationary vibration.
    """
    aw = _validate_nonnegative_finite("aw_m_s2", aw_m_s2)
    t = _validate_positive_finite("exposure_duration_s", exposure_duration_s)
    return float(aw * math.sqrt(t / _HOURS_8_S))


def vdv8_from_vdv(*, vdv_m_s1_75: float, reference_duration_s: float, exposure_duration_s: float) -> float:
    """Scale a VDV measured over a reference duration to an 8h-equivalent.

    VDV scales with the fourth root of time for stationary vibration:
    VDV(T2) = VDV(T1) * (T2/T1)^(1/4)
    """
    vdv = _validate_nonnegative_finite("vdv_m_s1_75", vdv_m_s1_75)
    t_ref = _validate_positive_finite("reference_duration_s", reference_duration_s)
    t_exp = _validate_positive_finite("exposure_duration_s", exposure_duration_s)
    # First scale to full exposure, then scale exposure -> 8h.
    vdv_exp = vdv * (t_exp / t_ref) ** 0.25
    return float(vdv_exp * (_HOURS_8_S / t_exp) ** 0.25)


def time_to_reach_a8(*, aw_m_s2: float, target_a8_m_s2: float) -> Optional[float]:
    """Solve exposure duration (s) required to reach a target A(8) at constant aw."""
    aw = _validate_nonnegative_finite("aw_m_s2", aw_m_s2)
    target = _validate_positive_finite("target_a8_m_s2", target_a8_m_s2)
    if aw <= 0.0:
        return None
    return float(_HOURS_8_S * (target / aw) ** 2)


def time_to_reach_vdv8(
    *, vdv_m_s1_75: float, reference_duration_s: float, target_vdv8_m_s1_75: float
) -> Optional[float]:
    """Solve exposure duration (s) required to reach a target VDV(8) given stationary vibration.

    Requires a VDV measured over a reference window (vdv, t_ref).
    """
    vdv = _validate_nonnegative_finite("vdv_m_s1_75", vdv_m_s1_75)
    t_ref = _validate_positive_finite("reference_duration_s", reference_duration_s)
    target = _validate_positive_finite("target_vdv8_m_s1_75", target_vdv8_m_s1_75)
    if vdv <= 0.0:
        return None

    # Derivation:
    # VDV(8) = VDV_ref * (T/ t_ref)^(1/4) * (8h / T)^(1/4)
    # => VDV(8) = VDV_ref * (8h / t_ref)^(1/4)   (independent of T) if vibration is stationary.
    # In practice, users use VDV measured over the exposure itself; here we provide a conservative
    # "time-to" using the exposure-scaling step only: VDV_exp = VDV_ref * (T/t_ref)^(1/4),
    # and then compare VDV_exp against an 8h-based threshold by scaling to 8h equivalence.
    #
    # To keep behavior deterministic and interpretable, we solve for T such that VDV_exp reaches
    # the target (treated as an 8h equivalent threshold for the scenario).
    return float(t_ref * (target / max(vdv, 1e-12)) ** 4)


def classify_hgcz_a8(a8_m_s2: float) -> WbvZone:
    a8 = _validate_nonnegative_finite("a8_m_s2", a8_m_s2)
    if a8 < _A8_LOWER:
        return "below_lower"
    if a8 > _A8_UPPER:
        return "above_upper"
    return "within_hgcz"


def classify_hgcz_vdv8(vdv8_m_s1_75: float) -> WbvZone:
    v = _validate_nonnegative_finite("vdv8_m_s1_75", vdv8_m_s1_75)
    if v < _VDV_LOWER:
        return "below_lower"
    if v > _VDV_UPPER:
        return "above_upper"
    return "within_hgcz"


def compute_wbv_exposure(inputs: WbvExposureInputs) -> WbvExposureResult:
    """Compute combined aw, A(8), optional VDV(8), and zones."""
    if not isinstance(inputs, WbvExposureInputs):
        raise TypeError("inputs must be a WbvExposureInputs")

    aw = combine_axes_iso2631(inputs.axis_aw)
    t_exp = _validate_positive_finite("exposure_duration_s", inputs.exposure_duration_s)

    a8 = a8_from_aw(aw_m_s2=aw, exposure_duration_s=t_exp)
    a8_zone = classify_hgcz_a8(a8)

    vdv8: Optional[float] = None
    vdv8_zone: Optional[WbvZone] = None
    t_vdv_lower: Optional[float] = None
    t_vdv_upper: Optional[float] = None

    if inputs.vdv_m_s1_75 is not None:
        if inputs.vdv_reference_duration_s is None:
            raise ValueError("vdv_reference_duration_s is required when vdv_m_s1_75 is provided")
        vdv8 = vdv8_from_vdv(
            vdv_m_s1_75=float(inputs.vdv_m_s1_75),
            reference_duration_s=float(inputs.vdv_reference_duration_s),
            exposure_duration_s=t_exp,
        )
        vdv8_zone = classify_hgcz_vdv8(vdv8)
        t_vdv_lower = time_to_reach_vdv8(
            vdv_m_s1_75=float(inputs.vdv_m_s1_75),
            reference_duration_s=float(inputs.vdv_reference_duration_s),
            target_vdv8_m_s1_75=_VDV_LOWER,
        )
        t_vdv_upper = time_to_reach_vdv8(
            vdv_m_s1_75=float(inputs.vdv_m_s1_75),
            reference_duration_s=float(inputs.vdv_reference_duration_s),
            target_vdv8_m_s1_75=_VDV_UPPER,
        )

    return WbvExposureResult(
        aw_combined_m_s2=float(aw),
        a8_m_s2=float(a8),
        a8_zone=a8_zone,
        a8_lower_bound_m_s2=float(_A8_LOWER),
        a8_upper_bound_m_s2=float(_A8_UPPER),
        vdv8_m_s1_75=vdv8,
        vdv8_zone=vdv8_zone,
        vdv8_lower_bound_m_s1_75=float(_VDV_LOWER),
        vdv8_upper_bound_m_s1_75=float(_VDV_UPPER),
        time_to_a8_lower_s=time_to_reach_a8(aw_m_s2=aw, target_a8_m_s2=_A8_LOWER),
        time_to_a8_upper_s=time_to_reach_a8(aw_m_s2=aw, target_a8_m_s2=_A8_UPPER),
        time_to_vdv8_lower_s=t_vdv_lower,
        time_to_vdv8_upper_s=t_vdv_upper,
    )


