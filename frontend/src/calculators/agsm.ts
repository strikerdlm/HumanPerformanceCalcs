/**
 * Anti-G Straining Maneuver (AGSM) effectiveness model.
 *
 * Deterministic, parameterized estimate of +Gz tolerance contributions from
 * anti-G suit (AGS), positive pressure breathing for G (PBG), and AGSM quality.
 *
 * Default deltas anchored to PubMed 17484342 (representative tolerance levels
 * by configuration during rapid-onset +Gz profiles):
 *   I   relaxed, no garment           ~3.4 Gz
 *   II  relaxed + AGS                 ≥6.5 Gz   →  Δ_suit ≈ 3.1
 *   III AGS + PBG                     ≥8.0 Gz   →  Δ_pbg  ≈ 1.5 (beyond suit)
 *   IV  AGS + AGSM                    ≥8.9 Gz   →  Δ_agsm ≈ 2.4 (beyond suit, full quality)
 *   V   AGS + PBG + AGSM              ≥9.0 Gz   (system cap / saturation)
 *
 * NOT an operational flight safety tool. Individual tolerance varies with
 * hydration, fatigue, illness, posture, onset rate, seat tilt, equipment fit,
 * and training status.
 */

export const AGSM_DEFAULT_BASELINE_RELAXED_GZ = 3.4;
export const AGSM_DEFAULT_MAX_SYSTEM_GZ = 9.0;
export const AGSM_DEFAULT_SUIT_DELTA_GZ = 6.5 - 3.4; // 3.1
export const AGSM_DEFAULT_PBG_DELTA_GZ = 8.0 - 6.5; // 1.5
export const AGSM_DEFAULT_AGSM_DELTA_GZ = 8.9 - 6.5; // 2.4

export interface AgsmInputs {
  /** Baseline +Gz tolerance under relaxed posture, no protection. */
  baseline_relaxed_gz?: number;
  anti_g_suit?: boolean;
  pressure_breathing_for_g?: boolean;
  /** AGSM quality factor in [0, 1]. 1 = optimal technique. */
  agsm_quality?: number;
  suit_delta_gz?: number;
  pbg_delta_gz?: number;
  agsm_delta_gz?: number;
  max_system_gz?: number;
}

export interface AgsmResult {
  baseline_relaxed_gz: number;
  suit_component_gz: number;
  pbg_component_gz: number;
  agsm_component_gz: number;
  raw_estimated_gz: number;
  capped_estimated_gz: number;
  was_capped: boolean;
}

/**
 * Estimate +Gz tolerance with AGS / PBG / AGSM components.
 *
 * Components:
 *   total = baseline + (AGS ? Δ_suit : 0) + (AGS && PBG ? Δ_pbg : 0)
 *         + (AGS && quality > 0 ? Δ_agsm × quality : 0)
 *   capped = min(total, max_system_gz)
 */
export function estimateGzToleranceWithAgsm(inputs: AgsmInputs = {}): AgsmResult {
  const baseline = inputs.baseline_relaxed_gz ?? AGSM_DEFAULT_BASELINE_RELAXED_GZ;
  if (!(baseline > 0)) {
    throw new Error('baseline_relaxed_gz must be > 0');
  }

  const suitDelta = inputs.suit_delta_gz ?? AGSM_DEFAULT_SUIT_DELTA_GZ;
  const pbgDelta = inputs.pbg_delta_gz ?? AGSM_DEFAULT_PBG_DELTA_GZ;
  const agsmDelta = inputs.agsm_delta_gz ?? AGSM_DEFAULT_AGSM_DELTA_GZ;
  if (suitDelta < 0 || pbgDelta < 0 || agsmDelta < 0) {
    throw new Error('Delta values must be >= 0');
  }

  const quality = inputs.agsm_quality ?? 1.0;
  if (quality < 0 || quality > 1) {
    throw new Error('agsm_quality must be within [0, 1]');
  }

  const maxGz = inputs.max_system_gz ?? AGSM_DEFAULT_MAX_SYSTEM_GZ;
  if (!(maxGz > 0)) {
    throw new Error('max_system_gz must be > 0');
  }

  const useSuit = inputs.anti_g_suit ?? true;
  const usePbg = inputs.pressure_breathing_for_g ?? false;

  const suitComponent = useSuit ? suitDelta : 0;
  const pbgComponent = useSuit && usePbg ? pbgDelta : 0;
  const agsmComponent = useSuit && quality > 0 ? agsmDelta * quality : 0;

  const raw = baseline + suitComponent + pbgComponent + agsmComponent;
  const capped = Math.min(raw, maxGz);

  return {
    baseline_relaxed_gz: baseline,
    suit_component_gz: suitComponent,
    pbg_component_gz: pbgComponent,
    agsm_component_gz: agsmComponent,
    raw_estimated_gz: raw,
    capped_estimated_gz: capped,
    was_capped: capped < raw,
  };
}
