# Worked examples

Copy-pasteable scripts the agent can adapt. Each one is self-contained;
run with `npx tsx <file>` from the `frontend/` directory of the
`HumanPerformanceCalcs` checkout (so `node_modules/` and `tsconfig.json`
are picked up).

The import path `<REPO>/frontend/src/calculators` is shorthand — replace
with the absolute path from `~/.claude/skills/aerospace-calculators/.repo_path`
or with a relative path that resolves to the same file.

---

## 1. Plan a 40 m / 35 min air dive (Bühlmann ZH-L16-C with 30/85 GF)

```ts
import { planZhL16Gf } from '<REPO>/frontend/src/calculators';

const plan = planZhL16Gf({
  max_depth_m: 40,
  bottom_time_min: 35,
  gas: { o2: 0.21 },
  gf_low: 0.30,
  gf_high: 0.85,
  model: 'zh-l16c-gf',
});

console.log(`Total deco: ${plan.total_decompression_minutes} min`);
console.log('Stops:');
for (const s of plan.stops) {
  console.log(`  ${s.depth_m} m → ${s.minutes} min`);
}
```

Reference: Bühlmann ZH-L16; Erik Baker (1998) *Gradient Factors*.

---

## 2. Score a STOP-BANG questionnaire

```ts
import { stopBangScore } from '<REPO>/frontend/src/calculators';

const r = stopBangScore({
  snoring: true,
  tired: true,
  observed_apnea: false,
  pressure: true,
  bmi_gt_35: true,
  age_gt_50: true,
  neck_gt_40cm: false,
  male: true,
});
console.log(`STOP-BANG ${r.score}/8 → ${r.risk_category} risk`);
// → STOP-BANG 6/8 → high risk
```

Reference: Chung et al. (2008), *Anesthesiology* 108:812.

---

## 3. CHA₂DS₂-VASc + HAS-BLED for a 78-year-old female with prior stroke

```ts
import { cha2ds2Vasc, hasBled } from '<REPO>/frontend/src/calculators';

const stroke = cha2ds2Vasc({
  congestive_heart_failure: false,
  hypertension: true,
  age_years: 78,
  diabetes: false,
  stroke_tia_or_thromboembolism: true,
  vascular_disease: false,
  female: true,
});
console.log(`CHA₂DS₂-VASc ${stroke.score} → ${stroke.stroke_risk_percent_per_year}% / yr`);
console.log(`Recommendation: ${stroke.recommendation}`);

const bleed = hasBled({
  hypertension_uncontrolled: true,
  abnormal_renal_function: false,
  abnormal_liver_function: false,
  stroke_history: true,
  bleeding_history_or_predisposition: false,
  labile_inr: false,
  age_years: 78,
  drugs_antiplatelet_or_nsaid: false,
  alcohol_excess: false,
});
console.log(`HAS-BLED ${bleed.score} → ${bleed.bleeding_risk_category} risk`);
```

References: Lip et al. (2010); Pisters et al. (2010).

---

## 4. PHS forecast with PSI overlay

```ts
import {
  simulatePHSTrajectory,
  physiologicalStrainIndex,
  predictedHeatStrain,
} from '<REPO>/frontend/src/calculators';

const params: Parameters<typeof predictedHeatStrain> = [
  200,    // metabolic rate W/m² (moderate)
  35,     // air temp °C
  35,     // mean radiant °C
  50,     // RH %
  0.3,    // air velocity m/s
  0.5,    // clothing clo
  120,    // exposure minutes
];
const traj = simulatePHSTrajectory(params, 5);
console.log('time   coreT  dehyd%  sweatL/h');
for (const p of traj) {
  console.log(`${p.time_min.toString().padStart(3)}m  ${p.coreTemp_C.toFixed(2)}  ${p.dehydration_percent.toFixed(2)}  ${p.sweatRate_L_h.toFixed(2)}`);
}
const psi = physiologicalStrainIndex({
  initial_core_temp_C: 37.0,
  final_core_temp_C: traj[traj.length - 1].coreTemp_C,
  initial_heart_rate_bpm: 70,
  final_heart_rate_bpm: 150,
});
console.log(`PSI = ${psi.psi.toFixed(2)} (${psi.category})`);
```

References: ISO 7933; Moran, Shitzer, Pandolf (1998).

---

