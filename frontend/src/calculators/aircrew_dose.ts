/**
 * Aircrew cosmic-radiation dose estimator — CARI-7-style lookup.
 *
 * Pure approximation that wraps a (flight-level × geomagnetic-latitude band ×
 * solar-phase) lookup of typical effective dose rates from open published
 * sources, then integrates dose over a route's duration.
 *
 * It is NOT a substitute for the FAA's CARI-7 / NAIRAS / EPCARD tools when
 * operational doses are required; use those for compliance reporting. The
 * published values used here are order-of-magnitude correct for typical
 * subsonic commercial cruise.
 *
 * Typical reference values (effective dose rate, µSv/h):
 *
 *   FL\Lat   |  0–15°N |  15–30° |  30–45° |  45–60° |   >60°
 *   ─────────┼─────────┼─────────┼─────────┼─────────┼─────────
 *   FL200   |   0.6   |   0.9   |   1.4   |   1.8   |   2.0
 *   FL300   |   1.7   |   2.4   |   3.4   |   4.4   |   5.0
 *   FL350   |   2.4   |   3.5   |   5.0   |   6.4   |   7.2
 *   FL400   |   3.2   |   4.6   |   6.5   |   8.4   |   9.4
 *   FL450   |   4.0   |   5.7   |   8.0   |  10.4   |  11.7
 *
 * Solar maximum reduces dose rate by roughly 30 % relative to solar minimum
 * because of heliospheric modulation of galactic cosmic rays.
 *
 * References:
 *   FAA Civil Aerospace Medical Institute. CARI-7 documentation.
 *     https://www.faa.gov/data_research/research/med_humanfacs/aeromedical/radiobiology/cari7
 *   NCRP Report No. 132 (2000). Radiation Protection Guidance for Activities
 *     in Low-Earth Orbit.
 *   ICRP Publication 132 (2016). Radiological Protection from Cosmic
 *     Radiation in Aviation.
 *   EU EURADOS WG11 (2009). Comparison of Codes Assessing Radiation Exposure
 *     of Aircraft Crew due to Galactic Cosmic Radiation.
 *
 * SCOPE: educational planning. Annual occupational limit (ICRP) is 20 mSv;
 * aircrew typical exposure 2–5 mSv/yr.
 */

export type GeomagneticLatitudeBand = 'eq_0_15' | 'low_15_30' | 'mid_30_45' | 'high_45_60' | 'polar_gt_60';

export type SolarPhase = 'minimum' | 'maximum';

const LATITUDE_BAND_FOR_DEG = (degLat: number): GeomagneticLatitudeBand => {
  const a = Math.abs(degLat);
  if (a < 15) return 'eq_0_15';
  if (a < 30) return 'low_15_30';
  if (a < 45) return 'mid_30_45';
  if (a < 60) return 'high_45_60';
  return 'polar_gt_60';
};

// Dose-rate table: solar minimum, µSv/h. Anchor flight levels at FL200, 300,
// 350, 400, 450. Linear interpolation between flight levels and clamping
// outside the range.
interface FlAnchor {
  fl: number;
  rates: Record<GeomagneticLatitudeBand, number>;
}

const SOLAR_MIN_RATES: ReadonlyArray<FlAnchor> = [
  { fl: 200, rates: { eq_0_15: 0.6, low_15_30: 0.9, mid_30_45: 1.4, high_45_60: 1.8, polar_gt_60: 2.0 } },
  { fl: 300, rates: { eq_0_15: 1.7, low_15_30: 2.4, mid_30_45: 3.4, high_45_60: 4.4, polar_gt_60: 5.0 } },
  { fl: 350, rates: { eq_0_15: 2.4, low_15_30: 3.5, mid_30_45: 5.0, high_45_60: 6.4, polar_gt_60: 7.2 } },
  { fl: 400, rates: { eq_0_15: 3.2, low_15_30: 4.6, mid_30_45: 6.5, high_45_60: 8.4, polar_gt_60: 9.4 } },
  { fl: 450, rates: { eq_0_15: 4.0, low_15_30: 5.7, mid_30_45: 8.0, high_45_60: 10.4, polar_gt_60: 11.7 } },
];

const SOLAR_PHASE_FACTOR: Record<SolarPhase, number> = {
  minimum: 1.0,
  maximum: 0.7,
};

function ensureFiniteNonNegative(name: string, v: number): number {
  if (!Number.isFinite(v) || v < 0) {
    throw new Error(`${name} must be a finite, non-negative number`);
  }
  return v;
}

