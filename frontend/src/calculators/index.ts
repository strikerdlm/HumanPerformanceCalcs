/**
 * Aerospace Medicine & Human Performance Calculator Suite
 * 
 * TypeScript implementation for publication-quality safety dashboards
 * 
 * Principal Investigator: Dr. Diego Malpica
 * Universidad Nacional de Colombia
 */

// Atmosphere & Altitude Physiology
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
  metersToFeet,
  feetToMeters,
  pascalToMmHg,
  mmHgToPascal,
  type ISAResult,
} from './atmosphere';

// Heat Stress & Environmental
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

// Clinical Calculators
export {
  bmrMifflinStJeor,
  computeAllBSA,
  egfrCKDEPI2009,
  pfRatio,
  interpretPFRatio,
  oxygenIndex,
  sixMinuteWalkDistance,
  computeWellsDVT,
  computeWellsPE,
  aaGradient,
  oxygenDelivery,
  type BMRResult,
  type BSAResults,
  type EGFRResult,
  type WellsDVTResult,
  type WellsPEResult,
  type WellsDVTInputs,
  type WellsPEInputs,
} from './clinical';

// Fatigue & Circadian
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

// Risk Assessment
export {
  spatialDisorientationRisk,
  assessTargetAcquisition,
  rangeForRequiredCycles,
  computeWbvExposure,
  computeMssqShort,
  MSSQ_ITEMS,
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
  type MssqPercentileBand,
  type MssqResult,
} from './risk';
