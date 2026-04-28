/**
 * Altitude / hypoxia effects on Dynamic Visual Acuity (DVA).
 *
 * Empirical lookup over the Wang et al. (2024) chamber-study cohort
 * (healthy adults, 20–24 y), bilinear in (altitude, time at altitude),
 * linear in target angular velocity.
 *
 * Reference:
 *   Wang, Y., et al. (2024). Influence of short-term hypoxia exposure on
 *   dynamic visual acuity. Frontiers in Neuroscience, 18:1428987.
 *   https://doi.org/10.3389/fnins.2024.1428987
 *
 * SCOPE: empirical, single-cohort. Not mechanistic. Inputs are clamped:
 *   altitude_m ∈ [0, 4500], time_at_altitude_min ∈ [0, 30],
 *   angular_velocity_deg_s ∈ [20, 80].
 */

export interface DvaEstimate {
  altitude_m: number;
  time_at_altitude_min: number;
  angular_velocity_deg_s: number;
  logmar: number;
  /** Approximate Snellen denominator at 20 ft (i.e. 20/X). */
  snellen_denominator_20ft: number;
}

const VELOCITIES_DEG_S: ReadonlyArray<number> = [20, 40, 60, 80];

interface DataRow {
  altitude_m: number;
  time_min: number;
  /** logMAR per velocity in VELOCITIES_DEG_S order. */
  logmar_by_velocity: ReadonlyArray<number>;
}

// Data extracted from Table 3 of Wang et al. (2024).
const DATA_ROWS: ReadonlyArray<DataRow> = [
  { altitude_m: 0, time_min: 0, logmar_by_velocity: [0.14, 0.13, 0.19, 0.18] },
  { altitude_m: 3500, time_min: 0, logmar_by_velocity: [0.12, 0.16, 0.15, 0.13] },
  { altitude_m: 3500, time_min: 30, logmar_by_velocity: [0.13, 0.14, 0.13, 0.16] },
  { altitude_m: 4000, time_min: 0, logmar_by_velocity: [0.09, 0.15, 0.15, 0.16] },
  { altitude_m: 4000, time_min: 30, logmar_by_velocity: [0.11, 0.12, 0.08, 0.13] },
  { altitude_m: 4500, time_min: 0, logmar_by_velocity: [0.14, 0.16, 0.15, 0.13] },
  { altitude_m: 4500, time_min: 30, logmar_by_velocity: [0.14, 0.17, 0.13, 0.15] },
];

function isFinite(x: number): boolean {
  return typeof x === 'number' && Number.isFinite(x);
}

function clamp(x: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, x));
}

function interp1d(x: number, x0: number, y0: number, x1: number, y1: number): number {
  if (x1 === x0) return y0;
  const t = (x - x0) / (x1 - x0);
  return y0 + t * (y1 - y0);
}

function interpVelocity(values: ReadonlyArray<number>, vel: number): number {
  const v = clamp(vel, VELOCITIES_DEG_S[0], VELOCITIES_DEG_S[VELOCITIES_DEG_S.length - 1]);
  for (let i = 0; i < VELOCITIES_DEG_S.length - 1; i++) {
    const v0 = VELOCITIES_DEG_S[i];
    const v1 = VELOCITIES_DEG_S[i + 1];
    if (v >= v0 && v <= v1) {
      return interp1d(v, v0, values[i], v1, values[i + 1]);
    }
  }
  return values[values.length - 1];
}

function sliceAtTime(targetTime: number): Array<readonly [number, ReadonlyArray<number>]> {
  const map = new Map<number, ReadonlyArray<number>>();
  for (const row of DATA_ROWS) {
    if (row.time_min === targetTime) {
      map.set(row.altitude_m, row.logmar_by_velocity);
    }
  }
  // For 30-min slice, no ground (0 m) data was reported; reuse t=0 ground.
  if (targetTime === 30 && !map.has(0)) {
    for (const row of DATA_ROWS) {
      if (row.altitude_m === 0 && row.time_min === 0) {
        map.set(0, row.logmar_by_velocity);
        break;
      }
    }
  }
  return Array.from(map.entries()).sort((a, b) => a[0] - b[0]);
}

function interpOverAltitude(
  alt: number,
  rows: Array<readonly [number, ReadonlyArray<number>]>,
  vel: number
): number {
  if (rows.length === 0) return 0;
  if (alt <= rows[0][0]) return interpVelocity(rows[0][1], vel);
  if (alt >= rows[rows.length - 1][0]) return interpVelocity(rows[rows.length - 1][1], vel);
  for (let i = 0; i < rows.length - 1; i++) {
    const [a0, vals0] = rows[i];
    const [a1, vals1] = rows[i + 1];
    if (alt >= a0 && alt <= a1) {
      const y0 = interpVelocity(vals0, vel);
      const y1 = interpVelocity(vals1, vel);
      return interp1d(alt, a0, y0, a1, y1);
    }
  }
  return interpVelocity(rows[rows.length - 1][1], vel);
}

/**
 * Convert logMAR to an approximate Snellen denominator at 20 ft.
 *
 * MAR = 10^logMAR; Snellen denominator = round(20 × MAR) (≥ 1).
 */
export function logmarToSnellenDenominator(logmar: number): number {
  if (!isFinite(logmar)) {
    throw new TypeError('logmar must be a finite number');
  }
  const mar = Math.pow(10, logmar);
  const denom = Math.round(20 * mar);
  return Math.max(1, denom);
}

/**
 * Estimate DVA logMAR using the Wang 2024 chamber-study lookup.
 * Bilinear over (altitude, time), linear over target velocity.
 */
export function estimateDvaLogmarWang2024(args: {
  altitude_m: number;
  time_at_altitude_min: number;
  angular_velocity_deg_s: number;
}): DvaEstimate {
  let { altitude_m, time_at_altitude_min, angular_velocity_deg_s } = args;

  if (!isFinite(altitude_m) || !isFinite(time_at_altitude_min) || !isFinite(angular_velocity_deg_s)) {
    throw new TypeError(
      'altitude_m, time_at_altitude_min, and angular_velocity_deg_s must be finite numbers'
    );
  }
  if (altitude_m < 0) throw new Error('altitude_m must be >= 0');
  if (time_at_altitude_min < 0) throw new Error('time_at_altitude_min must be >= 0');
  if (angular_velocity_deg_s <= 0) throw new Error('angular_velocity_deg_s must be > 0');

  altitude_m = clamp(altitude_m, 0, 4500);
  time_at_altitude_min = clamp(time_at_altitude_min, 0, 30);
  angular_velocity_deg_s = clamp(angular_velocity_deg_s, 20, 80);

  const row0 = sliceAtTime(0);
  const row30 = sliceAtTime(30);
  const y0 = interpOverAltitude(altitude_m, row0, angular_velocity_deg_s);
  const y30 = interpOverAltitude(altitude_m, row30, angular_velocity_deg_s);
  const logmar = interp1d(time_at_altitude_min, 0, y0, 30, y30);

  return {
    altitude_m,
    time_at_altitude_min,
    angular_velocity_deg_s,
    logmar,
    snellen_denominator_20ft: logmarToSnellenDenominator(logmar),
  };
}
