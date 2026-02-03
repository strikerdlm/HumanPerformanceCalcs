/**
 * International Standard Atmosphere (ISA) and atmospheric calculations
 * 
 * References:
 * - ISO 2533:1975 International Standard Atmosphere
 * - West, J.B. (2011). Respiratory Physiology: The Essentials (9th ed.)
 */

export interface ISAResult {
  temperature_C: number;
  temperature_K: number;
  pressure_Pa: number;
  pressure_hPa: number;
  pressure_mmHg: number;
  density_kg_m3: number;
  pO2_Pa: number;
  pO2_mmHg: number;
  altitude_m: number;
  altitude_ft: number;
}

// ISA constants
const SEA_LEVEL_TEMP_K = 288.15; // 15°C
const SEA_LEVEL_PRESSURE_PA = 101325;
const LAPSE_RATE = 0.0065; // K/m for troposphere
const GAS_CONSTANT = 287.058; // J/(kg·K) for dry air
const GRAVITY = 9.80665; // m/s²
const O2_FRACTION = 0.2095;
const TROPOPAUSE_M = 11000;
const TROPOPAUSE_TEMP_K = 216.65;

/**
 * Calculate International Standard Atmosphere properties
 * 
 * @param altitude_m - Altitude in meters (0-47000m supported)
 * @returns ISA properties at the given altitude
 */
export function standardAtmosphere(altitude_m: number): ISAResult {
  if (altitude_m < 0) {
    throw new Error('Altitude must be non-negative');
  }
  if (altitude_m > 47000) {
    throw new Error('Altitude must be below 47000m');
  }

  let temperature_K: number;
  let pressure_Pa: number;

  if (altitude_m <= TROPOPAUSE_M) {
    // Troposphere (0-11km): linear temperature decrease
    temperature_K = SEA_LEVEL_TEMP_K - LAPSE_RATE * altitude_m;
    pressure_Pa = SEA_LEVEL_PRESSURE_PA * 
      Math.pow(temperature_K / SEA_LEVEL_TEMP_K, GRAVITY / (LAPSE_RATE * GAS_CONSTANT));
  } else if (altitude_m <= 20000) {
    // Lower stratosphere (11-20km): isothermal
    temperature_K = TROPOPAUSE_TEMP_K;
    const p_tropopause = SEA_LEVEL_PRESSURE_PA * 
      Math.pow(TROPOPAUSE_TEMP_K / SEA_LEVEL_TEMP_K, GRAVITY / (LAPSE_RATE * GAS_CONSTANT));
    pressure_Pa = p_tropopause * 
      Math.exp(-GRAVITY * (altitude_m - TROPOPAUSE_M) / (GAS_CONSTANT * TROPOPAUSE_TEMP_K));
  } else if (altitude_m <= 32000) {
    // Upper stratosphere (20-32km): warming layer
    const STRAT_LAPSE = -0.001; // -1 K/km (warming)
    const ALT_20KM = 20000;
    const TEMP_20KM = TROPOPAUSE_TEMP_K;
    
    temperature_K = TEMP_20KM + STRAT_LAPSE * (altitude_m - ALT_20KM);
    
    const p_tropopause = SEA_LEVEL_PRESSURE_PA * 
      Math.pow(TROPOPAUSE_TEMP_K / SEA_LEVEL_TEMP_K, GRAVITY / (LAPSE_RATE * GAS_CONSTANT));
    const p_20km = p_tropopause * 
      Math.exp(-GRAVITY * (ALT_20KM - TROPOPAUSE_M) / (GAS_CONSTANT * TROPOPAUSE_TEMP_K));
    
    if (Math.abs(STRAT_LAPSE) < 1e-9) {
      pressure_Pa = p_20km * Math.exp(-GRAVITY * (altitude_m - ALT_20KM) / (GAS_CONSTANT * TEMP_20KM));
    } else {
      pressure_Pa = p_20km * 
        Math.pow(temperature_K / TEMP_20KM, -GRAVITY / (STRAT_LAPSE * GAS_CONSTANT));
    }
  } else {
    // Higher altitudes (simplified)
    temperature_K = 228.65;
    pressure_Pa = 868.02 * Math.exp(-GRAVITY * (altitude_m - 32000) / (GAS_CONSTANT * 228.65));
  }

  const temperature_C = temperature_K - 273.15;
  const pressure_hPa = pressure_Pa / 100;
  const pressure_mmHg = pressure_Pa / 133.322;
  const density = pressure_Pa / (GAS_CONSTANT * temperature_K);
  const pO2_Pa = pressure_Pa * O2_FRACTION;
  const pO2_mmHg = pO2_Pa / 133.322;

  return {
    temperature_C,
    temperature_K,
    pressure_Pa,
    pressure_hPa,
    pressure_mmHg,
    density_kg_m3: density,
    pO2_Pa,
    pO2_mmHg,
    altitude_m,
    altitude_ft: altitude_m / 0.3048,
  };
}

