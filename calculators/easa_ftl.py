"""EASA Flight Time Limitations (FTL) calculators (scoped, deterministic).

This module implements a narrow, table-driven subset of Part-ORO Subpart FTL:

- ORO.FTL.205(b)(1): Basic maximum daily FDP for acclimatised crew members (Table 2).
- ORO.FTL.205(b)(2) and (3): FDP for unknown acclimatisation (Table 3) and unknown under FRM (Table 4).
- CS FTL.1.205(b): Extension of FDP without in-flight rest (table of maximum daily FDP with extension).
- ORO.FTL.210: Cumulative duty and flight time limitations.

Primary source (official):
- EASA, "Easy Access Rules for Air Operations (Regulation (EU) No 965/2012) – Revision 22, February 2025"
  PDF download: https://www.easa.europa.eu/en/document-library/easy-access-rules/easy-access-rules-air-operations-regulation-eu-no-9652012

Notes / limitations:
- This is NOT a full ORO.FTL implementation (no standby rules, split duty, in-flight rest schemes,
  commander’s discretion, sector-specific WOCL reductions, or operator-specific FTL schemes).
- The "extension without in-flight rest" limits here are implemented from CS FTL.1.205(b) only.
"""

from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass
from typing import Final, Literal, Optional, Tuple


AcclimatisationState = Literal["acclimatised", "unknown", "unknown_frm"]


def parse_hhmm(hhmm: str) -> Tuple[int, int]:
    """Parse 'HH:MM' (24-hour clock) into (hour, minute).

    Raises:
        TypeError: If input is not a string.
        ValueError: If format is invalid or values out of range.
    """
    if not isinstance(hhmm, str):
        raise TypeError("hhmm must be a string like '07:30'")

    s = hhmm.strip()
    parts = s.split(":")
    if len(parts) != 2:
        raise ValueError("hhmm must be in 'HH:MM' format")
    try:
        h = int(parts[0])
        m = int(parts[1])
    except ValueError as e:
        raise ValueError("hhmm must contain integer hour and minute") from e
    if h < 0 or h > 23:
        raise ValueError("hour must be 0..23")
    if m < 0 or m > 59:
        raise ValueError("minute must be 0..59")
    return h, m


def _minutes_since_midnight(hhmm: str) -> int:
    h, m = parse_hhmm(hhmm)
    return h * 60 + m


def _parse_hhmm_duration_to_minutes(hhmm_duration: str) -> int:
    """Parse duration 'H:MM' or 'HH:MM' to whole minutes."""
    if not isinstance(hhmm_duration, str):
        raise TypeError("duration must be a string like '13:30'")
    s = hhmm_duration.strip()
    parts = s.split(":")
    if len(parts) != 2:
        raise ValueError("duration must be in 'H:MM' or 'HH:MM' format")
    try:
        h = int(parts[0])
        m = int(parts[1])
    except ValueError as e:
        raise ValueError("duration must contain integer hours and minutes") from e
    if h < 0:
        raise ValueError("duration hours must be >= 0")
    if m < 0 or m > 59:
        raise ValueError("duration minutes must be 0..59")
    return h * 60 + m


def _fmt_minutes_to_hours(minutes: int) -> float:
    if not isinstance(minutes, int):
        raise TypeError("minutes must be int")
    if minutes < 0:
        raise ValueError("minutes must be >= 0")
    return minutes / 60.0


