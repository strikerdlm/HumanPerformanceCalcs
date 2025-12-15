"""Crew duty time limit calculators (FAA 14 CFR Part 117: unaugmented operations).

This module implements deterministic lookups for:
- Maximum flight time (Table A to Part 117)
- Maximum flight duty period (FDP) for lineholders (Table B to Part 117)
- The "not acclimated" FDP reduction (-30 minutes) referenced by § 117.13(b)
- Cumulative limitations (flight time and FDP) per § 117.23
- Rest constraints per § 117.25 (10h rest with 8h sleep opportunity; 30h in 168h)

Primary sources (public law / official text)
-------------------------------------------
- eCFR: Table A to Part 117 (Maximum flight time limits for unaugmented operations)
  https://www.ecfr.gov/current/title-14/chapter-I/subchapter-G/part-117/appendix-Table%20A%20to%20Part%20117

- eCFR: Table B to Part 117 (FDP limits for unaugmented operations)
  https://www.ecfr.gov/current/title-14/chapter-I/subchapter-G/part-117/appendix-Table%20B%20to%20Part%20117

- eCFR: § 117.13 (FDP rules; not-acclimated reduction)
  https://www.ecfr.gov/current/title-14/chapter-I/subchapter-G/part-117/section-117.13

- eCFR: § 117.23 (cumulative limitations)
  https://www.ecfr.gov/current/title-14/chapter-I/subchapter-G/part-117/section-117.23

- eCFR: § 117.25 (rest period)
  https://www.ecfr.gov/current/title-14/chapter-I/subchapter-G/part-117/section-117.25

Notes
-----
- This is intentionally scoped to **unaugmented operations** and the two appendix tables.
- It does not attempt to model reserve rules, split duty, extensions, unexpected circumstances,
  acclimation theater rules beyond the boolean "not acclimated", or carrier-specific CBA terms.
"""

from __future__ import annotations

import math
import dataclasses
from dataclasses import dataclass
from typing import Final, Literal, Tuple

__all__ = [
    "Faa117Inputs",
    "Faa117Limits",
    "Faa117CumulativeInputs",
    "Faa117CumulativeResult",
    "parse_hhmm",
    "faa117_limits",
    "faa117_cumulative_limits",
]

TimeWindowLabel = Literal[
    "0000-0359",
    "0400-0459",
    "0500-0559",
    "0600-0659",
    "0700-1159",
    "1200-1259",
    "1300-1659",
    "1700-2159",
    "2200-2259",
    "2300-2359",
]


@dataclass(frozen=True, slots=True)
class Faa117Inputs:
    report_time_local_hhmm: str
    flight_segments: int
    not_acclimated: bool = False
    scheduled_flight_time_hours: float | None = None
    scheduled_fdp_hours: float | None = None


@dataclass(frozen=True, slots=True)
class Faa117Limits:
    report_time_minutes: int
    time_window: TimeWindowLabel
    flight_segments: int
    max_flight_time_hours: float
    max_fdp_hours: float
    min_rest_hours: float
    not_acclimated_reduction_hours: float
    flight_time_ok: bool | None
    fdp_ok: bool | None
    flight_time_margin_hours: float | None
    fdp_margin_hours: float | None


_MIN_REST_HOURS: Final[float] = 10.0
_REQUIRED_30H_IN_168H: Final[float] = 30.0

# § 117.23(b): flight time cumulative caps
_MAX_FLIGHT_TIME_672H: Final[float] = 100.0
_MAX_FLIGHT_TIME_365D: Final[float] = 1000.0

# § 117.23(c): FDP cumulative caps
_MAX_FDP_168H: Final[float] = 60.0
_MAX_FDP_672H: Final[float] = 190.0

# Table A to Part 117 — maximum flight time (hours) based on time of report (acclimated).
# Source: eCFR Table A (URL in module docstring).
_TABLE_A: Final[list[Tuple[Tuple[int, int], float]]] = [
    ((0, 4 * 60 + 59), 8.0),
    ((5 * 60, 19 * 60 + 59), 9.0),
    ((20 * 60, 23 * 60 + 59), 8.0),
]

