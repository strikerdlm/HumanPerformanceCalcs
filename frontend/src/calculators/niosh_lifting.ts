/**
 * Revised NIOSH Lifting Equation (Waters et al., 1993).
 *
 * Recommended Weight Limit (RWL), Lifting Index (LI), and a single-task
 * approximation of the Composite Lifting Index (CLI) for multi-task jobs.
 *
 *   RWL = LC · HM · VM · DM · AM · FM · CM
 *
 * All inputs and the load constant are metric:
 *   LC  = 23 kg
 *   HM  = 25 / H        (H in cm; HM=1 if H≤25, HM=0 if H>63)
 *   VM  = 1 − 0.003·|V−75|   (V in cm; VM=0 if V>175)
 *   DM  = 0.82 + 4.5/D       (D in cm; DM=1 if D<25, DM=0 if D>175)
 *   AM  = 1 − 0.0032·A       (A in degrees; AM=0 if A>135)
 *   FM  = lookup table (frequency, vertical region, work duration)
 *   CM  = lookup (coupling × vertical region)
 *
 * Reference:
 *   Waters, T.R., Putz-Anderson, V., Garg, A. (1993). Applications Manual
 *   for the Revised NIOSH Lifting Equation. NIOSH Pub. 94-110.
 *   https://www.cdc.gov/niosh/docs/94-110/default.html
 *
 * SCOPE: research/education. The CLI helper here implements the simplified
 * NIOSH 94-110 ranking sum. For complex job-rotation analyses, a full
 * task-decomposition tool (e.g. NIOSH ErgoMate) should be used.
 */

export type WorkDuration = 'short' | 'moderate' | 'long'; // ≤1 h | ≤2 h | ≤8 h
export type CouplingQuality = 'good' | 'fair' | 'poor';

export interface NioshLiftInputs {
  /** Load lifted, kg. */
  load_kg: number;
  /** Horizontal distance H from ankles to hands at lift origin/destination, cm. */
  horizontal_cm: number;
  /** Vertical height V of the hands at lift origin/destination, cm. */
  vertical_cm: number;
  /** Vertical travel distance D between origin and destination, cm. */
  vertical_travel_cm: number;
  /** Asymmetry angle A (twist away from sagittal plane), degrees. */
  asymmetry_deg: number;
  /** Lifting frequency, lifts/min. */
  frequency_per_min: number;
  /** Work-shift duration: ≤1 h, ≤2 h, or ≤8 h. */
  duration: WorkDuration;
  /** Coupling quality of the load. */
  coupling: CouplingQuality;
}

export interface NioshLiftResult {
  rwl_kg: number;
  lifting_index: number;
  multipliers: {
    HM: number;
    VM: number;
    DM: number;
    AM: number;
    FM: number;
    CM: number;
  };
  category: 'low' | 'moderate' | 'high' | 'very_high';
}

const LC_KG = 23.0;

function ensurePositive(name: string, v: number): number {
  if (!Number.isFinite(v) || v <= 0) {
    throw new Error(`${name} must be a finite, positive number`);
  }
  return v;
}

function ensureNonNegative(name: string, v: number): number {
  if (!Number.isFinite(v) || v < 0) {
    throw new Error(`${name} must be a finite, non-negative number`);
  }
  return v;
}

function horizontalMultiplier(H_cm: number): number {
  if (H_cm <= 25) return 1.0;
  if (H_cm > 63) return 0.0;
  return 25.0 / H_cm;
}

function verticalMultiplier(V_cm: number): number {
  if (V_cm > 175) return 0.0;
  return 1.0 - 0.003 * Math.abs(V_cm - 75);
}

function distanceMultiplier(D_cm: number): number {
  if (D_cm < 25) return 1.0;
  if (D_cm > 175) return 0.0;
  return 0.82 + 4.5 / D_cm;
}

function asymmetryMultiplier(A_deg: number): number {
  if (A_deg > 135) return 0.0;
  return 1.0 - 0.0032 * A_deg;
}

