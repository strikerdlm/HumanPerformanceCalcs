/**
 * Heat acclimatization scheduling and ACGIH TLV work-rest tables.
 *
 * Includes:
 *   - nioshHeatAcclimatizationDays  : NIOSH 2016-106 incremental schedule
 *                                     (20% on day 1 + 20%/day for new
 *                                     workers; 50% on day 1 + 20%/day for
 *                                     experienced workers returning after
 *                                     >7 days off heat)
 *   - acgihTlvWbgt                  : ACGIH 2024 TLV WBGT criterion (°C)
 *                                     by metabolic class × acclimatization
 *                                     × work-rest fraction
 *   - wbgtWorkRestRatio             : recommended hourly work-fraction at a
 *                                     given measured WBGT
 *
 * References:
 *   NIOSH (2016). Criteria for a Recommended Standard: Occupational
 *     Exposure to Heat and Hot Environments (Pub. 2016-106).
 *     https://www.cdc.gov/niosh/docs/2016-106/
 *   ACGIH (2024). TLVs and BEIs — Heat Stress and Strain.
 *
 * SCOPE: research/education. Site-specific medical and engineering controls
 * still apply.
 */

export type MetabolicClass = 'light' | 'moderate' | 'heavy' | 'very_heavy';
export type AcclimatizationStatus = 'acclimatized' | 'unacclimatized';

/**
 * NIOSH heat-acclimatization schedule.
 *
 *   New worker:        20% exposure on day 1, +20% each day → full at day 5.
 *   Experienced (≥7d off heat): 50% on day 1, 60% / 80% / 100% on days 2–4.
 *
 * Returns the recommended fraction of full-shift exposure for `day_index`.
 */
export function nioshHeatAcclimatizationDays(args: {
  /** 1-indexed day in the acclimatization period. */
  day_index: number;
  /** Whether the worker is new to heat or returning after >7 days off heat. */
  worker_status: 'new' | 'returning';
}): number {
  if (!Number.isInteger(args.day_index) || args.day_index < 1) {
    throw new Error('day_index must be a positive integer');
  }
  if (args.worker_status !== 'new' && args.worker_status !== 'returning') {
    throw new Error("worker_status must be 'new' or 'returning'");
  }

  if (args.worker_status === 'new') {
    if (args.day_index >= 5) return 1.0;
    return 0.2 * args.day_index;
  }
  // Returning: 0.5, 0.6, 0.8, 1.0
  const sched = [0.5, 0.6, 0.8, 1.0];
  if (args.day_index >= 4) return 1.0;
  return sched[args.day_index - 1];
}

// ACGIH 2024 TLV WBGT criteria (°C) by acclimatization × work-rest fraction
// × metabolic class. Values are the WBGT at which work should not continue
// for the given regime.
//
// Source: ACGIH TLVs & BEIs Heat Stress documentation (publicly summarized).
// `very_heavy` rest-only categories are intentionally undefined where ACGIH
// does not publish a value (the cell returns null).
const TLV_WBGT_C: Record<
  AcclimatizationStatus,
  Record<'work_100' | 'rest_25' | 'rest_50' | 'rest_75', Partial<Record<MetabolicClass, number>>>
> = {
  acclimatized: {
    work_100: { light: 29.5, moderate: 27.5, heavy: 26.0 },
    rest_25: { light: 30.5, moderate: 28.5, heavy: 27.5, very_heavy: 27.5 },
    rest_50: { light: 31.5, moderate: 29.5, heavy: 28.5, very_heavy: 28.5 },
    rest_75: { light: 32.5, moderate: 31.0, heavy: 30.0, very_heavy: 30.0 },
  },
  unacclimatized: {
    work_100: { light: 27.5, moderate: 25.0, heavy: 22.5 },
    rest_25: { light: 29.0, moderate: 26.5, heavy: 24.5 },
    rest_50: { light: 30.0, moderate: 28.0, heavy: 26.5, very_heavy: 25.0 },
    rest_75: { light: 31.0, moderate: 29.0, heavy: 28.0, very_heavy: 26.5 },
  },
};

export type WorkRestRegime = 'work_100' | 'rest_25' | 'rest_50' | 'rest_75';

/**
 * ACGIH 2024 TLV WBGT criterion (°C) for a given metabolic class,
 * acclimatization status, and work-rest regime. Returns `null` when the
 * combination is not published.
 */
export function acgihTlvWbgt(args: {
  metabolic_class: MetabolicClass;
  status: AcclimatizationStatus;
  regime: WorkRestRegime;
}): number | null {
  const row = TLV_WBGT_C[args.status]?.[args.regime];
  if (!row) throw new Error(`Unknown TLV cell: ${args.status} / ${args.regime}`);
  const v = row[args.metabolic_class];
  return v === undefined ? null : v;
}

export type WorkFraction = 'work_100' | 'rest_25' | 'rest_50' | 'rest_75' | 'rest_only';

export interface WorkRestRecommendation {
  measured_wbgt_C: number;
  metabolic_class: MetabolicClass;
  status: AcclimatizationStatus;
  /** Recommended work fraction per hour at the measured WBGT. */
  recommended_regime: WorkFraction;
  /** TLV criterion for the chosen regime (°C). */
  criterion_wbgt_C: number | null;
}

/**
 * Pick the most permissive ACGIH work-rest regime whose TLV criterion is
 * still ≥ the measured WBGT. If even the 25% / 75% rest regime is exceeded,
 * the function returns `rest_only`.
 */
export function wbgtWorkRestRatio(args: {
  measured_wbgt_C: number;
  metabolic_class: MetabolicClass;
  status: AcclimatizationStatus;
}): WorkRestRecommendation {
  const wbgt = args.measured_wbgt_C;
  if (!Number.isFinite(wbgt)) {
    throw new Error('measured_wbgt_C must be a finite number');
  }
  const order: WorkRestRegime[] = ['work_100', 'rest_25', 'rest_50', 'rest_75'];
  for (const r of order) {
    const crit = acgihTlvWbgt({ metabolic_class: args.metabolic_class, status: args.status, regime: r });
    if (crit !== null && wbgt <= crit) {
      return {
        measured_wbgt_C: wbgt,
        metabolic_class: args.metabolic_class,
        status: args.status,
        recommended_regime: r,
        criterion_wbgt_C: crit,
      };
    }
  }
  return {
    measured_wbgt_C: wbgt,
    metabolic_class: args.metabolic_class,
    status: args.status,
    recommended_regime: 'rest_only',
    criterion_wbgt_C: null,
  };
}
