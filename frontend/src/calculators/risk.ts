/**
 * Risk Assessment Calculators
 *
 * References:
 * - FAA Spatial Disorientation training materials
 * - Houben et al. (2022). Perception threshold of the vestibular Coriolis illusion. PubMed: 34924407
 * - Sjaardema et al. (2015). History and Evolution of the Johnson Criteria. SAND2015-6368
 * - Mansfield et al. (2009). Earth moving machine WBV. Industrial Health 47(4):402-410
 * - Orelaja et al. (2019). WBV health risk. J Healthcare Eng. DOI: 10.1155/2019/5723830
 * - Rivera et al. (2022). MSSQ-short cross-cultural adaptation. Rev Otorrinolaringol 82(2):172-178
 * - Golding, J.F. (2006). Motion sickness susceptibility. Autonomic Neuroscience 129(1-2):67-76
 */

// ──────────────────────────────────────────────────────────────────────
// Spatial Disorientation Risk Assessment
// ──────────────────────────────────────────────────────────────────────

const G_M_S2 = 9.80665;
const LEANS_THRESHOLD_DEG_S = 2.0;
const CANAL_ENTRAIN_MIN_S = 10.0;
const CANAL_ENTRAIN_MAX_S = 20.0;
const CORIOLIS_YAW_THRESHOLD = 10.0;

function clamp(x: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, x));
}

function smoothstep01(x: number): number {
  const v = clamp(x, 0, 1);
  return v * v * (3 - 2 * v);
}

export type RiskLevel = 'Low' | 'Moderate' | 'High' | 'Very High';

export interface SDInputs {
  imc: boolean;
  night: boolean;
  nvg: boolean;
  timeSinceHorizonS: number;
  yawRateDegS: number;
  sustainedTurnDurationS: number;
  headMovementDuringTurn: boolean;
  forwardAccelMS2: number;
  workload: number; // 0..1
}

export interface SDResult {
  riskIndex: number; // 0-100
  riskLevel: RiskLevel;
  likelyIllusions: string[];
  somatogravicTiltDeg: number;
  leansComponent: number;
  canalEntrainmentComponent: number;
  coriolisComponent: number;
  somatogravicComponent: number;
  cueDeprivationComponent: number;
}

function cueDeprivation(imc: boolean, night: boolean, nvg: boolean, timeSinceHorizonS: number): number {
  let base = 0;
  if (imc) base += 0.55;
  if (night) base += 0.25;
  if (nvg) base += 0.20;
  const t = clamp(timeSinceHorizonS, 0, 120);
  const timeFactor = smoothstep01(t / 60.0) * 0.35;
  return clamp(base + timeFactor, 0, 1);
}

function leansComponent(yawRate: number, duration: number): number {
  if (duration <= 0) return 0;
  const r = Math.abs(yawRate);
  const below = clamp((LEANS_THRESHOLD_DEG_S - r) / LEANS_THRESHOLD_DEG_S, 0, 1);
  const dur = smoothstep01(clamp(duration / CANAL_ENTRAIN_MAX_S, 0, 1));
  return below * dur;
}

function canalEntrainmentComponent(yawRate: number, duration: number): number {
  const r = Math.abs(yawRate);
  if (duration <= 0 || r < LEANS_THRESHOLD_DEG_S) return 0;
  const x = (duration - CANAL_ENTRAIN_MIN_S) / (CANAL_ENTRAIN_MAX_S - CANAL_ENTRAIN_MIN_S);
  return smoothstep01(x);
}

function coriolisComponent(yawRate: number, headMovement: boolean): number {
  if (!headMovement) return 0;
  const r = Math.abs(yawRate);
  if (r <= CORIOLIS_YAW_THRESHOLD) return 0;
  return smoothstep01((r - CORIOLIS_YAW_THRESHOLD) / 20.0);
}

function somatogravicTiltDeg(forwardAccel: number): number {
  return (Math.atan2(forwardAccel, G_M_S2) * 180) / Math.PI;
}

