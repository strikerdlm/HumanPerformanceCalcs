# Calculator catalog

Authoritative reference for every function in
`frontend/src/calculators/`. Import from
`'<REPO>/frontend/src/calculators'` (the package re-exports everything via
`index.ts`).

Conventions:
- `(args: T)` means the function takes a single options object of type `T`.
- Unit suffixes follow the function / type name (`_C`, `_kPa`, `_m_s`,
  `_mmHg`, `_msv_yr`, etc.).
- "Scope" identifies the validity envelope; respect it when invoking.

---

## Atmosphere & altitude physiology — `atmosphere.ts`

| Function | Signature | Returns | Reference |
|---|---|---|---|
| `standardAtmosphere` | `(altitude_m: number)` | `ISAResult { temperature_C, temperature_K, pressure_Pa, pressure_hPa, pressure_mmHg, density_kg_m3, pO2_Pa, pO2_mmHg, altitude_m, altitude_ft }` | ICAO Doc 7488-CD |
| `inspiredPO2` | `(altitude_m, FiO2=0.21)` | `number` (mmHg) | West (2012) |
| `alveolarPO2` | `(altitude_m, FiO2=0.21, PaCO2=40, RQ=0.8)` | `number` (mmHg) | West (2012) |
| `spo2Unacclimatized` | `(altitude_m)` | `number` (%) | West & Schoene (2001) |
| `spo2Acclimatized` | `(altitude_m)` | `number` (%) | West & Schoene (2001) |
| `oxygenContent` | `(Hb, SaO2_percent, PaO2)` | `number` (mL O₂/dL) | Hüfner constant 1.34 |
| `tissueRatio` | `(PtissueN2, Pambient)` | `number` | DCS supersaturation |
| `interpretTR` | `(tr)` | `'Low risk' \| 'Moderate risk' \| 'Elevated risk' \| 'High risk'` | — |
| `amsProbability` | `(AAE_km_days)` | `number` (0–1) | Lake Louise / Roach 1993 |
| `estimateTUC` | `(altitude_ft)` | `number` (s, may be Infinity) | USAF Flight Surgeon Handbook |
| `gLocTime` | `(Gz)` | `number` (s, may be Infinity) | Stoll curve, Whinnery 2006 |
| `cosmicDoseRate` | `(altitude_ft, isPolar=false)` | `number` (µSv/h) | Friedberg 1992 (simplified) |
| `pao2AtAltitude` | `(PaO2_ground_mmHg, FEV1_percent)` | `number` (mmHg) | Best-performing regression |
| `altitudeFromPressure` | `(pressure_hPa, sea_level=1013.25)` | `{ altitude_m, altitude_ft }` | Inverse ISA, troposphere only |
| `hapeRiskSuona2023` | `(age, spo2, transport_mode, fatigue, cough, sputum)` | `HAPERiskResult` | Suona et al., BMJ Open 2023 |
| `metersToFeet`, `feetToMeters`, `pascalToMmHg`, `mmHgToPascal` | unit conversions |  |  |

---

## SpO₂ models — `spo2Models.ts`

| Function | Signature | Returns | Reference |
|---|---|---|---|
| `niermeyerSpo2` | `(altitude_m, sex: 'male' \| 'female')` | `SpO2Result` | Niermeyer (cited in Tüshaus 2019) |
| `altVarSpo2` | `(altitude_m, spo2_12h, spo2_24h, hr_12h, hr_24h)` | `SpO2Result` | Alt et al. 2025, R²=0.706 |
| `tushausCascadeSpo2` | `(altitude_m, fi_o2=0.21, temp_c=37)` | `SpO2Result` | Tüshaus, *Physiological Reports* |
| `compareSpo2Models` | `(altitude_m, sex='male')` | `{ Niermeyer, Tushaus }` | — |

---

## Heat stress — `heatStress.ts`

