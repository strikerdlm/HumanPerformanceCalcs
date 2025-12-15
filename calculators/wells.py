"""Wells clinical prediction rules (DVT and PE).

These deterministic calculators implement the original/standard point systems for:

- Suspected lower-extremity deep vein thrombosis (DVT)
- Suspected pulmonary embolism (PE)

Primary references (original derivations/validation in common use):
- Wells PS, et al. (2003). *Evaluation of D-dimer in the diagnosis of suspected deep-vein thrombosis*.
  New England Journal of Medicine, 349(13), 1227–1235. https://doi.org/10.1056/NEJMoa023153
- Wells PS, et al. (2001). *Excluding Pulmonary Embolism at the Bedside without Diagnostic Imaging...*
  Annals of Internal Medicine, 135(2), 98–107. https://doi.org/10.7326/0003-4819-135-2-200107170-00010

Notes / limitations:
- These rules are intended to support structured clinical assessment; they are not diagnoses.
- D-dimer thresholds and imaging pathways are institution-, assay-, and patient-specific. This module
  returns risk strata only; downstream testing guidance should be applied per local protocols.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal, Optional

__all__ = [
    "WellsDvtInputs",
    "WellsDvtResult",
    "compute_wells_dvt",
    "WellsPeInputs",
    "WellsPeResult",
    "compute_wells_pe",
]


def _is_finite(x: float) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def _validate_nonnegative(name: str, x: float) -> float:
    v = float(x)
    if not _is_finite(v):
        raise TypeError(f"{name} must be a finite number")
    if v < 0.0:
        raise ValueError(f"{name} must be >= 0")
    return v


WellsDvtThreeTier = Literal["low", "moderate", "high"]
WellsDvtTwoTier = Literal["unlikely", "likely"]


@dataclass(frozen=True, slots=True)
class WellsDvtInputs:
    """Inputs for Wells DVT score (lower extremity).

    Criteria (+1 each unless specified):
    - active_cancer
    - paralysis_paresis_or_recent_plaster_immobilization
    - recently_bedridden_gt3d_or_major_surgery_within_12w
    - localized_tenderness_along_deep_venous_system
    - entire_leg_swollen
    - calf_swelling_gt_3cm_compared_to_asymptomatic_leg (can be derived from `calf_diff_cm`)
    - pitting_edema_confined_to_symptomatic_leg
    - collateral_superficial_veins_nonvaricose

    Subtraction:
    - alternative_diagnosis_as_likely_as_dvt: -2 points
    """

    active_cancer: bool = False
    paralysis_paresis_or_recent_plaster_immobilization: bool = False
    recently_bedridden_gt3d_or_major_surgery_within_12w: bool = False
    localized_tenderness_along_deep_venous_system: bool = False
    entire_leg_swollen: bool = False
    calf_diff_cm: Optional[float] = None
    calf_swelling_gt_3cm_compared_to_asymptomatic_leg: Optional[bool] = None
    pitting_edema_confined_to_symptomatic_leg: bool = False
    collateral_superficial_veins_nonvaricose: bool = False
    alternative_diagnosis_as_likely_as_dvt: bool = False


@dataclass(frozen=True, slots=True)
class WellsDvtResult:
    total_points: float
    points_positive: float
    points_negative: float
    three_tier: WellsDvtThreeTier
    two_tier: WellsDvtTwoTier
    calf_diff_cm_used: Optional[float]
    calf_swelling_gt_3cm: bool


def compute_wells_dvt(inputs: WellsDvtInputs) -> WellsDvtResult:
    """Compute Wells DVT score and stratification (2-tier and 3-tier)."""
    if not isinstance(inputs, WellsDvtInputs):
        raise TypeError("inputs must be WellsDvtInputs")

    calf_diff_cm_used: Optional[float] = None
    calf_swelling: bool

    if inputs.calf_swelling_gt_3cm_compared_to_asymptomatic_leg is not None:
        calf_swelling = bool(inputs.calf_swelling_gt_3cm_compared_to_asymptomatic_leg)
        if inputs.calf_diff_cm is not None:
            calf_diff_cm_used = _validate_nonnegative("calf_diff_cm", inputs.calf_diff_cm)
            derived = calf_diff_cm_used > 3.0
            if derived != calf_swelling:
                raise ValueError("calf_diff_cm conflicts with calf_swelling_gt_3cm_compared_to_asymptomatic_leg")
        else:
            calf_diff_cm_used = None
    else:
        if inputs.calf_diff_cm is None:
            calf_swelling = False
            calf_diff_cm_used = None
        else:
            calf_diff_cm_used = _validate_nonnegative("calf_diff_cm", inputs.calf_diff_cm)
            calf_swelling = calf_diff_cm_used > 3.0

    pos = 0.0
    if inputs.active_cancer:
        pos += 1.0
    if inputs.paralysis_paresis_or_recent_plaster_immobilization:
        pos += 1.0
    if inputs.recently_bedridden_gt3d_or_major_surgery_within_12w:
        pos += 1.0
    if inputs.localized_tenderness_along_deep_venous_system:
        pos += 1.0
    if inputs.entire_leg_swollen:
        pos += 1.0
    if calf_swelling:
        pos += 1.0
    if inputs.pitting_edema_confined_to_symptomatic_leg:
        pos += 1.0
    if inputs.collateral_superficial_veins_nonvaricose:
        pos += 1.0

    neg = 2.0 if inputs.alternative_diagnosis_as_likely_as_dvt else 0.0
    total = float(pos - neg)

    # 3-tier (classic): <=0 low, 1-2 moderate, >=3 high
    if total <= 0.0:
        three: WellsDvtThreeTier = "low"
    elif total <= 2.0:
        three = "moderate"
    else:
        three = "high"

    # 2-tier ("likely/unlikely"): <=1 unlikely, >=2 likely (commonly used dichotomization)
    two: WellsDvtTwoTier = "unlikely" if total <= 1.0 else "likely"

    return WellsDvtResult(
        total_points=float(total),
        points_positive=float(pos),
        points_negative=float(neg),
        three_tier=three,
        two_tier=two,
        calf_diff_cm_used=calf_diff_cm_used,
        calf_swelling_gt_3cm=bool(calf_swelling),
    )


WellsPeThreeTier = Literal["low", "moderate", "high"]
WellsPeTwoTier = Literal["unlikely", "likely"]


@dataclass(frozen=True, slots=True)
class WellsPeInputs:
    """Inputs for Wells PE score.

    Criteria:
    - clinical_signs_dvt: +3
    - pe_most_likely_diagnosis: +3 (alternative diagnosis less likely than PE)
    - heart_rate_bpm_gt_100: +1.5 (can be derived from `heart_rate_bpm`)
    - immobilization_ge3d_or_surgery_within_4w: +1.5
    - previous_dvt_or_pe: +1.5
    - hemoptysis: +1
    - malignancy_on_treatment_or_within_6m_or_palliative: +1
    """

    clinical_signs_dvt: bool = False
    pe_most_likely_diagnosis: bool = False
    heart_rate_bpm: Optional[float] = None
    heart_rate_bpm_gt_100: Optional[bool] = None
    immobilization_ge3d_or_surgery_within_4w: bool = False
    previous_dvt_or_pe: bool = False
    hemoptysis: bool = False
    malignancy_on_treatment_or_within_6m_or_palliative: bool = False


@dataclass(frozen=True, slots=True)
class WellsPeResult:
    total_points: float
    three_tier: WellsPeThreeTier
    two_tier: WellsPeTwoTier
    heart_rate_bpm_used: Optional[float]
    heart_rate_gt_100: bool


def compute_wells_pe(inputs: WellsPeInputs) -> WellsPeResult:
    """Compute Wells PE score and stratification (2-tier and 3-tier)."""
    if not isinstance(inputs, WellsPeInputs):
        raise TypeError("inputs must be WellsPeInputs")

    hr_used: Optional[float] = None
    hr_gt_100: bool

    if inputs.heart_rate_bpm_gt_100 is not None:
        hr_gt_100 = bool(inputs.heart_rate_bpm_gt_100)
        if inputs.heart_rate_bpm is not None:
            hr_used = _validate_nonnegative("heart_rate_bpm", inputs.heart_rate_bpm)
            derived = hr_used > 100.0
            if derived != hr_gt_100:
                raise ValueError("heart_rate_bpm conflicts with heart_rate_bpm_gt_100")
        else:
            hr_used = None
    else:
        if inputs.heart_rate_bpm is None:
            hr_gt_100 = False
            hr_used = None
        else:
            hr_used = _validate_nonnegative("heart_rate_bpm", inputs.heart_rate_bpm)
            hr_gt_100 = hr_used > 100.0

    total = 0.0
    if inputs.clinical_signs_dvt:
        total += 3.0
    if inputs.pe_most_likely_diagnosis:
        total += 3.0
    if hr_gt_100:
        total += 1.5
    if inputs.immobilization_ge3d_or_surgery_within_4w:
        total += 1.5
    if inputs.previous_dvt_or_pe:
        total += 1.5
    if inputs.hemoptysis:
        total += 1.0
    if inputs.malignancy_on_treatment_or_within_6m_or_palliative:
        total += 1.0

    # 3-tier (classic): <2 low, 2-6 moderate, >6 high
    if total < 2.0:
        three: WellsPeThreeTier = "low"
    elif total <= 6.0:
        three = "moderate"
    else:
        three = "high"

    # 2-tier: <=4 PE unlikely, >4 PE likely (commonly used dichotomization)
    two: WellsPeTwoTier = "unlikely" if total <= 4.0 else "likely"

    return WellsPeResult(
        total_points=float(total),
        three_tier=three,
        two_tier=two,
        heart_rate_bpm_used=hr_used,
        heart_rate_gt_100=bool(hr_gt_100),
    )