# Table B to Part 117 — FDP limits for lineholders based on scheduled start time and segments.
# Source: eCFR Table B snapshot (URL in module docstring).
#
# Segment columns are 1,2,3,4,5,6,7+
_TABLE_B: Final[dict[TimeWindowLabel, tuple[float, float, float, float, float, float, float]]] = {
    "0000-0359": (9, 9, 9, 9, 9, 9, 9),
    "0400-0459": (10, 10, 10, 10, 9, 9, 9),
    "0500-0559": (12, 12, 12, 12, 11.5, 11, 10.5),
    "0600-0659": (13, 13, 12, 12, 11.5, 11, 10.5),
    "0700-1159": (14, 14, 13, 13, 12.5, 12, 11.5),
    "1200-1259": (13, 13, 13, 13, 12.5, 12, 11.5),
    "1300-1659": (12, 12, 12, 12, 11.5, 11, 10.5),
    "1700-2159": (12, 12, 11, 11, 10, 9, 9),
    "2200-2259": (11, 11, 10, 10, 9, 9, 9),
    "2300-2359": (10, 10, 10, 9, 9, 9, 9),
}


def parse_hhmm(hhmm: str) -> int:
    """Parse 'HH:MM' into minutes since midnight."""
    if not isinstance(hhmm, str):
        raise TypeError("hhmm must be a string like 'HH:MM'")
    parts = hhmm.strip().split(":")
    if len(parts) != 2:
        raise ValueError("Time must be in HH:MM format")
    try:
        hh = int(parts[0])
        mm = int(parts[1])
    except ValueError as e:
        raise ValueError("Time must contain numeric HH and MM") from e
    if hh < 0 or hh > 23 or mm < 0 or mm > 59:
        raise ValueError("Time must be a valid 24h clock time")
    return hh * 60 + mm


def _window_label(mins: int) -> TimeWindowLabel:
    if 0 <= mins <= 3 * 60 + 59:
        return "0000-0359"
    if 4 * 60 <= mins <= 4 * 60 + 59:
        return "0400-0459"
    if 5 * 60 <= mins <= 5 * 60 + 59:
        return "0500-0559"
    if 6 * 60 <= mins <= 6 * 60 + 59:
        return "0600-0659"
    if 7 * 60 <= mins <= 11 * 60 + 59:
        return "0700-1159"
    if 12 * 60 <= mins <= 12 * 60 + 59:
        return "1200-1259"
    if 13 * 60 <= mins <= 16 * 60 + 59:
        return "1300-1659"
    if 17 * 60 <= mins <= 21 * 60 + 59:
        return "1700-2159"
    if 22 * 60 <= mins <= 22 * 60 + 59:
        return "2200-2259"
    return "2300-2359"


def _max_flight_time_hours(report_mins: int) -> float:
    for (lo, hi), hours in _TABLE_A:
        if lo <= report_mins <= hi:
            return float(hours)
    # Should be unreachable due to complete coverage.
    raise ValueError("Report time out of supported range")


def _fdp_from_table_b(window: TimeWindowLabel, segments: int) -> float:
    if segments <= 0:
        raise ValueError("flight_segments must be >= 1")
    col = min(segments, 7) - 1  # 1->0 ... 6->5, 7+->6
    return float(_TABLE_B[window][col])


def faa117_limits(inputs: Faa117Inputs) -> Faa117Limits:
    if not isinstance(inputs, Faa117Inputs):
        raise TypeError("inputs must be Faa117Inputs")

    report_mins = parse_hhmm(inputs.report_time_local_hhmm)
    window = _window_label(report_mins)
    seg = int(inputs.flight_segments)
    if seg < 1:
        raise ValueError("flight_segments must be >= 1")

    max_ft = _max_flight_time_hours(report_mins)
    base_fdp = _fdp_from_table_b(window, seg)
    reduction = 0.5 if bool(inputs.not_acclimated) else 0.0
    max_fdp = max(0.0, base_fdp - reduction)

    ft_ok = None
    fdp_ok = None
    ft_margin = None
    fdp_margin = None
    if inputs.scheduled_flight_time_hours is not None:
        ft = float(inputs.scheduled_flight_time_hours)
        ft_ok = ft <= max_ft
        ft_margin = float(max_ft - ft)
    if inputs.scheduled_fdp_hours is not None:
        fdp = float(inputs.scheduled_fdp_hours)
        fdp_ok = fdp <= max_fdp
        fdp_margin = float(max_fdp - fdp)

    return Faa117Limits(
        report_time_minutes=int(report_mins),
        time_window=window,
        flight_segments=seg,
        max_flight_time_hours=float(max_ft),
        max_fdp_hours=float(max_fdp),
        min_rest_hours=float(_MIN_REST_HOURS),
        not_acclimated_reduction_hours=float(reduction),
        flight_time_ok=ft_ok,
        fdp_ok=fdp_ok,
        flight_time_margin_hours=ft_margin,
        fdp_margin_hours=fdp_margin,
    )