| Function | Signature | Returns | Reference |
|---|---|---|---|
| `wbgtIndoor` | `(T_nwb, T_g)` | `number` (°C) | ISO 7243:2017 |
| `wbgtOutdoor` | `(T_nwb \| null, T_g, T_db, RH?)` | `number` (°C) | ISO 7243:2017 |
| `wbgtRiskAssessment` | `(wbgt)` | `WBGTResult` | — |
| `heatStressIndex` | `(M, T_db, RH, v, W_ext=0, T_g?)` | `number` (%) | Belding & Hatch 1955 |
| `hsiAssessment` | `(hsi)` | `HeatStressIndexResult` | — |
| `predictedHeatStrain` | `(M, T_a, T_mr, RH, v, clo, t_min, ...)` | `PHSResult` | ISO 7933:2023 (simplified) |
| `simulatePHSTrajectory` | `(params, stepMin=5)` | `PHSTrajectoryPoint[]` | — |
| `utci` | `(T_a, T_mr, v_10m, RH)` | `UTCIResult` | Bröde et al. 2012 |
| `utciCategory` | `(utci_C)` | `string` | — |
| `physiologicalStrainIndex` | `({ initial_core_temp_C, final_core_temp_C, initial_heart_rate_bpm, final_heart_rate_bpm })` | `PsiResult` (0–10 + 5 categories) | Moran, Shitzer, Pandolf 1998 |
| `sweatRateGonzalez2009` | `({ e_req_w_m2, e_max_w_m2, bsa_m2? })` | `{ m_sw_g_m2_h, m_sw_L_h }` | Gonzalez et al. 2009 |
| `phsHrModel` | `(PhsHrInputs)` — HR-derived M, full heat balance, sweat, HSI | `PhsHrResult` | ISO 7933:2004 + Malchaire 2006 |
| `ontarioSweatRate` | `({ bsa_m2, hr_rest_bpm, hr_exercise_bpm, t_rest_C, t_exercise_C })` | `{ sweat_rate_L_h, sweat_rate_mL_h }` | Malpica empirical |

PHS sweep helpers (`simulationSweeps.ts`):
| Function | Signature |
|---|---|
| `sweepPhsMetric1d` | sweeps one PHS input over a grid for `allowable_exposure_minutes`, `core_temperature_C_at_horizon`, or `dehydration_percent_body_mass_at_horizon` |
| `sweepPhsMetric2d` | 2-D grid version, returns `z_values: number[][]` |

---

## Cold stress — `coldStress.ts`, `coldWaterSurvival.ts`

| Function | Signature | Returns | Reference |
|---|---|---|---|
| `peakShiveringIntensity` | `(VO2max, BMI, age)` | `number` (mL O₂·kg⁻¹·min⁻¹) | Diego Malpica empirical |
| `windChillTemperature` | `({ temperature_C, wind_speed_m_s })` | `WindChillResult { wind_chill_F, wind_chill_C, out_of_range, note }` | Osczevski & Bluestein 2005 (NWS 2001) |
| `frostbiteRiskFromWindChill` | `(wind_chill_C)` | `'low' \| 'increased' \| 'high' \| 'very_high' \| 'severe'` | NWS frostbite chart |
| `frostbiteTimeMinutes` | `({ temperature_C, wind_speed_m_s })` | `number` (min, may be Infinity) | Tikuisis 2002 |
| `coldWaterSurvival` | `(water_temperature_c, options?)` | `ColdWaterSurvivalEstimate` | Hayward 1975 / TP-13822 Golden |
| `coldWaterSurvivalHayward1975Minutes` | `(t_w, { strict? })` | `number` (min) | Hayward 1975 |
| `coldWaterSurvivalGoldenLifejacketHours` | `(t_w, { strict? })` | `number` (h) | Transport Canada TP 13822 |

---

## Acclimatization & TLV work-rest — `acclimatization.ts`

| Function | Signature | Returns | Reference |
|---|---|---|---|
| `nioshHeatAcclimatizationDays` | `({ day_index, worker_status: 'new' \| 'returning' })` | fraction (0–1) | NIOSH Pub. 2016-106 |
| `acgihTlvWbgt` | `({ metabolic_class, status, regime })` | `number \| null` (°C) | ACGIH 2024 TLVs |
| `wbgtWorkRestRatio` | `({ measured_wbgt_C, metabolic_class, status })` | `WorkRestRecommendation` (most permissive regime) | ACGIH 2024 |

---

## Decompression & diving — `buhlmann.ts`, `nitrox.ts`, `oxygenToxicity.ts`, `dcs_risk.ts`

