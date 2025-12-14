"""SAFTE (patent-derived) fatigue effectiveness model (deterministic).

This module implements the core, openly citable SAFTE equations as documented in:

1) Patent text with explicit equations and default constants:
   - WO2012015383A1 (Google Patents): https://patents.google.com/patent/WO2012015383A1/en
   Equations used here (as numbered in the patent images):
   - (1) P = K * t
   - (2) S = SI * t
   - (3) SI = SP + SD
   - (4) SD = f * (Rc - Rt)
   - (5) SP = -a_s * c_t
   - (6) I = -I_max * exp(-(i * t_a / SI))
   - (7) c_t = cos(2π(T - p)/24) + β cos(4π(T - p - p')/24)
   - (8) E_t = 100 * (Rt/Rc) + C_t + I
   - (9) C_t = c_t * (a1 + a2*(Rc - Rt)/Rc)

2) An open-access paper that summarizes SAFTE use and parameters in an operational
   aviation setting (for context/triangulation, not as the primary equation source):
   - Frontiers in Public Health (PMC): https://pmc.ncbi.nlm.nih.gov/articles/PMC9623177/

Important scope notes
---------------------
- SAFTE and FAST are associated with patented/commercial implementations. This module
  implements only the openly documented, patent-equation core. It is provided for
  research/education use; verify licensing constraints for your intended use.
- FAST includes additional features (e.g., sleep prediction from duty schedules,
  circadian phase shifting / jet-lag handling, workload integration) that are not
  fully specified in public literature. This implementation focuses on:
  - Sleep history integration (explicit sleep episodes provided by user)
  - Multi-day forecasting of effectiveness on a fixed time grid
- Circadian phase shifting / jet lag algorithmic adjustments described in the patent
  are not implemented here (requires additional rule-set beyond the explicit equations).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Final, Iterable, Sequence

__all__ = [
    "SafteParameters",
    "SleepEpisode",
    "SafteInputs",
    "SaftePoint",
    "SafteSeries",
    "simulate_safte",
]


@dataclass(frozen=True, slots=True)
class SafteParameters:
    """SAFTE constants (patent defaults)."""

    # Reservoir capacity (sleep units)
    reservoir_capacity_rc: float = 2880.0
    # Awake depletion slope K [units/min]
    depletion_k_units_per_min: float = 0.5

    # Sleep debt factor f
    sleep_debt_f: float = 0.00312
    # Sleep propensity amplitude a_s [units]
    sleep_propensity_as: float = 0.55

    # Sleep inertia parameters (Eq. 6); I_max is in "percent points" (5 not 0.05)
    inertia_i_max: float = 5.0
    inertia_time_constant_i: float = 0.04
    inertia_applies_minutes: float = 120.0

    # Circadian process parameters (Eq. 7)
    circadian_beta: float = 0.5
    acrophase_p_hours: float = 18.0
    phase_offset_p_prime_hours: float = 3.0

    # Circadian amplitude scaling (Eq. 9) in percent points (7 and 5)
    a1_percent: float = 7.0
    a2_percent: float = 5.0

    # Sleep reservoir does not change within first N minutes of sleep (patent text)
    sleep_fill_delay_minutes: float = 5.0


@dataclass(frozen=True, slots=True)
class SleepEpisode:
    """A sleep interval within the simulation window.

    Times are expressed as minutes from simulation start, in a half-open interval:
    [start_min, end_min). Episodes must be non-overlapping and sorted.
    """

    start_min: float
    end_min: float


@dataclass(frozen=True, slots=True)
class SafteInputs:
    """Inputs for SAFTE simulation."""

    start_datetime_local: datetime
    horizon_minutes: int
    step_minutes: int
    sleep_episodes: tuple[SleepEpisode, ...]
    initial_reservoir_units: float | None = None
    params: SafteParameters = SafteParameters()


@dataclass(frozen=True, slots=True)
class SaftePoint:
    t_min: int
    local_hour: float
    asleep: bool
    reservoir_units: float
    circadian_process_ct: float
    circadian_amplitude_Ct: float
    sleep_intensity_SI: float
    inertia_I: float
    effectiveness_E: float


@dataclass(frozen=True, slots=True)
class SafteSeries:
    points: tuple[SaftePoint, ...]

    @property
    def min_effectiveness(self) -> float:
        return float(min(p.effectiveness_E for p in self.points))

    @property
    def max_effectiveness(self) -> float:
        return float(max(p.effectiveness_E for p in self.points))


def _is_finite(x: float) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def _validate_positive_int(name: str, v: int, *, min_value: int = 1) -> int:
    if not isinstance(v, int):
        raise TypeError(f"{name} must be an int")
    if v < min_value:
        raise ValueError(f"{name} must be >= {min_value}")
    return v


def _validate_params(p: SafteParameters) -> SafteParameters:
    if not isinstance(p, SafteParameters):
        raise TypeError("params must be a SafteParameters instance")
    if p.reservoir_capacity_rc <= 0.0:
        raise ValueError("reservoir_capacity_rc must be > 0")
    if p.depletion_k_units_per_min < 0.0:
        raise ValueError("depletion_k_units_per_min must be >= 0")
    if p.sleep_debt_f < 0.0:
        raise ValueError("sleep_debt_f must be >= 0")
    if p.sleep_fill_delay_minutes < 0.0:
        raise ValueError("sleep_fill_delay_minutes must be >= 0")
    if p.inertia_time_constant_i <= 0.0:
        raise ValueError("inertia_time_constant_i must be > 0")
    if p.inertia_applies_minutes <= 0.0:
        raise ValueError("inertia_applies_minutes must be > 0")
    return p


def _validate_sleep_episodes(episodes: Sequence[SleepEpisode], horizon_minutes: int) -> tuple[SleepEpisode, ...]:
    out: list[SleepEpisode] = []
    prev_end = -1.0
    for ep in episodes:
        if not isinstance(ep, SleepEpisode):
            raise TypeError("sleep_episodes must contain SleepEpisode entries")
        s = float(ep.start_min)
        e = float(ep.end_min)
        if not (_is_finite(s) and _is_finite(e)):
            raise ValueError("SleepEpisode times must be finite")
        if s < 0.0 or e < 0.0:
            raise ValueError("SleepEpisode times must be >= 0")
        if e <= s:
            raise ValueError("SleepEpisode must have end_min > start_min")
        if s < prev_end - 1e-12:
            raise ValueError("SleepEpisode intervals must be non-overlapping and sorted")
        if s > float(horizon_minutes) + 1e-12:
            break
        out.append(SleepEpisode(start_min=s, end_min=min(e, float(horizon_minutes))))
        prev_end = e
    return tuple(out)


def _local_hour(start: datetime, t_min: float) -> float:
    # Local time-of-day in hours, using start datetime's hour as anchor.
    base = float(start.hour) + float(start.minute) / 60.0 + float(start.second) / 3600.0
    return float((base + float(t_min) / 60.0) % 24.0)


def _circadian_process_ct(T_hours: float, p: SafteParameters) -> float:
    # Eq. (7)
    t = float(T_hours)
    a = 2.0 * math.pi * (t - p.acrophase_p_hours) / 24.0
    b = 4.0 * math.pi * (t - p.acrophase_p_hours - p.phase_offset_p_prime_hours) / 24.0
    return float(math.cos(a) + float(p.circadian_beta) * math.cos(b))


def _circadian_amplitude_Ct(ct: float, Rt: float, p: SafteParameters) -> float:
    # Eq. (9)
    rc = float(p.reservoir_capacity_rc)
    return float(ct * (float(p.a1_percent) + float(p.a2_percent) * (rc - Rt) / rc))


def _sleep_debt_SD(Rt: float, p: SafteParameters) -> float:
    # Eq. (4)
    rc = float(p.reservoir_capacity_rc)
    return float(p.sleep_debt_f * (rc - Rt))


def _sleep_propensity_SP(ct: float, p: SafteParameters) -> float:
    # Eq. (5)
    return float(-float(p.sleep_propensity_as) * ct)


def _sleep_intensity_SI(ct: float, Rt: float, p: SafteParameters) -> float:
    # Eq. (3) with Eq. (4) and Eq. (5)
    return float(_sleep_propensity_SP(ct, p) + _sleep_debt_SD(Rt, p))


def _sleep_inertia_I(minutes_awake: float, SI_at_wake: float, p: SafteParameters) -> float:
    # Eq. (6)
    if minutes_awake < 0.0:
        raise ValueError("minutes_awake must be >= 0")
    if minutes_awake > float(p.inertia_applies_minutes):
        return 0.0
    # Avoid divide-by-zero: if SI_at_wake is tiny or negative, inertia is treated as 0.
    if SI_at_wake <= 1e-9:
        return 0.0
    return float(-float(p.inertia_i_max) * math.exp(-(float(p.inertia_time_constant_i) * minutes_awake / SI_at_wake)))


def simulate_safte(inputs: SafteInputs, *, max_points: int = 200_000) -> SafteSeries:
    """Simulate patent-derived SAFTE effectiveness over time.

    Sleep episodes are explicit. Time is simulated on a fixed grid of `step_minutes`.
    """
    if not isinstance(inputs, SafteInputs):
        raise TypeError("inputs must be a SafteInputs instance")

    horizon = _validate_positive_int("horizon_minutes", int(inputs.horizon_minutes), min_value=1)
    step = _validate_positive_int("step_minutes", int(inputs.step_minutes), min_value=1)
    if horizon % step != 0:
        raise ValueError("horizon_minutes must be divisible by step_minutes")
    n = horizon // step + 1
    if n > int(max_points):
        raise ValueError("simulation too large; reduce horizon/step or raise max_points")

    p = _validate_params(inputs.params)
    episodes = _validate_sleep_episodes(inputs.sleep_episodes, horizon)

    rc = float(p.reservoir_capacity_rc)
    if inputs.initial_reservoir_units is None:
        Rt = rc
    else:
        Rt = float(inputs.initial_reservoir_units)
        if not _is_finite(Rt):
            raise ValueError("initial_reservoir_units must be finite")
        if Rt < 0.0 or Rt > rc:
            raise ValueError("initial_reservoir_units must be within [0, Rc]")

    ep_idx = 0
    asleep = False
    minutes_since_sleep_start = 0.0
    minutes_since_wake = float(p.inertia_applies_minutes) + 1.0
    SI_at_wake = 0.0

    points: list[SaftePoint] = []

    # Iterate fixed grid (bounded).
    for k in range(n):
        t_min = k * step
        # Determine asleep/awake state using episodes.
        while ep_idx < len(episodes) and float(t_min) >= episodes[ep_idx].end_min - 1e-12:
            ep_idx += 1

        now_asleep = False
        if ep_idx < len(episodes):
            ep = episodes[ep_idx]
            if float(t_min) >= ep.start_min - 1e-12 and float(t_min) < ep.end_min - 1e-12:
                now_asleep = True

        # Track sleep state transitions.
        if now_asleep and not asleep:
            asleep = True
            minutes_since_sleep_start = 0.0
        elif (not now_asleep) and asleep:
            asleep = False
            minutes_since_wake = 0.0
            # Record SI at wake using last computed SI.
            # (We will compute SI below using the current c_t and Rt, but we want SI
            #  at wake to reflect the last sleep instant; use the previous loop's
            #  value if available, otherwise recompute a proxy.)
            if points:
                SI_at_wake = float(points[-1].sleep_intensity_SI)
            else:
                # Fallback: compute at current state.
                T0 = _local_hour(inputs.start_datetime_local, float(t_min))
                ct0 = _circadian_process_ct(T0, p)
                SI_at_wake = _sleep_intensity_SI(ct0, Rt, p)

        # Circadian process at this time.
        T = _local_hour(inputs.start_datetime_local, float(t_min))
        ct = _circadian_process_ct(T, p)
        Ct = _circadian_amplitude_Ct(ct, Rt, p)

        SI = _sleep_intensity_SI(ct, Rt, p)

        # Inertia applies only after waking.
        I = 0.0 if asleep else _sleep_inertia_I(minutes_since_wake, SI_at_wake, p)

        E = float(100.0 * (Rt / rc) + Ct + I)

        points.append(
            SaftePoint(
                t_min=int(t_min),
                local_hour=T,
                asleep=bool(asleep),
                reservoir_units=float(Rt),
                circadian_process_ct=float(ct),
                circadian_amplitude_Ct=float(Ct),
                sleep_intensity_SI=float(SI),
                inertia_I=float(I),
                effectiveness_E=float(E),
            )
        )

        # Advance reservoir state to next step (except at last point).
        if k == n - 1:
            break

        dt = float(step)
        if asleep:
            minutes_since_sleep_start += dt
            # First N minutes of sleep: reservoir fixed.
            if minutes_since_sleep_start <= float(p.sleep_fill_delay_minutes) + 1e-12:
                Rt = Rt
            else:
                # Eq. (2): S = SI * t. Fill by SI*dt, bounded to [0, Rc].
                Rt = min(rc, Rt + float(SI) * dt)
        else:
            minutes_since_wake += dt
            # Eq. (1): P = K*t. Deplete by K*dt, bounded to [0, Rc].
            Rt = max(0.0, Rt - float(p.depletion_k_units_per_min) * dt)

    return SafteSeries(points=tuple(points))


