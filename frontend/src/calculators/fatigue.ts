/**
 * Fatigue, Circadian, and Duty-Time Calculators
 *
 * References:
 * - Mitler, M.M. et al. (1988). Catastrophes, sleep, and public policy. Sleep 11(1):100-109.
 * - Borbély, A.A. (1982). A two-process model of sleep regulation. Human Neurobiology 1:195-204.
 * - FAA 14 CFR Part 117 (Tables A & B): https://www.ecfr.gov/current/title-14/part-117
 * - EASA Part-ORO Subpart FTL (ORO.FTL.205, ORO.FTL.210)
 * - Hursh, S.R. et al. (2004). Fatigue models for applied research in warfighting. Aviat Space Environ Med.
 */

// ──────────────────────────────────────────────────────────────────────
// Mitler circadian performance model
// ──────────────────────────────────────────────────────────────────────

/**
 * Mitler's circadian performance model.
 *
 * P = (1/K) [K - cos²(θ) × (1 - cos(θ)/SD)²]  where θ = 2π(t + φ)/24
 *
 * @param t_hours - Time since epoch (hours)
 * @param phi_hours - Phase offset (hours)
 * @param SD - Sleep debt parameter (>0)
 * @param K - Scaling constant (>0)
 * @returns Performance score (unitless, higher = better)
 */
export function mitlerPerformance(
  t_hours: number,
  phi_hours: number,
  SD: number,
  K: number,
): number {
  if (SD <= 0) throw new Error('SD must be > 0');
  if (K <= 0) throw new Error('K must be > 0');

  const theta = (2.0 * Math.PI * (t_hours + phi_hours)) / 24.0;
  const c = Math.cos(theta);
  const value = (K - c * c * Math.pow(1.0 - c / SD, 2)) / K;
  return value;
}

/**
 * Simulate Mitler performance over a time grid.
 */
export interface MitlerTrajectoryPoint {
  t_hours: number;
  performance: number;
}

export function simulateMitlerTrajectory(
  phi_hours: number,
  SD: number,
  K: number,
  horizon_hours: number = 48,
  step_minutes: number = 10,
): MitlerTrajectoryPoint[] {
  if (horizon_hours <= 0) throw new Error('horizon_hours must be > 0');
  if (step_minutes <= 0) throw new Error('step_minutes must be > 0');

  const step_h = step_minutes / 60.0;
  const points: MitlerTrajectoryPoint[] = [];
  const maxSteps = Math.ceil(horizon_hours / step_h) + 1;

  for (let i = 0; i <= maxSteps && i * step_h <= horizon_hours; i++) {
    const t = i * step_h;
    points.push({
      t_hours: t,
      performance: mitlerPerformance(t, phi_hours, SD, K),
    });
  }
  return points;
}

// ──────────────────────────────────────────────────────────────────────
// Two-Process model components (Borbély 1982)
// ──────────────────────────────────────────────────────────────────────

/**
 * Homeostatic (waking) component: S = (Sa − L)·e^{-0.0343·t} + L
 */
export function homeostaticWaking(Sa: number, L: number, t_hours: number): number {
  return (Sa - L) * Math.exp(-0.0343 * t_hours) + L;
}

/**
 * Homeostatic (sleep) component: S' = U − (U − Sr)·e^{-0.381·t}
 */
export function homeostaticSleep(U: number, Sr: number, t_hours: number): number {
  return U - (U - Sr) * Math.exp(-0.381 * t_hours);
}

/**
 * Circadian component: C = M·cos((t − p)·π/12)
 */
export function circadianComponent(M: number, t_hours: number, p_hours: number): number {
  return M * Math.cos((t_hours - p_hours) * Math.PI / 12.0);
}

/**
 * Simulate Two-Process model over a wake/sleep cycle.
 */
export interface TwoProcessPoint {
  t_hours: number;
  S: number;
  C: number;
  alertness: number;
  asleep: boolean;
}

