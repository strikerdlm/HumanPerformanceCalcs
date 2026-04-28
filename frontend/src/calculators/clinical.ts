/**
 * Clinical Calculators
 * 
 * References:
 * - Mifflin, M.D. et al. (1990). Am J Clin Nutr - BMR equation
 * - DuBois & DuBois (1916). Archives of Internal Medicine - BSA
 * - Levey, A.S. et al. (2009). Ann Intern Med - CKD-EPI eGFR
 * - Wells et al. (2003). NEJM - DVT score
 * - Wells et al. (2001). Ann Intern Med - PE score
 */

export interface BMRResult {
  bmr_kcal_day: number;
  formula: string;
}

export interface BSAResults {
  Mosteller: number;
  DuBois: number;
  Haycock: number;
  Boyd: number;
}

export interface EGFRResult {
  value_ml_min_1_73m2: number;
  stage: string;
  category: string;
}

export interface WellsDVTResult {
  totalPoints: number;
  threeTier: 'Low' | 'Moderate' | 'High';
  twoTier: 'Unlikely' | 'Likely';
  probability: string;
}

export interface WellsPEResult {
  totalPoints: number;
  threeTier: 'Low' | 'Moderate' | 'High';
  twoTier: 'Unlikely' | 'Likely';
  probability: string;
}

/**
 * Calculate Basal Metabolic Rate using Mifflin-St Jeor equation
 * 
 * Reference: Mifflin, M.D. et al. (1990). Am J Clin Nutr 51:241-247
 */
export function bmrMifflinStJeor(
  weight_kg: number,
  height_cm: number,
  age_years: number,
  sex: 'Male' | 'Female'
): BMRResult {
  if (weight_kg <= 0 || height_cm <= 0 || age_years <= 0) {
    throw new Error('All parameters must be positive');
  }
  
  // BMR = 10×weight(kg) + 6.25×height(cm) − 5×age(years) + s
  // s = +5 for males, −161 for females
  const s = sex === 'Male' ? 5 : -161;
  const bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years + s;
  
  return {
    bmr_kcal_day: bmr,
    formula: 'Mifflin-St Jeor (1990)',
  };
}

/**
 * Calculate Body Surface Area using multiple formulas
 * 
 * References:
 * - Mosteller, R.D. (1987). N Engl J Med 317:1098
 * - Du Bois, D. & Du Bois, E.F. (1916). Archives of Internal Medicine 17:863-871
 * - Haycock, G.B. et al. (1978). J Pediatr 93:62-66
 * - Boyd, E. (1935). The Growth of the Surface Area of the Human Body
 */
export function computeAllBSA(height_cm: number, weight_kg: number): BSAResults {
  if (height_cm <= 0 || weight_kg <= 0) {
    throw new Error('Height and weight must be positive');
  }
  
  // Mosteller: BSA = √((height×weight)/3600)
  const mosteller = Math.sqrt((height_cm * weight_kg) / 3600);
  
  // DuBois: BSA = 0.007184 × height^0.725 × weight^0.425
  const dubois = 0.007184 * Math.pow(height_cm, 0.725) * Math.pow(weight_kg, 0.425);
  
  // Haycock: BSA = 0.024265 × height^0.3964 × weight^0.5378
  const haycock = 0.024265 * Math.pow(height_cm, 0.3964) * Math.pow(weight_kg, 0.5378);
  
  // Boyd: BSA = 0.0003207 × height^0.3 × weight^(0.7285 - 0.0188×log10(weight))
  const boyd = 0.0003207 * Math.pow(height_cm, 0.3) * 
    Math.pow(weight_kg, 0.7285 - 0.0188 * Math.log10(weight_kg));
  
  return {
    Mosteller: mosteller,
    DuBois: dubois,
    Haycock: haycock,
    Boyd: boyd,
  };
}

/**
 * Calculate eGFR using CKD-EPI 2009 equation
 * 
 * Reference: Levey, A.S. et al. (2009). Ann Intern Med 150:604-612
 */
