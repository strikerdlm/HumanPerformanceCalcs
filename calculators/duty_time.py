"""Crew duty time limit calculators (FAA 14 CFR Part 117: unaugmented operations).

This module implements deterministic lookups for:
- Maximum flight time (Table A to Part 117)
- Maximum flight duty period (FDP) for lineholders (Table B to Part 117)
- The "not acclimated" FDP reduction (-30 minutes) referenced by § 117.13(b)

Primary sources (public law / official text)
-------------------------------------------
- eCFR: Table A to Part 117 (Maximum flight time limits for unaugmented operations)
  https://www.ecfr.gov/current/title-14/chapter-I/subchapter-G/part-117/appendix-Table%20A%20to%20Part%20117

- eCFR: Table B to Part 117 (FDP limits for unaugmented operations)
  https://www.ecfr.gov/current/title-14/chapter-I/subchapter-G/part-117/appendix-Table%20B%20to%20Part%20117

- eCFR: § 117.13 (FDP rules; not-acclimated reduction)
  https://www.ecfr.gov/current/title-14/chapter-I/subchapter-G/part-117/section-117.13

Notes
-----
- This is intentionally scoped to **unaugmented operations** and the two appendix tables.
- It does not attempt to model reserve rules, split duty, extensions, unexpected circumstances,
  acclimation theater rules beyond the boolean "not acclimated", or carrier-specific CBA terms.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Final, Literal, Tuple

__all__ = [
    "Faa117Inputs",
    "Faa117Limits",
    "parse_hhmm",
    "faa117_limits",
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