@dataclass(frozen=True, slots=True)
class Faa117CumulativeInputs:
    """Cumulative-limit check inputs (rolling windows).

    All hour inputs are in hours.

    - `flight_time_last_672h`: total flight time in prior 672 consecutive hours
    - `flight_time_last_365d`: total flight time in prior 365 consecutive calendar days
    - `fdp_last_168h`: total FDP hours in prior 168 consecutive hours
    - `fdp_last_672h`: total FDP hours in prior 672 consecutive hours
    - `had_30h_free_past_168h`: whether the pilot had >=30 consecutive hours free from all duty in past 168h (§117.25(b))
    - `planned_flight_time_hours`: planned flight time for the upcoming assignment
    - `planned_fdp_hours`: planned FDP for the upcoming assignment
    """

    flight_time_last_672h: float
    flight_time_last_365d: float
    fdp_last_168h: float
    fdp_last_672h: float
    had_30h_free_past_168h: bool
    planned_flight_time_hours: float
    planned_fdp_hours: float


@dataclass(frozen=True, slots=True)
class Faa117CumulativeResult:
    max_flight_time_672h: float
    max_flight_time_365d: float
    max_fdp_168h: float
    max_fdp_672h: float
    required_30h_free_in_168h: float
    min_rest_hours: float
    flight_time_672h_ok: bool
    flight_time_365d_ok: bool
    fdp_168h_ok: bool
    fdp_672h_ok: bool
    had_30h_free_past_168h: bool
    flight_time_672h_margin_hours: float
    flight_time_365d_margin_hours: float
    fdp_168h_margin_hours: float
    fdp_672h_margin_hours: float


def faa117_cumulative_limits(inputs: Faa117CumulativeInputs) -> Faa117CumulativeResult:
    """Check cumulative flight-time and FDP limits per §117.23 and report margins.

    The comparison is done as "previous window total + planned assignment <= limit".
    """
    if not isinstance(inputs, Faa117CumulativeInputs):
        raise TypeError("inputs must be Faa117CumulativeInputs")

    ft672 = float(inputs.flight_time_last_672h)
    ft365 = float(inputs.flight_time_last_365d)
    fdp168 = float(inputs.fdp_last_168h)
    fdp672 = float(inputs.fdp_last_672h)
    plan_ft = float(inputs.planned_flight_time_hours)
    plan_fdp = float(inputs.planned_fdp_hours)

    for name, v in [
        ("flight_time_last_672h", ft672),
        ("flight_time_last_365d", ft365),
        ("fdp_last_168h", fdp168),
        ("fdp_last_672h", fdp672),
        ("planned_flight_time_hours", plan_ft),
        ("planned_fdp_hours", plan_fdp),
    ]:
        if not isinstance(v, (int, float)) or not math.isfinite(v):
            raise TypeError(f"{name} must be a finite number")
        if v < 0.0:
            raise ValueError(f"{name} must be >= 0")

    ft672_total = ft672 + plan_ft
    ft365_total = ft365 + plan_ft
    fdp168_total = fdp168 + plan_fdp
    fdp672_total = fdp672 + plan_fdp

    return Faa117CumulativeResult(
        max_flight_time_672h=float(_MAX_FLIGHT_TIME_672H),
        max_flight_time_365d=float(_MAX_FLIGHT_TIME_365D),
        max_fdp_168h=float(_MAX_FDP_168H),
        max_fdp_672h=float(_MAX_FDP_672H),
        required_30h_free_in_168h=float(_REQUIRED_30H_IN_168H),
        min_rest_hours=float(_MIN_REST_HOURS),
        flight_time_672h_ok=ft672_total <= _MAX_FLIGHT_TIME_672H,
        flight_time_365d_ok=ft365_total <= _MAX_FLIGHT_TIME_365D,
        fdp_168h_ok=fdp168_total <= _MAX_FDP_168H,
        fdp_672h_ok=fdp672_total <= _MAX_FDP_672H,
        had_30h_free_past_168h=bool(inputs.had_30h_free_past_168h),
        flight_time_672h_margin_hours=float(_MAX_FLIGHT_TIME_672H - ft672_total),
        flight_time_365d_margin_hours=float(_MAX_FLIGHT_TIME_365D - ft365_total),
        fdp_168h_margin_hours=float(_MAX_FDP_168H - fdp168_total),
        fdp_672h_margin_hours=float(_MAX_FDP_672H - fdp672_total),
    )


