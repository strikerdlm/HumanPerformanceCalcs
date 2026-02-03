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
