/**
 * Caffeine pharmacokinetics — single-compartment absorption + first-order
 * elimination, oral dose.
 *
 *   C(t) = (F · Dose · k_a) / (V_d · (k_a − k_el)) · (e^(−k_el·t) − e^(−k_a·t))
 *
 * Defaults (healthy adult, no smoking, no pregnancy):
 *   F   ≈ 0.99   (oral bioavailability)
 *   k_a ≈ 5 h⁻¹  (absorption rate constant)
 *   t½  ≈ 5 h   →  k_el = ln 2 / 5  ≈ 0.1386 h⁻¹
 *   V_d ≈ 0.5 L/kg
 *
 * Inter-individual variability is large (CYP1A2 polymorphism, smoking,
 * pregnancy, oral contraceptives). Override the defaults when a tighter
 * model is needed.
 *
 * References:
 *   Magkos F., Kavouras S.A. (2005). Caffeine use in sports, pharmacokinetics
 *     in man, and cellular mechanisms of action. Sports Med. 35:191–207.
 *   Institute of Medicine (2014). Caffeine in Food and Dietary Supplements:
 *     Examining Safety. Workshop Summary. National Academies Press.
 *
 * SCOPE: research/education. Not a substitute for clinical dosing guidance.
 */

export interface CaffeineDose {
  /** Time of the dose in hours from t=0. */
  time_h: number;
  /** Dose in mg. */
  dose_mg: number;
}

export interface CaffeineParameters {
  /** Oral bioavailability fraction F (0–1). */
  bioavailability: number;
  /** Absorption rate constant k_a (h⁻¹). */
  ka_per_h: number;
  /** Elimination half-life t½ (h). */
  half_life_h: number;
  /** Apparent volume of distribution V_d (L/kg). */
  vd_l_per_kg: number;
}

export const DEFAULT_CAFFEINE_PARAMS: CaffeineParameters = {
  bioavailability: 0.99,
  ka_per_h: 5.0,
  half_life_h: 5.0,
  vd_l_per_kg: 0.5,
};

export interface CaffeineSeries {
  time_h: number[];
  /** Plasma concentration in µg/mL (≡ mg/L). */
  concentration_ug_ml: number[];
  /** Peak concentration C_max within the simulated window. */
  cmax_ug_ml: number;
  /** Time of C_max within the simulated window. */
  tmax_h: number;
}

function ensurePositive(name: string, v: number): number {
  if (!Number.isFinite(v) || v <= 0) {
    throw new Error(`${name} must be a finite, positive number`);
  }
  return v;
}

function singleDoseConcentration(
  dose_mg: number,
  body_mass_kg: number,
  params: CaffeineParameters,
  delta_h: number
): number {
  if (delta_h < 0) return 0;
  const ka = params.ka_per_h;
  const kel = Math.LN2 / params.half_life_h;
  const Vd_L = params.vd_l_per_kg * body_mass_kg;
  if (Math.abs(ka - kel) < 1e-9) {
    // Degenerate ka == kel : C = (F·D·ka·t·e^(−ka·t)) / Vd
    return ((params.bioavailability * dose_mg * ka * delta_h) / Vd_L) * Math.exp(-ka * delta_h);
  }
  const numerator = params.bioavailability * dose_mg * ka;
  const denominator = Vd_L * (ka - kel);
  // mg/L == µg/mL.
  return (numerator / denominator) * (Math.exp(-kel * delta_h) - Math.exp(-ka * delta_h));
}

/**
 * Simulate plasma caffeine concentration over a fixed time grid (µg/mL).
 *
 * Multiple oral doses are superposed (single-compartment model is linear).
 */