export function simulateTwoProcess(
  wakeHours: number = 16,
  sleepHours: number = 8,
  cycles: number = 2,
  step_minutes: number = 10,
  Sa: number = 1.0,
  L: number = 0.17,
  U: number = 1.0,
  M: number = 0.5,
  p_hours: number = 16,
): TwoProcessPoint[] {
  const step_h = step_minutes / 60.0;
  const points: TwoProcessPoint[] = [];
  let globalT = 0;
  let currentS = Sa;

  const maxPoints = 5000;
  let pointCount = 0;

  for (let cycle = 0; cycle < cycles && pointCount < maxPoints; cycle++) {
    // Waking phase
    for (let i = 0; i * step_h <= wakeHours && pointCount < maxPoints; i++) {
      const t = i * step_h;
      const S = homeostaticWaking(currentS, L, t);
      const C = circadianComponent(M, globalT + t, p_hours);
      points.push({ t_hours: globalT + t, S, C, alertness: S + C, asleep: false });
      pointCount++;
    }
    currentS = homeostaticWaking(currentS, L, wakeHours);
    globalT += wakeHours;

    // Sleeping phase
    const sleepStart = currentS;
    for (let i = 0; i * step_h <= sleepHours && pointCount < maxPoints; i++) {
      const t = i * step_h;
      const S = homeostaticSleep(U, sleepStart, t);
      const C = circadianComponent(M, globalT + t, p_hours);
      points.push({ t_hours: globalT + t, S, C, alertness: S + C, asleep: true });
      pointCount++;
    }
    currentS = homeostaticSleep(U, sleepStart, sleepHours);
    globalT += sleepHours;
  }
  return points;
}

// ──────────────────────────────────────────────────────────────────────
// Jet lag recovery estimator
// ──────────────────────────────────────────────────────────────────────

export interface JetLagResult {
  daysToAdjust: number;
  adjustmentRateMinPerDay: number;
  direction: 'east' | 'west';
  timeZones: number;
}

/**
 * Estimate days to adjust from jet lag.
 * Westward: ~90 min/day; Eastward: ~60 min/day.
 */
export function jetLagDaysToAdjust(
  timeZones: number,
  direction: 'east' | 'west',
): JetLagResult {
  if (timeZones < 0) throw new Error('timeZones must be >= 0');
  const tz = Math.max(0, Math.round(timeZones));
  const minPerDay = direction === 'west' ? 90.0 : 60.0;
  const totalMinutes = tz * 60.0;
  return {
    daysToAdjust: totalMinutes / minPerDay,
    adjustmentRateMinPerDay: minPerDay,
    direction,
    timeZones: tz,
  };
}

// ──────────────────────────────────────────────────────────────────────
// FAA 14 CFR Part 117 (unaugmented operations)
// ──────────────────────────────────────────────────────────────────────

type TimeWindowLabel =
  | '0000-0359' | '0400-0459' | '0500-0559' | '0600-0659'
  | '0700-1159' | '1200-1259' | '1300-1659' | '1700-2159'
  | '2200-2259' | '2300-2359';

export interface Faa117Result {
  reportTimeMinutes: number;
  timeWindow: TimeWindowLabel;
  flightSegments: number;
  maxFlightTimeHours: number;
  maxFdpHours: number;
  minRestHours: number;
  notAcclimatedReduction: number;
}

// Table A — max flight time
function faaTableAMaxFlightTime(reportMins: number): number {
  if (reportMins >= 0 && reportMins <= 4 * 60 + 59) return 8.0;
  if (reportMins >= 5 * 60 && reportMins <= 19 * 60 + 59) return 9.0;
  return 8.0;
}

// Table B — FDP limits [segments: 1,2,3,4,5,6,7+]
const TABLE_B: Record<TimeWindowLabel, readonly number[]> = {
  '0000-0359': [9, 9, 9, 9, 9, 9, 9],
  '0400-0459': [10, 10, 10, 10, 9, 9, 9],
  '0500-0559': [12, 12, 12, 12, 11.5, 11, 10.5],
  '0600-0659': [13, 13, 12, 12, 11.5, 11, 10.5],
  '0700-1159': [14, 14, 13, 13, 12.5, 12, 11.5],
  '1200-1259': [13, 13, 13, 13, 12.5, 12, 11.5],
  '1300-1659': [12, 12, 12, 12, 11.5, 11, 10.5],
  '1700-2159': [12, 12, 11, 11, 10, 9, 9],
  '2200-2259': [11, 11, 10, 10, 9, 9, 9],
  '2300-2359': [10, 10, 10, 9, 9, 9, 9],
};

