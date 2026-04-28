/**
 * Hypobaric (altitude) DCS probability — logistic model on Tissue Ratio.
 *
 * Distinct from the algorithmic Bühlmann ZH-L16-GF planner in `buhlmann.ts`.
 * This module provides a probabilistic risk estimate suitable for crew
 * exposure planning at altitude, anchored to published USAF/NASA chamber
 * data via a logistic regression on the standard supersaturation index TR.
 *
 *   logit P = β₀ + β₁ · TR + β₂ · t_min + β₃ · exercise
 *
 * `exercise` is a 0/1 flag (0 = rest, 1 = mild exercise during the exposure).
 *
 * Default coefficient sets (selectable via `model`):
 *   conkin2011  — derived from Conkin et al., NASA TM-2011-216147 (USAF
 *                 hypobaric chamber dataset, "any DCS symptoms").
 *   webb1993    — derived from Webb & Pilmanis (1993) hypobaric chamber
 *                 study, "any symptoms", time term absent.
 *
 * Coefficients are approximate fits from the published reports — they are
 * exposed as overridable defaults and should NOT be treated as operational
 * limits. For mission planning use a validated tool (e.g. NASA PSAS/EVA risk
 * model, RAF/USAF chamber decision aids).
 *
 * References:
 *   Conkin J. (2011). Evidence-Based Approach to Hypobaric Decompression
 *     Sickness Data. NASA TM-2011-216147.
 *     https://ntrs.nasa.gov/citations/20110007932
 *   Webb J.T., Pilmanis A.A. (1993). A new preoxygenation procedure for
 *     extravehicular activity (EVA). Acta Astronautica 29:781–786.
 */

export type DcsModel = 'conkin2011' | 'webb1993';

export interface DcsLogisticCoefficients {
  intercept: number;
  beta_tr: number;
  beta_time_min: number;
  beta_exercise: number;
}

export const DCS_DEFAULT_COEFFS: Record<DcsModel, DcsLogisticCoefficients> = {
  conkin2011: { intercept: -8.6, beta_tr: 4.5, beta_time_min: 0.0028, beta_exercise: 0.5 },
  webb1993: { intercept: -8.43, beta_tr: 5.16, beta_time_min: 0, beta_exercise: 0.4 },
};

export interface DcsProbabilityInputs {
  /** Tissue Ratio (PtissueN2 / Pambient at the planned altitude). */
  tissue_ratio: number;
  /** Duration at altitude, minutes. */
  exposure_minutes: number;
  /** Mild exercise during exposure (true ≈ pump-arm or simulated EVA). */
  exercise: boolean;
  /** Coefficient set; defaults to Conkin 2011. */
  model?: DcsModel;
  /** Override β coefficients explicitly (takes precedence over model). */
  coeffs?: DcsLogisticCoefficients;
}

export interface DcsProbabilityResult {
  probability: number;
  logit: number;
  model: DcsModel | 'custom';
  coeffs: DcsLogisticCoefficients;
}

function logistic(x: number): number {
  if (x >= 0) {
    const e = Math.exp(-x);
    return 1 / (1 + e);
  }
  const e = Math.exp(x);
  return e / (1 + e);
}

/**
 * Estimate the probability of any DCS symptoms during a hypobaric exposure.
 */
export function dcsProbabilityAltitude(inputs: DcsProbabilityInputs): DcsProbabilityResult {
  if (!Number.isFinite(inputs.tissue_ratio) || inputs.tissue_ratio <= 0) {
    throw new Error('tissue_ratio must be a finite, positive number');
  }
  if (!Number.isFinite(inputs.exposure_minutes) || inputs.exposure_minutes < 0) {
    throw new Error('exposure_minutes must be a finite, non-negative number');
  }
  const model = inputs.model ?? 'conkin2011';
  const coeffs: DcsLogisticCoefficients = inputs.coeffs ?? DCS_DEFAULT_COEFFS[model];
  const x_exercise = inputs.exercise ? 1 : 0;
  const logit =
    coeffs.intercept +
    coeffs.beta_tr * inputs.tissue_ratio +
    coeffs.beta_time_min * inputs.exposure_minutes +
    coeffs.beta_exercise * x_exercise;
  return {
    probability: logistic(logit),
    logit,
    model: inputs.coeffs ? 'custom' : model,
    coeffs,
  };
}

/**
 * Convenience wrapper: solve the maximum exposure time before a target DCS
 * probability is reached at constant Tissue Ratio.
 *
 * Returns null when the model is independent of time (β_time_min = 0).
 */
export function dcsTimeToProbability(args: {
  tissue_ratio: number;
  exercise: boolean;
  target_probability: number;
  model?: DcsModel;
  coeffs?: DcsLogisticCoefficients;
}): number | null {
  if (!Number.isFinite(args.tissue_ratio) || args.tissue_ratio <= 0) {
    throw new Error('tissue_ratio must be a finite, positive number');
  }
  if (!Number.isFinite(args.target_probability) || args.target_probability <= 0 || args.target_probability >= 1) {
    throw new Error('target_probability must lie in (0, 1)');
  }
  const model = args.model ?? 'conkin2011';
  const coeffs = args.coeffs ?? DCS_DEFAULT_COEFFS[model];
  if (coeffs.beta_time_min === 0) return null;

  const x_exercise = args.exercise ? 1 : 0;
  const targetLogit = Math.log(args.target_probability / (1 - args.target_probability));
  const t = (targetLogit - coeffs.intercept - coeffs.beta_tr * args.tissue_ratio - coeffs.beta_exercise * x_exercise) / coeffs.beta_time_min;
  return Math.max(0, t);
}
