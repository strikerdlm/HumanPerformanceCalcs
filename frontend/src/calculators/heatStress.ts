/**
 * Heat Stress Calculators
 * 
 * References:
 * - ISO 7243:2017 Heat stress assessment (WBGT)
 * - ISO 7933:2023 Predicted Heat Strain (PHS)
 * - Belding & Hatch (1955) Heat Stress Index
 * - Bröde et al. (2012) UTCI operational procedure
 */

export interface WBGTResult {
  wbgt: number;
  riskCategory: 'Low' | 'Moderate' | 'High' | 'Extreme';
  recommendation: string;
}

export interface HeatStressIndexResult {
  hsi: number;
  category: string;
  recommendation: string;
}

export interface PHSResult {
  predictedCoreTemp_C: number;
  requiredSweatRate_L_h: number;
  maxSustainableSweatRate_L_h: number;
  actualSweatRate_L_h: number;
  predictedWaterLoss_L: number;
  dehydrationPercent: number;
  allowableExposure_min: number;
  limitingFactor: 'Core temperature limit' | 'Dehydration limit' | 'None';
}

export interface UTCIResult {
  utci_C: number;
  category: string;
  stressLevel: number;
}

/**
 * Calculate Wet Bulb Globe Temperature (WBGT) for indoor environments
 * 
 * Reference: ISO 7243:2017
 * 
 * @param T_nwb - Natural wet bulb temperature (°C)
 * @param T_g - Globe temperature (°C)
 * @returns WBGT in °C
 */
export function wbgtIndoor(T_nwb: number, T_g: number): number {
  // Indoor: WBGT = 0.7·T_nwb + 0.3·T_g
  return 0.7 * T_nwb + 0.3 * T_g;
}

/**
 * Calculate WBGT for outdoor environments with solar load
 * 
 * @param T_nwb - Natural wet bulb temperature (°C)
 * @param T_g - Globe temperature (°C)
 * @param T_db - Dry bulb temperature (°C)
 * @param RH - Relative humidity (%) - used if T_nwb not provided
 * @returns WBGT in °C
 */
export function wbgtOutdoor(
  T_nwb: number | null,
  T_g: number,
  T_db: number,
  RH?: number
): number {
  // If T_nwb not provided, estimate from T_db and RH
  let wetBulb = T_nwb;
  if (wetBulb === null && RH !== undefined) {
    wetBulb = estimateWetBulb(T_db, RH);
  }
  if (wetBulb === null) {
    throw new Error('Must provide T_nwb or RH');
  }
  
  // Outdoor: WBGT = 0.7·T_nwb + 0.2·T_g + 0.1·T_db
  return 0.7 * wetBulb + 0.2 * T_g + 0.1 * T_db;
}

/**
 * Estimate wet bulb temperature from dry bulb and RH
 * Simplified empirical approximation
 */
function estimateWetBulb(T_db: number, RH: number): number {
  // Stull (2011) approximation
  return T_db * Math.atan(0.151977 * Math.sqrt(RH + 8.313659)) +
    Math.atan(T_db + RH) - Math.atan(RH - 1.676331) +
    0.00391838 * Math.pow(RH, 1.5) * Math.atan(0.023101 * RH) -
    4.686035;
}

/**
 * Assess WBGT risk category
 */
export function wbgtRiskAssessment(wbgt: number): WBGTResult {
  let category: 'Low' | 'Moderate' | 'High' | 'Extreme';
  let recommendation: string;
  
  if (wbgt < 28) {
    category = 'Low';
    recommendation = 'Normal work activity with standard precautions';
  } else if (wbgt < 30) {
    category = 'Moderate';
    recommendation = 'Increase fluid intake, monitor for heat strain symptoms';
  } else if (wbgt < 32) {
    category = 'High';
    recommendation = 'Reduce physical activity, mandatory rest breaks, continuous monitoring';
  } else {
    category = 'Extreme';
    recommendation = 'Suspend non-essential outdoor activities, emergency protocols active';
  }
  
  return { wbgt, riskCategory: category, recommendation };
}

/**
 * Calculate Heat Stress Index (HSI)
 * 
 * Reference: Belding & Hatch (1955)
 * 
 * @param M - Metabolic rate (W/m²)
 * @param T_db - Dry bulb temperature (°C)
 * @param RH - Relative humidity (%)
 * @param v - Air velocity (m/s)
 * @param W_ext - External work (W/m²)
 * @param T_g - Globe temperature (°C)
 * @returns HSI percentage
 */
