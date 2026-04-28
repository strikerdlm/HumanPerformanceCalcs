/**
 * US EPA Air Quality Index (AQI), with the February 2024 PM2.5 update.
 *
 * Per-pollutant index from a piecewise-linear interpolation between
 * concentration breakpoints. Overall AQI = max of the sub-indices.
 *
 *   AQI = ((I_high − I_low) / (C_high − C_low)) · (C − C_low) + I_low
 *
 * Breakpoints (EPA AirNow Technical Assistance Document, Feb 2024):
 *   PM2.5 — 24-hour (µg/m³, post-2024 NAAQS strengthening)
 *   PM10  — 24-hour (µg/m³)
 *   O3    — 8-hour (ppm); fall back to 1-hour above 0.200 ppm
 *   CO    — 8-hour (ppm)
 *   SO2   — 1-hour (ppb); fall back to 24-hour above 304 ppb
 *   NO2   — 1-hour (ppb)
 *
 * Categories follow the standard EPA scale (Good → Hazardous).
 *
 * References:
 *   EPA. Technical Assistance Document for the Reporting of Daily Air
 *     Quality (AirNow). 2024.
 *     https://document.airnow.gov/technical-assistance-document-for-the-reporting-of-daily-air-quailty.pdf
 *   EPA. Final Updates to the Air Quality Index for Particulate Matter (Feb 2024).
 *     https://www.epa.gov/system/files/documents/2024-02/pm-naaqs-air-quality-index-fact-sheet.pdf
 */

export type AqiPollutant =
  | 'pm25_24h'
  | 'pm10_24h'
  | 'o3_8h'
  | 'o3_1h'
  | 'co_8h'
  | 'so2_1h'
  | 'so2_24h'
  | 'no2_1h';

export type AqiCategory =
  | 'Good'
  | 'Moderate'
  | 'Unhealthy for Sensitive Groups'
  | 'Unhealthy'
  | 'Very Unhealthy'
  | 'Hazardous';

export interface AqiSubIndex {
  pollutant: AqiPollutant;
  concentration: number;
  units: string;
  aqi: number;
  category: AqiCategory;
}

export interface AqiOverall {
  aqi: number;
  category: AqiCategory;
  dominant: AqiPollutant;
  sub_indices: AqiSubIndex[];
}

interface Breakpoint {
  c_low: number;
  c_high: number;
  i_low: number;
  i_high: number;
}

const AQI_CATEGORY_FOR_INDEX = (i: number): AqiCategory => {
  if (i <= 50) return 'Good';
  if (i <= 100) return 'Moderate';
  if (i <= 150) return 'Unhealthy for Sensitive Groups';
  if (i <= 200) return 'Unhealthy';
  if (i <= 300) return 'Very Unhealthy';
  return 'Hazardous';
};

// Concentrations are rounded/truncated by EPA to specific precisions before
// interpolation. We follow the AirNow technical assistance document.
const POLLUTANT_META: Record<AqiPollutant, { units: string; precision: number }> = {
  pm25_24h: { units: 'µg/m³', precision: 1 },
  pm10_24h: { units: 'µg/m³', precision: 0 },
  o3_8h: { units: 'ppm', precision: 3 },
  o3_1h: { units: 'ppm', precision: 3 },
  co_8h: { units: 'ppm', precision: 1 },
  so2_1h: { units: 'ppb', precision: 0 },
  so2_24h: { units: 'ppb', precision: 0 },
  no2_1h: { units: 'ppb', precision: 0 },
};