# ORO.FTL.205(b)(1) Table 2: acclimatised crew members.
# Row ranges are inclusive, expressed as [start_min, end_min] in minutes since midnight.
_ORO_FTL_205_TABLE2_ROWS: Final[Tuple[Tuple[int, int, Tuple[int, ...]], ...]] = (
    # start range, end range, values for sectors [1-2, 3, 4, 5, 6, 7, 8, 9, 10]
    (6 * 60 + 0, 13 * 60 + 29, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["13:00", "12:30", "12:00", "11:30", "11:00", "10:30", "10:00", "09:30", "09:00"])),
    (13 * 60 + 30, 13 * 60 + 59, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["12:45", "12:15", "11:45", "11:15", "10:45", "10:15", "09:45", "09:15", "09:00"])),
    (14 * 60 + 0, 14 * 60 + 29, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["12:30", "12:00", "11:30", "11:00", "10:30", "10:00", "09:30", "09:00", "09:00"])),
    (14 * 60 + 30, 14 * 60 + 59, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["12:15", "11:45", "11:15", "10:45", "10:15", "09:45", "09:15", "09:00", "09:00"])),
    (15 * 60 + 0, 15 * 60 + 29, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["12:00", "11:30", "11:00", "10:30", "10:00", "09:30", "09:00", "09:00", "09:00"])),
    (15 * 60 + 30, 15 * 60 + 59, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["11:45", "11:15", "10:45", "10:15", "09:45", "09:15", "09:00", "09:00", "09:00"])),
    (16 * 60 + 0, 16 * 60 + 29, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["11:30", "11:00", "10:30", "10:00", "09:30", "09:00", "09:00", "09:00", "09:00"])),
    (16 * 60 + 30, 16 * 60 + 59, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["11:15", "10:45", "10:15", "09:45", "09:15", "09:00", "09:00", "09:00", "09:00"])),
    (17 * 60 + 0, 4 * 60 + 59, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["11:00", "10:30", "10:00", "09:30", "09:00", "09:00", "09:00", "09:00", "09:00"])),
    (5 * 60 + 0, 5 * 60 + 14, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["12:00", "11:30", "11:00", "10:30", "10:00", "09:30", "09:00", "09:00", "09:00"])),
    (5 * 60 + 15, 5 * 60 + 29, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["12:15", "11:45", "11:15", "10:45", "10:15", "09:45", "09:15", "09:00", "09:00"])),
    (5 * 60 + 30, 5 * 60 + 44, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["12:30", "12:00", "11:30", "11:00", "10:30", "10:00", "09:30", "09:00", "09:00"])),
    (5 * 60 + 45, 5 * 60 + 59, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["12:45", "12:15", "11:45", "11:15", "10:45", "10:15", "09:45", "09:15", "09:00"])),
)


def _time_in_range(start_min: int, end_min: int, t_min: int) -> bool:
    """Return True if t is within [start_min, end_min], supporting wrap-around ranges."""
    if start_min <= end_min:
        return start_min <= t_min <= end_min
    # Wrap-around (e.g., 17:00–04:59)
    return t_min >= start_min or t_min <= end_min


def _lookup_table2_max_fdp_minutes(reference_time_hhmm: str, sectors: int) -> int:
    if not isinstance(sectors, int):
        raise TypeError("sectors must be int")
    if sectors < 1 or sectors > 10:
        raise ValueError("sectors must be between 1 and 10 for Table 2")

    t_min = _minutes_since_midnight(reference_time_hhmm)
    col_idx = 0 if sectors <= 2 else (sectors - 2)
    # col_idx maps: 1-2 -> 0, 3 -> 1, ..., 10 -> 8
    if col_idx < 0 or col_idx > 8:
        raise ValueError("unsupported sectors for Table 2")

    for start_min, end_min, values in _ORO_FTL_205_TABLE2_ROWS:
        if _time_in_range(start_min, end_min, t_min):
            return int(values[col_idx])
    raise ValueError("reference_time_hhmm did not match any Table 2 row")


# ORO.FTL.205(b)(2) Table 3 and (b)(3) Table 4 (unknown acclimatisation): not start-time dependent.
_ORO_FTL_205_TABLE3_UNKNOWN: Final[Tuple[int, ...]] = tuple(
    _parse_hhmm_duration_to_minutes(x) for x in ["11:00", "10:30", "10:00", "09:30", "09:00", "09:00", "09:00"]
)
_ORO_FTL_205_TABLE4_UNKNOWN_FRM: Final[Tuple[int, ...]] = tuple(
    _parse_hhmm_duration_to_minutes(x) for x in ["12:00", "11:30", "11:00", "10:30", "10:00", "09:30", "09:00"]
)


def _lookup_unknown_state_max_fdp_minutes(state: AcclimatisationState, sectors: int) -> int:
    if not isinstance(sectors, int):
        raise TypeError("sectors must be int")
    if sectors < 1 or sectors > 8:
        raise ValueError("sectors must be between 1 and 8 for unknown-acclimatisation tables")

    col_idx = 0 if sectors <= 2 else (sectors - 2)
    if col_idx < 0 or col_idx > 6:
        raise ValueError("unsupported sectors for unknown-acclimatisation tables")

    if state == "unknown":
        return int(_ORO_FTL_205_TABLE3_UNKNOWN[col_idx])
    if state == "unknown_frm":
        return int(_ORO_FTL_205_TABLE4_UNKNOWN_FRM[col_idx])
    raise ValueError("state must be 'unknown' or 'unknown_frm'")