export function heatStressIndex(
  M: number,
  T_db: number,
  RH: number,
  v: number,
  W_ext: number = 0,
  T_g?: number
): number {
  const T_mrt = T_g ?? T_db;
  
  // Mean skin temperature assumption
  const T_sk = 35;
  
  // Vapor pressures
  const P_sk = 5.67; // kPa at skin temp
  const P_a = saturationVaporPressure(T_db) * (RH / 100);
  
  // Heat transfer coefficients
  const h_c = 8.3 * Math.sqrt(v); // Convective (W/m²K)
  const h_r = 4.7; // Radiative (W/m²K)
  
  // Heat exchanges
  const C = h_c * (T_db - T_sk); // Convective
  const R = h_r * (T_mrt - T_sk); // Radiative
  
  // Required evaporative heat loss
  const E_req = (M - W_ext) + C + R;
  
  // Maximum evaporative capacity
  const E_max = 16.7 * h_c * (P_sk - P_a);
  
  // HSI = (E_req / E_max) × 100
  const hsi = E_max > 0 ? (E_req / E_max) * 100 : 100;
  
  return Math.max(0, Math.min(100, hsi));
}

/**
 * Assess HSI result
 */
export function hsiAssessment(hsi: number): HeatStressIndexResult {
  let category: string;
  let recommendation: string;
  
  if (hsi < 20) {
    category = 'Acceptable';
    recommendation = 'No restrictions required';
  } else if (hsi < 40) {
    category = 'Mild strain';
    recommendation = 'Monitor for symptoms, ensure adequate hydration';
  } else if (hsi < 70) {
    category = 'Moderate strain';
    recommendation = 'Work-rest cycles recommended, enhanced monitoring';
  } else if (hsi < 100) {
    category = 'High strain';
    recommendation = 'Limited exposure time, frequent rest periods required';
  } else {
    category = 'Uncompensable heat stress';
    recommendation = 'Immediate action required - body cannot maintain thermal balance';
  }
  
  return { hsi, category, recommendation };
}

/**
 * Calculate Predicted Heat Strain (PHS) - ISO 7933 inspired
 * 
 * Simplified implementation capturing core concepts
 */
