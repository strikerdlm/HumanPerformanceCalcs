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

// ---------------------------------------------------------------------------
// CHA₂DS₂-VASc — Lip et al. (2010) CHEST 137:263
// ---------------------------------------------------------------------------

export interface CHA2DS2VAScInputs {
  congestive_heart_failure: boolean;
  hypertension: boolean;
  age_years: number;
  diabetes: boolean;
  stroke_tia_or_thromboembolism: boolean;
  vascular_disease: boolean;
  female: boolean;
}

export interface CHA2DS2VAScResult {
  score: number;
  stroke_risk_percent_per_year: number;
  recommendation: string;
}

// Annual stroke risk by CHA₂DS₂-VASc score (Lip et al. 2010, Friberg 2012 refinement).
const CHA2DS2_RISK_PERCENT: Record<number, number> = {
  0: 0,
  1: 1.3,
  2: 2.2,
  3: 3.2,
  4: 4.0,
  5: 6.7,
  6: 9.8,
  7: 9.6,
  8: 6.7,
  9: 15.2,
};

/**
 * Compute the CHA₂DS₂-VASc stroke-risk score for non-valvular AF.
 *
 *   C  Congestive heart failure        +1
 *   H  Hypertension                    +1
 *   A₂ Age ≥ 75                        +2
 *   D  Diabetes mellitus               +1
 *   S₂ Stroke / TIA / thromboembolism  +2
 *   V  Vascular disease (MI, PAD, aortic plaque) +1
 *   A  Age 65–74                       +1
 *   Sc Sex category (female)           +1
 *
 * Reference:
 *   Lip G.Y.H., Nieuwlaat R., Pisters R., Lane D.A., Crijns H.J. (2010).
 *   CHEST 137:263. https://doi.org/10.1378/chest.09-1584
 */
export function cha2ds2Vasc(inputs: CHA2DS2VAScInputs): CHA2DS2VAScResult {
  if (!Number.isFinite(inputs.age_years) || inputs.age_years < 0) {
    throw new Error('age_years must be a finite, non-negative number');
  }
  let score = 0;
  if (inputs.congestive_heart_failure) score += 1;
  if (inputs.hypertension) score += 1;
  if (inputs.age_years >= 75) score += 2;
  else if (inputs.age_years >= 65) score += 1;
  if (inputs.diabetes) score += 1;
  if (inputs.stroke_tia_or_thromboembolism) score += 2;
  if (inputs.vascular_disease) score += 1;
  if (inputs.female) score += 1;

  const risk = CHA2DS2_RISK_PERCENT[score] ?? 15.2;
  let recommendation: string;
  if (score === 0) {
    recommendation = 'No antithrombotic therapy generally required';
  } else if (score === 1) {
    recommendation =
      'Consider oral anticoagulant therapy (especially in males); decision shared with patient';
  } else {
    recommendation = 'Oral anticoagulant therapy recommended';
  }

  return { score, stroke_risk_percent_per_year: risk, recommendation };
}

// ---------------------------------------------------------------------------
// HAS-BLED — Pisters et al. (2010) CHEST 138:1093
// ---------------------------------------------------------------------------

export interface HasBledInputs {
  hypertension_uncontrolled: boolean;
  abnormal_renal_function: boolean;
  abnormal_liver_function: boolean;
  stroke_history: boolean;
  bleeding_history_or_predisposition: boolean;
  labile_inr: boolean;
  age_years: number;
  drugs_antiplatelet_or_nsaid: boolean;
  alcohol_excess: boolean;
}

export interface HasBledResult {
  score: number;
  bleeding_risk_category: 'low' | 'moderate' | 'high';
  bleeds_per_100_patient_years: number;
}