function couplingMultiplier(coupling: CouplingQuality, V_cm: number): number {
  const vHigh = V_cm >= 75;
  switch (coupling) {
    case 'good':
      return 1.0;
    case 'fair':
      return vHigh ? 1.0 : 0.95;
    case 'poor':
      return 0.9;
  }
}

// NIOSH 94-110 Table 5: Frequency Multiplier (FM)
// Rows: lifts/min. Columns: [V<75, V≥75] for each duration.
// Frequencies above 15/min set FM=0 in all bins.
const FM_TABLE: ReadonlyArray<{
  freq: number;
  short: [number, number];
  moderate: [number, number];
  long: [number, number];
}> = [
  { freq: 0.2, short: [1.0, 1.0], moderate: [0.95, 0.95], long: [0.85, 0.85] },
  { freq: 0.5, short: [0.97, 0.97], moderate: [0.92, 0.92], long: [0.81, 0.81] },
  { freq: 1, short: [0.94, 0.94], moderate: [0.88, 0.88], long: [0.75, 0.75] },
  { freq: 2, short: [0.91, 0.91], moderate: [0.84, 0.84], long: [0.65, 0.65] },
  { freq: 3, short: [0.88, 0.88], moderate: [0.79, 0.79], long: [0.55, 0.55] },
  { freq: 4, short: [0.84, 0.84], moderate: [0.72, 0.72], long: [0.45, 0.45] },
  { freq: 5, short: [0.8, 0.8], moderate: [0.6, 0.6], long: [0.35, 0.35] },
  { freq: 6, short: [0.75, 0.75], moderate: [0.5, 0.5], long: [0.27, 0.27] },
  { freq: 7, short: [0.7, 0.7], moderate: [0.42, 0.42], long: [0.22, 0.22] },
  { freq: 8, short: [0.6, 0.6], moderate: [0.35, 0.35], long: [0.18, 0.18] },
  { freq: 9, short: [0.52, 0.52], moderate: [0.3, 0.3], long: [0.0, 0.15] },
  { freq: 10, short: [0.45, 0.45], moderate: [0.26, 0.26], long: [0.0, 0.13] },
  { freq: 11, short: [0.41, 0.41], moderate: [0.0, 0.23], long: [0.0, 0.0] },
  { freq: 12, short: [0.37, 0.37], moderate: [0.0, 0.21], long: [0.0, 0.0] },
  { freq: 13, short: [0.0, 0.34], moderate: [0.0, 0.0], long: [0.0, 0.0] },
  { freq: 14, short: [0.0, 0.31], moderate: [0.0, 0.0], long: [0.0, 0.0] },
  { freq: 15, short: [0.0, 0.28], moderate: [0.0, 0.0], long: [0.0, 0.0] },
];

function frequencyMultiplier(
  frequency_per_min: number,
  V_cm: number,
  duration: WorkDuration
): number {
  const f = ensureNonNegative('frequency_per_min', frequency_per_min);
  if (f > 15) return 0.0;
  const vIdx = V_cm >= 75 ? 1 : 0;

  // Use the row at the largest tabulated frequency ≤ f (NIOSH AM 94-110
  // recommends rounding up to the next tabulated frequency for safety).
  let chosen = FM_TABLE[0];
  for (const row of FM_TABLE) {
    if (row.freq <= f + 1e-9) chosen = row;
    else break;
  }
  // For very low frequencies (<0.2/min) NIOSH uses the 0.2 row.
  return chosen[duration][vIdx];
}

/**
 * Compute the Recommended Weight Limit (kg) and Lifting Index (LI = load / RWL)
 * for a single-task lift.
 */
