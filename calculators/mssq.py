"""Motion Sickness Susceptibility Questionnaire — Short Form (MSSQ-short).

This module implements deterministic scoring for the MSSQ-short as a simple
sum of item Likert scores for two sections:

- Section A: childhood (up to ~12 years)
- Section B: adulthood (recent years; instrument-dependent)

Scoring and response scale (open description)
--------------------------------------------
An open-access cross-cultural adaptation paper describes MSSQ-short items scored on a
Likert scale 0–3 and reports the maximum score (54 total; 27 per section):

- Rivera R. et al. (2022). *Adaptación transcultural del cuestionario Motion sickness
  susceptibility questionnaire form short (MSSQ-SHORT) para la población adulta chilena*.
  Revista de otorrinolaringología y cirugía de cabeza y cuello, 82(2), 172–178.
  https://doi.org/10.4067/S0718-48162022000200172
  Full text (SciELO): https://www.scielo.cl/scielo.php?script=sci_arttext&pid=S0718-48162022000200172

Primary conceptual references
-----------------------------
- Golding, J. F. (1998). Motion sickness susceptibility questionnaire revised and its
  relationship to other forms of sickness. *Brain Research Bulletin*, 47(5), 507–516.
  https://doi.org/10.1016/S0361-9230(98)00091-4
- Golding, J. F. (2006). Motion sickness susceptibility. *Autonomic Neuroscience*, 129(1–2), 67–76.
  https://doi.org/10.1016/j.autneu.2006.07.019

Notes / limitations
-------------------
- This implementation outputs **raw sums** (A, B, Total) and an **optional quartile band**
  relative to the small Rivera et al. (2022) pre-test sample (n=51). It is not a universal
  population percentile.
- Item wording and recall windows differ across MSSQ variants and translations; users should
  validate against their local instrument version if used operationally.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final, Literal, Sequence, Tuple

__all__ = [
    "MSSQ_SHORT_ITEMS",
    "MssqShortInputs",
    "MssqShortResult",
    "compute_mssq_short",
]


MssqLikert0to3 = Literal[0, 1, 2, 3]


MSSQ_SHORT_ITEMS: Final[Tuple[str, ...]] = (
    "Car / automobile",
    "Bus / coach",
    "Train",
    "Aircraft / airplane",
    "Small boat",
    "Ship / large boat",
    "Swing",
    "Playground equipment",
    "Amusement rides (e.g., rollercoaster)",
)


_MAX_ITEM_SCORE: Final[int] = 3
_N_ITEMS_PER_SECTION: Final[int] = 9
_SECTION_MAX: Final[int] = _N_ITEMS_PER_SECTION * _MAX_ITEM_SCORE  # 27
_TOTAL_MAX: Final[int] = 2 * _SECTION_MAX  # 54


# Quartiles reported in Rivera et al. (2022) pre-test sample (n=51).
_RIVERA_P25: Final[float] = 2.13
_RIVERA_P50: Final[float] = 9.0
_RIVERA_P75: Final[float] = 17.4


def _is_finite(x: float) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def _validate_item_score(name: str, v: int) -> int:
    if not isinstance(v, int):
        raise TypeError(f"{name} must be int in [0, 3]")
    if v < 0 or v > _MAX_ITEM_SCORE:
        raise ValueError(f"{name} must be in [0, 3]")
    return v


def _validate_section_scores(name: str, scores: Sequence[int]) -> Tuple[int, ...]:
    if not isinstance(scores, (list, tuple)):
        raise TypeError(f"{name} must be a list/tuple of 9 integers in [0, 3]")
    if len(scores) != _N_ITEMS_PER_SECTION:
        raise ValueError(f"{name} must have exactly 9 items")
    out: list[int] = []
    for i, s in enumerate(scores):
        out.append(_validate_item_score(f"{name}[{i}]", s))
    return tuple(out)


@dataclass(frozen=True, slots=True)
class MssqShortInputs:
    """Inputs for MSSQ-short.

    The expected order is `MSSQ_SHORT_ITEMS`.
    Each item is a Likert score 0–3 (0=never, 3=frequently) as described in Rivera et al. (2022).
    """

    section_a_scores_0_3: Tuple[int, ...]
    section_b_scores_0_3: Tuple[int, ...]


PercentileBand = Literal["<P25", "P25–P50", "P50–P75", ">=P75"]


@dataclass(frozen=True, slots=True)
class MssqShortResult:
    section_a_sum_0_27: int
    section_b_sum_0_27: int
    total_sum_0_54: int
    rivera_2022_percentile_band: PercentileBand
    rivera_2022_reference: Tuple[float, float, float]


def compute_mssq_short(inputs: MssqShortInputs) -> MssqShortResult:
    """Compute MSSQ-short sums and a quartile band relative to Rivera et al. (2022) sample.

    Returns:
        MssqShortResult:
          - sums (A, B, total)
          - a quartile band based on reported P25/P50/P75 from Rivera et al. (2022)
    """
    if not isinstance(inputs, MssqShortInputs):
        raise TypeError("inputs must be MssqShortInputs")

    a = _validate_section_scores("section_a_scores_0_3", inputs.section_a_scores_0_3)
    b = _validate_section_scores("section_b_scores_0_3", inputs.section_b_scores_0_3)

    a_sum = int(sum(a))
    b_sum = int(sum(b))
    total = int(a_sum + b_sum)

    if a_sum < 0 or a_sum > _SECTION_MAX:
        raise ValueError("Section A sum out of bounds")
    if b_sum < 0 or b_sum > _SECTION_MAX:
        raise ValueError("Section B sum out of bounds")
    if total < 0 or total > _TOTAL_MAX:
        raise ValueError("Total sum out of bounds")

    # Quartile band relative to Rivera et al. (2022) pre-test sample.
    # Note: this is not a universal percentile; it's a simple banding vs reported quartiles.
    t = float(total)
    if not _is_finite(t):
        raise RuntimeError("Unexpected non-finite total score")

    if t < _RIVERA_P25:
        band: PercentileBand = "<P25"
    elif t < _RIVERA_P50:
        band = "P25–P50"
    elif t < _RIVERA_P75:
        band = "P50–P75"
    else:
        band = ">=P75"

    return MssqShortResult(
        section_a_sum_0_27=a_sum,
        section_b_sum_0_27=b_sum,
        total_sum_0_54=total,
        rivera_2022_percentile_band=band,
        rivera_2022_reference=(_RIVERA_P25, _RIVERA_P50, _RIVERA_P75),
    )