/**
 * Compute HAS-BLED bleeding-risk score for AF patients on anticoagulation.
 *
 *   H  Hypertension (uncontrolled, SBP > 160)        +1
 *   A  Abnormal renal function                        +1
 *   A  Abnormal liver function                        +1
 *   S  Stroke history                                 +1
 *   B  Bleeding history or predisposition             +1
 *   L  Labile INR                                     +1
 *   E  Elderly (age > 65)                             +1
 *   D  Drugs (antiplatelet / NSAID)                   +1
 *   D  Alcohol excess (≥ 8 units/week)                +1
 *
 * Reference:
 *   Pisters R., Lane D.A., Nieuwlaat R., et al. (2010). CHEST 138:1093.
 *   https://doi.org/10.1378/chest.10-0134
 */
export function hasBled(inputs: HasBledInputs): HasBledResult {
  if (!Number.isFinite(inputs.age_years) || inputs.age_years < 0) {
    throw new Error('age_years must be a finite, non-negative number');
  }
  let score = 0;
  if (inputs.hypertension_uncontrolled) score += 1;
  if (inputs.abnormal_renal_function) score += 1;
  if (inputs.abnormal_liver_function) score += 1;
  if (inputs.stroke_history) score += 1;
  if (inputs.bleeding_history_or_predisposition) score += 1;
  if (inputs.labile_inr) score += 1;
  if (inputs.age_years > 65) score += 1;
  if (inputs.drugs_antiplatelet_or_nsaid) score += 1;
  if (inputs.alcohol_excess) score += 1;

  // Bleeds per 100 patient-years (Pisters 2010 Euro Heart Survey cohort).
  const RISK: Record<number, number> = {
    0: 1.13,
    1: 1.02,
    2: 1.88,
    3: 3.74,
    4: 8.7,
    5: 12.5,
    6: 12.5,
    7: 12.5,
    8: 12.5,
    9: 12.5,
  };

  let category: HasBledResult['bleeding_risk_category'];
  if (score < 2) category = 'low';
  else if (score === 2) category = 'moderate';
  else category = 'high';

  return {
    score,
    bleeding_risk_category: category,
    bleeds_per_100_patient_years: RISK[score] ?? 12.5,
  };
}

// ---------------------------------------------------------------------------
// STOP-BANG — Chung et al. (2008) Anesthesiology 108:812
// ---------------------------------------------------------------------------

export interface StopBangInputs {
  /** Snoring loudly. */
  snoring: boolean;
  /** Daytime tiredness. */
  tired: boolean;
  /** Observed apnea. */
  observed_apnea: boolean;
  /** High blood pressure (or treated for hypertension). */
  pressure: boolean;
  /** BMI > 35 kg/m². */
  bmi_gt_35: boolean;
  /** Age > 50. */
  age_gt_50: boolean;
  /** Neck circumference > 40 cm (16 in). */
  neck_gt_40cm: boolean;
  /** Male sex. */
  male: boolean;
}

export interface StopBangResult {
  score: number;
  risk_category: 'low' | 'intermediate' | 'high';
}

/**
 * Compute the STOP-BANG score for obstructive sleep apnea screening.
 *
 *   STOP    Snoring, Tired, Observed apnea, Pressure
 *   BANG    BMI > 35, Age > 50, Neck > 40 cm, Gender (male)
 *
 * Risk stratification:
 *   0–2 yes : low
 *   3–4 yes : intermediate
 *   5–8 yes : high
 *
 * High risk also when ≥2 STOP items + (male OR BMI > 35 OR neck > 40 cm).
 *
 * Reference:
 *   Chung F., Yegneswaran B., Liao P., et al. (2008). STOP questionnaire:
 *   a tool to screen patients for obstructive sleep apnea. Anesthesiology
 *   108:812. https://doi.org/10.1097/ALN.0b013e31816d83e4
 */
