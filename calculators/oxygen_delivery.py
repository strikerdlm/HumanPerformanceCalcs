"""Oxygen content and oxygen delivery (CaO2 / DO2 / DO2I).

Core equations (standard physiology)
-----------------------------------
Arterial oxygen content (CaO2):

    CaO2 = (Hufner * Hb * SaO2) + (alpha * PaO2)

Where:
- Hb in g/dL
- SaO2 as fraction (0–1)
- PaO2 in mmHg
- Hufner is oxygen-carrying capacity per gram Hb (commonly ~1.34 mL O2/g Hb)
- alpha is dissolved oxygen solubility in plasma (commonly ~0.003 mL O2/dL/mmHg)

Oxygen delivery (DO2):

    DO2 (mL O2/min) = CO (L/min) * CaO2 (mL O2/dL) * 10

Oxygen delivery index (DO2I):

    DO2I = DO2 / BSA

Primary reference anchor (open, equation context)
-------------------------------------------------
The classic paper below uses oxygen content/capacity concepts and discusses methodology:
- Filley, G. F., et al. (1954). J Clin Invest. https://doi.org/10.1172/JCI102922

Notes
-----
- Because constants vary by source and measurement convention (e.g., 1.34–1.39 mL/g),
  this module exposes `hufner_ml_per_g` and `alpha_ml_per_dl_per_mmhg` as parameters.
- This is a deterministic calculator; interpretation thresholds depend on context (ICU vs altitude vs exercise).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

__all__ = [
    "OxygenDeliveryInputs",
    "OxygenDeliveryResult",
    "compute_oxygen_delivery",
    "dubois_bsa_m2",
]


def _is_finite(x: float) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def _validate_positive(name: str, x: float) -> float:
    v = float(x)
    if not _is_finite(v):
        raise TypeError(f"{name} must be a finite number")
    if v <= 0.0:
        raise ValueError(f"{name} must be > 0")
    return v


def _validate_nonnegative(name: str, x: float) -> float:
    v = float(x)
    if not _is_finite(v):
        raise TypeError(f"{name} must be a finite number")
    if v < 0.0:
        raise ValueError(f"{name} must be >= 0")
    return v


def dubois_bsa_m2(*, height_cm: float, weight_kg: float) -> float:
    """DuBois & DuBois BSA formula (commonly used clinical approximation).

    BSA (m^2) = 0.007184 * height_cm^0.725 * weight_kg^0.425
    """
    h = _validate_positive("height_cm", height_cm)
    w = _validate_positive("weight_kg", weight_kg)
    return float(0.007184 * (h**0.725) * (w**0.425))


@dataclass(frozen=True, slots=True)
class OxygenDeliveryInputs:
    hb_g_dl: float
    sao2_frac: float
    pao2_mmhg: float
    cardiac_output_l_min: float
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bsa_m2: Optional[float] = None
    hufner_ml_per_g: float = 1.34
    alpha_ml_per_dl_per_mmhg: float = 0.003


@dataclass(frozen=True, slots=True)
class OxygenDeliveryResult:
    cao2_ml_o2_dl: float
    o2_bound_ml_o2_dl: float
    o2_dissolved_ml_o2_dl: float
    do2_ml_o2_min: float
    bsa_m2: Optional[float]
    do2i_ml_o2_min_m2: Optional[float]


def compute_oxygen_delivery(inputs: OxygenDeliveryInputs) -> OxygenDeliveryResult:
    if not isinstance(inputs, OxygenDeliveryInputs):
        raise TypeError("inputs must be OxygenDeliveryInputs")

    hb = _validate_nonnegative("hb_g_dl", inputs.hb_g_dl)
    sao2 = float(inputs.sao2_frac)
    if not _is_finite(sao2) or sao2 < 0.0 or sao2 > 1.0:
        raise ValueError("sao2_frac must be between 0 and 1")
    pao2 = _validate_nonnegative("pao2_mmhg", inputs.pao2_mmhg)
    co = _validate_positive("cardiac_output_l_min", inputs.cardiac_output_l_min)
    huf = _validate_positive("hufner_ml_per_g", inputs.hufner_ml_per_g)
    alpha = _validate_positive("alpha_ml_per_dl_per_mmhg", inputs.alpha_ml_per_dl_per_mmhg)

    o2_bound = float(huf * hb * sao2)
    o2_diss = float(alpha * pao2)
    cao2 = float(o2_bound + o2_diss)

    do2 = float(co * cao2 * 10.0)  # dL/L = 10

    bsa: Optional[float] = None
    if inputs.bsa_m2 is not None:
        bsa = _validate_positive("bsa_m2", inputs.bsa_m2)
    elif inputs.height_cm is not None and inputs.weight_kg is not None:
        bsa = dubois_bsa_m2(height_cm=float(inputs.height_cm), weight_kg=float(inputs.weight_kg))

    do2i: Optional[float] = None
    if bsa is not None:
        do2i = float(do2 / bsa)

    return OxygenDeliveryResult(
        cao2_ml_o2_dl=float(cao2),
        o2_bound_ml_o2_dl=float(o2_bound),
        o2_dissolved_ml_o2_dl=float(o2_diss),
        do2_ml_o2_min=float(do2),
        bsa_m2=bsa,
        do2i_ml_o2_min_m2=do2i,
    )