function windowLabel(mins: number): TimeWindowLabel {
  if (mins <= 3 * 60 + 59) return '0000-0359';
  if (mins <= 4 * 60 + 59) return '0400-0459';
  if (mins <= 5 * 60 + 59) return '0500-0559';
  if (mins <= 6 * 60 + 59) return '0600-0659';
  if (mins <= 11 * 60 + 59) return '0700-1159';
  if (mins <= 12 * 60 + 59) return '1200-1259';
  if (mins <= 16 * 60 + 59) return '1300-1659';
  if (mins <= 21 * 60 + 59) return '1700-2159';
  if (mins <= 22 * 60 + 59) return '2200-2259';
  return '2300-2359';
}

/**
 * Parse HH:MM to minutes since midnight.
 */
export function parseHHMM(hhmm: string): number {
  const parts = hhmm.trim().split(':');
  if (parts.length !== 2) throw new Error('Time must be in HH:MM format');
  const hh = parseInt(parts[0], 10);
  const mm = parseInt(parts[1], 10);
  if (isNaN(hh) || isNaN(mm) || hh < 0 || hh > 23 || mm < 0 || mm > 59) {
    throw new Error('Invalid time');
  }
  return hh * 60 + mm;
}

/**
 * FAA Part 117 duty/flight time limits (unaugmented).
 */
export function faa117Limits(
  reportTimeHHMM: string,
  flightSegments: number,
  notAcclimated: boolean = false,
): Faa117Result {
  if (flightSegments < 1) throw new Error('flightSegments must be >= 1');

  const reportMins = parseHHMM(reportTimeHHMM);
  const window = windowLabel(reportMins);
  const maxFt = faaTableAMaxFlightTime(reportMins);

  const col = Math.min(flightSegments, 7) - 1;
  const baseFdp = TABLE_B[window][col];
  const reduction = notAcclimated ? 0.5 : 0.0;

  return {
    reportTimeMinutes: reportMins,
    timeWindow: window,
    flightSegments,
    maxFlightTimeHours: maxFt,
    maxFdpHours: Math.max(0, baseFdp - reduction),
    minRestHours: 10.0,
    notAcclimatedReduction: reduction,
  };
}

// ──────────────────────────────────────────────────────────────────────
// FAA §117.23 cumulative limits
// ──────────────────────────────────────────────────────────────────────

export interface Faa117CumulativeResult {
  flightTime672hOk: boolean;
  flightTime365dOk: boolean;
  fdp168hOk: boolean;
  fdp672hOk: boolean;
  flightTime672hMargin: number;
  flightTime365dMargin: number;
  fdp168hMargin: number;
  fdp672hMargin: number;
}

export function faa117CumulativeLimits(
  ft672h: number,
  ft365d: number,
  fdp168h: number,
  fdp672h: number,
  plannedFt: number,
  plannedFdp: number,
): Faa117CumulativeResult {
  const ft672 = ft672h + plannedFt;
  const ft365 = ft365d + plannedFt;
  const fdp168 = fdp168h + plannedFdp;
  const fdp672 = fdp672h + plannedFdp;

  return {
    flightTime672hOk: ft672 <= 100,
    flightTime365dOk: ft365 <= 1000,
    fdp168hOk: fdp168 <= 60,
    fdp672hOk: fdp672 <= 190,
    flightTime672hMargin: 100 - ft672,
    flightTime365dMargin: 1000 - ft365,
    fdp168hMargin: 60 - fdp168,
    fdp672hMargin: 190 - fdp672,
  };
}

// ──────────────────────────────────────────────────────────────────────
// EASA ORO.FTL.205 (simplified table lookup)
// ──────────────────────────────────────────────────────────────────────

