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
