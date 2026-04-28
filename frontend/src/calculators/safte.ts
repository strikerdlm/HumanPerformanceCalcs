/**
 * SAFTE (patent-derived) Sleep, Activity, Fatigue, and Task Effectiveness model.
 *
 * Implements only the openly documented patent-equation core (WO2012015383A1):
 *   (1) P  = K · t                             (awake reservoir depletion)
 *   (2) S  = SI · t                            (sleep reservoir filling)
 *   (3) SI = SP + SD                           (sleep intensity)
 *   (4) SD = f · (Rc − Rt)                     (sleep debt)
 *   (5) SP = −a_s · c_t                        (sleep propensity)
 *   (6) I  = −I_max · exp(−(i · t_a / SI_at_wake))  (sleep inertia)
 *   (7) c_t = cos(2π(T − p)/24) + β · cos(4π(T − p − p′)/24)
 *   (8) E_t = 100 · (Rt/Rc) + C_t + I
 *   (9) C_t = c_t · (a1 + a2 · (Rc − Rt) / Rc)
 *
 * SCOPE: research/education. Not the full FAST commercial implementation. Does
 * not include circadian phase shifting / jet-lag handling, or workload models.
 *
 * References:
 *   - Patent WO2012015383A1 (Google Patents).
 *   - Frontiers in Public Health (PMC9623177) — operational SAFTE summary.
 */

export interface SafteParameters {
  /** Reservoir capacity Rc (sleep units). */
  reservoir_capacity_rc: number;
  /** Awake depletion slope K (units/min). */
  depletion_k_units_per_min: number;

  /** Sleep debt factor f. */
  sleep_debt_f: number;
  /** Sleep propensity amplitude a_s. */
  sleep_propensity_as: number;

  /** Inertia I_max (percent points). */
  inertia_i_max: number;
  /** Inertia decay constant i. */
  inertia_time_constant_i: number;
  /** Window after wake during which inertia applies (min). */
  inertia_applies_minutes: number;

  /** Circadian β (Eq. 7). */
  circadian_beta: number;
  /** Acrophase p (h). */
  acrophase_p_hours: number;
  /** Phase offset p′ (h). */
  phase_offset_p_prime_hours: number;

  /** Circadian amplitude scaling a1 (percent points). */
  a1_percent: number;
  /** Circadian amplitude scaling a2 (percent points). */
  a2_percent: number;

  /** Sleep reservoir does not change for the first N minutes of sleep. */
  sleep_fill_delay_minutes: number;
}

export const DEFAULT_SAFTE_PARAMETERS: SafteParameters = {
  reservoir_capacity_rc: 2880.0,
  depletion_k_units_per_min: 0.5,
  sleep_debt_f: 0.00312,
  sleep_propensity_as: 0.55,
  inertia_i_max: 5.0,
  inertia_time_constant_i: 0.04,
  inertia_applies_minutes: 120.0,
  circadian_beta: 0.5,
  acrophase_p_hours: 18.0,
  phase_offset_p_prime_hours: 3.0,
  a1_percent: 7.0,
  a2_percent: 5.0,
  sleep_fill_delay_minutes: 5.0,
};

/**
 * A sleep interval in `[start_min, end_min)` measured from simulation start.
 * Episodes must be non-overlapping and sorted in chronological order.
 */
export interface SleepEpisode {
  start_min: number;
  end_min: number;
}

export interface SafteInputs {
  /** Start of simulation in local time (Date). Used to anchor circadian phase. */
  start_datetime_local: Date;
  horizon_minutes: number;
  step_minutes: number;
  sleep_episodes: SleepEpisode[];
  /** Default: full reservoir Rc. */
  initial_reservoir_units?: number;
  params?: SafteParameters;
}

export interface SaftePoint {
  t_min: number;
  local_hour: number;
  asleep: boolean;
  reservoir_units: number;
  circadian_process_ct: number;
  circadian_amplitude_Ct: number;
  sleep_intensity_SI: number;
  inertia_I: number;
  effectiveness_E: number;
}