export type AcclimatisationState = 'acclimatised' | 'unknown' | 'unknown_frm';

export interface EasaFdpResult {
  maxDailyFdpHours: number;
  sourceTable: string;
  sectors: number;
}

/**
 * EASA maximum daily FDP (simplified).
 * Acclimatised: Table 2 reference range 9-14h depending on start time and sectors.
 * Unknown/FRM: Tables 3/4 are start-time-independent.
 */
export function easaMaxDailyFdp(
  reportTimeHHMM: string,
  sectors: number,
  state: AcclimatisationState = 'acclimatised',
): EasaFdpResult {
  if (sectors < 1 || sectors > 10) throw new Error('sectors must be 1-10');

  const col = sectors <= 2 ? 0 : Math.min(sectors - 2, 8);

  if (state === 'unknown') {
    const table3 = [11, 10.5, 10, 9.5, 9, 9, 9];
    return {
      maxDailyFdpHours: table3[Math.min(col, 6)],
      sourceTable: 'ORO.FTL.205(b)(2) Table 3',
      sectors,
    };
  }
  if (state === 'unknown_frm') {
    const table4 = [12, 11.5, 11, 10.5, 10, 9.5, 9];
    return {
      maxDailyFdpHours: table4[Math.min(col, 6)],
      sourceTable: 'ORO.FTL.205(b)(3) Table 4',
      sectors,
    };
  }

  // Acclimatised — Table 2 (simplified: use peak-window values for 07:00-11:59)
  const reportMins = parseHHMM(reportTimeHHMM);
  const hour = Math.floor(reportMins / 60);

  // Base values for 1-2 sectors at each window block
  let baseFdp: number;
  if (hour >= 7 && hour < 12) baseFdp = 14;
  else if (hour >= 6 && hour < 7) baseFdp = 13;
  else if (hour >= 12 && hour < 13) baseFdp = 13;
  else if (hour >= 5 && hour < 6) baseFdp = 12;
  else if (hour >= 13 && hour < 17) baseFdp = 12;
  else if (hour >= 17 && hour < 22) baseFdp = 11;
  else baseFdp = 9;

  // Reduce for additional sectors (0.5h per extra sector beyond 2, min 9h)
  const sectorReduction = col * 0.5;
  const fdp = Math.max(9, baseFdp - sectorReduction);

  return {
    maxDailyFdpHours: fdp,
    sourceTable: 'ORO.FTL.205(b)(1) Table 2',
    sectors,
  };
}

// ──────────────────────────────────────────────────────────────────────
// EASA ORO.FTL.210 cumulative limits
// ──────────────────────────────────────────────────────────────────────

export interface EasaCumulativeResult {
  duty7dOk: boolean;
  duty14dOk: boolean;
  duty28dOk: boolean;
  ft28dOk: boolean;
  ftYearOk: boolean;
  ft12moOk: boolean;
  duty7dMargin: number;
  duty14dMargin: number;
  duty28dMargin: number;
  ft28dMargin: number;
  ftYearMargin: number;
  ft12moMargin: number;
}

export function easaCumulativeLimits(
  duty7d: number, duty14d: number, duty28d: number,
  ft28d: number, ftYear: number, ft12mo: number,
  plannedDuty: number, plannedFt: number,
): EasaCumulativeResult {
  const d7 = duty7d + plannedDuty;
  const d14 = duty14d + plannedDuty;
  const d28 = duty28d + plannedDuty;
  const f28 = ft28d + plannedFt;
  const fy = ftYear + plannedFt;
  const f12 = ft12mo + plannedFt;

  return {
    duty7dOk: d7 <= 60, duty14dOk: d14 <= 110, duty28dOk: d28 <= 190,
    ft28dOk: f28 <= 100, ftYearOk: fy <= 900, ft12moOk: f12 <= 1000,
    duty7dMargin: 60 - d7, duty14dMargin: 110 - d14, duty28dMargin: 190 - d28,
    ft28dMargin: 100 - f28, ftYearMargin: 900 - fy, ft12moMargin: 1000 - f12,
  };
}