## 5. NIOSH Lifting Index for a single lift

```ts
import { recommendedWeightLimit } from '<REPO>/frontend/src/calculators';

const r = recommendedWeightLimit({
  load_kg: 18,
  horizontal_cm: 35,
  vertical_cm: 60,
  vertical_travel_cm: 50,
  asymmetry_deg: 30,
  frequency_per_min: 2,
  duration: 'long',           // 'short' = ≤1h, 'moderate' = ≤2h, 'long' = ≤8h
  coupling: 'fair',
});
console.log(`RWL = ${r.rwl_kg.toFixed(2)} kg`);
console.log(`LI  = ${r.lifting_index.toFixed(2)} → ${r.category}`);
```

Reference: NIOSH Pub. 94-110 (Waters et al. 1993).

---

## 6. Aircrew annual cosmic-radiation dose

```ts
import { aircrewDoseRate, annualCrewDose } from '<REPO>/frontend/src/calculators';

const cruise = aircrewDoseRate({
  flight_level: 380,
  latitude_deg: 45,
  solar_phase: 'minimum',
});
console.log(`Cruise dose rate: ${cruise.dose_rate_uSv_h.toFixed(2)} µSv/h`);

const annual = annualCrewDose({
  block_hours_per_year: 750,
  representative_dose_rate_uSv_h: cruise.dose_rate_uSv_h,
});
console.log(`Annual dose: ${(annual / 1000).toFixed(2)} mSv`);
```

References: FAA CARI-7; ICRP 132; NCRP 132.

---

## 7. SAFTE 24-hour effectiveness simulation

```ts
import { simulateSafte } from '<REPO>/frontend/src/calculators';

const series = simulateSafte({
  start_datetime_local: new Date('2025-04-28T08:00:00'),
  horizon_minutes: 24 * 60,
  step_minutes: 15,
  sleep_episodes: [{ start_min: 16 * 60, end_min: 24 * 60 }], // sleep 24:00–08:00
});
console.log(`min E = ${series.min_effectiveness.toFixed(1)}`);
console.log(`max E = ${series.max_effectiveness.toFixed(1)}`);
```

Reference: Patent WO2012015383A1.

---

## 8. AQI from PM2.5 + O3

```ts
import { overallAqi } from '<REPO>/frontend/src/calculators';

const r = overallAqi({ pm25_24h: 32.4, o3_8h: 0.072 });
console.log(`AQI = ${r.aqi} (${r.category}); dominant = ${r.dominant}`);
```

Reference: EPA AirNow Technical Assistance Document (2024).

---

## 9. Caffeine PK across the day

```ts
import { caffeinePharmacokinetics } from '<REPO>/frontend/src/calculators';

const r = caffeinePharmacokinetics({
  doses: [
    { time_h: 0, dose_mg: 200 },        // morning espresso
    { time_h: 4, dose_mg: 100 },        // post-lunch
    { time_h: 8, dose_mg: 50 },         // afternoon
  ],
  body_mass_kg: 75,
  horizon_h: 24,
  step_h: 0.5,
});
console.log(`Cmax = ${r.cmax_ug_ml.toFixed(2)} µg/mL @ t=${r.tmax_h.toFixed(1)} h`);
```

Reference: Magkos & Kavouras (2005), *Sports Med.* 35:191.

---

## 10. Dive nitrox planning combo

```ts
import {
  bestMix,
  maxOperatingDepth,
  cnsToxicityFraction,
  pulmonaryOTU,
} from '<REPO>/frontend/src/calculators';

const fo2 = bestMix({ depth_m: 30, po2_target: 1.4 });
const mod  = maxOperatingDepth({ fo2, po2_max: 1.4 });
const cns  = cnsToxicityFraction({ po2_ata: 1.4, exposure_minutes: 30 });
const otu  = pulmonaryOTU({ po2_ata: 1.4, exposure_minutes: 30 });
console.log(`Best mix at 30 m / 1.4 ata → EAN${(fo2 * 100).toFixed(0)}`);
console.log(`MOD: ${mod.toFixed(1)} m`);
console.log(`CNS: ${(cns.single_exposure_fraction * 100).toFixed(1)}% of single-exposure clock`);
console.log(`OTU: ${otu.toFixed(1)}`);
```

References: NOAA Diving Manual; Bardin & Lambertsen 1970.