/**
 * Calculate inspired oxygen partial pressure (PiO₂)
 * 
 * @param altitude_m - Altitude in meters
 * @param FiO2 - Fraction of inspired oxygen (default 0.21)
 * @returns PiO₂ in mmHg
 */
export function inspiredPO2(altitude_m: number, FiO2: number = 0.21): number {
  if (FiO2 < 0 || FiO2 > 1) {
    throw new Error('FiO2 must be between 0 and 1');
  }
  
  const isa = standardAtmosphere(altitude_m);
  const PH2O = 47; // Water vapor pressure at body temperature (mmHg)
  return FiO2 * (isa.pressure_mmHg - PH2O);
}

/**
 * Calculate alveolar oxygen pressure (PAO₂) using the alveolar gas equation
 * 
 * Reference: West, J.B. (2011). Respiratory Physiology
 * 
 * @param altitude_m - Altitude in meters
 * @param FiO2 - Fraction of inspired oxygen
 * @param PaCO2 - Arterial CO₂ pressure in mmHg
 * @param RQ - Respiratory quotient (typically 0.8)
 * @returns PAO₂ in mmHg
 */
export function alveolarPO2(
  altitude_m: number,
  FiO2: number = 0.21,
  PaCO2: number = 40,
  RQ: number = 0.8
): number {
  if (RQ <= 0) {
    throw new Error('RQ must be positive');
  }
  
  const PiO2 = inspiredPO2(altitude_m, FiO2);
  return PiO2 - (PaCO2 / RQ);
}

/**
 * Estimate SpO₂ for unacclimatized individuals at altitude
 * 
 * Reference: West, J.B. & Schoene, R.B. (2001). High Altitude Medicine and Physiology
 * 
 * @param altitude_m - Altitude in meters
 * @returns Estimated SpO₂ percentage
 */
export function spo2Unacclimatized(altitude_m: number): number {
  if (altitude_m <= 0) return 98;
  
  // Empirical fit based on altitude physiology data
  // Uses sigmoid-like decay model
  const x = altitude_m / 1000;
  
  if (x <= 1.5) {
    return 98 - 0.5 * x;
  } else if (x <= 3) {
    return 97.25 - 1.5 * (x - 1.5);
  } else if (x <= 5) {
    return 95 - 3.5 * (x - 3);
  } else if (x <= 7) {
    return 88 - 5 * (x - 5);
  } else {
    return Math.max(40, 78 - 4 * (x - 7));
  }
}

/**
 * Estimate SpO₂ for acclimatized individuals at altitude
 * 
 * @param altitude_m - Altitude in meters
 * @returns Estimated SpO₂ percentage
 */
export function spo2Acclimatized(altitude_m: number): number {
  const unacclimated = spo2Unacclimatized(altitude_m);
  // Acclimatization provides ~3-5% improvement
  const improvement = Math.min(5, altitude_m / 1000);
  return Math.min(98, unacclimated + improvement);
}

/**
 * Estimate oxygen content (CaO₂) in blood
 * 
 * @param Hb - Hemoglobin concentration (g/dL)
 * @param SaO2_percent - Oxygen saturation (%)
 * @param PaO2 - Arterial oxygen pressure (mmHg)
 * @returns CaO₂ in mL/dL
 */
export function oxygenContent(
  Hb: number,
  SaO2_percent: number,
  PaO2: number
): number {
  if (Hb < 0 || SaO2_percent < 0 || SaO2_percent > 100 || PaO2 < 0) {
    throw new Error('Invalid input parameters');
  }
  
  const HUFNER_CONSTANT = 1.34; // mL O₂/g Hb
  const ALPHA = 0.003; // mL O₂/dL/mmHg (dissolved O₂)
  
  const boundO2 = HUFNER_CONSTANT * Hb * (SaO2_percent / 100);
  const dissolvedO2 = ALPHA * PaO2;
  
  return boundO2 + dissolvedO2;
}

/**
 * Calculate tissue ratio for decompression assessment
 * 
 * @param PtissueN2 - Tissue nitrogen partial pressure (mmHg)
 * @param Pambient - Ambient pressure (mmHg)
 * @returns Tissue ratio (TR)
 */
export function tissueRatio(PtissueN2: number, Pambient: number): number {
  if (Pambient <= 0) {
    throw new Error('Ambient pressure must be positive');
  }
  return PtissueN2 / Pambient;
}