# CS FTL.1.205(b) "Maximum daily FDP with extension" table (without in-flight rest)
_CS_FTL_1205B_EXTENSION_ROWS: Final[Tuple[Tuple[int, int, Tuple[Optional[int], ...]], ...]] = (
    # start range, end range, values for sectors [1-2, 3, 4, 5] in minutes (None => Not allowed)
    (6 * 60 + 0, 6 * 60 + 14, (None, None, None, None)),
    (6 * 60 + 15, 6 * 60 + 29, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["13:15", "12:45", "12:15", "11:45"])),
    (6 * 60 + 30, 6 * 60 + 44, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["13:30", "13:00", "12:30", "12:00"])),
    (6 * 60 + 45, 6 * 60 + 59, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["13:45", "13:15", "12:45", "12:15"])),
    (7 * 60 + 0, 13 * 60 + 29, tuple(_parse_hhmm_duration_to_minutes(x) for x in ["14:00", "13:30", "13:00", "12:30"])),
    (13 * 60 + 30, 13 * 60 + 59, ( _parse_hhmm_duration_to_minutes("13:45"), _parse_hhmm_duration_to_minutes("13:15"), _parse_hhmm_duration_to_minutes("12:45"), None)),
    (14 * 60 + 0, 14 * 60 + 29, ( _parse_hhmm_duration_to_minutes("13:30"), _parse_hhmm_duration_to_minutes("13:00"), _parse_hhmm_duration_to_minutes("12:30"), None)),
    (14 * 60 + 30, 14 * 60 + 59, ( _parse_hhmm_duration_to_minutes("13:15"), _parse_hhmm_duration_to_minutes("12:45"), _parse_hhmm_duration_to_minutes("12:15"), None)),
    (15 * 60 + 0, 15 * 60 + 29, ( _parse_hhmm_duration_to_minutes("13:00"), _parse_hhmm_duration_to_minutes("12:30"), _parse_hhmm_duration_to_minutes("12:00"), None)),
    (15 * 60 + 30, 15 * 60 + 59, ( _parse_hhmm_duration_to_minutes("12:45"), None, None, None)),
    (16 * 60 + 0, 16 * 60 + 29, ( _parse_hhmm_duration_to_minutes("12:30"), None, None, None)),
    (16 * 60 + 30, 16 * 60 + 59, ( _parse_hhmm_duration_to_minutes("12:15"), None, None, None)),
    (17 * 60 + 0, 17 * 60 + 29, ( _parse_hhmm_duration_to_minutes("12:00"), None, None, None)),
    (17 * 60 + 30, 17 * 60 + 59, ( _parse_hhmm_duration_to_minutes("11:45"), None, None, None)),
    (18 * 60 + 0, 18 * 60 + 29, ( _parse_hhmm_duration_to_minutes("11:30"), None, None, None)),
    (18 * 60 + 30, 18 * 60 + 59, ( _parse_hhmm_duration_to_minutes("11:15"), None, None, None)),
    (19 * 60 + 0, 3 * 60 + 59, (None, None, None, None)),
    (4 * 60 + 0, 4 * 60 + 14, (None, None, None, None)),
    (4 * 60 + 15, 4 * 60 + 29, (None, None, None, None)),
    (4 * 60 + 30, 4 * 60 + 44, (None, None, None, None)),
    (4 * 60 + 45, 4 * 60 + 59, (None, None, None, None)),
    (5 * 60 + 0, 5 * 60 + 14, (None, None, None, None)),
    (5 * 60 + 15, 5 * 60 + 29, (None, None, None, None)),
    (5 * 60 + 30, 5 * 60 + 44, (None, None, None, None)),
    (5 * 60 + 45, 5 * 60 + 59, (None, None, None, None)),
)