export function recommendedWeightLimit(inputs: NioshLiftInputs): NioshLiftResult {
  ensurePositive('load_kg', inputs.load_kg);
  ensureNonNegative('horizontal_cm', inputs.horizontal_cm);
  ensureNonNegative('vertical_cm', inputs.vertical_cm);
  ensureNonNegative('vertical_travel_cm', inputs.vertical_travel_cm);
  ensureNonNegative('asymmetry_deg', inputs.asymmetry_deg);

  const HM = horizontalMultiplier(inputs.horizontal_cm);
  const VM = verticalMultiplier(inputs.vertical_cm);
  const DM = distanceMultiplier(inputs.vertical_travel_cm);
  const AM = asymmetryMultiplier(inputs.asymmetry_deg);
  const FM = frequencyMultiplier(inputs.frequency_per_min, inputs.vertical_cm, inputs.duration);
  const CM = couplingMultiplier(inputs.coupling, inputs.vertical_cm);

  const rwl = LC_KG * HM * VM * DM * AM * FM * CM;
  const li = rwl > 0 ? inputs.load_kg / rwl : Infinity;

  let category: NioshLiftResult['category'];
  if (li <= 1.0) category = 'low';
  else if (li <= 2.0) category = 'moderate';
  else if (li <= 3.0) category = 'high';
  else category = 'very_high';

  return {
    rwl_kg: rwl,
    lifting_index: li,
    multipliers: { HM, VM, DM, AM, FM, CM },
    category,
  };
}

/** Lifting Index given a load and a precomputed RWL. */
export function liftingIndex(load_kg: number, rwl_kg: number): number {
  ensurePositive('load_kg', load_kg);
  if (rwl_kg <= 0) return Infinity;
  return load_kg / rwl_kg;
}

/**
 * Composite Lifting Index for a multi-task job.
 *
 * Implements the NIOSH 94-110 simplified ranking-sum:
 *   1) Compute the Frequency-Independent Lifting Index (FILI = load/FIRWL)
 *      and Single-Task Lifting Index (STLI = load/STRWL) for each task.
 *   2) Sort tasks by descending FILI.
 *   3) CLI = STLI₁ + Σ_{i≥2} FILIᵢ · ( 1/FM(Σ_{k≤i}fₖ) − 1/FM(Σ_{k<i}fₖ) )
 *
 * Each task's frequency contributes additively to the cumulative FM lookup at
 * the vertical region and duration of the highest-FILI task.
 */
export function compositeLiftingIndex(tasks: NioshLiftInputs[]): {
  cli: number;
  per_task: { stli: number; fili: number; rwl_kg: number; firwl_kg: number }[];
} {
  if (tasks.length === 0) {
    throw new Error('compositeLiftingIndex requires at least one task');
  }

  const perTask = tasks.map((task) => {
    const result = recommendedWeightLimit(task);
    const FM = result.multipliers.FM;
    const firwl = FM > 0 ? result.rwl_kg / FM : 0;
    const stli = result.lifting_index;
    const fili = firwl > 0 ? task.load_kg / firwl : Infinity;
    return { task, stli, fili, rwl_kg: result.rwl_kg, firwl_kg: firwl };
  });

  // Sort by FILI descending.
  perTask.sort((a, b) => b.fili - a.fili);

  // The "anchor" task sets the V region and duration for cumulative-FM lookup.
  const anchor = perTask[0].task;

  let cumulativeFreq = anchor.frequency_per_min;
  let cli = perTask[0].stli;

  for (let i = 1; i < perTask.length; i++) {
    const taskI = perTask[i].task;
    const fmBefore = frequencyMultiplier(cumulativeFreq, anchor.vertical_cm, anchor.duration);
    cumulativeFreq += taskI.frequency_per_min;
    const fmAfter = frequencyMultiplier(cumulativeFreq, anchor.vertical_cm, anchor.duration);
    const invDelta = (fmAfter > 0 ? 1.0 / fmAfter : Infinity) - (fmBefore > 0 ? 1.0 / fmBefore : Infinity);
    cli += perTask[i].fili * invDelta;
  }

  return { cli, per_task: perTask.map(({ stli, fili, rwl_kg, firwl_kg }) => ({ stli, fili, rwl_kg, firwl_kg })) };
}

export const NIOSH_LOAD_CONSTANT_KG = LC_KG;