export function predictedHeatStrain(
  metabolicRate_W_m2: number,
  airTemp_C: number,
  meanRadiantTemp_C: number,
  relativeHumidity_percent: number,
  airVelocity_m_s: number,
  clothingInsulation_clo: number,
  exposure_min: number,
  mechanicalPower_W_m2: number = 0,
  bodyMass_kg: number = 75,
  _bodySurfaceArea_m2: number = 1.9, // Reserved for future use
  baselineCoreTemp_C: number = 37.0,
  coreTempLimit_C: number = 38.5,
  dehydrationLimit_percent: number = 5.0
): PHSResult {
  // Constants
  const SPECIFIC_HEAT_BODY = 3.49; // kJ/(kg·K)
  const SKIN_TEMP = 36.0;
  const Icl = clothingInsulation_clo * 0.155; // Convert to m²K/W
  
  // Net metabolic heat
  const M_net = metabolicRate_W_m2 - mechanicalPower_W_m2;
  
  // Ambient vapor pressure
  const P_a = saturationVaporPressure(airTemp_C) * (relativeHumidity_percent / 100);
  
  // Heat transfer coefficients
  const h_c = 8.7 * Math.pow(airVelocity_m_s, 0.6);
  const h_r = 4.7;
  const h_combined = h_c + h_r;
  
  // Operative temperature
  const T_op = (h_c * airTemp_C + h_r * meanRadiantTemp_C) / h_combined;
  
  // Clothing factor
  const f_cl = 1 + 0.31 * clothingInsulation_clo;
  
  // Clothing surface temperature (iterative simplification)
  const T_cl = SKIN_TEMP - Icl * h_combined * f_cl * (SKIN_TEMP - T_op);
  
  // Dry heat exchange
  const H_dry = h_combined * f_cl * (T_cl - T_op);
  
  // Required evaporation
  const E_req = M_net - H_dry;
  
  // Maximum evaporative capacity
  const P_sk = saturationVaporPressure(SKIN_TEMP);
  const E_max = 16.7 * h_c * f_cl * (P_sk - P_a);
  
  // Actual sweat rate (limited by max sustainable)
  const maxSustainable_L_h = 1.0 + (metabolicRate_W_m2 - 200) * 0.002;
  const requiredSweat_L_h = Math.max(0, E_req / 2430) * 3600 / 1000;
  const actualSweat_L_h = Math.min(requiredSweat_L_h, maxSustainable_L_h);
  
  // Core temperature rise
  const uncompensatedHeat = Math.max(0, E_req - E_max);
  const heatStorage = uncompensatedHeat * (exposure_min / 60);
  const coreTempRise = heatStorage / (bodyMass_kg * SPECIFIC_HEAT_BODY * 1000) * 3600;
  const predictedCoreTemp = baselineCoreTemp_C + coreTempRise;
  
  // Water loss
  const waterLoss_L = actualSweat_L_h * (exposure_min / 60);
  const dehydrationPercent = (waterLoss_L / bodyMass_kg) * 100;
  
  // Allowable exposure
  let allowableExposure_min = exposure_min;
  let limitingFactor: PHSResult['limitingFactor'] = 'None';
  
  // Check core temp limit
  if (predictedCoreTemp > coreTempLimit_C) {
    const allowedRise = coreTempLimit_C - baselineCoreTemp_C;
    allowableExposure_min = Math.min(
      allowableExposure_min,
      (allowedRise * bodyMass_kg * SPECIFIC_HEAT_BODY * 1000 / uncompensatedHeat) * 60 / 3600
    );
    limitingFactor = 'Core temperature limit';
  }
  
  // Check dehydration limit
  const timeToDehydrationLimit = dehydrationLimit_percent > 0 
    ? (dehydrationLimit_percent * bodyMass_kg / 100) / actualSweat_L_h * 60
    : Infinity;
  
  if (timeToDehydrationLimit < allowableExposure_min) {
    allowableExposure_min = timeToDehydrationLimit;
    limitingFactor = 'Dehydration limit';
  }
  
  return {
    predictedCoreTemp_C: Math.min(42, predictedCoreTemp),
    requiredSweatRate_L_h: requiredSweat_L_h,
    maxSustainableSweatRate_L_h: maxSustainable_L_h,
    actualSweatRate_L_h: actualSweat_L_h,
    predictedWaterLoss_L: waterLoss_L,
    dehydrationPercent,
    allowableExposure_min: Math.max(0, allowableExposure_min),
    limitingFactor,
  };
}

/**
 * Calculate Universal Thermal Climate Index (UTCI)
 * 
 * Reference: Bröde et al. (2012) Int J Biometeorol
 * 
 * Polynomial approximation for -50°C to +50°C
 */
export function utci(
  airTemp_C: number,
  meanRadiantTemp_C: number,
  windSpeed_10m_m_s: number,
  relativeHumidity_percent: number
): UTCIResult {
  const Ta = airTemp_C;
  const Tmrt = meanRadiantTemp_C;
  const D_Tmrt = Tmrt - Ta;
  
  // Wind speed at 10m, clamped to valid range
  let va = Math.max(0.5, Math.min(17, windSpeed_10m_m_s));
  
  // Convert RH to vapor pressure (kPa)
  const es = saturationVaporPressure(Ta);
  const Pa = es * (relativeHumidity_percent / 100);
  
  // Polynomial coefficients (6th order approximation)
  // Simplified from full UTCI operational procedure
  const utci_val = Ta +
    0.607562052 +
    -0.0227712343 * Ta +
    8.06470249e-4 * Ta * Ta +
    -1.54271372e-4 * Ta * Ta * Ta +
    -3.24651735e-6 * Ta * Ta * Ta * Ta +
    7.32602852e-8 * Ta * Ta * Ta * Ta * Ta +
    1.35959073e-9 * Ta * Ta * Ta * Ta * Ta * Ta +
    -2.25836520 * va +
    0.0880326035 * Ta * va +
    0.00216844454 * Ta * Ta * va +
    -1.53347087e-5 * Ta * Ta * Ta * va +
    -5.72983704e-7 * Ta * Ta * Ta * Ta * va +
    -2.55090145e-9 * Ta * Ta * Ta * Ta * Ta * va +
    -0.751269505 * va * va +
    -0.00408350271 * Ta * va * va +
    -5.21670675e-5 * Ta * Ta * va * va +
    1.94544667e-6 * Ta * Ta * Ta * va * va +
    -1.14099531e-8 * Ta * Ta * Ta * Ta * va * va +
    0.158137256 * va * va * va +
    -6.57263143e-5 * Ta * va * va * va +
    2.22697524e-7 * Ta * Ta * va * va * va +
    -4.16117031e-8 * Ta * Ta * Ta * va * va * va +
    -0.0127762753 * va * va * va * va +
    9.66891875e-6 * Ta * va * va * va * va +
    2.52785852e-9 * Ta * Ta * va * va * va * va +
    4.56306672e-4 * va * va * va * va * va +
    -1.74202546e-7 * Ta * va * va * va * va * va +
    -5.91491269e-6 * va * va * va * va * va * va +
    0.398374029 * D_Tmrt +
    1.83945314e-4 * Ta * D_Tmrt +
    -1.73754510e-4 * Ta * Ta * D_Tmrt +
    -7.60781159e-7 * Ta * Ta * Ta * D_Tmrt +
    3.77830287e-8 * Ta * Ta * Ta * Ta * D_Tmrt +
    5.43079673e-10 * Ta * Ta * Ta * Ta * Ta * D_Tmrt +
    -0.0200518269 * va * D_Tmrt +
    8.92859837e-4 * Ta * va * D_Tmrt +
    3.45433048e-6 * Ta * Ta * va * D_Tmrt +
    -3.77925774e-7 * Ta * Ta * Ta * va * D_Tmrt +
    -1.69699377e-9 * Ta * Ta * Ta * Ta * va * D_Tmrt +
    0.100 * Pa;
  
  return {
    utci_C: utci_val,
    category: utciCategory(utci_val),
    stressLevel: utciStressLevel(utci_val),
  };
}