/**
 * Interpret tissue ratio for DCS risk
 * 
 * @param tr - Tissue ratio
 * @returns Risk interpretation string
 */
export function interpretTR(tr: number): string {
  if (tr < 1.5) return 'Low risk';
  if (tr < 1.7) return 'Moderate risk';
  if (tr < 2.0) return 'Elevated risk';
  return 'High risk';
}

/**
 * Estimate Acute Mountain Sickness (AMS) probability
 * 
 * Reference: Roach, R.C. et al. (1993). Lake Louise scoring system
 * 
 * @param accumulatedAltitudeExposure - AAE in km·days
 * @returns Probability of AMS (0-1)
 */
export function amsProbability(accumulatedAltitudeExposure: number): number {
  if (accumulatedAltitudeExposure < 0) return 0;
  
  // Logistic model fit to epidemiological data
  const k = 0.8; // Steepness
  const x0 = 2.5; // Midpoint (50% probability)
  
  return 1 / (1 + Math.exp(-k * (accumulatedAltitudeExposure - x0)));
}

/**
 * Estimate Time of Useful Consciousness (TUC) at altitude
 * 
 * Reference: Ernsting, J. & Nicholson, A.N. (2016). Aviation Medicine
 * 
 * @param altitude_ft - Altitude in feet
 * @returns TUC in seconds
 */
export function estimateTUC(altitude_ft: number): number {
  // Reference TUC values (USAF)
  const TUC_TABLE: [number, number][] = [
    [18000, Infinity],
    [22000, 600], // 10 min
    [25000, 300], // 5 min
    [28000, 150], // 2.5 min
    [30000, 90],  // 1.5 min
    [35000, 45],  // 45 sec
    [40000, 20],  // 20 sec
    [43000, 12],  // 12 sec
    [45000, 9],   // 9 sec
    [50000, 5],   // 5 sec
  ];

  if (altitude_ft <= TUC_TABLE[0][0]) {
    return Infinity;
  }
  
  if (altitude_ft >= TUC_TABLE[TUC_TABLE.length - 1][0]) {
    return TUC_TABLE[TUC_TABLE.length - 1][1];
  }

  // Linear interpolation
  for (let i = 0; i < TUC_TABLE.length - 1; i++) {
    const [alt1, tuc1] = TUC_TABLE[i];
    const [alt2, tuc2] = TUC_TABLE[i + 1];
    
    if (altitude_ft >= alt1 && altitude_ft < alt2) {
      if (!isFinite(tuc1)) return Infinity;
      const ratio = (altitude_ft - alt1) / (alt2 - alt1);
      return tuc1 + ratio * (tuc2 - tuc1);
    }
  }
  
  return 5;
}

/**
 * Estimate G-LOC time at sustained +Gz
 * 
 * Reference: Whinnery, J.E. & Forster, E.M. (2006). Aviation, Space, and Environmental Medicine
 * 
 * @param Gz - Sustained G-force (positive)
 * @returns Time to G-LOC in seconds
 */
export function gLocTime(Gz: number): number {
  if (Gz < 1) return Infinity;
  if (Gz < 5) return Infinity; // Below ~5g, many tolerate indefinitely
  
  // Simplified Stoll curve approximation
  // Higher G = shorter tolerance
  const tolerance = 150 / Math.pow(Gz - 4, 1.5);
  return Math.max(3, tolerance);
}

/**
 * Calculate cosmic radiation dose rate at altitude
 * 
 * Reference: Friedberg, W. et al. (1992). Radiation Protection Dosimetry
 * 
 * @param altitude_ft - Altitude in feet
 * @param isPolar - Whether flying polar route (>60° latitude)
 * @returns Dose rate in µSv/h
 */
export function cosmicDoseRate(altitude_ft: number, isPolar: boolean = false): number {
  // Simplified linear model
  // Real models use CARI-7 or similar
  const baseRate = 0.05; // µSv/h at sea level
  const altitudeMultiplier = 0.1 / 10000; // Increase per 10000 ft
  
  let rate = baseRate + altitude_ft * altitudeMultiplier;
  
  if (isPolar) {
    rate *= 1.5; // Polar routes have ~50% higher exposure
  }
  
  return rate;
}

// Utility functions
export function metersToFeet(meters: number): number {
  return meters / 0.3048;
}

export function feetToMeters(feet: number): number {
  return feet * 0.3048;
}

export function pascalToMmHg(pa: number): number {
  return pa / 133.322;
}

export function mmHgToPascal(mmHg: number): number {
  return mmHg * 133.322;
}