function somatogravicComp(tiltDeg: number): number {
  return smoothstep01(clamp(Math.abs(tiltDeg) / 30.0, 0, 1));
}

export function spatialDisorientationRisk(inputs: SDInputs): SDResult {
  if (inputs.workload < 0 || inputs.workload > 1) {
    throw new Error('workload must be 0..1');
  }

  const cue = cueDeprivation(inputs.imc, inputs.night, inputs.nvg, inputs.timeSinceHorizonS);
  const leans = leansComponent(inputs.yawRateDegS, inputs.sustainedTurnDurationS);
  const entrain = canalEntrainmentComponent(inputs.yawRateDegS, inputs.sustainedTurnDurationS);
  const coriolis = coriolisComponent(inputs.yawRateDegS, inputs.headMovementDuringTurn);
  const tilt = somatogravicTiltDeg(inputs.forwardAccelMS2);
  const somato = somatogravicComp(tilt);

  const vestibularSum = clamp((leans + entrain + 1.2 * coriolis + 1.1 * somato) / 4.3, 0, 1);
  const amplifier = clamp(0.55 + 0.45 * cue, 0, 1) * clamp(0.70 + 0.30 * inputs.workload, 0, 1);
  const combined = clamp(vestibularSum * amplifier, 0, 1);
  const riskIndex = clamp(100 * (1 - Math.exp(-2.2 * combined)), 0, 100);

  let riskLevel: RiskLevel;
  if (riskIndex < 25) riskLevel = 'Low';
  else if (riskIndex < 50) riskLevel = 'Moderate';
  else if (riskIndex < 75) riskLevel = 'High';
  else riskLevel = 'Very High';

  const illusions: string[] = [];
  if (leans >= 0.45) illusions.push('Leans (slow unnoticed bank)');
  if (entrain >= 0.45) illusions.push('Post-turn canal entrainment (graveyard spiral/spin)');
  if (coriolis >= 0.35) illusions.push('Coriolis illusion (head movement during turn)');
  if (somato >= 0.35 && cue >= 0.35) illusions.push('Somatogravic illusion (GIA pitch misperception)');

  return {
    riskIndex, riskLevel, likelyIllusions: illusions,
    somatogravicTiltDeg: tilt,
    leansComponent: clamp(leans, 0, 1),
    canalEntrainmentComponent: clamp(entrain, 0, 1),
    coriolisComponent: clamp(coriolis, 0, 1),
    somatogravicComponent: clamp(somato, 0, 1),
    cueDeprivationComponent: clamp(cue, 0, 1),
  };
}

// ──────────────────────────────────────────────────────────────────────
// NVG/EO Target Acquisition (Johnson/ACQUIRE criteria)
// ──────────────────────────────────────────────────────────────────────

export type CriteriaFamily = 'johnson' | 'acquire';
export type DiscriminationLevel = 'detection' | 'orientation' | 'classification' | 'recognition' | 'identification';

export interface ImagingSystem {
  horizontalPixels: number;
  verticalPixels: number;
  horizontalFovDeg: number;
  verticalFovDeg: number;
}

export interface Target {
  widthM: number;
  heightM: number;
}

export interface NvgAcquisitionResult {
  criteria: CriteriaFamily;
  discrimination: DiscriminationLevel;
  rangeM: number;
  targetDimensionM: number;
  ifovDegPerPixel: number;
  targetAngularDeg: number;
  pixelsOnTarget: number;
  cyclesOnTarget: number;
  requiredCyclesN50: number;
  meetsN50: boolean;
  ratioToN50: number;
}

const JOHNSON_N50: Partial<Record<DiscriminationLevel, number>> = {
  detection: 1.0, orientation: 1.4, recognition: 4.0, identification: 6.4,
};

const ACQUIRE_N50: Partial<Record<DiscriminationLevel, number>> = {
  detection: 0.75, classification: 1.5, recognition: 3.0, identification: 6.0,
};