/**
 * Get UTCI thermal stress category
 */
export function utciCategory(utci_C: number): string {
  if (utci_C < -40) return 'Extreme cold stress';
  if (utci_C < -27) return 'Very strong cold stress';
  if (utci_C < -13) return 'Strong cold stress';
  if (utci_C < 0) return 'Moderate cold stress';
  if (utci_C < 9) return 'Slight cold stress';
  if (utci_C < 26) return 'No thermal stress';
  if (utci_C < 32) return 'Moderate heat stress';
  if (utci_C < 38) return 'Strong heat stress';
  if (utci_C < 46) return 'Very strong heat stress';
  return 'Extreme heat stress';
}

/**
 * Get numeric stress level (-5 to +5)
 */
function utciStressLevel(utci_C: number): number {
  if (utci_C < -40) return -5;
  if (utci_C < -27) return -4;
  if (utci_C < -13) return -3;
  if (utci_C < 0) return -2;
  if (utci_C < 9) return -1;
  if (utci_C < 26) return 0;
  if (utci_C < 32) return 1;
  if (utci_C < 38) return 2;
  if (utci_C < 46) return 3;
  return 4;
}

/**
 * Calculate saturation vapor pressure (kPa) using Magnus formula
 */
function saturationVaporPressure(temp_C: number): number {
  return 0.6108 * Math.exp((17.27 * temp_C) / (temp_C + 237.3));
}

/**
 * Simulate PHS trajectory over time
 */
export interface PHSTrajectoryPoint {
  time_min: number;
  coreTemp_C: number;
  dehydration_percent: number;
  sweatRate_L_h: number;
}

export function simulatePHSTrajectory(
  params: Parameters<typeof predictedHeatStrain>,
  stepMin: number = 5
): PHSTrajectoryPoint[] {
  const [
    metabolicRate, airTemp, meanRadiant, rh, airVel, clo, totalExposure,
    mechPower, bodyMass, bsa, baseCore, coreLimit, dehydLimit
  ] = params;
  
  const points: PHSTrajectoryPoint[] = [];
  const steps = Math.ceil(totalExposure / stepMin);
  
  for (let i = 0; i <= steps; i++) {
    const time = Math.min(i * stepMin, totalExposure);
    const result = predictedHeatStrain(
      metabolicRate, airTemp, meanRadiant, rh, airVel, clo, time,
      mechPower, bodyMass, bsa, baseCore, coreLimit, dehydLimit
    );
    
    points.push({
      time_min: time,
      coreTemp_C: result.predictedCoreTemp_C,
      dehydration_percent: result.dehydrationPercent,
      sweatRate_L_h: result.actualSweatRate_L_h,
    });
  }
  
  return points;
}

// ---------------------------------------------------------------------------
// Physiological Strain Index — Moran et al. (1998)
// ---------------------------------------------------------------------------

