/**
 * Cold-exposure physiology calculators.
 *
 * Includes:
 *   - peakShiveringIntensity : VO₂max / BMI / age regression
 *   - windChillTemperature   : National Weather Service 2001 formula (Osczevski
 *                              & Bluestein), returning index in °F and °C
 *   - frostbiteRiskFromWindChill : risk categorization per the NWS frostbite
 *                              time chart anchored to the wind-chill index
 *   - frostbiteTimeMinutes   : Tikuisis (2002) facial-skin frostbite-time fit
 *
 * References:
 *   Osczevski R., Bluestein M. (2005). The new wind chill equivalent
 *     temperature chart. Bull. Amer. Meteor. Soc. 86:1453–1458.
 *   National Weather Service (2001). New Wind Chill Temperature Index.
 *   Tikuisis P. (1996, updated 2002). Heat balance precludes hypothermia in
 *     men immersed in cold water; and Polar Biol. 25(4):243–250.
 */

export type FrostbiteRisk =
  | 'low'
  | 'increased'
  | 'high'
  | 'very_high'
  | 'severe';

export interface WindChillResult {
  /** Wind-chill index in °F (NWS 2001 formula). */
  wind_chill_F: number;
  /** Wind-chill index in °C. */
  wind_chill_C: number;
  /** True when conditions fall outside the formula's valid envelope. */
  out_of_range: boolean;
  /** Plain-English note when out_of_range = true. */
  note: string;
}

/**
 * Predict peak shivering intensity (mL O₂·kg⁻¹·min⁻¹).
 *
 * Shiv_peak = 30.5 + 0.348·VO₂max − 0.909·BMI − 0.233·Age
 */
export function peakShiveringIntensity(
  vo2max_mlkgmin: number,
  bmi: number,
  age_years: number
): number {
  return (
    30.5 +
    0.348 * Number(vo2max_mlkgmin) -
    0.909 * Number(bmi) -
    0.233 * Number(age_years)
  );
}

/**
 * National Weather Service (2001) Wind Chill Temperature.
 *
 *   WC_°F = 35.74 + 0.6215·T_°F − 35.75·V_mph^0.16 + 0.4275·T_°F·V_mph^0.16
 *
 * Validity envelope: T ≤ 50 °F (10 °C) AND V ≥ 3 mph (~4.8 km/h). Outside
 * the envelope the function returns the air temperature plus an
 * `out_of_range` flag.
 */
export function windChillTemperature(args: {
  temperature_C: number;
  /** Wind speed in m/s. */
  wind_speed_m_s: number;
}): WindChillResult {
  const { temperature_C, wind_speed_m_s } = args;
  if (!Number.isFinite(temperature_C) || !Number.isFinite(wind_speed_m_s) || wind_speed_m_s < 0) {
    throw new Error('temperature_C and wind_speed_m_s must be finite, with wind_speed_m_s >= 0');
  }
  const tempF = temperature_C * 9 / 5 + 32;
  const windMph = wind_speed_m_s * 2.23694;

  if (tempF > 50 || windMph < 3) {
    return {
      wind_chill_F: tempF,
      wind_chill_C: temperature_C,
      out_of_range: true,
      note: 'NWS formula valid only for T ≤ 50 °F (10 °C) and V ≥ 3 mph (4.8 km/h)',
    };
  }

  const vPow = Math.pow(windMph, 0.16);
  const wcF = 35.74 + 0.6215 * tempF - 35.75 * vPow + 0.4275 * tempF * vPow;
  return {
    wind_chill_F: wcF,
    wind_chill_C: ((wcF - 32) * 5) / 9,
    out_of_range: false,
    note: '',
  };
}

/**
 * Frostbite risk category from the wind-chill index, anchored to the NWS
 * frostbite-time chart (Osczevski & Bluestein 2005).
 *
 *   ≥ −27 °C : low (≥30 min exposure to onset)
 *   −27 to −39 °C : increased (10–30 min)
 *   −39 to −47 °C : high (5–10 min)
 *   −47 to −54 °C : very high (2–5 min)
 *   < −54 °C : severe (<2 min)
 */
export function frostbiteRiskFromWindChill(wind_chill_C: number): FrostbiteRisk {
  if (!Number.isFinite(wind_chill_C)) {
    throw new Error('wind_chill_C must be finite');
  }
  if (wind_chill_C >= -27) return 'low';
  if (wind_chill_C >= -39) return 'increased';
  if (wind_chill_C >= -47) return 'high';
  if (wind_chill_C >= -54) return 'very_high';
  return 'severe';
}

/**
 * Tikuisis (2002) facial-skin frostbite-time estimate.
 *
 *   FT_min = ((-24.5 · (0.667·V_kmh + 4.8)^0.16) + 2111) · (-T_°C − 4.8)^(-1.668)
 *
 * Defined only for T_°C < -4.8 °C (above this temperature frostbite is not
 * predicted in still or moving air); otherwise returns Infinity.
 *
 * Reference: Tikuisis P. (2002). Predicting onset of frostbite. Polar Biol.
 * 25:243–250. https://doi.org/10.1007/s00300-001-0335-x
 */
export function frostbiteTimeMinutes(args: {
  temperature_C: number;
  /** Wind speed in m/s (converted internally to km/h). */
  wind_speed_m_s: number;
}): number {
  const { temperature_C, wind_speed_m_s } = args;
  if (!Number.isFinite(temperature_C)) {
    throw new Error('temperature_C must be finite');
  }
  if (!Number.isFinite(wind_speed_m_s) || wind_speed_m_s < 0) {
    throw new Error('wind_speed_m_s must be finite and >= 0');
  }
  if (temperature_C >= -4.8) return Infinity;
  const v_kmh = wind_speed_m_s * 3.6;
  const term1 = -24.5 * Math.pow(0.667 * v_kmh + 4.8, 0.16) + 2111;
  const term2 = Math.pow(-temperature_C - 4.8, -1.668);
  return Math.max(0, term1 * term2);
}
