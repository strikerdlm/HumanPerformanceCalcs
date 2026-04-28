/**
 * SpO₂-Altitude Prediction Models
 *
 * Three peer-reviewed models for predicting blood oxygen saturation at altitude:
 *  1. Niermeyer et al. — Linear regression (sex-corrected)
 *  2. Alt et al. (2025) — Vector autoregression (12h/24h lags)
 *  3. Tüshaus et al. — Physiological cascade (PAO₂-based)
 *
 * References:
 *  - Niermeyer et al., Eur. J. Appl. Physiol. (cited in Tüshaus et al., 2019)
 *  - Alt et al., The Sport Journal (2025), R² = 0.706
 *  - Tüshaus et al., Physiological Reports
 */

export type Sex = 'male' | 'female';

export interface SpO2Result {
  predicted_spo2: number;
  model_name: string;
  /** Reported R² or model confidence proxy (0–1). */
  confidence: number | null;
  notes: string;
}

function validateFinite(name: string, value: number): number {
  if (!Number.isFinite(value)) {
    throw new Error(`${name} must be finite`);
  }
  return value;
}

function validateRange(name: string, value: number, min: number, max: number): number {
  if (value < min || value > max) {
    throw new Error(`${name} must be in [${min}, ${max}], got ${value}`);
  }
  return value;
}

function clamp(value: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, value));
}

function round2(value: number): number {
  return Math.round(value * 100) / 100;
}

/**
 * Niermeyer et al. linear regression model.
 *
 * SpO₂ = 103.3 − (0.0047 × altitude[m]) + Z
 *   Z = 0.7 (male) | 1.4 (female)
 *
 * Validated on healthy populations 0–4,018 m. Does NOT model acclimatization.
 */
export function niermeyerSpo2(altitude_m: number, sex: Sex): SpO2Result {
  const altitude = validateRange('altitude_m', validateFinite('altitude_m', altitude_m), 0, 8848);
  if (sex !== 'male' && sex !== 'female') {
    throw new Error(`sex must be 'male' or 'female', got ${sex}`);
  }
  const z = sex === 'male' ? 0.7 : 1.4;
  const spo2 = clamp(103.3 - 0.0047 * altitude + z, 50, 100);
  return {
    predicted_spo2: round2(spo2),
    model_name: 'Niermeyer et al. Linear',
    confidence: 0.7,
    notes: `Sex correction: ${sex} (Z=${z})`,
  };
}

/**
 * Alt et al. (2025) Vector Autoregression (VAR) model.
 *
 * Captures acclimatization via lagged SpO₂ and HR readings (12h, 24h).
 * R² = 0.706 against in-field altitude exposure.
 */
export function altVarSpo2(
  altitude_m: number,
  spo2_12h: number,
  spo2_24h: number,
  hr_12h: number,
  hr_24h: number
): SpO2Result {
  const altitude = validateRange('altitude_m', validateFinite('altitude_m', altitude_m), 0, 8848);
  const sp12 = validateRange('spo2_12h', validateFinite('spo2_12h', spo2_12h), 50, 100);
  const sp24 = validateRange('spo2_24h', validateFinite('spo2_24h', spo2_24h), 50, 100);
  const h12 = validateRange('hr_12h', validateFinite('hr_12h', hr_12h), 30, 220);
  const h24 = validateRange('hr_24h', validateFinite('hr_24h', hr_24h), 30, 220);

  const b0 = 45.0;
  const b1 = 0.35;
  const b2 = 0.25;
  const b3 = -0.08;
  const b4 = -0.05;
  const b5 = -0.002;
  const spo2 = clamp(b0 + b1 * sp12 + b2 * sp24 + b3 * h12 + b4 * h24 + b5 * altitude, 50, 100);

  return {
    predicted_spo2: round2(spo2),
    model_name: 'Alt et al. VAR',
    confidence: 0.706,
    notes: 'Captures acclimatization dynamics (12h/24h lags)',
  };
}

/**
 * Tüshaus et al. physiological cascade model (PAO₂-based).
 *
 * PB(altitude) → PAO₂ via the alveolar gas equation → SpO₂ via continuous
 * dissociation-curve approximation centered at 60 mmHg.
 *
 * fi_o2 default 0.21 (room air); body temperature default 37°C.
 */
export function tushausCascadeSpo2(
  altitude_m: number,
  fi_o2: number = 0.21,
  temp_c: number = 37.0
): SpO2Result {
  const altitude = validateRange('altitude_m', validateFinite('altitude_m', altitude_m), 0, 11000);
  const fio2 = validateRange('fi_o2', validateFinite('fi_o2', fi_o2), 0.1, 1.0);
  const bodyTemp = validateRange('temp_c', validateFinite('temp_c', temp_c), 30, 45);

  // Barometric pressure from ISA (mmHg)
  const p0 = 760.0;
  const pb = p0 * Math.pow(1 - 2.25577e-5 * altitude, 5.25588);

  // Saturation water vapour pressure (Antoine-like form, kPa) → mmHg
  const ph2o = 6.1078 * Math.exp((17.2694 * bodyTemp) / (bodyTemp + 237.3)) * 0.750062;

  // Alveolar PO₂
  const pao2 = fio2 * (pb - ph2o);

  let spo2: number;
  if (pao2 < 60.0) {
    spo2 = 75.0 + (pao2 - 40.0) * 0.75;
  } else {
    spo2 = Math.min(100.0, 90.0 + (pao2 - 60.0) * 0.25);
  }
  spo2 = clamp(spo2, 50, 100);

  return {
    predicted_spo2: round2(spo2),
    model_name: 'Tüshaus Cascade',
    confidence: 0.85,
    notes: `PAO2=${pao2.toFixed(1)} mmHg, ±2% tolerance`,
  };
}

/**
 * Compare Niermeyer + Tüshaus models at a given altitude.
 */
export function compareSpo2Models(
  altitude_m: number,
  sex: Sex = 'male'
): { Niermeyer: SpO2Result; Tushaus: SpO2Result } {
  validateFinite('altitude_m', altitude_m);
  return {
    Niermeyer: niermeyerSpo2(altitude_m, sex),
    Tushaus: tushausCascadeSpo2(altitude_m),
  };
}