// Post-2024 PM2.5 breakpoints (NAAQS strengthening of Feb 2024).
const BREAKPOINTS: Record<AqiPollutant, ReadonlyArray<Breakpoint>> = {
  pm25_24h: [
    { c_low: 0.0, c_high: 9.0, i_low: 0, i_high: 50 },
    { c_low: 9.1, c_high: 35.4, i_low: 51, i_high: 100 },
    { c_low: 35.5, c_high: 55.4, i_low: 101, i_high: 150 },
    { c_low: 55.5, c_high: 125.4, i_low: 151, i_high: 200 },
    { c_low: 125.5, c_high: 225.4, i_low: 201, i_high: 300 },
    { c_low: 225.5, c_high: 325.4, i_low: 301, i_high: 500 },
  ],
  pm10_24h: [
    { c_low: 0, c_high: 54, i_low: 0, i_high: 50 },
    { c_low: 55, c_high: 154, i_low: 51, i_high: 100 },
    { c_low: 155, c_high: 254, i_low: 101, i_high: 150 },
    { c_low: 255, c_high: 354, i_low: 151, i_high: 200 },
    { c_low: 355, c_high: 424, i_low: 201, i_high: 300 },
    { c_low: 425, c_high: 604, i_low: 301, i_high: 500 },
  ],
  // 8-hour O3 caps at AQI 300 (0.200 ppm); above that use 1-hour O3.
  o3_8h: [
    { c_low: 0.0, c_high: 0.054, i_low: 0, i_high: 50 },
    { c_low: 0.055, c_high: 0.07, i_low: 51, i_high: 100 },
    { c_low: 0.071, c_high: 0.085, i_low: 101, i_high: 150 },
    { c_low: 0.086, c_high: 0.105, i_low: 151, i_high: 200 },
    { c_low: 0.106, c_high: 0.2, i_low: 201, i_high: 300 },
  ],
  // 1-hour O3 only used when AQI ≥ 101 (concentrations ≥ 0.125 ppm).
  o3_1h: [
    { c_low: 0.125, c_high: 0.164, i_low: 101, i_high: 150 },
    { c_low: 0.165, c_high: 0.204, i_low: 151, i_high: 200 },
    { c_low: 0.205, c_high: 0.404, i_low: 201, i_high: 300 },
    { c_low: 0.405, c_high: 0.604, i_low: 301, i_high: 500 },
  ],
  co_8h: [
    { c_low: 0.0, c_high: 4.4, i_low: 0, i_high: 50 },
    { c_low: 4.5, c_high: 9.4, i_low: 51, i_high: 100 },
    { c_low: 9.5, c_high: 12.4, i_low: 101, i_high: 150 },
    { c_low: 12.5, c_high: 15.4, i_low: 151, i_high: 200 },
    { c_low: 15.5, c_high: 30.4, i_low: 201, i_high: 300 },
    { c_low: 30.5, c_high: 50.4, i_low: 301, i_high: 500 },
  ],
  // 1-hour SO2 caps at AQI 200 (304 ppb); above that use 24-hour SO2.
  so2_1h: [
    { c_low: 0, c_high: 35, i_low: 0, i_high: 50 },
    { c_low: 36, c_high: 75, i_low: 51, i_high: 100 },
    { c_low: 76, c_high: 185, i_low: 101, i_high: 150 },
    { c_low: 186, c_high: 304, i_low: 151, i_high: 200 },
  ],
  so2_24h: [
    { c_low: 305, c_high: 604, i_low: 201, i_high: 300 },
    { c_low: 605, c_high: 1004, i_low: 301, i_high: 500 },
  ],
  no2_1h: [
    { c_low: 0, c_high: 53, i_low: 0, i_high: 50 },
    { c_low: 54, c_high: 100, i_low: 51, i_high: 100 },
    { c_low: 101, c_high: 360, i_low: 101, i_high: 150 },
    { c_low: 361, c_high: 649, i_low: 151, i_high: 200 },
    { c_low: 650, c_high: 1249, i_low: 201, i_high: 300 },
    { c_low: 1250, c_high: 2049, i_low: 301, i_high: 500 },
  ],
};

function truncate(value: number, decimals: number): number {
  const factor = Math.pow(10, decimals);
  return Math.floor(value * factor) / factor;
}

function ensureNonNegativeFinite(name: string, v: number): number {
  if (!Number.isFinite(v) || v < 0) {
    throw new Error(`${name} must be a finite, non-negative number`);
  }
  return v;
}

function interpolateBreakpoint(c: number, bp: Breakpoint): number {
  return Math.round(((bp.i_high - bp.i_low) / (bp.c_high - bp.c_low)) * (c - bp.c_low) + bp.i_low);
}

/**
 * Convert a single-pollutant concentration to its AQI sub-index.
 *
 * Concentrations are first truncated to EPA precision, then matched to the
 * appropriate breakpoint and linearly interpolated to an integer AQI.
 */
export function aqiFromConcentration(
  pollutant: AqiPollutant,
  concentration: number
): AqiSubIndex {
  ensureNonNegativeFinite('concentration', concentration);
  const meta = POLLUTANT_META[pollutant];
  const c = truncate(concentration, meta.precision);
  const breakpoints = BREAKPOINTS[pollutant];
  for (const bp of breakpoints) {
    if (c >= bp.c_low && c <= bp.c_high) {
      const aqi = interpolateBreakpoint(c, bp);
      return {
        pollutant,
        concentration: c,
        units: meta.units,
        aqi,
        category: AQI_CATEGORY_FOR_INDEX(aqi),
      };
    }
  }
  // Above the highest breakpoint → cap at the last interval's high index.
  const last = breakpoints[breakpoints.length - 1];
  return {
    pollutant,
    concentration: c,
    units: meta.units,
    aqi: last.i_high,
    category: AQI_CATEGORY_FOR_INDEX(last.i_high),
  };
}

/**
 * Compute the overall AQI from a set of pollutant readings.
 *
 * Provide whichever pollutants are available; the function returns the
 * maximum sub-index along with the dominant pollutant.
 */
export function overallAqi(readings: Partial<Record<AqiPollutant, number>>): AqiOverall {
  const sub: AqiSubIndex[] = [];
  for (const key of Object.keys(readings) as AqiPollutant[]) {
    const v = readings[key];
    if (v === undefined) continue;
    sub.push(aqiFromConcentration(key, v));
  }
  if (sub.length === 0) {
    throw new Error('overallAqi requires at least one pollutant reading');
  }
  let dominant = sub[0];
  for (const s of sub) {
    if (s.aqi > dominant.aqi) dominant = s;
  }
  return {
    aqi: dominant.aqi,
    category: dominant.category,
    dominant: dominant.pollutant,
    sub_indices: sub,
  };
}

/** Bucket a numeric AQI into its named category. */
export function aqiCategory(aqi: number): AqiCategory {
  if (!Number.isFinite(aqi) || aqi < 0) {
    throw new Error('aqi must be a non-negative finite number');
  }
  return AQI_CATEGORY_FOR_INDEX(aqi);
}