export type PsiCategory =
  | 'no_strain'
  | 'low_strain'
  | 'moderate_strain'
  | 'high_strain'
  | 'very_high_strain';

export interface PsiResult {
  /** PSI value on a 0–10 scale. */
  psi: number;
  category: PsiCategory;
  core_component: number;
  heart_rate_component: number;
}

/**
 * Physiological Strain Index (PSI) — Moran, Shitzer, Pandolf (1998).
 *
 *   PSI = 5·(T_ct − T_c0) / (39 − T_c0) + 5·(HR_t − HR_0) / (180 − HR_0)
 *
 * Bounds: 0 (no strain) – 10 (extreme strain). Each component contributes
 * up to 5 points. Asymptotes 39 °C and 180 bpm reflect typical experimental
 * upper limits for healthy adults.
 *
 * Reference:
 *   Moran D.S., Shitzer A., Pandolf K.B. (1998). A physiological strain
 *   index to evaluate heat stress. Am. J. Physiol. 275(1):R129–R134.
 *   https://doi.org/10.1152/ajpregu.1998.275.1.R129
 */
export function physiologicalStrainIndex(args: {
  initial_core_temp_C: number;
  final_core_temp_C: number;
  initial_heart_rate_bpm: number;
  final_heart_rate_bpm: number;
}): PsiResult {
  const { initial_core_temp_C, final_core_temp_C, initial_heart_rate_bpm, final_heart_rate_bpm } =
    args;

  for (const [name, v] of Object.entries(args)) {
    if (!Number.isFinite(v)) {
      throw new Error(`${name} must be a finite number`);
    }
  }
  if (initial_core_temp_C >= 39) {
    throw new Error('initial_core_temp_C must be < 39 °C (PSI asymptote)');
  }
  if (initial_heart_rate_bpm >= 180) {
    throw new Error('initial_heart_rate_bpm must be < 180 bpm (PSI asymptote)');
  }

  const coreComp = (5 * (final_core_temp_C - initial_core_temp_C)) / (39 - initial_core_temp_C);
  const hrComp =
    (5 * (final_heart_rate_bpm - initial_heart_rate_bpm)) / (180 - initial_heart_rate_bpm);
  const psi = Math.max(0, Math.min(10, coreComp + hrComp));

  let category: PsiCategory;
  if (psi < 2) category = 'no_strain';
  else if (psi < 4) category = 'low_strain';
  else if (psi < 6) category = 'moderate_strain';
  else if (psi < 8) category = 'high_strain';
  else category = 'very_high_strain';

  return {
    psi,
    category,
    core_component: coreComp,
    heart_rate_component: hrComp,
  };
}

// ---------------------------------------------------------------------------
// Sweat-rate prediction — Gonzalez et al. (2009) / Sawka extension
// ---------------------------------------------------------------------------

export interface SweatRateGonzalez2009Inputs {
  /** Required evaporation, W/m². */
  e_req_w_m2: number;
  /** Maximum evaporative capacity of the environment, W/m². */
  e_max_w_m2: number;
  /** Body surface area, m² (used to convert g·m⁻²·h⁻¹ → L/h). */
  bsa_m2?: number;
}

export interface SweatRateGonzalez2009Result {
  /** Mass-rate of sweat per unit body surface area, g·m⁻²·h⁻¹. */
  m_sw_g_m2_h: number;
  /** Whole-body sweat rate, L/h (only when `bsa_m2` is supplied). */
  m_sw_L_h: number | null;
}

/**
 * Whole-body sweat-rate prediction — Gonzalez et al. (2009).
 *
 *   m_sw (g·m⁻²·h⁻¹) = 147 + 1.527·E_req − 0.87·E_max
 *
 * Validated against laboratory and field exercise data including Sawka et al.
 * later refinements; integrates required evaporation and the environment's
 * maximum evaporative capacity.
 *
 * Reference:
 *   Gonzalez R.R., Cheuvront S.N., Montain S.J., Goodman D.A., Blanchard L.A.,
 *   Berglund L.G., Sawka M.N. (2009). Expanded prediction equations of human
 *   sweat loss and water needs. J. Appl. Physiol. 107(2):379–388.
 *   https://doi.org/10.1152/japplphysiol.00089.2009
 */
