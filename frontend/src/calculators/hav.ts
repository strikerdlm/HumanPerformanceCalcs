/**
 * Hand-Arm Vibration (HAV) — ISO 5349-1:2001 + HSE points method.
 *
 * Inputs are already frequency-weighted accelerations per axis (a_hwx, a_hwy,
 * a_hwz, m/s²). Frequency-weighting filters (W_h) are NOT implemented here;
 * supply pre-weighted single-axis r.m.s. values from the measuring device.
 *
 *   a_hv     = √(a_hwx² + a_hwy² + a_hwz²)
 *   A(8)     = a_hv · √(T_exp / 8 h)
 *   points   = a_hv² · T_exp_h · 2          (HSE simplified points)
 *
 * UK HSE PAV thresholds (Control of Vibration at Work Regulations 2005):
 *   Exposure Action Value (EAV) = 2.5 m/s² A(8) ≡ 100 points
 *   Exposure Limit Value  (ELV) = 5.0 m/s² A(8) ≡ 400 points
 *
 * EU Directive 2002/44/EC uses the same 2.5 / 5.0 m/s² A(8) values.
 *
 * References:
 *   ISO 5349-1:2001 Mechanical vibration — Measurement and evaluation of
 *     human exposure to hand-transmitted vibration. https://www.iso.org/standard/32355.html
 *   HSE (UK). Hand-arm vibration at work. https://www.hse.gov.uk/vibration/hav/
 *   EU Directive 2002/44/EC.
 *
 * Pairs with the whole-body-vibration helpers in `risk.ts`.
 */

export type HavZone = 'below_eav' | 'eav_to_elv' | 'above_elv';

export interface HavInputs {
  /** Frequency-weighted r.m.s. acceleration on the x-axis (m/s²). */
  ahwx_m_s2: number;
  /** Frequency-weighted r.m.s. acceleration on the y-axis (m/s²). */
  ahwy_m_s2: number;
  /** Frequency-weighted r.m.s. acceleration on the z-axis (m/s²). */
  ahwz_m_s2: number;
  /** Total daily trigger-time exposure to vibration, hours. */
  exposure_duration_h: number;
}

export interface HavResult {
  /** ahv vector sum across axes, m/s². */
  ahv_m_s2: number;
  /** 8-hour energy-equivalent total acceleration, m/s² A(8). */
  a8_m_s2: number;
  /** HSE simplified daily exposure points (action 100, limit 400). */
  exposure_points: number;
  zone: HavZone;
  eav_m_s2: number;
  elv_m_s2: number;
  /** Maximum trigger time before reaching the EAV given the supplied a_hv. */
  time_to_eav_h: number | null;
  /** Maximum trigger time before reaching the ELV given the supplied a_hv. */
  time_to_elv_h: number | null;
}

const EAV_M_S2 = 2.5;
const ELV_M_S2 = 5.0;

function ensureNonNegative(name: string, v: number): number {
  if (!Number.isFinite(v) || v < 0) {
    throw new Error(`${name} must be a finite, non-negative number`);
  }
  return v;
}

function ensurePositive(name: string, v: number): number {
  if (!Number.isFinite(v) || v <= 0) {
    throw new Error(`${name} must be a finite, positive number`);
  }
  return v;
}

/**
 * Combine the three frequency-weighted axis r.m.s. values into the ahv
 * vector sum (ISO 5349-1 §6).
 */
export function ahvFromAxes(ahwx: number, ahwy: number, ahwz: number): number {
  ensureNonNegative('ahwx_m_s2', ahwx);
  ensureNonNegative('ahwy_m_s2', ahwy);
  ensureNonNegative('ahwz_m_s2', ahwz);
  return Math.sqrt(ahwx * ahwx + ahwy * ahwy + ahwz * ahwz);
}

/**
 * 8-hour energy-equivalent A(8) from a single-tool ahv and trigger time.
 */
export function havA8FromAhv(ahv_m_s2: number, exposure_duration_h: number): number {
  ensureNonNegative('ahv_m_s2', ahv_m_s2);
  ensurePositive('exposure_duration_h', exposure_duration_h);
  return ahv_m_s2 * Math.sqrt(exposure_duration_h / 8.0);
}

/**
 * HSE simplified exposure points from a tool ahv and trigger time.
 *   points = (a_hv / 2.5)² · (T_exp_h / 8) · 100
 *           = a_hv² · T_exp_h · 2
 *   Action value 2.5 m/s² A(8) → 100 points
 *   Limit value  5.0 m/s² A(8) → 400 points
 */
export function havExposurePoints(ahv_m_s2: number, exposure_duration_h: number): number {
  ensureNonNegative('ahv_m_s2', ahv_m_s2);
  ensurePositive('exposure_duration_h', exposure_duration_h);
  return ahv_m_s2 * ahv_m_s2 * exposure_duration_h * 2.0;
}

/** Combined HSE points for several tools used during the same shift. */
export function totalHavExposurePoints(
  tools: { ahv_m_s2: number; exposure_duration_h: number }[]
): number {
  let total = 0;
  for (const t of tools) {
    total += havExposurePoints(t.ahv_m_s2, t.exposure_duration_h);
  }
  return total;
}

/** Classify A(8) against the HSE/EU action and limit values. */
export function classifyHavZone(a8_m_s2: number): HavZone {
  ensureNonNegative('a8_m_s2', a8_m_s2);
  if (a8_m_s2 < EAV_M_S2) return 'below_eav';
  if (a8_m_s2 > ELV_M_S2) return 'above_elv';
  return 'eav_to_elv';
}

/** Solve the maximum daily trigger time before A(8) reaches a target. */
function timeToReachA8(ahv_m_s2: number, target_a8: number): number | null {
  if (ahv_m_s2 <= 0) return null;
  return 8.0 * Math.pow(target_a8 / ahv_m_s2, 2);
}

/**
 * Full HAV exposure computation: per-axis combination, A(8), HSE points,
 * HSE zone classification, and time-to-action / time-to-limit guidance.
 */
export function computeHavExposure(inputs: HavInputs): HavResult {
  const ahv = ahvFromAxes(inputs.ahwx_m_s2, inputs.ahwy_m_s2, inputs.ahwz_m_s2);
  const t = ensurePositive('exposure_duration_h', inputs.exposure_duration_h);
  const a8 = havA8FromAhv(ahv, t);
  const points = havExposurePoints(ahv, t);
  return {
    ahv_m_s2: ahv,
    a8_m_s2: a8,
    exposure_points: points,
    zone: classifyHavZone(a8),
    eav_m_s2: EAV_M_S2,
    elv_m_s2: ELV_M_S2,
    time_to_eav_h: timeToReachA8(ahv, EAV_M_S2),
    time_to_elv_h: timeToReachA8(ahv, ELV_M_S2),
  };
}

export const HAV_EAV_M_S2 = EAV_M_S2;
export const HAV_ELV_M_S2 = ELV_M_S2;