function interpolateFlightLevel(fl: number, band: GeomagneticLatitudeBand): number {
  if (fl <= SOLAR_MIN_RATES[0].fl) return SOLAR_MIN_RATES[0].rates[band];
  if (fl >= SOLAR_MIN_RATES[SOLAR_MIN_RATES.length - 1].fl) {
    return SOLAR_MIN_RATES[SOLAR_MIN_RATES.length - 1].rates[band];
  }
  for (let i = 0; i < SOLAR_MIN_RATES.length - 1; i++) {
    const lo = SOLAR_MIN_RATES[i];
    const hi = SOLAR_MIN_RATES[i + 1];
    if (fl >= lo.fl && fl <= hi.fl) {
      const frac = (fl - lo.fl) / (hi.fl - lo.fl);
      return lo.rates[band] + frac * (hi.rates[band] - lo.rates[band]);
    }
  }
  return SOLAR_MIN_RATES[SOLAR_MIN_RATES.length - 1].rates[band];
}

export interface CrewDoseRateInputs {
  /** Flight level (hundreds of feet). FL350 = 35 000 ft. */
  flight_level: number;
  /** Geomagnetic latitude in degrees (positive or negative). */
  latitude_deg: number;
  solar_phase?: SolarPhase;
}

export interface CrewDoseRateResult {
  /** Effective dose rate, µSv/h. */
  dose_rate_uSv_h: number;
  flight_level: number;
  latitude_band: GeomagneticLatitudeBand;
  solar_phase: SolarPhase;
}

/** Cosmic-radiation effective dose rate for steady cruise at altitude. */
export function aircrewDoseRate(inputs: CrewDoseRateInputs): CrewDoseRateResult {
  ensureFiniteNonNegative('flight_level', inputs.flight_level);
  if (!Number.isFinite(inputs.latitude_deg)) {
    throw new Error('latitude_deg must be finite');
  }
  const band = LATITUDE_BAND_FOR_DEG(inputs.latitude_deg);
  const solar: SolarPhase = inputs.solar_phase ?? 'minimum';
  const baseRate = interpolateFlightLevel(inputs.flight_level, band);
  return {
    dose_rate_uSv_h: baseRate * SOLAR_PHASE_FACTOR[solar],
    flight_level: inputs.flight_level,
    latitude_band: band,
    solar_phase: solar,
  };
}

export interface RouteSegment {
  flight_level: number;
  latitude_deg: number;
  duration_h: number;
}

export interface RouteDoseResult {
  total_dose_uSv: number;
  total_duration_h: number;
  segments: Array<{ segment: RouteSegment; rate_uSv_h: number; dose_uSv: number }>;
  solar_phase: SolarPhase;
}

/**
 * Total cosmic-radiation effective dose (µSv) for a multi-segment route.
 *
 * Each segment contributes `rate · duration`. Solar phase applies uniformly.
 */
export function crewCosmicDoseEstimate(args: {
  route: RouteSegment[];
  solar_phase?: SolarPhase;
}): RouteDoseResult {
  if (args.route.length === 0) {
    throw new Error('route must contain at least one segment');
  }
  const solar = args.solar_phase ?? 'minimum';
  let total = 0;
  let totalH = 0;
  const segments: RouteDoseResult['segments'] = [];
  for (const seg of args.route) {
    ensureFiniteNonNegative('segment.duration_h', seg.duration_h);
    const r = aircrewDoseRate({
      flight_level: seg.flight_level,
      latitude_deg: seg.latitude_deg,
      solar_phase: solar,
    });
    const dose = r.dose_rate_uSv_h * seg.duration_h;
    total += dose;
    totalH += seg.duration_h;
    segments.push({ segment: seg, rate_uSv_h: r.dose_rate_uSv_h, dose_uSv: dose });
  }
  return { total_dose_uSv: total, total_duration_h: totalH, segments, solar_phase: solar };
}

/**
 * Annual aircrew dose given an average crew utilization. Assumes a constant
 * flight-level × latitude profile per block hour.
 */
export function annualCrewDose(args: {
  block_hours_per_year: number;
  representative_dose_rate_uSv_h: number;
}): number {
  ensureFiniteNonNegative('block_hours_per_year', args.block_hours_per_year);
  ensureFiniteNonNegative('representative_dose_rate_uSv_h', args.representative_dose_rate_uSv_h);
  return args.block_hours_per_year * args.representative_dose_rate_uSv_h;
}