export function egfrCKDEPI2009(
  serumCreatinine_mg_dL: number,
  age_years: number,
  sex: 'Male' | 'Female',
  isBlack: boolean = false
): EGFRResult {
  if (serumCreatinine_mg_dL <= 0 || age_years <= 0) {
    throw new Error('Invalid parameters');
  }
  
  const Scr = serumCreatinine_mg_dL;
  const kappa = sex === 'Female' ? 0.7 : 0.9;
  const alpha = sex === 'Female' ? -0.329 : -0.411;
  const sexMultiplier = sex === 'Female' ? 1.018 : 1.0;
  const raceMultiplier = isBlack ? 1.159 : 1.0;
  
  const minRatio = Math.min(Scr / kappa, 1);
  const maxRatio = Math.max(Scr / kappa, 1);
  
  const egfr = 141 *
    Math.pow(minRatio, alpha) *
    Math.pow(maxRatio, -1.209) *
    Math.pow(0.993, age_years) *
    sexMultiplier *
    raceMultiplier;
  
  // Determine CKD stage
  let stage: string;
  let category: string;
  
  if (egfr >= 90) {
    stage = 'G1';
    category = 'Normal or high';
  } else if (egfr >= 60) {
    stage = 'G2';
    category = 'Mildly decreased';
  } else if (egfr >= 45) {
    stage = 'G3a';
    category = 'Mildly to moderately decreased';
  } else if (egfr >= 30) {
    stage = 'G3b';
    category = 'Moderately to severely decreased';
  } else if (egfr >= 15) {
    stage = 'G4';
    category = 'Severely decreased';
  } else {
    stage = 'G5';
    category = 'Kidney failure';
  }
  
  return {
    value_ml_min_1_73m2: egfr,
    stage,
    category,
  };
}

/**
 * Calculate PaO₂/FiO₂ ratio (P/F ratio)
 */
export function pfRatio(PaO2_mmHg: number, FiO2: number): number {
  if (FiO2 <= 0 || FiO2 > 1) {
    throw new Error('FiO2 must be between 0 and 1');
  }
  return PaO2_mmHg / FiO2;
}

/**
 * Interpret P/F ratio
 */
export function interpretPFRatio(ratio: number): string {
  if (ratio >= 400) return 'Normal';
  if (ratio >= 300) return 'Mild hypoxemia';
  if (ratio >= 200) return 'Moderate (mild ARDS)';
  if (ratio >= 100) return 'Severe (moderate ARDS)';
  return 'Very severe (severe ARDS)';
}

/**
 * Calculate Oxygen Index (OI)
 * OI = (FiO₂ × MAP × 100) / PaO₂
 */
export function oxygenIndex(
  PaO2_mmHg: number,
  FiO2: number,
  meanAirwayPressure_cmH2O: number
): number {
  if (PaO2_mmHg <= 0) {
    throw new Error('PaO2 must be positive');
  }
  return (FiO2 * 100 * meanAirwayPressure_cmH2O) / PaO2_mmHg;
}

/**
 * Calculate predicted 6-Minute Walk Distance (6MWD)
 * 
 * Reference: Enright & Sherrill (1998). Am J Respir Crit Care Med
 */
export function sixMinuteWalkDistance(
  height_cm: number,
  weight_kg: number,
  age_years: number,
  sex: 'Male' | 'Female'
): { predicted_m: number; lowerLimitNormal_m: number } {
  let predicted: number;
  
  if (sex === 'Male') {
    predicted = (7.57 * height_cm) - (5.02 * age_years) - (1.76 * weight_kg) - 309;
  } else {
    predicted = (2.11 * height_cm) - (2.29 * weight_kg) - (5.78 * age_years) + 667;
  }
  
  // LLN is typically predicted - 2*SE (SE ≈ 50-70m)
  const se = sex === 'Male' ? 56 : 58;
  const lln = predicted - 2 * se;
  
  return {
    predicted_m: Math.max(0, predicted),
    lowerLimitNormal_m: Math.max(0, lln),
  };
}