export interface SafteSeries {
  points: SaftePoint[];
  min_effectiveness: number;
  max_effectiveness: number;
}

function validateParams(p: SafteParameters): SafteParameters {
  if (p.reservoir_capacity_rc <= 0) throw new Error('reservoir_capacity_rc must be > 0');
  if (p.depletion_k_units_per_min < 0) throw new Error('depletion_k_units_per_min must be >= 0');
  if (p.sleep_debt_f < 0) throw new Error('sleep_debt_f must be >= 0');
  if (p.sleep_fill_delay_minutes < 0) throw new Error('sleep_fill_delay_minutes must be >= 0');
  if (p.inertia_time_constant_i <= 0) throw new Error('inertia_time_constant_i must be > 0');
  if (p.inertia_applies_minutes <= 0) throw new Error('inertia_applies_minutes must be > 0');
  return p;
}

function validateSleepEpisodes(episodes: SleepEpisode[], horizon: number): SleepEpisode[] {
  const out: SleepEpisode[] = [];
  let prevEnd = -1;
  for (const ep of episodes) {
    const s = ep.start_min;
    const e = ep.end_min;
    if (!Number.isFinite(s) || !Number.isFinite(e)) {
      throw new Error('SleepEpisode times must be finite');
    }
    if (s < 0 || e < 0) throw new Error('SleepEpisode times must be >= 0');
    if (e <= s) throw new Error('SleepEpisode must have end_min > start_min');
    if (s < prevEnd - 1e-12) {
      throw new Error('SleepEpisode intervals must be non-overlapping and sorted');
    }
    if (s > horizon + 1e-12) break;
    out.push({ start_min: s, end_min: Math.min(e, horizon) });
    prevEnd = e;
  }
  return out;
}

function localHour(start: Date, t_min: number): number {
  const base = start.getHours() + start.getMinutes() / 60 + start.getSeconds() / 3600;
  return ((base + t_min / 60) % 24 + 24) % 24;
}

function circadianProcessCt(T_hours: number, p: SafteParameters): number {
  const a = (2 * Math.PI * (T_hours - p.acrophase_p_hours)) / 24;
  const b =
    (4 * Math.PI * (T_hours - p.acrophase_p_hours - p.phase_offset_p_prime_hours)) / 24;
  return Math.cos(a) + p.circadian_beta * Math.cos(b);
}

function circadianAmplitudeCt(ct: number, Rt: number, p: SafteParameters): number {
  const rc = p.reservoir_capacity_rc;
  return ct * (p.a1_percent + p.a2_percent * (rc - Rt) / rc);
}

function sleepDebtSD(Rt: number, p: SafteParameters): number {
  return p.sleep_debt_f * (p.reservoir_capacity_rc - Rt);
}

function sleepPropensitySP(ct: number, p: SafteParameters): number {
  return -p.sleep_propensity_as * ct;
}

function sleepIntensitySI(ct: number, Rt: number, p: SafteParameters): number {
  return sleepPropensitySP(ct, p) + sleepDebtSD(Rt, p);
}

function sleepInertiaI(minutes_awake: number, SI_at_wake: number, p: SafteParameters): number {
  if (minutes_awake < 0) throw new Error('minutes_awake must be >= 0');
  if (minutes_awake > p.inertia_applies_minutes) return 0;
  if (SI_at_wake <= 1e-9) return 0;
  return -p.inertia_i_max * Math.exp(-(p.inertia_time_constant_i * minutes_awake) / SI_at_wake);
}

/**
 * Simulate patent-derived SAFTE effectiveness over `horizon_minutes` on a
 * fixed `step_minutes` grid. Sleep episodes must be supplied explicitly.
 */