export function caffeinePharmacokinetics(args: {
  doses: CaffeineDose[];
  body_mass_kg: number;
  horizon_h: number;
  step_h?: number;
  params?: Partial<CaffeineParameters>;
}): CaffeineSeries {
  if (args.doses.length === 0) {
    throw new Error('At least one CaffeineDose is required');
  }
  ensurePositive('body_mass_kg', args.body_mass_kg);
  const horizon = ensurePositive('horizon_h', args.horizon_h);
  const step = ensurePositive('step_h', args.step_h ?? 0.25);
  if (step > horizon) {
    throw new Error('step_h must be <= horizon_h');
  }

  const params: CaffeineParameters = {
    bioavailability: args.params?.bioavailability ?? DEFAULT_CAFFEINE_PARAMS.bioavailability,
    ka_per_h: args.params?.ka_per_h ?? DEFAULT_CAFFEINE_PARAMS.ka_per_h,
    half_life_h: args.params?.half_life_h ?? DEFAULT_CAFFEINE_PARAMS.half_life_h,
    vd_l_per_kg: args.params?.vd_l_per_kg ?? DEFAULT_CAFFEINE_PARAMS.vd_l_per_kg,
  };
  if (params.bioavailability <= 0 || params.bioavailability > 1) {
    throw new Error('bioavailability must be in (0, 1]');
  }
  ensurePositive('ka_per_h', params.ka_per_h);
  ensurePositive('half_life_h', params.half_life_h);
  ensurePositive('vd_l_per_kg', params.vd_l_per_kg);

  for (const d of args.doses) {
    if (!Number.isFinite(d.time_h) || d.time_h < 0) {
      throw new Error('CaffeineDose.time_h must be a finite, non-negative number');
    }
    ensurePositive('CaffeineDose.dose_mg', d.dose_mg);
  }

  const times: number[] = [];
  const concentrations: number[] = [];
  let cmax = 0;
  let tmax = 0;

  for (let t = 0; t <= horizon + 1e-9; t += step) {
    let c = 0;
    for (const dose of args.doses) {
      const dt = t - dose.time_h;
      if (dt >= 0) c += singleDoseConcentration(dose.dose_mg, args.body_mass_kg, params, dt);
    }
    times.push(t);
    concentrations.push(c);
    if (c > cmax) {
      cmax = c;
      tmax = t;
    }
  }

  return {
    time_h: times,
    concentration_ug_ml: concentrations,
    cmax_ug_ml: cmax,
    tmax_h: tmax,
  };
}

/** Steady-state plasma concentration after repeated dosing every τ hours. */
export function caffeineSteadyState(args: {
  dose_mg_per_interval: number;
  interval_h: number;
  body_mass_kg: number;
  params?: Partial<CaffeineParameters>;
}): { c_avg_ug_ml: number; c_max_ss_ug_ml: number; c_min_ss_ug_ml: number } {
  ensurePositive('dose_mg_per_interval', args.dose_mg_per_interval);
  const tau = ensurePositive('interval_h', args.interval_h);
  ensurePositive('body_mass_kg', args.body_mass_kg);

  const params: CaffeineParameters = {
    bioavailability: args.params?.bioavailability ?? DEFAULT_CAFFEINE_PARAMS.bioavailability,
    ka_per_h: args.params?.ka_per_h ?? DEFAULT_CAFFEINE_PARAMS.ka_per_h,
    half_life_h: args.params?.half_life_h ?? DEFAULT_CAFFEINE_PARAMS.half_life_h,
    vd_l_per_kg: args.params?.vd_l_per_kg ?? DEFAULT_CAFFEINE_PARAMS.vd_l_per_kg,
  };

  const Vd_L = params.vd_l_per_kg * args.body_mass_kg;
  const kel = Math.LN2 / params.half_life_h;
  const c_avg = (params.bioavailability * args.dose_mg_per_interval) / (Vd_L * kel * tau);
  const c_max_ss = c_avg * (kel * tau) / (1 - Math.exp(-kel * tau));
  const c_min_ss = c_max_ss * Math.exp(-kel * tau);
  return { c_avg_ug_ml: c_avg, c_max_ss_ug_ml: c_max_ss, c_min_ss_ug_ml: c_min_ss };
}