/**
 * Calculate Wells DVT Score
 * 
 * Reference: Wells et al. (2003). NEJM 349:1227-1235
 */
export interface WellsDVTInputs {
  activeCancer: boolean;
  paralysisOrRecentPlaster: boolean;
  bedriddenGt3dOrMajorSurgery12w: boolean;
  localizedTenderness: boolean;
  entireLegSwollen: boolean;
  calfSwellingGt3cm: boolean;
  pittingEdema: boolean;
  collateralVeins: boolean;
  alternativeDiagnosisLikely: boolean;
}

export function computeWellsDVT(inputs: WellsDVTInputs): WellsDVTResult {
  let points = 0;
  
  if (inputs.activeCancer) points += 1;
  if (inputs.paralysisOrRecentPlaster) points += 1;
  if (inputs.bedriddenGt3dOrMajorSurgery12w) points += 1;
  if (inputs.localizedTenderness) points += 1;
  if (inputs.entireLegSwollen) points += 1;
  if (inputs.calfSwellingGt3cm) points += 1;
  if (inputs.pittingEdema) points += 1;
  if (inputs.collateralVeins) points += 1;
  if (inputs.alternativeDiagnosisLikely) points -= 2;
  
  // 3-tier interpretation
  let threeTier: WellsDVTResult['threeTier'];
  let probability: string;
  
  if (points <= 0) {
    threeTier = 'Low';
    probability = '~5%';
  } else if (points <= 2) {
    threeTier = 'Moderate';
    probability = '~17%';
  } else {
    threeTier = 'High';
    probability = '~53%';
  }
  
  // 2-tier interpretation
  const twoTier: WellsDVTResult['twoTier'] = points < 2 ? 'Unlikely' : 'Likely';
  
  return {
    totalPoints: points,
    threeTier,
    twoTier,
    probability,
  };
}

/**
 * Calculate Wells PE Score
 * 
 * Reference: Wells et al. (2001). Ann Intern Med 135:98-107
 */
export interface WellsPEInputs {
  clinicalSignsDVT: boolean;
  peMostLikelyDiagnosis: boolean;
  heartRateGt100: boolean;
  immobilizationOrSurgery4w: boolean;
  previousDVTorPE: boolean;
  hemoptysis: boolean;
  malignancy: boolean;
}

export function computeWellsPE(inputs: WellsPEInputs): WellsPEResult {
  let points = 0;
  
  if (inputs.clinicalSignsDVT) points += 3;
  if (inputs.peMostLikelyDiagnosis) points += 3;
  if (inputs.heartRateGt100) points += 1.5;
  if (inputs.immobilizationOrSurgery4w) points += 1.5;
  if (inputs.previousDVTorPE) points += 1.5;
  if (inputs.hemoptysis) points += 1;
  if (inputs.malignancy) points += 1;
  
  // 3-tier interpretation
  let threeTier: WellsPEResult['threeTier'];
  let probability: string;
  
  if (points < 2) {
    threeTier = 'Low';
    probability = '~3.6%';
  } else if (points <= 6) {
    threeTier = 'Moderate';
    probability = '~20.5%';
  } else {
    threeTier = 'High';
    probability = '~66.7%';
  }
  
  // 2-tier interpretation
  const twoTier: WellsPEResult['twoTier'] = points <= 4 ? 'Unlikely' : 'Likely';
  
  return {
    totalPoints: points,
    threeTier,
    twoTier,
    probability,
  };
}

/**
 * Calculate A-a Gradient
 * 
 * Reference: Filley et al. (1954). J Clin Invest
 */
export function aaGradient(
  PaO2_mmHg: number,
  PaCO2_mmHg: number,
  FiO2: number,
  altitude_m: number = 0,
  RQ: number = 0.8
): { PAO2_mmHg: number; aaGradient_mmHg: number; normalUpper_mmHg: number } {
  // Calculate barometric pressure at altitude
  const Pb = 760 * Math.exp(-altitude_m / 8434);
  const PH2O = 47;
  
  // Alveolar gas equation
  const PAO2 = FiO2 * (Pb - PH2O) - (PaCO2_mmHg / RQ);
  
  // A-a gradient
  const gradient = PAO2 - PaO2_mmHg;
  
  // Normal upper limit (age-dependent, simplified)
  const normalUpper = 15; // For young adults at sea level
  
  return {
    PAO2_mmHg: PAO2,
    aaGradient_mmHg: gradient,
    normalUpper_mmHg: normalUpper,
  };
}

