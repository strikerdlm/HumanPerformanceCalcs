/**
 * Bühlmann ZH-L16 decompression model with Erik Baker–style Gradient Factors.
 *
 * Deterministic, bounded engine. Implements neo-Haldanian inert gas loading via
 * the Schreiner equation and computes ascent ceilings from Bühlmann M-value
 * parameters modified by GF.
 *
 * Coefficient tables and equations cross-checked against the open DecoTengu
 * reference implementation (see https://wrobell.dcmod.org/decotengu/).
 *
 * IMPORTANT: educational/research use only. Does NOT model bubble dynamics,
 * micro-bubbles, or individual susceptibility. Validate against operational
 * procedures and professional guidance.
 */

export type BuhlmannModelVariant = 'zh-l16b-gf' | 'zh-l16c-gf';

export interface GasMix {
  /** O₂ fraction (0–1). */
  o2: number;
  /** He fraction (0–1). Default 0. */
  he?: number;
}

export interface DecompressionStop {
  depth_m: number;
  minutes: number;
}

export interface BuhlmannPlan {
  model: BuhlmannModelVariant;
  max_depth_m: number;
  bottom_time_min: number;
  gf_low: number;
  gf_high: number;
  surface_pressure_bar: number;
  stops: DecompressionStop[];
  total_decompression_minutes: number;
}

const LOG_2 = Math.log(2);
const WATER_VAPOUR_PRESSURE_BAR = 0.0627;
const METER_TO_BAR = 0.09985;

// ZH-L16B coefficients
const ZHL16B_N2_A: ReadonlyArray<number> = [
  1.1696, 1.0, 0.8618, 0.7562, 0.6667, 0.56, 0.4947, 0.45,
  0.4187, 0.3798, 0.3497, 0.3223, 0.285, 0.2737, 0.2523, 0.2327,
];
const ZHL16B_N2_B: ReadonlyArray<number> = [
  0.5578, 0.6514, 0.7222, 0.7825, 0.8126, 0.8434, 0.8693, 0.891,
  0.9092, 0.9222, 0.9319, 0.9403, 0.9477, 0.9544, 0.9602, 0.9653,
];
const ZHL16B_HE_A: ReadonlyArray<number> = [
  1.6189, 1.383, 1.1919, 1.0458, 0.922, 0.8205, 0.7305, 0.6502,
  0.595, 0.5545, 0.5333, 0.5189, 0.5181, 0.5176, 0.5172, 0.5119,
];
const ZHL16B_HE_B: ReadonlyArray<number> = [
  0.477, 0.5747, 0.6527, 0.7223, 0.7582, 0.7957, 0.8279, 0.8553,
  0.8757, 0.8903, 0.8997, 0.9073, 0.9122, 0.9171, 0.9217, 0.9267,
];
const ZHL16B_N2_HALF_MIN: ReadonlyArray<number> = [
  5.0, 8.0, 12.5, 18.5, 27.0, 38.3, 54.3, 77.0, 109.0, 146.0, 187.0, 239.0, 305.0, 390.0, 498.0, 635.0,
];
const ZHL16B_HE_HALF_MIN: ReadonlyArray<number> = [
  1.88, 3.02, 4.72, 6.99, 10.21, 14.48, 20.53, 29.11, 41.2, 55.19, 70.69, 90.34, 115.29, 147.42, 188.24, 240.03,
];

