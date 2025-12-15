"""Alveolar–arterial oxygen gradient (A–a gradient).

Definitions
-----------
The A–a oxygen gradient is:

    A–a = PAO2 − PaO2

where:
- PAO2 is calculated using the alveolar gas equation, and
- PaO2 is measured arterial oxygen tension.

Primary reference (open)
------------------------
- Filley, G. F., Grégoire, F., & Wright, G. W. (1954).
  *Alveolar and arterial oxygen tensions and the significance of the
  alveolar-arterial oxygen tension difference in normal men*.
  Journal of Clinical Investigation, 33(4), 517–529. https://doi.org/10.1172/JCI102922

Age effect (supporting reference; full text may require access)
--------------------------------------------------------------
- Harris, E. A., et al. (1974). *The Normal Alveolar-Arterial Oxygen-Tension Gradient in Man*.
  Clinical Science, 46(1), 89–104. https://doi.org/10.1042/cs0460089

Notes
-----
- This module provides a transparent computation and a **reference** normal range based on
  Filley et al. (1954) (resting air-breathing cohort at ~1600 ft elevation).
- Many clinical “age-adjusted” shortcut formulas exist; because they are not consistently sourced
  in open primary literature, this implementation exposes a conservative optional heuristic as such.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final, Literal, Optional

from .atmosphere import alveolar_PO2

__all__ = [
    "AaGradientInputs",
    "AaGradientResult",
    "compute_aa_gradient",
]

AaNormalModel = Literal["filley1954_rest_air_1600ft", "heuristic_age_over4_plus4"]


def _is_finite(x: float) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def _validate_nonnegative(name: str, x: float) -> float:
    v = float(x)
    if not _is_finite(v):
        raise TypeError(f"{name} must be a finite number")
    if v < 0.0:
        raise ValueError(f"{name} must be >= 0")
    return v


def _validate_positive(name: str, x: float) -> float:
    v = float(x)
    if not _is_finite(v):
        raise TypeError(f"{name} must be a finite number")
    if v <= 0.0:
        raise ValueError(f"{name} must be > 0")
    return v


@dataclass(frozen=True, slots=True)
class AaGradientInputs:
    altitude_m: float
    pao2_mmHg: float
    paco2_mmHg: float = 40.0
    fio2: float = 0.21
    rq: float = 0.8
    age_years: Optional[float] = None
    normal_model: AaNormalModel = "filley1954_rest_air_1600ft"


@dataclass(frozen=True, slots=True)
class AaGradientResult:
    pao2_mmHg: float
    pao2_calc_mmHg: float
    aa_gradient_mmHg: float
    altitude_m: float
    fio2: float
    paco2_mmHg: float
    rq: float
    normal_model: AaNormalModel
    normal_mean_mmHg: Optional[float]
    normal_sd_mmHg: Optional[float]
    normal_upper_approx_mmHg: Optional[float]


# Filley et al. (1954) reported mean A–a ≈ 9.7 mmHg, SD ≈ 5.3 mmHg at rest breathing air
# at ~1600 ft elevation (their lab).
_FILLEY_MEAN: Final[float] = 9.7
_FILLEY_SD: Final[float] = 5.3


def compute_aa_gradient(inputs: AaGradientInputs) -> AaGradientResult:
    """Compute PAO2 (via alveolar gas equation) and A–a gradient.

    - altitude_m: meters
    - PaO2, PaCO2: mmHg
    - FiO2: fraction [0,1]
    - RQ: respiratory quotient (dimensionless)
    """
    if not isinstance(inputs, AaGradientInputs):
        raise TypeError("inputs must be AaGradientInputs")

    alt = _validate_nonnegative("altitude_m", inputs.altitude_m)
    pao2 = _validate_nonnegative("pao2_mmHg", inputs.pao2_mmHg)
    paco2 = _validate_nonnegative("paco2_mmHg", inputs.paco2_mmHg)
    fio2 = float(inputs.fio2)
    rq = float(inputs.rq)
    if not _is_finite(fio2) or fio2 < 0.0 or fio2 > 1.0:
        raise ValueError("fio2 must be between 0 and 1")
    if not _is_finite(rq) or rq <= 0.0:
        raise ValueError("rq must be > 0")

    pao2_calc = float(alveolar_PO2(alt, FiO2=fio2, PaCO2=paco2, RQ=rq))
    aa = float(pao2_calc - pao2)

    normal_mean: Optional[float] = None
    normal_sd: Optional[float] = None
    normal_upper: Optional[float] = None

    if inputs.normal_model == "filley1954_rest_air_1600ft":
        normal_mean = _FILLEY_MEAN
        normal_sd = _FILLEY_SD
        # "Upper approx": mean + 2 SD (not a strict clinical threshold).
        normal_upper = float(_FILLEY_MEAN + 2.0 * _FILLEY_SD)
    elif inputs.normal_model == "heuristic_age_over4_plus4":
        if inputs.age_years is None:
            raise ValueError("age_years is required for heuristic_age_over4_plus4")
        age = _validate_nonnegative("age_years", inputs.age_years)
        normal_upper = float(age / 4.0 + 4.0)
    else:
        raise ValueError(f"Unknown normal_model: {inputs.normal_model}")

    return AaGradientResult(
        pao2_mmHg=float(pao2),
        pao2_calc_mmHg=float(pao2_calc),
        aa_gradient_mmHg=float(aa),
        altitude_m=float(alt),
        fio2=float(fio2),
        paco2_mmHg=float(paco2),
        rq=float(rq),
        normal_model=inputs.normal_model,
        normal_mean_mmHg=normal_mean,
        normal_sd_mmHg=normal_sd,
        normal_upper_approx_mmHg=normal_upper,
    )