function angularSizeDeg(sizeM: number, rangeM: number): number {
  return (2.0 * Math.atan2(sizeM, 2.0 * rangeM) * 180) / Math.PI;
}

export function assessTargetAcquisition(
  criteria: CriteriaFamily,
  discrimination: DiscriminationLevel,
  system: ImagingSystem,
  target: Target,
  rangeM: number,
  criticalDimension: 'width' | 'height' = 'height',
): NvgAcquisitionResult {
  const table = criteria === 'johnson' ? JOHNSON_N50 : ACQUIRE_N50;
  const n50 = table[discrimination];
  if (n50 === undefined) {
    throw new Error(`${discrimination} not defined for ${criteria} criteria`);
  }
  if (rangeM <= 0) throw new Error('rangeM must be > 0');

  const dimM = criticalDimension === 'width' ? target.widthM : target.heightM;
  const fovDeg = criticalDimension === 'width' ? system.horizontalFovDeg : system.verticalFovDeg;
  const px = criticalDimension === 'width' ? system.horizontalPixels : system.verticalPixels;
  const ifov = fovDeg / px;
  const theta = angularSizeDeg(dimM, rangeM);
  const pixOnTarget = theta / ifov;
  const cycles = Math.max(0, pixOnTarget / 2.0);
  const ratio = n50 > 0 ? cycles / n50 : Infinity;

  return {
    criteria, discrimination, rangeM, targetDimensionM: dimM,
    ifovDegPerPixel: ifov, targetAngularDeg: theta,
    pixelsOnTarget: pixOnTarget, cyclesOnTarget: cycles,
    requiredCyclesN50: n50, meetsN50: cycles >= n50, ratioToN50: ratio,
  };
}

/**
 * Compute cycles-on-target along a chosen critical dimension (Nyquist: cycles ≈ pixels/2).
 */
export function cyclesOnTarget(args: {
  system: ImagingSystem;
  target: Target;
  rangeM: number;
  criticalDimension?: 'width' | 'height';
}): number {
  const criticalDimension = args.criticalDimension ?? 'height';
  if (args.rangeM <= 0) throw new Error('rangeM must be > 0');
  const dimM = criticalDimension === 'width' ? args.target.widthM : args.target.heightM;
  const fovDeg = criticalDimension === 'width' ? args.system.horizontalFovDeg : args.system.verticalFovDeg;
  const px = criticalDimension === 'width' ? args.system.horizontalPixels : args.system.verticalPixels;
  const ifov = fovDeg / px;
  const theta = angularSizeDeg(dimM, args.rangeM);
  const pixOnTarget = theta / ifov;
  return Math.max(0, pixOnTarget / 2);
}

/**
 * Compute max range for a given number of required cycles.
 */
export function rangeForRequiredCycles(
  system: ImagingSystem,
  target: Target,
  requiredCycles: number,
  criticalDimension: 'width' | 'height' = 'height',
): number {
  if (requiredCycles <= 0) throw new Error('requiredCycles must be > 0');
  const dimM = criticalDimension === 'width' ? target.widthM : target.heightM;
  const fovDeg = criticalDimension === 'width' ? system.horizontalFovDeg : system.verticalFovDeg;
  const px = criticalDimension === 'width' ? system.horizontalPixels : system.verticalPixels;
  const ifov = fovDeg / px;
  const pixelsNeeded = 2 * requiredCycles;
  const thetaDeg = pixelsNeeded * ifov;
  const thetaRad = (thetaDeg * Math.PI) / 180;
  const denom = 2.0 * Math.tan(thetaRad / 2.0);
  if (denom <= 0) throw new Error('Invalid geometry');
  return dimM / denom;
}

// ──────────────────────────────────────────────────────────────────────
// Whole-Body Vibration (ISO 2631-1 style)
// ──────────────────────────────────────────────────────────────────────

export type WbvZone = 'below_lower' | 'within_hgcz' | 'above_upper';