// ZH-L16C coefficients
const ZHL16C_N2_A: ReadonlyArray<number> = [
  1.2599, 1.0, 0.8618, 0.7562, 0.62, 0.5043, 0.441, 0.4,
  0.375, 0.35, 0.3295, 0.3065, 0.2835, 0.261, 0.248, 0.2327,
];
const ZHL16C_N2_B = ZHL16B_N2_B;
const ZHL16C_HE_A: ReadonlyArray<number> = [
  1.7424, 1.383, 1.1919, 1.0458, 0.922, 0.8205, 0.7305, 0.6502,
  0.595, 0.5545, 0.5333, 0.5189, 0.5181, 0.5176, 0.5172, 0.5119,
];
const ZHL16C_HE_B: ReadonlyArray<number> = [
  0.4245, 0.5747, 0.6527, 0.7223, 0.7582, 0.7957, 0.8279, 0.8553,
  0.8757, 0.8903, 0.8997, 0.9073, 0.9122, 0.9171, 0.9217, 0.9267,
];
const ZHL16C_N2_HALF_MIN: ReadonlyArray<number> = [
  4.0, 8.0, 12.5, 18.5, 27.0, 38.3, 54.3, 77.0, 109.0, 146.0, 187.0, 239.0, 305.0, 390.0, 498.0, 635.0,
];
const ZHL16C_HE_HALF_MIN: ReadonlyArray<number> = [
  1.51, 3.02, 4.72, 6.99, 10.21, 14.48, 20.53, 29.11, 41.2, 55.19, 70.69, 90.34, 115.29, 147.42, 188.24, 240.03,
];

interface ModelCoeffs {
  n2_a: ReadonlyArray<number>;
  n2_b: ReadonlyArray<number>;
  he_a: ReadonlyArray<number>;
  he_b: ReadonlyArray<number>;
  n2_half_min: ReadonlyArray<number>;
  he_half_min: ReadonlyArray<number>;
}

function coeffsForModel(model: BuhlmannModelVariant): ModelCoeffs {
  if (model === 'zh-l16b-gf') {
    return {
      n2_a: ZHL16B_N2_A,
      n2_b: ZHL16B_N2_B,
      he_a: ZHL16B_HE_A,
      he_b: ZHL16B_HE_B,
      n2_half_min: ZHL16B_N2_HALF_MIN,
      he_half_min: ZHL16B_HE_HALF_MIN,
    };
  }
  if (model === 'zh-l16c-gf') {
    return {
      n2_a: ZHL16C_N2_A,
      n2_b: ZHL16C_N2_B,
      he_a: ZHL16C_HE_A,
      he_b: ZHL16C_HE_B,
      n2_half_min: ZHL16C_N2_HALF_MIN,
      he_half_min: ZHL16C_HE_HALF_MIN,
    };
  }
  throw new Error('Unsupported model variant');
}

function gasN2(gas: GasMix): number {
  return 1 - gas.o2 - (gas.he ?? 0);
}

function validateGf(gf: number, name: string): number {
  if (!Number.isFinite(gf)) throw new Error(`${name} must be a finite number`);
  if (!(gf > 0 && gf <= 1.5)) throw new Error(`${name} must be in (0, 1.5]`);
  return gf;
}

function validateDepth(depth: number, name: string): number {
  if (!Number.isFinite(depth)) throw new Error(`${name} must be a finite number`);
  if (depth < 0) throw new Error(`${name} must be >= 0`);
  return depth;
}

function validatePressureBar(p: number, name: string): number {
  if (!Number.isFinite(p)) throw new Error(`${name} must be a finite number`);
  if (p <= 0) throw new Error(`${name} must be > 0`);
  return p;
}

function absPressureBar(depth_m: number, surface_pressure_bar: number): number {
  return surface_pressure_bar + depth_m * METER_TO_BAR;
}

function schreiner(p_i: number, p_alv: number, r: number, k: number, t: number): number {
  return p_alv + r * (t - 1.0 / k) - (p_alv - p_i - r / k) * Math.exp(-k * t);
}

function eqGfLimit(
  gf: number,
  p_n2: number,
  p_he: number,
  a_n2: number,
  b_n2: number,
  a_he: number,
  b_he: number
): number {
  const g = validateGf(gf, 'gf');
  const p = p_n2 + p_he;
  if (p <= 0) return 0;
  const a = (a_n2 * p_n2 + a_he * p_he) / p;
  const b = (b_n2 * p_n2 + b_he * p_he) / p;
  return (p - a * g) / (g / b + 1 - g);
}

function kConstants(half_times_min: ReadonlyArray<number>): number[] {
  return half_times_min.map((v) => LOG_2 / v);
}