/**
 * Calculate oxygen delivery (DO₂)
 */
export function oxygenDelivery(
  Hb_g_dL: number,
  SaO2_percent: number,
  PaO2_mmHg: number,
  cardiacOutput_L_min: number,
  BSA_m2?: number
): { CaO2_mL_dL: number; DO2_mL_min: number; DO2I_mL_min_m2?: number } {
  // Calculate oxygen content
  const CaO2 = (1.34 * Hb_g_dL * (SaO2_percent / 100)) + (0.003 * PaO2_mmHg);

  // Oxygen delivery
  const DO2 = CaO2 * cardiacOutput_L_min * 10;

  // Indexed value if BSA provided
  const DO2I = BSA_m2 ? DO2 / BSA_m2 : undefined;

  return {
    CaO2_mL_dL: CaO2,
    DO2_mL_min: DO2,
    DO2I_mL_min_m2: DO2I,
  };
}

// ---------------------------------------------------------------------------
// Individual BSA formulas (matching Python `calculators.clinical`)
// ---------------------------------------------------------------------------

function requirePositive(name: string, value: number): number {
  if (!Number.isFinite(value) || value <= 0) {
    throw new Error(`${name} must be > 0`);
  }
  return value;
}

/**
 * Boyd (1935) weight-only BSA, returned in m².
 *
 * BSA_cm² = 4.688 × w_g^0.8168 − 0.0154 × log10(w_g);  BSA_m² = BSA_cm² / 10000
 */
export function bsaBoyd(weight_kg: number): number {
  requirePositive('weight_kg', weight_kg);
  const wG = weight_kg * 1000;
  const bsaCm2 = 4.688 * Math.pow(wG, 0.8168) - 0.0154 * Math.log10(Math.max(wG, 1));
  return bsaCm2 / 10000;
}

/** DuBois & DuBois (1916): BSA = 0.007184 × h^0.725 × w^0.425. */
export function bsaDubois(height_cm: number, weight_kg: number): number {
  requirePositive('height_cm', height_cm);
  requirePositive('weight_kg', weight_kg);
  return 0.007184 * Math.pow(height_cm, 0.725) * Math.pow(weight_kg, 0.425);
}

/** Haycock et al. (1978): BSA = 0.024265 × h^0.3964 × w^0.5378. */
export function bsaHaycock(height_cm: number, weight_kg: number): number {
  requirePositive('height_cm', height_cm);
  requirePositive('weight_kg', weight_kg);
  return 0.024265 * Math.pow(height_cm, 0.3964) * Math.pow(weight_kg, 0.5378);
}

/** Mosteller (1987): BSA = √((h × w) / 3600). */
export function bsaMosteller(height_cm: number, weight_kg: number): number {
  requirePositive('height_cm', height_cm);
  requirePositive('weight_kg', weight_kg);
  return Math.sqrt((height_cm * weight_kg) / 3600);
}

/** DuBois BSA helper (alias for `bsaDubois`) used by oxygen-delivery callers. */
export function duboisBsaM2(args: { height_cm: number; weight_kg: number }): number {
  return bsaDubois(args.height_cm, args.weight_kg);
}

// ---------------------------------------------------------------------------
// Full A–a gradient calculator (Filley 1954 normal range or age heuristic)
// ---------------------------------------------------------------------------

export type AaNormalModel = 'filley1954_rest_air_1600ft' | 'heuristic_age_over4_plus4';

export interface AaGradientInputs {
  altitude_m: number;
  pao2_mmHg: number;
  paco2_mmHg?: number;
  fio2?: number;
  rq?: number;
  age_years?: number;
  normal_model?: AaNormalModel;
}