| Function | Signature | Returns | Reference |
|---|---|---|---|
| `planZhL16Gf` | `(PlanZhL16GfOptions)` — descent / bottom / ascent / stop schedule | `BuhlmannPlan` (stops, total deco minutes) | Bühlmann ZH-L16-B/C; Erik Baker GF |
| `maxOperatingDepth` | `({ fo2, po2_max })` | `number` (m) | NOAA Diving Manual |
| `equivalentAirDepth` | `({ fo2, depth_m })` | `number` (m) | NOAA |
| `bestMix` | `({ depth_m, po2_target })` | `number` (FO₂ fraction) | NOAA |
| `equivalentNarcoticDepth` | `({ fo2, fhe, depth_m })` | `number` (m, O₂ narcotic) | Convention |
| `endNoOxygenNarcosis` | `({ fo2, fhe, depth_m })` | `number` (m, O₂ non-narcotic) | Convention |
| `po2AtDepth` | `(fo2, depth_m)` | `number` (ata) | — |
| `cnsToxicityFraction` | `({ po2_ata, exposure_minutes })` | `NoaaCnsResult` | NOAA Diving Manual |
| `pulmonaryOTU` | `({ po2_ata, exposure_minutes })` | `number` (OTU) | Bardin & Lambertsen 1970 |
| `totalPulmonaryOTU` | `(segments[])` | `number` | — |
| `arieliPowerEquation` | `({ exposure_minutes, po2_ata? \| po2_kpa? })` | `{ k_cns, k_pot, ... }` | Arieli et al. 2002 |
| `dcsProbabilityAltitude` | `({ tissue_ratio, exposure_minutes, exercise, model? })` | `DcsProbabilityResult` | Conkin 2011; Webb 1993 |
| `dcsTimeToProbability` | `({ tissue_ratio, exercise, target_probability, model? })` | `number \| null` (min) | — |

---

## Fatigue, circadian, sleep — `safte.ts`, `fatigue.ts`, `sleep.ts`, `caffeine.ts`

| Function | Signature | Returns | Reference |
|---|---|---|---|
| `simulateSafte` | `(SafteInputs, { max_points? })` | `SafteSeries` (per-step effectiveness, reservoir, inertia) | Patent WO2012015383A1 |
| `mitlerPerformance` | `(t_h, phi_h, SD, K)` | `number` | Mitler |
| `simulateMitlerTrajectory` | `({ phi_hours, SD, K, horizon_hours, step_minutes, max_points })` | `MitlerTrajectory` | — |
| `homeostaticWaking`, `homeostaticSleep`, `circadianComponent`, `simulateTwoProcess` | two-process model | — | Borbély |
| `jetLagDaysToAdjust` | `({ time_zones_crossed, direction })` | `JetLagResult` | — |
| `faa117Limits`, `faa117CumulativeLimits` | duty time | `Faa117Result` / `Faa117CumulativeResult` | FAA 14 CFR §117 |
| `easaMaxDailyFdp`, `easaCumulativeLimits` | duty time | EASA results | EASA ORO.FTL |
| `parseHHMM` | `('HH:MM')` | `number` (decimal h) | — |
| `kssScoreInterpret` | `(score: 1–9)` | `KssResult` | Åkerstedt & Gillberg 1990 |
| `epworthScore` | `(items: number[8])` | `EpworthResult` | Johns 1991 |
| `psqiScore` | `(PsqiComponents)` | `PsqiResult` (global ≤5 = good sleeper) | Buysse 1989 |
| `caffeinePharmacokinetics` | `({ doses[], body_mass_kg, horizon_h, step_h?, params? })` | `CaffeineSeries` (µg/mL over time) | Magkos & Kavouras 2005 |
| `caffeineSteadyState` | `({ dose_mg_per_interval, interval_h, body_mass_kg })` | `{ c_avg, c_max_ss, c_min_ss }` | — |

---

## Aerospace operational risk — `risk.ts`, `agsm.ts`, `aircrew_dose.ts`