const HOURS_8_S = 8 * 3600;
const A8_LOWER = 0.47;
const A8_UPPER = 0.93;
// VDV thresholds reserved for future VDV(8) display
export const VDV_LOWER = 8.5;
export const VDV_UPPER = 17.0;
const KX = 1.4;
const KY = 1.4;
const KZ = 1.0;

export interface WbvInputs {
  awxMS2: number;
  awyMS2: number;
  awzMS2: number;
  exposureDurationS: number;
}

export interface WbvResult {
  awCombined: number;
  a8: number;
  a8Zone: WbvZone;
  a8Lower: number;
  a8Upper: number;
  timeToA8LowerH: number | null;
  timeToA8UpperH: number | null;
}

function classifyA8(a8: number): WbvZone {
  if (a8 < A8_LOWER) return 'below_lower';
  if (a8 > A8_UPPER) return 'above_upper';
  return 'within_hgcz';
}

export function computeWbvExposure(inputs: WbvInputs): WbvResult {
  const aw = Math.sqrt(
    Math.pow(KX * inputs.awxMS2, 2) +
    Math.pow(KY * inputs.awyMS2, 2) +
    Math.pow(KZ * inputs.awzMS2, 2),
  );
  const a8 = aw * Math.sqrt(inputs.exposureDurationS / HOURS_8_S);
  const a8Zone = classifyA8(a8);

  const timeToLowerS = aw > 0 ? HOURS_8_S * Math.pow(A8_LOWER / aw, 2) : null;
  const timeToUpperS = aw > 0 ? HOURS_8_S * Math.pow(A8_UPPER / aw, 2) : null;

  return {
    awCombined: aw, a8, a8Zone,
    a8Lower: A8_LOWER, a8Upper: A8_UPPER,
    timeToA8LowerH: timeToLowerS !== null ? timeToLowerS / 3600 : null,
    timeToA8UpperH: timeToUpperS !== null ? timeToUpperS / 3600 : null,
  };
}

// ──────────────────────────────────────────────────────────────────────
// Whole-Body Vibration — extended ISO 2631-1 helpers (matches Python wbv module)
// ──────────────────────────────────────────────────────────────────────

export interface WbvAxisWeightedRms {
  awx_m_s2: number;
  awy_m_s2: number;
  awz_m_s2: number;
}

export interface WbvExposureInputsExt {
  axis_aw: WbvAxisWeightedRms;
  exposure_duration_s: number;
  vdv_m_s1_75?: number;
  vdv_reference_duration_s?: number;
}

export interface WbvExposureResultExt {
  aw_combined_m_s2: number;
  a8_m_s2: number;
  a8_zone: WbvZone;
  a8_lower_bound_m_s2: number;
  a8_upper_bound_m_s2: number;
  vdv8_m_s1_75: number | null;
  vdv8_zone: WbvZone | null;
  vdv8_lower_bound_m_s1_75: number;
  vdv8_upper_bound_m_s1_75: number;
  time_to_a8_lower_s: number | null;
  time_to_a8_upper_s: number | null;
  time_to_vdv8_lower_s: number | null;
  time_to_vdv8_upper_s: number | null;
}

function ensureNonNegativeFinite(name: string, value: number): number {
  if (!Number.isFinite(value) || value < 0) {
    throw new Error(`${name} must be a finite, non-negative number`);
  }
  return value;
}

function ensurePositiveFinite(name: string, value: number): number {
  if (!Number.isFinite(value) || value <= 0) {
    throw new Error(`${name} must be a finite, positive number`);
  }
  return value;
}

/**
 * Combine axis frequency-weighted r.m.s. accelerations using kx=ky=1.4, kz=1.0.
 */
export function combineAxesIso2631(axis_aw: WbvAxisWeightedRms): number {
  const awx = ensureNonNegativeFinite('awx_m_s2', axis_aw.awx_m_s2);
  const awy = ensureNonNegativeFinite('awy_m_s2', axis_aw.awy_m_s2);
  const awz = ensureNonNegativeFinite('awz_m_s2', axis_aw.awz_m_s2);
  return Math.sqrt(Math.pow(KX * awx, 2) + Math.pow(KY * awy, 2) + Math.pow(KZ * awz, 2));
}