export function stopBangScore(inputs: StopBangInputs): StopBangResult {
  const stop_yes =
    Number(inputs.snoring) + Number(inputs.tired) + Number(inputs.observed_apnea) + Number(inputs.pressure);
  const bang_yes =
    Number(inputs.bmi_gt_35) + Number(inputs.age_gt_50) + Number(inputs.neck_gt_40cm) + Number(inputs.male);
  const score = stop_yes + bang_yes;

  let category: StopBangResult['risk_category'];
  if (score >= 5) category = 'high';
  else if (score >= 3) category = 'intermediate';
  else category = 'low';

  // Refinement: 2+ STOP items + male / BMI>35 / neck>40 → reclassify intermediate as high.
  if (
    category !== 'high' &&
    stop_yes >= 2 &&
    (inputs.male || inputs.bmi_gt_35 || inputs.neck_gt_40cm)
  ) {
    category = 'high';
  }

  return { score, risk_category: category };
}

// ---------------------------------------------------------------------------
// Karvonen target HR + Borg RPE
// ---------------------------------------------------------------------------

export type MaxHeartRateFormula = 'fox220' | 'tanaka2001';

export interface KarvonenResult {
  hr_max_bpm: number;
  hr_reserve_bpm: number;
  target_hr_low_bpm: number;
  target_hr_high_bpm: number;
  formula: MaxHeartRateFormula;
}

/**
 * Karvonen (1957) heart-rate-reserve target zone.
 *
 *   HR_max    = 220 − age (Fox)  OR  208 − 0.7·age (Tanaka 2001)
 *   HRR       = HR_max − HR_rest
 *   Target HR = HR_rest + intensity·HRR
 *
 * Reference:
 *   Karvonen M.J., Kentala E., Mustala O. (1957). The effects of training
 *   on heart rate; a longitudinal study. Ann. Med. Exp. Biol. Fenn. 35:307.
 *   Tanaka H., Monahan K.D., Seals D.R. (2001). Age-predicted maximal heart
 *   rate revisited. J. Am. Coll. Cardiol. 37:153.
 */
export function karvonenTargetHR(args: {
  age_years: number;
  resting_hr_bpm: number;
  intensity_low_fraction: number;
  intensity_high_fraction: number;
  hr_max_formula?: MaxHeartRateFormula;
}): KarvonenResult {
  if (!Number.isFinite(args.age_years) || args.age_years < 0) {
    throw new Error('age_years must be a finite, non-negative number');
  }
  if (!Number.isFinite(args.resting_hr_bpm) || args.resting_hr_bpm <= 0) {
    throw new Error('resting_hr_bpm must be a finite, positive number');
  }
  for (const f of [args.intensity_low_fraction, args.intensity_high_fraction]) {
    if (!Number.isFinite(f) || f < 0 || f > 1) {
      throw new Error('intensity fractions must lie in [0, 1]');
    }
  }
  if (args.intensity_high_fraction < args.intensity_low_fraction) {
    throw new Error('intensity_high_fraction must be >= intensity_low_fraction');
  }

  const formula = args.hr_max_formula ?? 'tanaka2001';
  const hr_max = formula === 'fox220' ? 220 - args.age_years : 208 - 0.7 * args.age_years;
  const hrr = hr_max - args.resting_hr_bpm;
  return {
    hr_max_bpm: hr_max,
    hr_reserve_bpm: hrr,
    target_hr_low_bpm: args.resting_hr_bpm + args.intensity_low_fraction * hrr,
    target_hr_high_bpm: args.resting_hr_bpm + args.intensity_high_fraction * hrr,
    formula,
  };
}

/**
 * Approximate HR for a Borg RPE rating (6–20 scale).
 *
 *   HR_bpm ≈ 10 · RPE
 *
 * Reference: Borg G.A.V. (1982). Psychophysical bases of perceived exertion.
 * Med. Sci. Sports Exerc. 14:377.
 */
export function borgRPEtoHR(rpe: number): number {
  if (!Number.isFinite(rpe) || rpe < 6 || rpe > 20) {
    throw new Error('Borg RPE must be in [6, 20]');
  }
  return rpe * 10;
}