def _lookup_extension_max_fdp_minutes(reference_time_hhmm: str, sectors: int) -> Optional[int]:
    if not isinstance(sectors, int):
        raise TypeError("sectors must be int")
    if sectors < 1 or sectors > 5:
        raise ValueError("sectors must be between 1 and 5 for CS FTL.1.205(b) extension table")

    t_min = _minutes_since_midnight(reference_time_hhmm)
    col_idx = 0 if sectors <= 2 else (sectors - 2)
    if col_idx < 0 or col_idx > 3:
        raise ValueError("unsupported sectors for extension table")

    for start_min, end_min, values in _CS_FTL_1205B_EXTENSION_ROWS:
        if _time_in_range(start_min, end_min, t_min):
            return values[col_idx]
    raise ValueError("reference_time_hhmm did not match any extension table row")


@dataclass(frozen=True, slots=True)
class EasaFtlFdpInputs:
    """Inputs for maximum daily FDP lookups (table-driven)."""

    reference_time_local_hhmm: str
    flight_sectors: int
    acclimatisation_state: AcclimatisationState = "acclimatised"
    request_extension_without_inflight_rest: bool = False


@dataclass(frozen=True, slots=True)
class EasaFtlFdpResult:
    """Result for maximum daily FDP calculation."""

    max_daily_fdp_hours: float
    source_table: str
    extension_max_daily_fdp_hours: float | None
    extension_allowed: bool


def easa_max_daily_fdp(inputs: EasaFtlFdpInputs) -> EasaFtlFdpResult:
    """Compute the maximum daily FDP under EASA Part-ORO FTL (scoped tables).

    Returns:
        EasaFtlFdpResult: maximum FDP (hours) and optional max under planned extension w/o in-flight rest.
    """
    if not isinstance(inputs, EasaFtlFdpInputs):
        raise TypeError("inputs must be EasaFtlFdpInputs")

    state = inputs.acclimatisation_state
    if state not in ("acclimatised", "unknown", "unknown_frm"):
        raise ValueError("acclimatisation_state must be 'acclimatised', 'unknown', or 'unknown_frm'")

    sectors = int(inputs.flight_sectors)
    if state == "acclimatised":
        max_min = _lookup_table2_max_fdp_minutes(inputs.reference_time_local_hhmm, sectors)
        source = "ORO.FTL.205(b)(1) Table 2 (acclimatised)"
    else:
        max_min = _lookup_unknown_state_max_fdp_minutes(state, sectors)
        source = "ORO.FTL.205(b)(2) Table 3 (unknown)" if state == "unknown" else "ORO.FTL.205(b)(3) Table 4 (unknown under FRM)"

    ext_minutes: Optional[int] = None
    if bool(inputs.request_extension_without_inflight_rest) and state == "acclimatised":
        ext_minutes = _lookup_extension_max_fdp_minutes(inputs.reference_time_local_hhmm, sectors)

    return EasaFtlFdpResult(
        max_daily_fdp_hours=float(_fmt_minutes_to_hours(int(max_min))),
        source_table=source,
        extension_max_daily_fdp_hours=float(_fmt_minutes_to_hours(int(ext_minutes))) if ext_minutes is not None else None,
        extension_allowed=ext_minutes is not None,
    )


@dataclass(frozen=True, slots=True)
class EasaOroFtl210Inputs:
    """Inputs for ORO.FTL.210 cumulative limits checks (hours)."""

    duty_last_7d_hours: float
    duty_last_14d_hours: float
    duty_last_28d_hours: float
    flight_time_last_28d_hours: float
    flight_time_calendar_year_hours: float
    flight_time_last_12mo_hours: float
    planned_duty_hours: float
    planned_flight_time_hours: float


@dataclass(frozen=True, slots=True)
class EasaOroFtl210Result:
    max_duty_7d_hours: float
    max_duty_14d_hours: float
    max_duty_28d_hours: float
    max_flight_time_28d_hours: float
    max_flight_time_calendar_year_hours: float
    max_flight_time_12mo_hours: float
    duty_7d_ok: bool
    duty_14d_ok: bool
    duty_28d_ok: bool
    flight_time_28d_ok: bool
    flight_time_calendar_year_ok: bool
    flight_time_12mo_ok: bool
    duty_7d_margin_hours: float
    duty_14d_margin_hours: float
    duty_28d_margin_hours: float
    flight_time_28d_margin_hours: float
    flight_time_calendar_year_margin_hours: float
    flight_time_12mo_margin_hours: float