/** A(8) from a frequency-weighted r.m.s. acceleration over an exposure duration. */
export function a8FromAw(args: { aw_m_s2: number; exposure_duration_s: number }): number {
  const aw = ensureNonNegativeFinite('aw_m_s2', args.aw_m_s2);
  const t = ensurePositiveFinite('exposure_duration_s', args.exposure_duration_s);
  return aw * Math.sqrt(t / HOURS_8_S);
}

/** Scale a VDV measured over `reference_duration_s` to an 8h-equivalent VDV. */
export function vdv8FromVdv(args: {
  vdv_m_s1_75: number;
  reference_duration_s: number;
  exposure_duration_s: number;
}): number {
  const vdv = ensureNonNegativeFinite('vdv_m_s1_75', args.vdv_m_s1_75);
  const tRef = ensurePositiveFinite('reference_duration_s', args.reference_duration_s);
  const tExp = ensurePositiveFinite('exposure_duration_s', args.exposure_duration_s);
  const vdvExp = vdv * Math.pow(tExp / tRef, 0.25);
  return vdvExp * Math.pow(HOURS_8_S / tExp, 0.25);
}

/** Solve exposure duration (s) required to reach a target A(8) at a constant aw. */
export function timeToReachA8(args: { aw_m_s2: number; target_a8_m_s2: number }): number | null {
  const aw = ensureNonNegativeFinite('aw_m_s2', args.aw_m_s2);
  const target = ensurePositiveFinite('target_a8_m_s2', args.target_a8_m_s2);
  if (aw <= 0) return null;
  return HOURS_8_S * Math.pow(target / aw, 2);
}

/** Solve exposure duration (s) required to reach a target VDV(8). */
export function timeToReachVdv8(args: {
  vdv_m_s1_75: number;
  reference_duration_s: number;
  target_vdv8_m_s1_75: number;
}): number | null {
  const vdv = ensureNonNegativeFinite('vdv_m_s1_75', args.vdv_m_s1_75);
  const tRef = ensurePositiveFinite('reference_duration_s', args.reference_duration_s);
  const target = ensurePositiveFinite('target_vdv8_m_s1_75', args.target_vdv8_m_s1_75);
  if (vdv <= 0) return null;
  return tRef * Math.pow(target / Math.max(vdv, 1e-12), 4);
}

/** Classify A(8) against the Health Guidance Caution Zone (Orelaja et al., 2019). */
export function classifyHgczA8(a8_m_s2: number): WbvZone {
  const a8 = ensureNonNegativeFinite('a8_m_s2', a8_m_s2);
  if (a8 < A8_LOWER) return 'below_lower';
  if (a8 > A8_UPPER) return 'above_upper';
  return 'within_hgcz';
}

/** Classify VDV(8) against the HGCZ thresholds (8.5 / 17 m/s^1.75). */
export function classifyHgczVdv8(vdv8_m_s1_75: number): WbvZone {
  const v = ensureNonNegativeFinite('vdv8_m_s1_75', vdv8_m_s1_75);
  if (v < VDV_LOWER) return 'below_lower';
  if (v > VDV_UPPER) return 'above_upper';
  return 'within_hgcz';
}