| Function | Signature | Returns | Reference |
|---|---|---|---|
| `spatialDisorientationRisk` | `(SDInputs: imc, night, nvg, yaw rate, ...)` | `SDResult { riskIndex 0–100, riskLevel, likelyIllusions[], component scores }` | FAA SD training |
| `assessTargetAcquisition` | `(criteria, discrimination, system, target, rangeM, criticalDimension?)` | `NvgAcquisitionResult { cyclesOnTarget, requiredCyclesN50, meetsN50, ratioToN50 }` | Sjaardema 2015 (SAND2015-6368) |
| `cyclesOnTarget` | `({ system, target, rangeM, criticalDimension? })` | `number` | — |
| `rangeForRequiredCycles` | `(system, target, requiredCycles, criticalDimension?)` | `number` (m) | — |
| `computeWbvExposure` | `(WbvInputs)` | `WbvResult { aw, A(8), zone, time-to-thresholds }` | ISO 2631-1 |
| `combineAxesIso2631`, `a8FromAw`, `vdv8FromVdv`, `timeToReachA8`, `timeToReachVdv8`, `classifyHgczA8`, `classifyHgczVdv8`, `computeWbvExposureExt` | full ISO 2631-1 helpers | — | — |
| `computeMssqShort` | `(sectionA[9], sectionB[9])` | `MssqResult { totalSum, percentileBand }` | Rivera 2022 (Spanish norms) |
| `estimateGzToleranceWithAgsm` | `(AgsmInputs)` | `AgsmResult` (suit/PBG/AGSM components, capped at max_system_gz) | PubMed 17484342 |
| `aircrewDoseRate` | `({ flight_level, latitude_deg, solar_phase? })` | `{ dose_rate_uSv_h, latitude_band }` | FAA CARI-7; ICRP 132 |
| `crewCosmicDoseEstimate` | `({ route: RouteSegment[], solar_phase? })` | `RouteDoseResult` | — |
| `annualCrewDose` | `({ block_hours_per_year, representative_dose_rate_uSv_h })` | `number` (µSv/yr) | — |

---

## Industrial hygiene & ergonomics — `noiseExposure.ts`, `hav.ts`, `niosh_lifting.ts`, `ergonomics.ts`, `ventilation.ts`, `aqi.ts`, `occupationalHealth.ts`