_ORO_FTL_210_MAX_DUTY_7D: Final[float] = 60.0
_ORO_FTL_210_MAX_DUTY_14D: Final[float] = 110.0
_ORO_FTL_210_MAX_DUTY_28D: Final[float] = 190.0
_ORO_FTL_210_MAX_FLIGHT_28D: Final[float] = 100.0
_ORO_FTL_210_MAX_FLIGHT_CAL_YEAR: Final[float] = 900.0
_ORO_FTL_210_MAX_FLIGHT_12MO: Final[float] = 1000.0


def easa_oroflt_210_cumulative_limits(inputs: EasaOroFtl210Inputs) -> EasaOroFtl210Result:
    """Check EASA ORO.FTL.210 cumulative duty and flight time limitations.

    Comparison is made as: (already accumulated) + (planned assignment) <= limit.
    """
    if not isinstance(inputs, EasaOroFtl210Inputs):
        raise TypeError("inputs must be EasaOroFtl210Inputs")

    vals = {
        "duty_last_7d_hours": float(inputs.duty_last_7d_hours),
        "duty_last_14d_hours": float(inputs.duty_last_14d_hours),
        "duty_last_28d_hours": float(inputs.duty_last_28d_hours),
        "flight_time_last_28d_hours": float(inputs.flight_time_last_28d_hours),
        "flight_time_calendar_year_hours": float(inputs.flight_time_calendar_year_hours),
        "flight_time_last_12mo_hours": float(inputs.flight_time_last_12mo_hours),
        "planned_duty_hours": float(inputs.planned_duty_hours),
        "planned_flight_time_hours": float(inputs.planned_flight_time_hours),
    }
    for name, v in vals.items():
        if not math.isfinite(v):
            raise TypeError(f"{name} must be a finite number")
        if v < 0.0:
            raise ValueError(f"{name} must be >= 0")

    duty7 = vals["duty_last_7d_hours"] + vals["planned_duty_hours"]
    duty14 = vals["duty_last_14d_hours"] + vals["planned_duty_hours"]
    duty28 = vals["duty_last_28d_hours"] + vals["planned_duty_hours"]
    ft28 = vals["flight_time_last_28d_hours"] + vals["planned_flight_time_hours"]
    fty = vals["flight_time_calendar_year_hours"] + vals["planned_flight_time_hours"]
    ft12 = vals["flight_time_last_12mo_hours"] + vals["planned_flight_time_hours"]

    return EasaOroFtl210Result(
        max_duty_7d_hours=float(_ORO_FTL_210_MAX_DUTY_7D),
        max_duty_14d_hours=float(_ORO_FTL_210_MAX_DUTY_14D),
        max_duty_28d_hours=float(_ORO_FTL_210_MAX_DUTY_28D),
        max_flight_time_28d_hours=float(_ORO_FTL_210_MAX_FLIGHT_28D),
        max_flight_time_calendar_year_hours=float(_ORO_FTL_210_MAX_FLIGHT_CAL_YEAR),
        max_flight_time_12mo_hours=float(_ORO_FTL_210_MAX_FLIGHT_12MO),
        duty_7d_ok=duty7 <= _ORO_FTL_210_MAX_DUTY_7D,
        duty_14d_ok=duty14 <= _ORO_FTL_210_MAX_DUTY_14D,
        duty_28d_ok=duty28 <= _ORO_FTL_210_MAX_DUTY_28D,
        flight_time_28d_ok=ft28 <= _ORO_FTL_210_MAX_FLIGHT_28D,
        flight_time_calendar_year_ok=fty <= _ORO_FTL_210_MAX_FLIGHT_CAL_YEAR,
        flight_time_12mo_ok=ft12 <= _ORO_FTL_210_MAX_FLIGHT_12MO,
        duty_7d_margin_hours=float(_ORO_FTL_210_MAX_DUTY_7D - duty7),
        duty_14d_margin_hours=float(_ORO_FTL_210_MAX_DUTY_14D - duty14),
        duty_28d_margin_hours=float(_ORO_FTL_210_MAX_DUTY_28D - duty28),
        flight_time_28d_margin_hours=float(_ORO_FTL_210_MAX_FLIGHT_28D - ft28),
        flight_time_calendar_year_margin_hours=float(_ORO_FTL_210_MAX_FLIGHT_CAL_YEAR - fty),
        flight_time_12mo_margin_hours=float(_ORO_FTL_210_MAX_FLIGHT_12MO - ft12),
    )


