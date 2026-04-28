/**
 * Cold-water immersion survival time (hypothermia-limited).
 *
 * IMPORTANT SCOPE: hypothermia-limited survival only. Does NOT model:
 *   - cold shock (first ~3–5 min)
 *   - swimming failure (typically <30 min)
 *   - drowning risk (waves, exhaustion, panic, airway loss)
 *
 * References:
 *   - Hayward, J. S., Eckerson, J. D., & Collis, M. L. (1975).
 *     Thermal balance and survival time prediction of man in cold water.
 *     J. Appl. Physiol. PMID: 1139445.
 *   - Transport Canada (2003). TP 13822 — Survival in Cold Waters,
 *     citing Golden (1996): 1h@5°C, 2h@10°C, 6h@15°C (clothed + lifejacket).
 */

export type ColdWaterSurvivalModel =
  | 'hayward_1975'
  | 'golden_lifejacket_tp13822';

export interface ColdWaterSurvivalEstimate {
  model: ColdWaterSurvivalModel;
  water_temperature_c: number;
  survival_time_minutes: number;
  /** survival_time_minutes / 60 (convenience). */
  survival_time_hours: number;
  notes: string[];
}

const HAYWARD_A = 15.0;
const HAYWARD_B = 7.2;
const HAYWARD_C = 0.0785;
const HAYWARD_D = 0.0034;

const GOLDEN_POINTS: ReadonlyArray<readonly [number, number]> = [
  [5.0, 1.0],
  [10.0, 2.0],
  [15.0, 6.0],
];

function ensureFinite(name: string, value: number): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new TypeError(`${name} must be a finite number`);
  }
  return value;
}

/**
 * Hayward (1975) survival time (minutes) from water temperature.
 *
 * t_s = 15 + 7.2 / (0.0785 − 0.0034·T_w)
 *
 * Singular near T_w ≈ 23.1°C; only valid for cold water. With strict=true,
 * enforces 0–20°C as conservative validity range.
 */
export function coldWaterSurvivalHayward1975Minutes(
  water_temperature_c: number,
  options: { strict?: boolean } = {}
): number {
  const tw = ensureFinite('water_temperature_c', water_temperature_c);
  const strict = options.strict ?? false;
  if (strict && (tw < 0 || tw > 20)) {
    throw new Error('Hayward (1975) equation should be used for 0–20°C water only');
  }
  const denom = HAYWARD_C - HAYWARD_D * tw;
  if (denom <= 0) {
    throw new Error(
      'Hayward (1975) equation undefined for this water temperature (denominator <= 0)'
    );
  }
  const minutes = HAYWARD_A + HAYWARD_B / denom;
  if (minutes <= 0) {
    throw new Error('Computed survival time is non-physical (<= 0 minutes)');
  }
  return minutes;
}

/**
 * Golden / TP 13822 survival time (hours) for fully-clothed casualty + lifejacket.
 *
 * Piecewise-linear interpolation over: 1h@5°C, 2h@10°C, 6h@15°C.
 * Outside [5,15]°C is clamped (or rejected when strict).
 */
export function coldWaterSurvivalGoldenLifejacketHours(
  water_temperature_c: number,
  options: { strict?: boolean } = {}
): number {
  const tw = ensureFinite('water_temperature_c', water_temperature_c);
  const strict = options.strict ?? false;
  const [tMin, hMin] = GOLDEN_POINTS[0];
  const [tMid, hMid] = GOLDEN_POINTS[1];
  const [tMax, hMax] = GOLDEN_POINTS[2];

  if (strict && (tw < tMin || tw > tMax)) {
    throw new Error('Golden lifejacket curve supported for 5–15°C only');
  }
  if (tw <= tMin) return hMin;
  if (tw >= tMax) return hMax;
  if (tw <= tMid) {
    const frac = (tw - tMin) / (tMid - tMin);
    return hMin + frac * (hMid - hMin);
  }
  const frac = (tw - tMid) / (tMax - tMid);
  return hMid + frac * (hMax - hMid);
}

/**
 * Combined cold-water survival estimator (model-selectable).
 */
export function coldWaterSurvival(
  water_temperature_c: number,
  options: { model?: ColdWaterSurvivalModel; strict?: boolean } = {}
): ColdWaterSurvivalEstimate {
  const model = options.model ?? 'hayward_1975';
  if (model !== 'hayward_1975' && model !== 'golden_lifejacket_tp13822') {
    throw new Error(`Unsupported model: ${model}`);
  }
  const tw = ensureFinite('water_temperature_c', water_temperature_c);
  const notes: string[] = [
    'Hypothermia-limited guidance only (does not model cold shock/swim failure/drowning risk).',
  ];

  let minutes: number;
  if (model === 'hayward_1975') {
    minutes = coldWaterSurvivalHayward1975Minutes(tw, { strict: options.strict });
    notes.push('Hayward et al. (1975) temperature-only equation.');
  } else {
    const hours = coldWaterSurvivalGoldenLifejacketHours(tw, { strict: options.strict });
    minutes = hours * 60;
    notes.push(
      'Transport Canada TP 13822 (2003) cites Golden (1996): 1h@5°C, 2h@10°C, 6h@15°C (linear interp).'
    );
  }

  return {
    model,
    water_temperature_c: tw,
    survival_time_minutes: minutes,
    survival_time_hours: minutes / 60,
    notes,
  };
}