| Function | Signature | Returns | Reference |
|---|---|---|---|
| `permissibleDuration` | `(spl_dba, criterion=90, exchange=5)` | `number` (h) | OSHA 29 CFR §1910.95 |
| `noiseDoseOsha` | `(levels[], durations[])` | `number` (%) | OSHA |
| `noiseDoseNiosh` | `(levels[], durations[])` | `number` (%) | NIOSH (Pub. 98-126) |
| `ahvFromAxes` | `(ahwx, ahwy, ahwz)` | `number` (m/s²) | ISO 5349-1:2001 |
| `havA8FromAhv` | `(ahv, exposure_h)` | `number` (m/s² A(8)) | ISO 5349-1 |
| `havExposurePoints` | `(ahv, exposure_h)` | `number` (HSE pts; 100=EAV, 400=ELV) | HSE |
| `totalHavExposurePoints` | `(tools[])` | `number` | — |
| `classifyHavZone` | `(a8)` | `'below_eav' \| 'eav_to_elv' \| 'above_elv'` | — |
| `computeHavExposure` | `(HavInputs)` | `HavResult` | ISO 5349-1 + HSE |
| `recommendedWeightLimit` | `(NioshLiftInputs)` | `NioshLiftResult { rwl_kg, lifting_index, multipliers, category }` | NIOSH Pub. 94-110 (Waters 1993) |
| `liftingIndex` | `(load_kg, rwl_kg)` | `number` | — |
| `compositeLiftingIndex` | `(tasks: NioshLiftInputs[])` | `{ cli, per_task[] }` | NIOSH 94-110 |
| `rebaScore` | `(RebaInputs)` | `RebaResult { reba_score, score_a/b, table_c, activity_score, risk_level }` | Hignett & McAtamney 2000 |
| `rulaScore` | `(RulaInputs)` | `RulaResult { rula_score 1–7, risk_level }` | McAtamney & Corlett 1993 |
| `dilutionAirflow` | `({ generation_rate, tlv, mixing_factor })` | `number` (vol/min in caller's units) | ACGIH IVM |
| `respiratorMaximumUseConcentration` | `({ respirator: RespiratorClass, tlv })` | `{ apf, muc }` | OSHA 29 CFR §1910.134 |
| `ashrae62OutdoorAirflow` | `({ category, area_m2, occupants? })` | `{ vbz_l_s, ... }` | ASHRAE 62.1-2022 |
| `lpsToCfm`, `cfmToLps` | unit conversions | — | — |
| `aqiFromConcentration` | `(pollutant, concentration)` | `AqiSubIndex` | EPA AirNow 2024 |
| `overallAqi` | `(readings: Partial<Record<AqiPollutant, number>>)` | `AqiOverall { aqi, dominant, sub_indices }` | EPA |
| `aqiCategory` | `(aqi)` | `AqiCategory` | EPA |
| `calculateTwaExposure` | `(concentrations[], durations_h[])` | `number` (8-h TWA) | ACGIH |
| `calculateAdjustedTlvUnusualSchedule` | `(tlv_twa, hpd, dpw)` | `number` | Brief & Scala |
| `calculateMixedExposureIndex` | `(exposures, names)` | `number` (≤1 acceptable) | ACGIH |
| `assessExposureRisk` | `(chemical_name, conc, duration_h=8)` | `ExposureRiskAssessment` | ACGIH 2024 |
| `calculatePermissibleExposureTime` | `(chemical_name, conc)` | `number` (h, ≤8) | Haber's rule |
| `generateExposureReport` | `(facility, date, exposures)` | plain-text report | — |
| `calculateBiologicalExposureIndex` | `(chemical_name, biomarker_conc, sample_timing?)` | `BeiAssessment` | ACGIH BEI |
| `AEROSPACE_CHEMICALS` | constant table | hydrazine, UDMH, MMH, JP-8, NTO, benzene, toluene, methylene chloride | ACGIH 2024 |

---

## Vision — `visionAltitude.ts`

| Function | Signature | Returns | Reference |
|---|---|---|---|
| `estimateDvaLogmarWang2024` | `({ altitude_m, time_at_altitude_min, angular_velocity_deg_s })` | `DvaEstimate { logmar, snellen_denominator_20ft }` | Wang et al. 2024 (chamber study) |
| `logmarToSnellenDenominator` | `(logmar)` | `number` | — |

---

## Clinical / aviation-medical — `clinical.ts`

| Function | Signature | Returns | Reference |
|---|---|---|---|
| `bmrMifflinStJeor` | `(weight_kg, height_cm, age, sex)` | `BMRResult` (kcal/day) | Mifflin 1990 |
| `bsaBoyd`, `bsaDubois`, `bsaHaycock`, `bsaMosteller` | per-formula BSA (m²) | — | original sources |
| `computeAllBSA` | `(height_cm, weight_kg)` | `BSAResults` (all four) | — |
| `duboisBsaM2` | `({ height_cm, weight_kg })` | `number` | — |
| `egfrCKDEPI2009` | `(scr_mg_dL, age, sex, isBlack=false)` | `EGFRResult` (with CKD stage) | Levey 2009 |
| `pfRatio`, `interpretPFRatio`, `oxygenIndex` | gas-exchange | — | — |
| `sixMinuteWalkDistance` | `(height, weight, age, sex)` | `{ predicted_m, lowerLimitNormal_m }` | Enright & Sherrill 1998 |
| `computeWellsDVT` | `(WellsDVTInputs)` | `WellsDVTResult` | Wells 2003 |
| `computeWellsPE` | `(WellsPEInputs)` | `WellsPEResult` | Wells 2001 |
| `aaGradient`, `computeAaGradient` | A–a gradient (simple + full) | `AaGradientResult` (incl. Filley normal range) | Filley 1954 |
| `oxygenDelivery`, `computeOxygenDelivery` | DO₂ / DO₂I | — | — |
| `cha2ds2Vasc` | `(CHA2DS2VAScInputs)` | `{ score, stroke_risk_percent_per_year, recommendation }` | Lip 2010 |
| `hasBled` | `(HasBledInputs)` | `{ score, bleeding_risk_category, bleeds_per_100_patient_years }` | Pisters 2010 |
| `stopBangScore` | `(StopBangInputs)` | `{ score, risk_category }` | Chung 2008 |
| `karvonenTargetHR` | `({ age, hr_rest, intensity_low, intensity_high, hr_max_formula? })` | `KarvonenResult` | Karvonen 1957 / Tanaka 2001 |
| `borgRPEtoHR` | `(rpe ∈ [6, 20])` | `number` (bpm ≈ 10·RPE) | Borg 1982 |

---

## Constants and tables (re-exported)

- `NIOSH_LOAD_CONSTANT_KG = 23`
- `HAV_EAV_M_S2 = 2.5`, `HAV_ELV_M_S2 = 5.0`
- `VDV_LOWER = 8.5`, `VDV_UPPER = 17.0`
- `OSHA_ASSIGNED_PROTECTION_FACTORS` — 15-respirator APF table
- `ASHRAE_62_1_RATES` — outdoor-air rates per occupancy class
- `AEROSPACE_CHEMICALS` — ACGIH TLV/BEI table for 8 aerospace chemicals
- `MSSQ_ITEMS` — Spanish-norms MSSQ-short item list
- `DEFAULT_CAFFEINE_PARAMS`, `DCS_DEFAULT_COEFFS`, `DEFAULT_SAFTE_PARAMETERS`,
  `AGSM_DEFAULT_*`