export interface AaGradientResult {
  pao2_mmHg: number;
  pao2_calc_mmHg: number;
  aa_gradient_mmHg: number;
  altitude_m: number;
  fio2: number;
  paco2_mmHg: number;
  rq: number;
  normal_model: AaNormalModel;
  normal_mean_mmHg: number | null;
  normal_sd_mmHg: number | null;
  normal_upper_approx_mmHg: number | null;
}

const FILLEY_MEAN = 9.7;
const FILLEY_SD = 5.3;

/**
 * Alveolar gas equation (mmHg) using ISA barometric pressure at altitude.
 *
 * PAO₂ = FiO₂ × (Pb − PH₂O) − PaCO₂ / RQ
 */
function alveolarPO2Local(
  altitude_m: number,
  fio2: number,
  paco2_mmHg: number,
  rq: number
): number {
  // Reuse the Pb model from the alveolar gas implementation in atmosphere.ts
  // by mirroring the Python `standard_atmosphere`-derived Pb in mmHg.
  // Constants below match `calculators/atmosphere.py` exactly.
  const T0 = 288.15;
  const P0 = 101325;
  const L = 0.0065;
  const R = 8.31447;
  const g = 9.80665;
  const M = 0.0289644;
  const h = Math.max(0, altitude_m);
  let pPa: number;
  if (h <= 11000) {
    const T = T0 - L * h;
    pPa = P0 * Math.pow(T / T0, (g * M) / (R * L));
  } else {
    const T11 = T0 - L * 11000;
    const P11 = P0 * Math.pow(T11 / T0, (g * M) / (R * L));
    if (h <= 20000) {
      pPa = P11 * Math.exp((-g * M * (h - 11000)) / (R * T11));
    } else {
      const Ls = -0.001;
      const T20 = T11;
      const P20 = P11 * Math.exp((-g * M * (20000 - 11000)) / (R * T11));
      const T = T20 - Ls * (h - 20000);
      pPa = P20 * Math.pow(T / T20, (g * M) / (R * Ls));
    }
  }
  const Pb_mmHg = pPa / 133.322;
  const PH2O = 47.0;
  return fio2 * (Pb_mmHg - PH2O) - paco2_mmHg / rq;
}

/** Compute alveolar gas A–a oxygen gradient with reference normal range. */
export function computeAaGradient(inputs: AaGradientInputs): AaGradientResult {
  const altitude_m = inputs.altitude_m;
  const pao2_mmHg = inputs.pao2_mmHg;
  const paco2_mmHg = inputs.paco2_mmHg ?? 40.0;
  const fio2 = inputs.fio2 ?? 0.21;
  const rq = inputs.rq ?? 0.8;
  const normal_model: AaNormalModel = inputs.normal_model ?? 'filley1954_rest_air_1600ft';

  if (!Number.isFinite(altitude_m) || altitude_m < 0) {
    throw new Error('altitude_m must be >= 0');
  }
  if (!Number.isFinite(pao2_mmHg) || pao2_mmHg < 0) {
    throw new Error('pao2_mmHg must be >= 0');
  }
  if (!Number.isFinite(paco2_mmHg) || paco2_mmHg < 0) {
    throw new Error('paco2_mmHg must be >= 0');
  }
  if (!Number.isFinite(fio2) || fio2 < 0 || fio2 > 1) {
    throw new Error('fio2 must be between 0 and 1');
  }
  if (!Number.isFinite(rq) || rq <= 0) {
    throw new Error('rq must be > 0');
  }

  const pao2_calc_mmHg = alveolarPO2Local(altitude_m, fio2, paco2_mmHg, rq);
  const aa = pao2_calc_mmHg - pao2_mmHg;

  let normal_mean_mmHg: number | null = null;
  let normal_sd_mmHg: number | null = null;
  let normal_upper_approx_mmHg: number | null = null;

  if (normal_model === 'filley1954_rest_air_1600ft') {
    normal_mean_mmHg = FILLEY_MEAN;
    normal_sd_mmHg = FILLEY_SD;
    normal_upper_approx_mmHg = FILLEY_MEAN + 2 * FILLEY_SD;
  } else {
    if (inputs.age_years === undefined) {
      throw new Error('age_years is required for heuristic_age_over4_plus4');
    }
    if (!Number.isFinite(inputs.age_years) || inputs.age_years < 0) {
      throw new Error('age_years must be >= 0');
    }
    normal_upper_approx_mmHg = inputs.age_years / 4 + 4;
  }

  return {
    pao2_mmHg,
    pao2_calc_mmHg,
    aa_gradient_mmHg: aa,
    altitude_m,
    fio2,
    paco2_mmHg,
    rq,
    normal_model,
    normal_mean_mmHg,
    normal_sd_mmHg,
    normal_upper_approx_mmHg,
  };
}