export function sweatRateGonzalez2009(
  args: SweatRateGonzalez2009Inputs
): SweatRateGonzalez2009Result {
  const { e_req_w_m2, e_max_w_m2, bsa_m2 } = args;
  if (!Number.isFinite(e_req_w_m2) || !Number.isFinite(e_max_w_m2)) {
    throw new Error('e_req_w_m2 and e_max_w_m2 must be finite numbers');
  }
  const m_sw = 147 + 1.527 * e_req_w_m2 - 0.87 * e_max_w_m2;
  const positive = Math.max(0, m_sw);

  let m_sw_L_h: number | null = null;
  if (bsa_m2 !== undefined) {
    if (!Number.isFinite(bsa_m2) || bsa_m2 <= 0) {
      throw new Error('bsa_m2 must be a finite, positive number');
    }
    m_sw_L_h = (positive * bsa_m2) / 1000;
  }

  return { m_sw_g_m2_h: positive, m_sw_L_h };
}

// ---------------------------------------------------------------------------
// PHS-HR (Predicted Heat Strain using Heart Rate) — Malchaire 2006
// ---------------------------------------------------------------------------

export type PhsHrTempRisk = 'low' | 'moderate' | 'high' | 'very_high';
export type PhsHrStrainRisk = 'low' | 'moderate' | 'high' | 'very_high';
export type PhsHrSweatRisk = 'low' | 'moderate' | 'high' | 'very_high';

export interface PhsHrInputs {
  /** Air temperature, °C. */
  air_temp_C: number;
  /** Mean radiant temperature, °C. */
  mean_radiant_temp_C: number;
  /** Ambient water-vapour pressure, kPa. */
  vapor_pressure_kPa: number;
  /** Air velocity, m/s. */
  air_velocity_m_s: number;
  /** Current heart rate, bpm. */
  hr_bpm: number;
  /** Resting heart rate, bpm. */
  hr_rest_bpm: number;
  /** Clothing insulation, clo. */
  clothing_clo: number;
  /** Age, years. */
  age_years: number;
  /** Body weight, kg. */
  weight_kg: number;
  /** Skin temperature assumption, °C (default 35.0). */
  skin_temp_C?: number;
  /** Exposure duration, minutes (default 60). */
  duration_min?: number;
}

export interface PhsHrHeatExchanges {
  metabolic_rate_W_m2: number;
  convective_W_m2: number;
  radiative_W_m2: number;
  evaporative_required_W_m2: number;
  evaporative_max_W_m2: number;
  evaporative_actual_W_m2: number;
  heat_storage_W_m2: number;
  skin_temp_C: number;
}

export interface PhsHrResult {
  heat_exchanges: PhsHrHeatExchanges;
  core_temperature_rise_C: number;
  predicted_core_temp_C: number;
  heart_rate_strain: number;
  predicted_sweat_rate_L_h: number;
  heat_strain_index: number;
  duration_min: number;
  interpretation: {
    core_temperature_risk: PhsHrTempRisk;
    heat_strain_risk: PhsHrStrainRisk;
    sweat_rate_risk: PhsHrSweatRisk;
    recommendations: string[];
  };
}

const PHS_HR_DELTA_HV_KJ_KG = 2454; // Latent heat of vaporization
const PHS_HR_SIGMA_W_M2_K4 = 5.67e-8;
const PHS_HR_CSP_BODY_KJ_KG_K = 3.5;

function ensureRange(name: string, value: number, lo: number, hi: number): number {
  if (!Number.isFinite(value) || value < lo || value > hi) {
    throw new Error(`${name} must be a finite number in [${lo}, ${hi}]`);
  }
  return value;
}