interface TissueLoad {
  p_n2: number;
  p_he: number;
}

function tissueLoadStep(args: {
  abs_p_bar: number;
  duration_min: number;
  rate_bar_per_min: number;
  gas: GasMix;
  k_n2: ReadonlyArray<number>;
  k_he: ReadonlyArray<number>;
  tissues: ReadonlyArray<TissueLoad>;
}): TissueLoad[] {
  if (args.duration_min <= 0) throw new Error('duration_min must be > 0');

  const f_n2 = gasN2(args.gas);
  const f_he = args.gas.he ?? 0;
  if (f_n2 < 0 || f_he < 0 || args.gas.o2 < 0) {
    throw new Error('Gas fractions must be >= 0');
  }
  if (args.gas.o2 + f_he >= 1) {
    throw new Error('Invalid gas mix: o2 + he must be < 1');
  }

  const p_alv_n2 = f_n2 * (args.abs_p_bar - WATER_VAPOUR_PRESSURE_BAR);
  const p_alv_he = f_he * (args.abs_p_bar - WATER_VAPOUR_PRESSURE_BAR);
  const r_n2 = f_n2 * args.rate_bar_per_min;
  const r_he = f_he * args.rate_bar_per_min;

  const out: TissueLoad[] = [];
  for (let i = 0; i < args.tissues.length; i++) {
    const { p_n2, p_he } = args.tissues[i];
    out.push({
      p_n2: schreiner(p_n2, p_alv_n2, r_n2, args.k_n2[i], args.duration_min),
      p_he: schreiner(p_he, p_alv_he, r_he, args.k_he[i], args.duration_min),
    });
  }
  return out;
}

function ceilingLimitBar(
  gf: number,
  tissues: ReadonlyArray<TissueLoad>,
  c: ModelCoeffs
): number {
  let ceiling = 0;
  for (let i = 0; i < tissues.length; i++) {
    const lim = eqGfLimit(
      gf,
      tissues[i].p_n2,
      tissues[i].p_he,
      c.n2_a[i],
      c.n2_b[i],
      c.he_a[i],
      c.he_b[i]
    );
    if (lim > ceiling) ceiling = lim;
  }
  return ceiling;
}

export interface PlanZhL16GfOptions {
  max_depth_m: number;
  bottom_time_min: number;
  gas: GasMix;
  include_descent_in_bottom_time?: boolean;
  gf_low?: number;
  gf_high?: number;
  model?: BuhlmannModelVariant;
  surface_pressure_bar?: number;
  descent_rate_m_per_min?: number;
  ascent_rate_m_per_min?: number;
  stop_step_m?: number;
  max_stop_minutes?: number;
  max_total_runtime_minutes?: number;
}

/**
 * Plan decompression stops for a square dive profile using ZH-L16-GF.
 *
 * Profile: descent → bottom time → ascent with stops at `stop_step_m`
 * increments. Single-gas (no gas switching during ascent in this version).
 */
