/**
 * Oxygen toxicity tracking for diving and hyperbaric exposures.
 *
 * Implements three openly-published methods:
 *   1. NOAA Oxygen Exposure Limits — single-exposure CNS clock (linear lookup
 *      of max minutes vs PO₂; cumulative exposure expressed as a fraction).
 *   2. Bardin & Lambertsen (1970) Pulmonary OTU / UPTD —
 *        OTU = t · ((PO₂ − 0.5) / 0.5)^0.83  for PO₂ > 0.5 ata
 *      "Single exposure" / "daily" dose units.
 *   3. Arieli et al. (2002) Power Equation — non-linear regressive index
 *      for CNS-OT and Pulmonary-OT. PO₂ in kPa, time in minutes.
 *        K_CNS = (t/60)² · (PO₂/100)^6.8
 *        K_POT = (t/60)² · (PO₂/100)^4.57
 *
 * References:
 *   NOAA Diving Manual (5th ed., 2017), Table 15-1 (Oxygen Exposure Limits).
 *   Bardin H., Lambertsen C.J. (1970). Univ. of Pennsylvania IFEM Report.
 *   Arieli R., Yalov A., Goldenshluger A. (2002). Modeling pulmonary and CNS
 *     O₂ toxicity and estimation of parameters for humans. J. Appl. Physiol.
 *     92:248-256. https://doi.org/10.1152/japplphysiol.00434.2001
 *
 * Pairs with the Bühlmann ZH-L16-GF planner in `buhlmann.ts`.
 */

function ensureNonNegativeFinite(name: string, v: number): number {
  if (!Number.isFinite(v) || v < 0) {
    throw new Error(`${name} must be a finite, non-negative number`);
  }
  return v;
}

function ensurePositiveFinite(name: string, v: number): number {
  if (!Number.isFinite(v) || v <= 0) {
    throw new Error(`${name} must be a finite, positive number`);
  }
  return v;
}

// NOAA Diving Manual (5th ed.), Oxygen Exposure Limits Table.
// Anchor points for the single-exposure CNS clock (max minutes per PO₂ in ata).
const NOAA_SINGLE_EXPOSURE_MIN: ReadonlyArray<readonly [number, number]> = [
  [0.6, 720],
  [0.7, 570],
  [0.8, 450],
  [0.9, 360],
  [1.0, 300],
  [1.1, 240],
  [1.2, 210],
  [1.3, 180],
  [1.4, 150],
  [1.5, 120],
  [1.6, 45],
];

const NOAA_DAILY_MAX_MIN: ReadonlyArray<readonly [number, number]> = [
  [0.6, 720],
  [0.7, 570],
  [0.8, 450],
  [0.9, 360],
  [1.0, 300],
  [1.1, 270],
  [1.2, 240],
  [1.3, 210],
  [1.4, 180],
  [1.5, 150],
  [1.6, 150],
];

function lookupNoaaMinutes(
  table: ReadonlyArray<readonly [number, number]>,
  po2_ata: number
): number {
  if (po2_ata <= table[0][0]) return table[0][1];
  if (po2_ata >= table[table.length - 1][0]) {
    return table[table.length - 1][1];
  }
  for (let i = 0; i < table.length - 1; i++) {
    const [p0, t0] = table[i];
    const [p1, t1] = table[i + 1];
    if (po2_ata >= p0 && po2_ata <= p1) {
      const frac = (po2_ata - p0) / (p1 - p0);
      return t0 + frac * (t1 - t0);
    }
  }
  return table[table.length - 1][1];
}

export interface NoaaCnsResult {
  po2_ata: number;
  exposure_minutes: number;
  single_exposure_max_min: number;
  daily_max_min: number;
  /** Fraction of the single-exposure CNS clock consumed (0–1+). */
  single_exposure_fraction: number;
  /** Fraction of the 24-hour CNS clock consumed (0–1+). */
  daily_fraction: number;
}

/**
 * NOAA Oxygen Exposure Limits CNS clock.
 *
 * Returns the consumed fractions of the single-exposure and 24-hour CNS
 * limits for a continuous exposure at PO₂ for the given duration. PO₂ ≤ 0.5
 * ata is considered safe (zero-dose by NOAA convention).
 */