function phsHrInterpret(result: {
  predicted_core_temp_C: number;
  heat_strain_index: number;
  predicted_sweat_rate_L_h: number;
  heat_exchanges: PhsHrHeatExchanges;
}): PhsHrResult['interpretation'] {
  const core = result.predicted_core_temp_C;
  const strain = result.heat_strain_index;
  const sweat = result.predicted_sweat_rate_L_h;

  let temp_risk: PhsHrTempRisk;
  if (core < 37.5) temp_risk = 'low';
  else if (core < 38.0) temp_risk = 'moderate';
  else if (core < 38.5) temp_risk = 'high';
  else temp_risk = 'very_high';

  let strain_risk: PhsHrStrainRisk;
  if (strain < 2) strain_risk = 'low';
  else if (strain < 4) strain_risk = 'moderate';
  else if (strain < 6) strain_risk = 'high';
  else strain_risk = 'very_high';

  let sweat_risk: PhsHrSweatRisk;
  if (sweat < 0.5) sweat_risk = 'low';
  else if (sweat < 1.0) sweat_risk = 'moderate';
  else if (sweat < 1.5) sweat_risk = 'high';
  else sweat_risk = 'very_high';

  const recs: string[] = [];
  if (core > 38.0) recs.push('Implement active cooling measures immediately');
  if (strain > 4) {
    recs.push('Reduce work intensity or duration');
    recs.push('Increase rest periods in cool environment');
  }
  if (sweat > 1.0) {
    recs.push(`Ensure fluid replacement rate of at least ${(sweat * 1.5).toFixed(2)} L/h`);
  }
  if (
    result.heat_exchanges.evaporative_required_W_m2 >
    result.heat_exchanges.evaporative_max_W_m2
  ) {
    recs.push('Consider lighter, more breathable clothing');
    recs.push('Increase air movement if possible');
  }
  return {
    core_temperature_risk: temp_risk,
    heat_strain_risk: strain_risk,
    sweat_rate_risk: sweat_risk,
    recommendations: recs,
  };
}

/**
 * Predicted Heat Strain using Heart Rate (PHS-HR).
 *
 * Heart-rate-derived metabolic rate fed into a simplified PHS-style heat
 * balance to estimate core-temperature rise, sweat rate, and a 0–10 heat
 * strain index. Distinct from the ISO 7933 PHS implementation in
 * `predictedHeatStrain`, which is metabolic-rate-driven.
 *
 * References:
 *   ISO 7933:2004 — Ergonomics of the thermal environment.
 *   Malchaire J. (2006). Predicted Heat Strain Model.
 *
 * SCOPE: research/education. Validate site-specific assumptions before use.
 */
export function phsHrModel(inputs: PhsHrInputs): PhsHrResult {
  ensureRange('air_temp_C', inputs.air_temp_C, 0, 60);
  ensureRange('mean_radiant_temp_C', inputs.mean_radiant_temp_C, 0, 80);
  ensureRange('vapor_pressure_kPa', inputs.vapor_pressure_kPa, 0, 10);
  ensureRange('air_velocity_m_s', inputs.air_velocity_m_s, 0, 5);
  ensureRange('hr_bpm', inputs.hr_bpm, 50, 200);
  ensureRange('hr_rest_bpm', inputs.hr_rest_bpm, 40, 100);
  ensureRange('clothing_clo', inputs.clothing_clo, 0, 3);
  ensureRange('age_years', inputs.age_years, 18, 70);
  ensureRange('weight_kg', inputs.weight_kg, 40, 150);

  const tsk = inputs.skin_temp_C ?? 35.0;
  const duration_min = inputs.duration_min ?? 60;
  if (!Number.isFinite(duration_min) || duration_min <= 0) {
    throw new Error('duration_min must be a finite, positive number');
  }

  // Heat-transfer coefficients
  const hc = 8.3 * Math.pow(inputs.air_velocity_m_s, 0.6);
  const he = 16.5 * hc;

  // Metabolic rate from HR ratio (capped at 400 W/m²)
  let M = 58.2; // resting baseline
  const hr_max = 220 - inputs.age_years;
  const hr_reserve = hr_max - inputs.hr_rest_bpm;
  if (inputs.hr_bpm > inputs.hr_rest_bpm && hr_reserve > 0) {
    const ratio = (inputs.hr_bpm - inputs.hr_rest_bpm) / hr_reserve;
    M = Math.min(400, 58.2 + ratio * (300 - 58.2));
  }

  // Clothing factors
  const Rcl = inputs.clothing_clo * 0.155; // m²·K/W
  const permeability = 0.45 + 0.55 * Math.exp(-0.3 * inputs.clothing_clo);

  // Convective heat exchange
  const C = (hc * (tsk - inputs.air_temp_C)) / (1 + hc * Rcl);

  // Linearized radiative coefficient and exchange
  const Tmrt_K = inputs.mean_radiant_temp_C + 273.15;
  const hr_rad =
    (4 * PHS_HR_SIGMA_W_M2_K4 * Math.pow(Tmrt_K, 3)) /
    (1 + Rcl * 4 * PHS_HR_SIGMA_W_M2_K4 * Math.pow(Tmrt_K, 3));
  const R = hr_rad * (tsk - inputs.mean_radiant_temp_C);

  // Required evaporation, max evaporation, actual evaporation
  const E_req = M - C - R;
  const psk_sat = 0.6105 * Math.exp((17.27 * tsk) / (tsk + 237.3));
  const E_max = he * (psk_sat - inputs.vapor_pressure_kPa) * permeability;
  const E_act = Math.min(E_req, E_max);

  // Heat storage and core temperature rise
  const S = M - C - R - E_act;
  const dT_core =
    (S * duration_min * 60) / (inputs.weight_kg * PHS_HR_CSP_BODY_KJ_KG_K * 1000);
  const T_core_final = 37.0 + dT_core;

  // Heart-rate strain and sweat rate
  const hr_strain = (inputs.hr_bpm - inputs.hr_rest_bpm) / Math.max(1e-9, hr_max - inputs.hr_rest_bpm);
  const sweat = Math.max(0, E_act / PHS_HR_DELTA_HV_KJ_KG);

  // 0–10 heat strain index
  const hsi = Math.min(
    10,
    Math.max(0, 5 * ((T_core_final - 37) / 2) + 5 * Math.max(0, hr_strain))
  );

  const heat_exchanges: PhsHrHeatExchanges = {
    metabolic_rate_W_m2: M,
    convective_W_m2: C,
    radiative_W_m2: R,
    evaporative_required_W_m2: E_req,
    evaporative_max_W_m2: E_max,
    evaporative_actual_W_m2: E_act,
    heat_storage_W_m2: S,
    skin_temp_C: tsk,
  };

  const partial = {
    predicted_core_temp_C: T_core_final,
    heat_strain_index: hsi,
    predicted_sweat_rate_L_h: sweat,
    heat_exchanges,
  };

  return {
    heat_exchanges,
    core_temperature_rise_C: dT_core,
    predicted_core_temp_C: T_core_final,
    heart_rate_strain: hr_strain,
    predicted_sweat_rate_L_h: sweat,
    heat_strain_index: hsi,
    duration_min,
    interpretation: phsHrInterpret(partial),
  };
}