export function planZhL16Gf(opts: PlanZhL16GfOptions): BuhlmannPlan {
  const {
    max_depth_m,
    bottom_time_min,
    gas,
    include_descent_in_bottom_time = true,
    gf_low = 0.3,
    gf_high = 0.85,
    model = 'zh-l16c-gf',
    surface_pressure_bar = 1.01325,
    descent_rate_m_per_min = 20.0,
    ascent_rate_m_per_min = 10.0,
    stop_step_m = 3.0,
    max_stop_minutes = 240,
    max_total_runtime_minutes = 12 * 60,
  } = opts;

  const depth = validateDepth(max_depth_m, 'max_depth_m');
  if (!Number.isFinite(bottom_time_min) || bottom_time_min <= 0) {
    throw new Error('bottom_time_min must be > 0');
  }
  const sp = validatePressureBar(surface_pressure_bar, 'surface_pressure_bar');
  if (!Number.isFinite(descent_rate_m_per_min) || descent_rate_m_per_min <= 0) {
    throw new Error('descent_rate_m_per_min must be > 0');
  }
  if (!Number.isFinite(ascent_rate_m_per_min) || ascent_rate_m_per_min <= 0) {
    throw new Error('ascent_rate_m_per_min must be > 0');
  }
  if (!Number.isInteger(max_stop_minutes) || max_stop_minutes <= 0) {
    throw new Error('max_stop_minutes must be a positive int');
  }
  if (!Number.isInteger(max_total_runtime_minutes) || max_total_runtime_minutes <= 0) {
    throw new Error('max_total_runtime_minutes must be a positive int');
  }
  if (!Number.isFinite(stop_step_m) || stop_step_m <= 0) {
    throw new Error('stop_step_m must be a positive number');
  }
  const gfL = validateGf(gf_low, 'gf_low');
  const gfH = validateGf(gf_high, 'gf_high');
  if (gfH < gfL) throw new Error('gf_high must be >= gf_low');

  const coeffs = coeffsForModel(model);
  const k_n2 = kConstants(coeffs.n2_half_min);
  const k_he = kConstants(coeffs.he_half_min);

  const start_p_n2 = 0.7902 * (sp - WATER_VAPOUR_PRESSURE_BAR);
  let tissues: TissueLoad[] = Array.from({ length: 16 }, () => ({
    p_n2: start_p_n2,
    p_he: 0,
  }));

  let runtime = 0;

  // Descent
  let descent_time = 0;
  if (depth > 0) {
    descent_time = depth / descent_rate_m_per_min;
    if (descent_time > 0) {
      const rate = (depth * METER_TO_BAR) / descent_time;
      tissues = tissueLoadStep({
        abs_p_bar: absPressureBar(0, sp),
        duration_min: descent_time,
        rate_bar_per_min: rate,
        gas,
        k_n2,
        k_he,
        tissues,
      });
      runtime += descent_time;
    }
  }

  // Bottom time
  let t_depth = bottom_time_min;
  if (include_descent_in_bottom_time) {
    t_depth = Math.max(0, bottom_time_min - descent_time);
  }
  if (t_depth > 0) {
    tissues = tissueLoadStep({
      abs_p_bar: absPressureBar(depth, sp),
      duration_min: t_depth,
      rate_bar_per_min: 0,
      gas,
      k_n2,
      k_he,
      tissues,
    });
    runtime += t_depth;
  }

  const surface_bar = sp;
  const stops: DecompressionStop[] = [];
  let current_depth = depth;
  const bottom_depth = current_depth;
  const bottom_tissues: TissueLoad[] = tissues.map((t) => ({ ...t }));

  function simulateAscent(from_depth: number, to_depth: number, t0: TissueLoad[]): TissueLoad[] {
    if (to_depth >= from_depth) return t0;
    const travel = from_depth - to_depth;
    const time = travel / ascent_rate_m_per_min;
    const rate = -((travel * METER_TO_BAR) / time);
    return tissueLoadStep({
      abs_p_bar: absPressureBar(from_depth, sp),
      duration_min: time,
      rate_bar_per_min: rate,
      gas,
      k_n2,
      k_he,
      tissues: t0,
    });
  }

  function commitAscent(target_depth_m: number): void {
    const d0 = current_depth;
    const d1 = target_depth_m;
    if (d1 > d0) throw new Error('Target depth must be <= current depth for ascent');
    if (d1 === d0) return;
    const travel = d0 - d1;
    const time = travel / ascent_rate_m_per_min;
    const rate = -((travel * METER_TO_BAR) / time);
    tissues = tissueLoadStep({
      abs_p_bar: absPressureBar(d0, sp),
      duration_min: time,
      rate_bar_per_min: rate,
      gas,
      k_n2,
      k_he,
      tissues,
    });
    runtime += time;
    current_depth = d1;
  }

  // Find first stop on the stop-step grid
  let first_stop_depth_m = 0;
  let first_stop_bar = surface_bar;

  let candidate = Math.floor(bottom_depth / stop_step_m) * stop_step_m;
  if (candidate >= bottom_depth - 1e-12) {
    candidate = Math.max(0, candidate - stop_step_m);
  }

  let foundFirstStop = false;
  while (candidate > 0) {
    const tissues_at_candidate = simulateAscent(bottom_depth, candidate, bottom_tissues);
    const ceiling = ceilingLimitBar(gfL, tissues_at_candidate, coeffs);
    const next_candidate = Math.max(0, candidate - stop_step_m);
    const next_amb = absPressureBar(next_candidate, sp);

    if (next_candidate > 0 && next_amb >= ceiling - 1e-12) {
      candidate = next_candidate;
      continue;
    }

    first_stop_depth_m = candidate;
    first_stop_bar = absPressureBar(first_stop_depth_m, sp);
    tissues = tissues_at_candidate;
    const travel = bottom_depth - first_stop_depth_m;
    runtime += travel / ascent_rate_m_per_min;
    current_depth = first_stop_depth_m;
    foundFirstStop = true;
    break;
  }

  if (!foundFirstStop) {
    const ceiling_at_surface = ceilingLimitBar(gfL, bottom_tissues, coeffs);
    if (ceiling_at_surface <= surface_bar + 1e-12) {
      return {
        model,
        max_depth_m: depth,
        bottom_time_min,
        gf_low: gfL,
        gf_high: gfH,
        surface_pressure_bar: sp,
        stops: [],
        total_decompression_minutes: 0,
      };
    }
    first_stop_depth_m = stop_step_m;
    first_stop_bar = absPressureBar(first_stop_depth_m, sp);
    tissues = simulateAscent(bottom_depth, first_stop_depth_m, bottom_tissues);
    runtime += (bottom_depth - first_stop_depth_m) / ascent_rate_m_per_min;
    current_depth = first_stop_depth_m;
  }

  let total_stop_minutes = 0;
  const p_step = stop_step_m * METER_TO_BAR;
  let n_stops = Math.round((first_stop_bar - surface_bar) / p_step);
  if (n_stops <= 0) n_stops = 1;
  const gf_step = (gfH - gfL) / n_stops;

  let safetyIterations = 0;
  for (let stop_index = 0; stop_index < n_stops; stop_index++) {
    safetyIterations++;
    if (safetyIterations > 500) {
      throw new Error('Decompression planning exceeded iteration budget');
    }
    if (runtime > max_total_runtime_minutes) {
      throw new Error('Decompression planning exceeded max_total_runtime_minutes');
    }

    const next_depth = Math.max(0, current_depth - stop_step_m);
    let gf_next = gfL + gf_step * (stop_index + 1);
    if (next_depth <= 0) gf_next = gfH;
    gf_next = Math.max(gfL, Math.min(gfH, gf_next));

    let stop_minutes = 0;
    while (true) {
      if (stop_minutes >= max_stop_minutes) {
        throw new Error('Exceeded max_stop_minutes at decompression stops');
      }
      if (runtime > max_total_runtime_minutes) {
        throw new Error('Decompression planning exceeded max_total_runtime_minutes');
      }

      tissues = tissueLoadStep({
        abs_p_bar: absPressureBar(current_depth, sp),
        duration_min: 1,
        rate_bar_per_min: 0,
        gas,
        k_n2,
        k_he,
        tissues,
      });
      runtime += 1;
      stop_minutes += 1;
      total_stop_minutes += 1;

      const next_amb = absPressureBar(next_depth, sp);
      const ceiling = ceilingLimitBar(gf_next, tissues, coeffs);
      if (next_amb >= ceiling - 1e-12) break;
    }

    stops.push({ depth_m: current_depth, minutes: stop_minutes });

    if (next_depth <= 0) {
      current_depth = 0;
      break;
    }

    commitAscent(next_depth);
  }

  return {
    model,
    max_depth_m: depth,
    bottom_time_min,
    gf_low: gfL,
    gf_high: gfH,
    surface_pressure_bar: sp,
    stops,
    total_decompression_minutes: total_stop_minutes,
  };
}
