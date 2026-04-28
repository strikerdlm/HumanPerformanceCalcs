/**
 * Sleep / sleepiness questionnaires with published scoring rules.
 *
 *   Karolinska Sleepiness Scale (KSS) — single 1–9 item (Åkerstedt & Gillberg 1990)
 *   Epworth Sleepiness Scale (ESS)    — 8 situations × 0–3 (Johns 1991)
 *   Pittsburgh Sleep Quality Index (PSQI) — 7 components × 0–3 (Buysse 1989)
 *
 * References:
 *   Åkerstedt T., Gillberg M. (1990). Subjective and objective sleepiness in the
 *     active individual. Int. J. Neurosci. 52:29–37.
 *   Johns M.W. (1991). A new method for measuring daytime sleepiness: the
 *     Epworth Sleepiness Scale. Sleep 14:540–545. https://doi.org/10.1093/sleep/14.6.540
 *   Buysse D.J., Reynolds C.F. III, Monk T.H., Berman S.R., Kupfer D.J. (1989).
 *     The Pittsburgh Sleep Quality Index: a new instrument for psychiatric
 *     practice and research. Psychiatry Res. 28:193–213.
 *     https://doi.org/10.1016/0165-1781(89)90047-4
 *
 * SCOPE: research/education. PSQI implementation accepts the seven precomputed
 * component scores rather than the 19 raw questionnaire items, so callers must
 * derive components per the Buysse 1989 scoring manual.
 */

// ─── KSS ────────────────────────────────────────────────────────────────

export type KssLevel = 'alert' | 'neutral' | 'sleepy' | 'very_sleepy' | 'extreme';

export interface KssResult {
  score: number;
  level: KssLevel;
  description: string;
}

const KSS_DESCRIPTIONS: Record<number, string> = {
  1: 'Extremely alert',
  2: 'Very alert',
  3: 'Alert',
  4: 'Rather alert',
  5: 'Neither alert nor sleepy',
  6: 'Some signs of sleepiness',
  7: 'Sleepy, but no effort to stay awake',
  8: 'Sleepy, some effort to stay awake',
  9: 'Very sleepy, great effort to stay awake, fighting sleep',
};

/** Karolinska Sleepiness Scale interpretation (1–9 single-item scale). */
export function kssScoreInterpret(score: number): KssResult {
  if (!Number.isInteger(score) || score < 1 || score > 9) {
    throw new Error('KSS score must be an integer in [1, 9]');
  }
  let level: KssLevel;
  if (score <= 3) level = 'alert';
  else if (score <= 5) level = 'neutral';
  else if (score <= 7) level = 'sleepy';
  else if (score === 8) level = 'very_sleepy';
  else level = 'extreme';
  return { score, level, description: KSS_DESCRIPTIONS[score] };
}

// ─── Epworth Sleepiness Scale ───────────────────────────────────────────

export type EpworthCategory = 'normal' | 'mild' | 'moderate' | 'severe';

export interface EpworthResult {
  total: number;
  category: EpworthCategory;
  description: string;
}

/**
 * Epworth Sleepiness Scale total — 8 items, each scored 0 (no chance of
 * dozing) – 3 (high chance of dozing).
 *
 * Categories (Johns 1991 + later Sleep journal updates):
 *   0–7  normal
 *   8–9  mild (borderline) excessive daytime sleepiness
 *   10–15 moderate excessive daytime sleepiness
 *   16–24 severe excessive daytime sleepiness
 */
export function epworthScore(items: number[]): EpworthResult {
  if (items.length !== 8) {
    throw new Error('Epworth Sleepiness Scale requires exactly 8 items');
  }
  let total = 0;
  for (const v of items) {
    if (!Number.isInteger(v) || v < 0 || v > 3) {
      throw new Error('Each Epworth item must be an integer in [0, 3]');
    }
    total += v;
  }
  let category: EpworthCategory;
  let description: string;
  if (total <= 7) {
    category = 'normal';
    description = 'Normal range; no excessive daytime sleepiness';
  } else if (total <= 9) {
    category = 'mild';
    description = 'Borderline / mild excessive daytime sleepiness';
  } else if (total <= 15) {
    category = 'moderate';
    description = 'Moderate excessive daytime sleepiness; medical evaluation suggested';
  } else {
    category = 'severe';
    description = 'Severe excessive daytime sleepiness; clinical evaluation recommended';
  }
  return { total, category, description };
}

// ─── PSQI ───────────────────────────────────────────────────────────────

export interface PsqiComponents {
  /** C1 — Subjective sleep quality (0–3). */
  subjective_quality: number;
  /** C2 — Sleep latency (0–3). */
  latency: number;
  /** C3 — Sleep duration (0–3). */
  duration: number;
  /** C4 — Habitual sleep efficiency (0–3). */
  efficiency: number;
  /** C5 — Sleep disturbances (0–3). */
  disturbances: number;
  /** C6 — Use of sleeping medication (0–3). */
  medication: number;
  /** C7 — Daytime dysfunction (0–3). */
  daytime_dysfunction: number;
}

export type PsqiCategory = 'good_sleeper' | 'poor_sleeper';

export interface PsqiResult {
  global_score: number;
  category: PsqiCategory;
  components: PsqiComponents;
}

function ensureComponentScore(name: string, v: number): number {
  if (!Number.isInteger(v) || v < 0 || v > 3) {
    throw new Error(`${name} must be an integer in [0, 3]`);
  }
  return v;
}

/**
 * Pittsburgh Sleep Quality Index global score (sum of seven 0–3 components).
 *
 * Cutoff (Buysse 1989, validated repeatedly): global score > 5 ≡ "poor
 * sleeper" with sensitivity 89.6% and specificity 86.5% in the original
 * validation cohort.
 */
export function psqiScore(components: PsqiComponents): PsqiResult {
  const c1 = ensureComponentScore('subjective_quality', components.subjective_quality);
  const c2 = ensureComponentScore('latency', components.latency);
  const c3 = ensureComponentScore('duration', components.duration);
  const c4 = ensureComponentScore('efficiency', components.efficiency);
  const c5 = ensureComponentScore('disturbances', components.disturbances);
  const c6 = ensureComponentScore('medication', components.medication);
  const c7 = ensureComponentScore('daytime_dysfunction', components.daytime_dysfunction);
  const total = c1 + c2 + c3 + c4 + c5 + c6 + c7;
  return {
    global_score: total,
    category: total > 5 ? 'poor_sleeper' : 'good_sleeper',
    components,
  };
}
