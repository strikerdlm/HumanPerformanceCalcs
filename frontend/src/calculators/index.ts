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
  altitudeFromPressure,
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
  physiologicalStrainIndex,
  sweatRateGonzalez2009,
  type WBGTResult,
  type HeatStressIndexResult,
  type PHSResult,
  type UTCIResult,
  type PHSTrajectoryPoint,
  type PsiCategory,
  type PsiResult,
  type SweatRateGonzalez2009Inputs,
  type SweatRateGonzalez2009Result,
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
export {
  peakShiveringIntensity,
  windChillTemperature,
  frostbiteRiskFromWindChill,
  frostbiteTimeMinutes,
  type FrostbiteRisk,
  type WindChillResult,
} from './coldStress';
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
  cha2ds2Vasc,
  hasBled,
  stopBangScore,
  karvonenTargetHR,
  borgRPEtoHR,
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
  type CHA2DS2VAScInputs,
  type CHA2DS2VAScResult,
  type HasBledInputs,
  type HasBledResult,
  type StopBangInputs,
  type StopBangResult,
  type MaxHeartRateFormula,
  type KarvonenResult,
} from './clinical';

// ─── NIOSH lifting equation ────────────────────────────────────────────
export {
  recommendedWeightLimit,
  liftingIndex,
  compositeLiftingIndex,
  NIOSH_LOAD_CONSTANT_KG,
  type NioshLiftInputs,
  type NioshLiftResult,
  type WorkDuration,
  type CouplingQuality,
} from './niosh_lifting';

// ─── Hand-arm vibration (ISO 5349-1 + HSE points) ──────────────────────
export {
  ahvFromAxes,
  havA8FromAhv,
  havExposurePoints,
  totalHavExposurePoints,
  classifyHavZone,
  computeHavExposure,
  HAV_EAV_M_S2,
  HAV_ELV_M_S2,
  type HavInputs,
  type HavResult,
  type HavZone,
} from './hav';

// ─── US EPA Air Quality Index (2024) ───────────────────────────────────
export {
  aqiFromConcentration,
  overallAqi,
  aqiCategory,
  type AqiPollutant,
  type AqiCategory,
  type AqiSubIndex,
  type AqiOverall,
} from './aqi';

// ─── Industrial ventilation + respirator selection ─────────────────────
export {
  dilutionAirflow,
  respiratorMaximumUseConcentration,
  ashrae62OutdoorAirflow,
  lpsToCfm,
  cfmToLps,
  OSHA_ASSIGNED_PROTECTION_FACTORS,
  ASHRAE_62_1_RATES,
  type RespiratorClass,
  type Ashrae62Occupancy,
} from './ventilation';

// ─── Nitrox / mixed-gas dive helpers ───────────────────────────────────
export {
  maxOperatingDepth,
  equivalentAirDepth,
  bestMix,
  equivalentNarcoticDepth,
  endNoOxygenNarcosis,
  po2AtDepth,
} from './nitrox';

// ─── Oxygen toxicity (CNS / OTU / Arieli Power Equation) ───────────────
export {
  cnsToxicityFraction,
  pulmonaryOTU,
  totalPulmonaryOTU,
  arieliPowerEquation,
  type NoaaCnsResult,
  type ArieliPowerResult,
} from './oxygenToxicity';

// ─── Caffeine pharmacokinetics ─────────────────────────────────────────
export {
  caffeinePharmacokinetics,
  caffeineSteadyState,
  DEFAULT_CAFFEINE_PARAMS,
  type CaffeineDose,
  type CaffeineParameters,
  type CaffeineSeries,
} from './caffeine';

// ─── Heat acclimatization (NIOSH 2016-106 + ACGIH 2024 TLV) ───────────
export {
  nioshHeatAcclimatizationDays,
  acgihTlvWbgt,
  wbgtWorkRestRatio,
  type MetabolicClass,
  type AcclimatizationStatus,
  type WorkRestRegime,
  type WorkFraction,
  type WorkRestRecommendation,
} from './acclimatization';

// ─── Sleep / sleepiness questionnaires ─────────────────────────────────
export {
  kssScoreInterpret,
  epworthScore,
  psqiScore,
  type KssLevel,
  type KssResult,
  type EpworthCategory,
  type EpworthResult,
  type PsqiCategory,
  type PsqiComponents,
  type PsqiResult,
} from './sleep';

// ─── Hypobaric DCS probability (Conkin / Webb logistic models) ────────
export {
  dcsProbabilityAltitude,
  dcsTimeToProbability,
  DCS_DEFAULT_COEFFS,
  type DcsModel,
  type DcsLogisticCoefficients,
  type DcsProbabilityInputs,
  type DcsProbabilityResult,
} from './dcs_risk';

// ─── Postural ergonomics — REBA + RULA ────────────────────────────────
export {
  rebaScore,
  rulaScore,
  type RebaInputs,
  type RebaResult,
  type RebaTrunkPosition,
  type RebaNeckPosition,
  type RebaLegPosition,
  type RebaUpperArm,
  type RebaLowerArm,
  type RebaWrist,
  type RebaCoupling,
  type RulaInputs,
  type RulaResult,
  type RulaUpperArm,
  type RulaLowerArm,
  type RulaWrist,
  type RulaWristTwist,
  type RulaNeck,
  type RulaTrunk,
  type RulaLegs,
  type RulaForceLoad,
} from './ergonomics';

// ─── Aircrew cosmic radiation dose (CARI-7-style) ─────────────────────
export {
  aircrewDoseRate,
  crewCosmicDoseEstimate,
  annualCrewDose,
  type GeomagneticLatitudeBand,
  type SolarPhase,
  type CrewDoseRateInputs,
  type CrewDoseRateResult,
  type RouteSegment,
  type RouteDoseResult,
} from './aircrew_dose';

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