// ---------------------------------------------------------------------------
// Full Oxygen Delivery (CaO₂ / DO₂ / DO₂I) — matches Python compute_oxygen_delivery
// ---------------------------------------------------------------------------

export interface OxygenDeliveryInputs {
  hb_g_dl: number;
  /** SaO₂ as fraction [0, 1]. */
  sao2_frac: number;
  pao2_mmhg: number;
  cardiac_output_l_min: number;
  height_cm?: number;
  weight_kg?: number;
  bsa_m2?: number;
  /** Hüfner constant — mL O₂ per g Hb (typical 1.34–1.39). */
  hufner_ml_per_g?: number;
  /** O₂ solubility in plasma — mL O₂ per dL per mmHg (typical 0.003). */
  alpha_ml_per_dl_per_mmhg?: number;
}

export interface OxygenDeliveryResult {
  cao2_ml_o2_dl: number;
  o2_bound_ml_o2_dl: number;
  o2_dissolved_ml_o2_dl: number;
  do2_ml_o2_min: number;
  bsa_m2: number | null;
  do2i_ml_o2_min_m2: number | null;
}

export function computeOxygenDelivery(inputs: OxygenDeliveryInputs): OxygenDeliveryResult {
  if (!Number.isFinite(inputs.hb_g_dl) || inputs.hb_g_dl < 0) {
    throw new Error('hb_g_dl must be >= 0');
  }
  if (!Number.isFinite(inputs.sao2_frac) || inputs.sao2_frac < 0 || inputs.sao2_frac > 1) {
    throw new Error('sao2_frac must be between 0 and 1');
  }
  if (!Number.isFinite(inputs.pao2_mmhg) || inputs.pao2_mmhg < 0) {
    throw new Error('pao2_mmhg must be >= 0');
  }
  const co = requirePositive('cardiac_output_l_min', inputs.cardiac_output_l_min);
  const huf = requirePositive('hufner_ml_per_g', inputs.hufner_ml_per_g ?? 1.34);
  const alpha = requirePositive(
    'alpha_ml_per_dl_per_mmhg',
    inputs.alpha_ml_per_dl_per_mmhg ?? 0.003
  );

  const o2Bound = huf * inputs.hb_g_dl * inputs.sao2_frac;
  const o2Diss = alpha * inputs.pao2_mmhg;
  const cao2 = o2Bound + o2Diss;
  const do2 = co * cao2 * 10;

  let bsa: number | null = null;
  if (inputs.bsa_m2 !== undefined) {
    bsa = requirePositive('bsa_m2', inputs.bsa_m2);
  } else if (inputs.height_cm !== undefined && inputs.weight_kg !== undefined) {
    bsa = duboisBsaM2({ height_cm: inputs.height_cm, weight_kg: inputs.weight_kg });
  }

  return {
    cao2_ml_o2_dl: cao2,
    o2_bound_ml_o2_dl: o2Bound,
    o2_dissolved_ml_o2_dl: o2Diss,
    do2_ml_o2_min: do2,
    bsa_m2: bsa,
    do2i_ml_o2_min_m2: bsa !== null ? do2 / bsa : null,
  };
}