export function simulateSafte(
  inputs: SafteInputs,
  options: { max_points?: number } = {}
): SafteSeries {
  const max_points = options.max_points ?? 200_000;
  const horizon = inputs.horizon_minutes;
  const step = inputs.step_minutes;
  if (!Number.isInteger(horizon) || horizon < 1) {
    throw new Error('horizon_minutes must be a positive integer');
  }
  if (!Number.isInteger(step) || step < 1) {
    throw new Error('step_minutes must be a positive integer');
  }
  if (horizon % step !== 0) {
    throw new Error('horizon_minutes must be divisible by step_minutes');
  }
  const n = horizon / step + 1;
  if (n > max_points) {
    throw new Error('simulation too large; reduce horizon/step or raise max_points');
  }

  const params = validateParams(inputs.params ?? DEFAULT_SAFTE_PARAMETERS);
  const episodes = validateSleepEpisodes(inputs.sleep_episodes, horizon);

  const rc = params.reservoir_capacity_rc;
  let Rt = inputs.initial_reservoir_units ?? rc;
  if (!Number.isFinite(Rt)) throw new Error('initial_reservoir_units must be finite');
  if (Rt < 0 || Rt > rc) throw new Error('initial_reservoir_units must be within [0, Rc]');

  let epIdx = 0;
  let asleep = false;
  let minutesSinceSleepStart = 0;
  let minutesSinceWake = params.inertia_applies_minutes + 1;
  let SI_at_wake = 0;

  const points: SaftePoint[] = [];

  for (let k = 0; k < n; k++) {
    const t_min = k * step;

    while (epIdx < episodes.length && t_min >= episodes[epIdx].end_min - 1e-12) {
      epIdx++;
    }

    let nowAsleep = false;
    if (epIdx < episodes.length) {
      const ep = episodes[epIdx];
      if (t_min >= ep.start_min - 1e-12 && t_min < ep.end_min - 1e-12) {
        nowAsleep = true;
      }
    }

    if (nowAsleep && !asleep) {
      asleep = true;
      minutesSinceSleepStart = 0;
    } else if (!nowAsleep && asleep) {
      asleep = false;
      minutesSinceWake = 0;
      if (points.length > 0) {
        SI_at_wake = points[points.length - 1].sleep_intensity_SI;
      } else {
        const T0 = localHour(inputs.start_datetime_local, t_min);
        const ct0 = circadianProcessCt(T0, params);
        SI_at_wake = sleepIntensitySI(ct0, Rt, params);
      }
    }

    const T = localHour(inputs.start_datetime_local, t_min);
    const ct = circadianProcessCt(T, params);
    const Ct = circadianAmplitudeCt(ct, Rt, params);
    const SI = sleepIntensitySI(ct, Rt, params);
    const I = asleep ? 0 : sleepInertiaI(minutesSinceWake, SI_at_wake, params);
    const E = 100 * (Rt / rc) + Ct + I;

    points.push({
      t_min,
      local_hour: T,
      asleep,
      reservoir_units: Rt,
      circadian_process_ct: ct,
      circadian_amplitude_Ct: Ct,
      sleep_intensity_SI: SI,
      inertia_I: I,
      effectiveness_E: E,
    });

    if (k === n - 1) break;

    const dt = step;
    if (asleep) {
      minutesSinceSleepStart += dt;
      if (minutesSinceSleepStart > params.sleep_fill_delay_minutes + 1e-12) {
        Rt = Math.min(rc, Rt + SI * dt);
      }
    } else {
      minutesSinceWake += dt;
      Rt = Math.max(0, Rt - params.depletion_k_units_per_min * dt);
    }
  }

  let minE = points[0]?.effectiveness_E ?? 0;
  let maxE = minE;
  for (const p of points) {
    if (p.effectiveness_E < minE) minE = p.effectiveness_E;
    if (p.effectiveness_E > maxE) maxE = p.effectiveness_E;
  }

  return {
    points,
    min_effectiveness: minE,
    max_effectiveness: maxE,
  };
}