export function cnsToxicityFraction(args: {
  /** Inspired oxygen partial pressure, ata. */
  po2_ata: number;
  /** Duration of the continuous exposure, minutes. */
  exposure_minutes: number;
}): NoaaCnsResult {
  const po2 = ensureNonNegativeFinite('po2_ata', args.po2_ata);
  const t = ensureNonNegativeFinite('exposure_minutes', args.exposure_minutes);
  if (po2 < 0.5) {
    return {
      po2_ata: po2,
      exposure_minutes: t,
      single_exposure_max_min: Infinity,
      daily_max_min: Infinity,
      single_exposure_fraction: 0,
      daily_fraction: 0,
    };
  }
  const singleMax = lookupNoaaMinutes(NOAA_SINGLE_EXPOSURE_MIN, po2);
  const dailyMax = lookupNoaaMinutes(NOAA_DAILY_MAX_MIN, po2);
  return {
    po2_ata: po2,
    exposure_minutes: t,
    single_exposure_max_min: singleMax,
    daily_max_min: dailyMax,
    single_exposure_fraction: singleMax > 0 ? t / singleMax : Infinity,
    daily_fraction: dailyMax > 0 ? t / dailyMax : Infinity,
  };
}

/**
 * Pulmonary OTU / UPTD per Bardin & Lambertsen (1970).
 *
 *   OTU = t · ((PO₂ − 0.5) / 0.5)^0.83   for PO₂ > 0.5 ata
 *   OTU = 0                              for PO₂ ≤ 0.5
 *
 * Daily-mission guidance:
 *   ≤ 300 OTU — single-exposure recreational ceiling
 *   ≤ 600 OTU/day — typical operational ceiling
 *   > 1000 OTU — symptomatic risk increases sharply
 */
export function pulmonaryOTU(args: {
  /** Inspired oxygen partial pressure, ata. */
  po2_ata: number;
  /** Exposure duration, minutes. */
  exposure_minutes: number;
}): number {
  const po2 = ensureNonNegativeFinite('po2_ata', args.po2_ata);
  const t = ensureNonNegativeFinite('exposure_minutes', args.exposure_minutes);
  if (po2 <= 0.5) return 0;
  return t * Math.pow((po2 - 0.5) / 0.5, 0.83);
}

/** Sum OTU contributions across multiple constant-PO₂ exposure segments. */
export function totalPulmonaryOTU(
  segments: { po2_ata: number; exposure_minutes: number }[]
): number {
  let sum = 0;
  for (const s of segments) sum += pulmonaryOTU(s);
  return sum;
}

export interface ArieliPowerResult {
  /** CNS toxicity index. */
  k_cns: number;
  /** Pulmonary toxicity index. */
  k_pot: number;
  po2_kpa: number;
  exposure_minutes: number;
}

/**
 * Arieli et al. (2002) Power Equation toxicity indices.
 *
 *   K_CNS  = (t/60)² · (PO₂_kPa / 100)^6.8
 *   K_POT  = (t/60)² · (PO₂_kPa / 100)^4.57
 *
 * Provide PO₂ in kPa (1 ata ≈ 101.325 kPa). The function also accepts an
 * `po2_ata` for convenience.
 */
export function arieliPowerEquation(args: {
  exposure_minutes: number;
  po2_ata?: number;
  po2_kpa?: number;
}): ArieliPowerResult {
  const t = ensurePositiveFinite('exposure_minutes', args.exposure_minutes);
  let po2_kpa: number;
  if (args.po2_kpa !== undefined) {
    po2_kpa = ensurePositiveFinite('po2_kpa', args.po2_kpa);
  } else if (args.po2_ata !== undefined) {
    po2_kpa = ensurePositiveFinite('po2_ata', args.po2_ata) * 101.325;
  } else {
    throw new Error('Provide either po2_ata or po2_kpa');
  }
  const tHours = t / 60;
  const ratio = po2_kpa / 100;
  return {
    k_cns: tHours * tHours * Math.pow(ratio, 6.8),
    k_pot: tHours * tHours * Math.pow(ratio, 4.57),
    po2_kpa,
    exposure_minutes: t,
  };
}