// ---------------------------------------------------------------------------
// Ontario sweat-rate estimator — Malpica (legacy)
// ---------------------------------------------------------------------------

/**
 * Ontario sweat-rate estimator (Diego Malpica's legacy implementation).
 *
 *   sweat_L_h = 0.019 · BSA_m² · (Δhr · Δt) / (hr_rest · t_rest)
 *
 * Where Δhr = hr_exercise − hr_rest, Δt = t_exercise − t_rest, and
 * BSA_m² is supplied by the caller (e.g. via `bsaMosteller`). Returns
 * sweat rate in L/h (the legacy script multiplies by 1000 only for mL/h
 * display).
 *
 * NOTE: this empirical estimator is included for parity with the legacy
 * Streamlit suite. For research-grade prediction prefer `sweatRateGonzalez2009`.
 */
export function ontarioSweatRate(args: {
  bsa_m2: number;
  hr_rest_bpm: number;
  hr_exercise_bpm: number;
  t_rest_C: number;
  t_exercise_C: number;
}): { sweat_rate_L_h: number; sweat_rate_mL_h: number } {
  const { bsa_m2, hr_rest_bpm, hr_exercise_bpm, t_rest_C, t_exercise_C } = args;
  if (!Number.isFinite(bsa_m2) || bsa_m2 <= 0) {
    throw new Error('bsa_m2 must be a finite, positive number');
  }
  if (!Number.isFinite(hr_rest_bpm) || hr_rest_bpm <= 0) {
    throw new Error('hr_rest_bpm must be a finite, positive number');
  }
  if (!Number.isFinite(hr_exercise_bpm) || hr_exercise_bpm <= 0) {
    throw new Error('hr_exercise_bpm must be a finite, positive number');
  }
  if (!Number.isFinite(t_rest_C) || t_rest_C === 0) {
    throw new Error('t_rest_C must be finite and non-zero (Kelvin should be used to avoid this)');
  }
  if (!Number.isFinite(t_exercise_C)) {
    throw new Error('t_exercise_C must be a finite number');
  }
  const dHR = hr_exercise_bpm - hr_rest_bpm;
  const dT = t_exercise_C - t_rest_C;
  const sweat_L_h = (0.019 * bsa_m2 * (dHR * dT)) / (hr_rest_bpm * t_rest_C);
  return { sweat_rate_L_h: sweat_L_h, sweat_rate_mL_h: sweat_L_h * 1000 };
}
