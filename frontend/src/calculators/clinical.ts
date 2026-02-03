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