/** Full WBV exposure computation matching Python `compute_wbv_exposure`. */
export function computeWbvExposureExt(inputs: WbvExposureInputsExt): WbvExposureResultExt {
  const aw = combineAxesIso2631(inputs.axis_aw);
  const tExp = ensurePositiveFinite('exposure_duration_s', inputs.exposure_duration_s);
  const a8 = a8FromAw({ aw_m_s2: aw, exposure_duration_s: tExp });
  const a8_zone = classifyHgczA8(a8);

  let vdv8: number | null = null;
  let vdv8_zone: WbvZone | null = null;
  let time_to_vdv8_lower_s: number | null = null;
  let time_to_vdv8_upper_s: number | null = null;

  if (inputs.vdv_m_s1_75 !== undefined) {
    if (inputs.vdv_reference_duration_s === undefined) {
      throw new Error('vdv_reference_duration_s is required when vdv_m_s1_75 is provided');
    }
    vdv8 = vdv8FromVdv({
      vdv_m_s1_75: inputs.vdv_m_s1_75,
      reference_duration_s: inputs.vdv_reference_duration_s,
      exposure_duration_s: tExp,
    });
    vdv8_zone = classifyHgczVdv8(vdv8);
    time_to_vdv8_lower_s = timeToReachVdv8({
      vdv_m_s1_75: inputs.vdv_m_s1_75,
      reference_duration_s: inputs.vdv_reference_duration_s,
      target_vdv8_m_s1_75: VDV_LOWER,
    });
    time_to_vdv8_upper_s = timeToReachVdv8({
      vdv_m_s1_75: inputs.vdv_m_s1_75,
      reference_duration_s: inputs.vdv_reference_duration_s,
      target_vdv8_m_s1_75: VDV_UPPER,
    });
  }

  return {
    aw_combined_m_s2: aw,
    a8_m_s2: a8,
    a8_zone,
    a8_lower_bound_m_s2: A8_LOWER,
    a8_upper_bound_m_s2: A8_UPPER,
    vdv8_m_s1_75: vdv8,
    vdv8_zone,
    vdv8_lower_bound_m_s1_75: VDV_LOWER,
    vdv8_upper_bound_m_s1_75: VDV_UPPER,
    time_to_a8_lower_s: timeToReachA8({ aw_m_s2: aw, target_a8_m_s2: A8_LOWER }),
    time_to_a8_upper_s: timeToReachA8({ aw_m_s2: aw, target_a8_m_s2: A8_UPPER }),
    time_to_vdv8_lower_s,
    time_to_vdv8_upper_s,
  };
}

// ──────────────────────────────────────────────────────────────────────
// MSSQ-short scoring
// ──────────────────────────────────────────────────────────────────────

export const MSSQ_ITEMS: readonly string[] = [
  'Car / automobile', 'Bus / coach', 'Train', 'Aircraft / airplane',
  'Small boat', 'Ship / large boat', 'Swing', 'Playground equipment',
  'Amusement rides (e.g., rollercoaster)',
];

export type MssqPercentileBand = '<P25' | 'P25-P50' | 'P50-P75' | '>=P75';

export interface MssqResult {
  sectionASum: number; // 0-27
  sectionBSum: number; // 0-27
  totalSum: number;    // 0-54
  percentileBand: MssqPercentileBand;
}

// Rivera et al. (2022) pre-test quartiles (n=51)
const RIVERA_P25 = 2.13;
const RIVERA_P50 = 9.0;
const RIVERA_P75 = 17.4;

export function computeMssqShort(
  sectionA: readonly number[],
  sectionB: readonly number[],
): MssqResult {
  if (sectionA.length !== 9 || sectionB.length !== 9) {
    throw new Error('Each section must have exactly 9 items');
  }
  for (const s of [...sectionA, ...sectionB]) {
    if (s < 0 || s > 3 || !Number.isInteger(s)) {
      throw new Error('Item scores must be integers 0-3');
    }
  }

  const aSum = sectionA.reduce((a, b) => a + b, 0);
  const bSum = sectionB.reduce((a, b) => a + b, 0);
  const total = aSum + bSum;

  let band: MssqPercentileBand;
  if (total < RIVERA_P25) band = '<P25';
  else if (total < RIVERA_P50) band = 'P25-P50';
  else if (total < RIVERA_P75) band = 'P50-P75';
  else band = '>=P75';

  return { sectionASum: aSum, sectionBSum: bSum, totalSum: total, percentileBand: band };
}
