/**
 * Aerospace Medicine & Human Performance Calculator Suite
 *
 * TypeScript implementations of every Streamlit/Python calculator in
 * `calculators/`, organized by physiological domain.
 *
 * Principal Investigator: Dr. Diego Malpica
 * Universidad Nacional de Colombia
 */

// ─── Atmosphere & Altitude Physiology ──────────────────────────────────
export {
  standardAtmosphere,
  inspiredPO2,
  alveolarPO2,
  spo2Unacclimatized,
  spo2Acclimatized,
  oxygenContent,
  tissueRatio,
  interpretTR,
  amsProbability,
  estimateTUC,
  gLocTime,
  cosmicDoseRate,
  pao2AtAltitude,
  hapeRiskSuona2023,
  metersToFeet,
  feetToMeters,
  pascalToMmHg,
  mmHgToPascal,
  type ISAResult,
  type TransportMode,
  type HAPERiskResult,
} from './atmosphere';

// ─── SpO₂ models (Niermeyer / Alt VAR / Tüshaus) ───────────────────────
export {
  niermeyerSpo2,
  altVarSpo2,
  tushausCascadeSpo2,
  compareSpo2Models,
  type Sex,
  type SpO2Result,
} from './spo2Models';

// ─── Heat stress, PHS, UTCI ────────────────────────────────────────────
export {
  wbgtIndoor,
  wbgtOutdoor,
  wbgtRiskAssessment,
  heatStressIndex,
  hsiAssessment,
  predictedHeatStrain,
  utci,
  utciCategory,
  simulatePHSTrajectory,
  type WBGTResult,
  type HeatStressIndexResult,
  type PHSResult,
  type UTCIResult,
  type PHSTrajectoryPoint,
} from './heatStress';

// ─── PHS parameter sweeps ──────────────────────────────────────────────
export {
  sweepPhsMetric1d,
  sweepPhsMetric2d,
  type PHSSweepParameter,
  type PHSSweepMetric,
  type PHSSweep1DResult,
  type PHSSweep2DResult,
  type PHSScenario,
} from './simulationSweeps';

// ─── Cold-stress physiology ────────────────────────────────────────────
export { peakShiveringIntensity } from './coldStress';
export {
  coldWaterSurvival,
  coldWaterSurvivalHayward1975Minutes,
  coldWaterSurvivalGoldenLifejacketHours,
  type ColdWaterSurvivalEstimate,
  type ColdWaterSurvivalModel,
} from './coldWaterSurvival';

// ─── Vision at altitude ────────────────────────────────────────────────
export {
  estimateDvaLogmarWang2024,
  logmarToSnellenDenominator,
  type DvaEstimate,
} from './visionAltitude';

// ─── Anti-G straining maneuver (AGSM) ──────────────────────────────────
export {
  estimateGzToleranceWithAgsm,
  AGSM_DEFAULT_BASELINE_RELAXED_GZ,
  AGSM_DEFAULT_MAX_SYSTEM_GZ,
  AGSM_DEFAULT_SUIT_DELTA_GZ,
  AGSM_DEFAULT_PBG_DELTA_GZ,
  AGSM_DEFAULT_AGSM_DELTA_GZ,
  type AgsmInputs,
  type AgsmResult,
} from './agsm';

// ─── Noise exposure (OSHA / NIOSH) ─────────────────────────────────────
export {
  permissibleDuration,
  noiseDoseOsha,
  noiseDoseNiosh,
} from './noiseExposure';

// ─── Occupational health (TLV / TWA / BEI / Aerospace chemicals) ───────
export {
  AEROSPACE_CHEMICALS,
  calculateTwaExposure,
  calculateAdjustedTlvUnusualSchedule,
  calculateMixedExposureIndex,
  assessExposureRisk,
  calculatePermissibleExposureTime,
  generateExposureReport,
  calculateBiologicalExposureIndex,
  type ChemicalExposureData,
  type ChemicalUnits,
  type ExposureRiskLevel,
  type ExposureRiskAssessment,
  type BeiAssessment,
} from './occupationalHealth';

// ─── SAFTE fatigue model ───────────────────────────────────────────────
export {
  simulateSafte,
  DEFAULT_SAFTE_PARAMETERS,
  type SafteParameters,
  type SleepEpisode,
  type SafteInputs,
  type SaftePoint,
  type SafteSeries,
} from './safte';

// ─── Bühlmann ZH-L16-GF decompression ──────────────────────────────────
export {
  planZhL16Gf,
  type BuhlmannPlan,
  type BuhlmannModelVariant,
  type DecompressionStop,
  type GasMix,
  type PlanZhL16GfOptions,
} from './buhlmann';

// ─── Clinical calculators ──────────────────────────────────────────────
export {
  bmrMifflinStJeor,
  computeAllBSA,
  bsaBoyd,
  bsaDubois,
  bsaHaycock,
  bsaMosteller,
  duboisBsaM2,
  egfrCKDEPI2009,
  pfRatio,
  interpretPFRatio,
  oxygenIndex,
  sixMinuteWalkDistance,
  computeWellsDVT,
  computeWellsPE,
  aaGradient,
  oxygenDelivery,
  computeAaGradient,
  computeOxygenDelivery,
  type BMRResult,
  type BSAResults,
  type EGFRResult,
  type WellsDVTResult,
  type WellsPEResult,
  type WellsDVTInputs,
  type WellsPEInputs,
  type AaGradientInputs,
  type AaGradientResult,
  type AaNormalModel,
  type OxygenDeliveryInputs,
  type OxygenDeliveryResult,
} from './clinical';

// ─── Fatigue & circadian ───────────────────────────────────────────────
export {
  mitlerPerformance,
  simulateMitlerTrajectory,
  homeostaticWaking,
  homeostaticSleep,
  circadianComponent,
  simulateTwoProcess,
  jetLagDaysToAdjust,
  faa117Limits,
  faa117CumulativeLimits,
  parseHHMM,
  easaMaxDailyFdp,
  easaCumulativeLimits,
  type MitlerTrajectoryPoint,
  type TwoProcessPoint,
  type JetLagResult,
  type Faa117Result,
  type Faa117CumulativeResult,
  type AcclimatisationState,
  type EasaFdpResult,
  type EasaCumulativeResult,
} from './fatigue';

// ─── Risk assessment (SD / NVG / WBV / MSSQ) ───────────────────────────
export {
  spatialDisorientationRisk,
  assessTargetAcquisition,
  cyclesOnTarget,
  rangeForRequiredCycles,
  computeWbvExposure,
  combineAxesIso2631,
  a8FromAw,
  vdv8FromVdv,
  timeToReachA8,
  timeToReachVdv8,
  classifyHgczA8,
  classifyHgczVdv8,
  computeWbvExposureExt,
  computeMssqShort,
  MSSQ_ITEMS,
  VDV_LOWER,
  VDV_UPPER,
  type RiskLevel,
  type SDInputs,
  type SDResult,
  type CriteriaFamily,
  type DiscriminationLevel,
  type ImagingSystem,
  type Target,
  type NvgAcquisitionResult,
  type WbvZone,
  type WbvInputs,
  type WbvResult,
  type WbvAxisWeightedRms,
  type WbvExposureInputsExt,
  type WbvExposureResultExt,
  type MssqPercentileBand,
  type MssqResult,
} from './risk';
