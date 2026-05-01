# Aerospace Medicine & Human Performance Calculator Suite

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19955917.svg)](https://doi.org/10.5281/zenodo.19955917)

A peer-reviewed, deterministic library of aerospace medicine, industrial hygiene, and occupational health calculators — written in TypeScript, delivered as ES modules, and usable from Node, the browser, FastAPI, or Claude.

> **Author:** Dr. Diego Malpica, MD — Aerospace Medicine Specialist, Universidad Nacional de Colombia · [GitHub](https://github.com/strikerdlm)
> **Status:** active research project — not for clinical decision-making without independent validation.

---

## What this is

| Layer | Path | What it gives you |
|---|---|---|
| **TypeScript calculator library (primary)** | [`frontend/src/calculators/`](frontend/src/calculators) | ~150 pure functions across 28 modules. Zero runtime dependencies. Importable from any TS/JS project. |
| **React 19 + Vite UI** | [`frontend/`](frontend) | Browser dashboard that consumes the calculator library. ECharts plots, glassmorphism layout, Tailwind v3. |
| **FastAPI server** | [`api/main.py`](api/main.py) | HTTP wrapper exposing a subset of calculators for non-JS clients (R, Python, MATLAB). |
| **LLM agent skill** | [`.claude/skills/aerospace-calculators/`](.claude/skills/aerospace-calculators) | Installable Claude skill that lets any LLM-backed agent invoke the calculators by name. See [Use with Claude / LLMs](#use-with-claude--llms). |
| **Streamlit app (legacy)** | [`streamlit_app.py`](streamlit_app.py) | The original Python implementation. Still works; not the recommended entry point. |

The TS port is now the source of truth. Every calculator in `calculators/*.py` has a TypeScript counterpart with matching numerical behavior; many additions in TS (NIOSH lifting, REBA/RULA, AQI, nitrox, oxygen-toxicity, caffeine PK, CHA₂DS₂-VASc, etc.) have no Python sibling.

---

## Quick install — pick one path

### A. TypeScript / Node (recommended for data scientists)

```bash
git clone https://github.com/strikerdlm/HumanPerformanceCalcs.git
cd HumanPerformanceCalcs/frontend
npm install
```

Use the calculators directly from any Node script:

```ts
// my_script.ts — run with: npx tsx my_script.ts
import {
  predictedHeatStrain,
  physiologicalStrainIndex,
  planZhL16Gf,
  cha2ds2Vasc,
  niermeyerSpo2,
  recommendedWeightLimit,
} from './frontend/src/calculators';

// ISO 7933 PHS at 35°C, 50% RH, moderate work
const phs = predictedHeatStrain(200, 35, 35, 50, 0.3, 0.5, 60);
console.log(`Core temp at 60 min: ${phs.predictedCoreTemp_C.toFixed(2)}°C`);

// Bühlmann ZH-L16-C-GF dive plan: 40 m air, 35 min bottom time
const dive = planZhL16Gf({ max_depth_m: 40, bottom_time_min: 35, gas: { o2: 0.21 } });
console.log(`${dive.stops.length} deco stops, ${dive.total_decompression_minutes} min total`);

// SpO₂ at 3000 m via Niermeyer
const spo2 = niermeyerSpo2(3000, 'male');
console.log(`Predicted SpO₂: ${spo2.predicted_spo2}%`);
```

### B. Browser dashboard

```bash
cd frontend
npm install
npm run dev          # Vite dev server at http://localhost:5173
npm run build        # Static production bundle to frontend/dist/
```

### C. FastAPI server (for R / Python / MATLAB callers)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
# Open http://localhost:8000/docs for the OpenAPI explorer
```

### D. Streamlit (legacy)

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

> ⚠️ The Streamlit app is feature-frozen. New calculators land in TS only. We keep `streamlit_app.py` running for reproducibility of past analyses; new work should use paths A–C.

---

## Calculator catalog

28 modules, ~150 exported functions. The full machine-readable catalog (with citations) lives in [`.claude/skills/aerospace-calculators/CATALOG.md`](.claude/skills/aerospace-calculators/CATALOG.md). Quick map:

| Domain | Modules |
|---|---|
| **Atmospheric & altitude physiology** | `atmosphere`, `spo2Models`, `visionAltitude` |
| **Heat / cold / thermal stress** | `heatStress`, `coldStress`, `coldWaterSurvival`, `acclimatization`, `simulationSweeps` |
| **Decompression & diving** | `buhlmann`, `nitrox`, `oxygenToxicity`, `dcs_risk` |
| **Fatigue, circadian, sleep** | `safte`, `fatigue`, `sleep`, `caffeine` |
| **Aerospace operational risk** | `risk` (SD / NVG / WBV / MSSQ), `agsm`, `aircrew_dose` |
| **Industrial hygiene & ergonomics** | `noiseExposure`, `hav`, `niosh_lifting`, `ergonomics`, `ventilation`, `aqi`, `occupationalHealth` |
| **Clinical / aviation-medical** | `clinical` (BMR, BSA×4, eGFR, P/F, OI, 6MWD, Wells DVT/PE, A–a gradient, DO₂/DO₂I, CHA₂DS₂-VASc, HAS-BLED, STOP-BANG, Karvonen, Borg) |

Every function has primary references in its file-level JSDoc. A representative slice:

| Function | Reference |
|---|---|
| `standardAtmosphere`, `alveolarPO2`, `pao2AtAltitude` | ISO 2533:1975; West (2012) |
| `niermeyerSpo2`, `altVarSpo2`, `tushausCascadeSpo2` | Niermeyer; Alt et al. 2025; Tüshaus |
| `predictedHeatStrain`, `phsHrModel` | ISO 7933:2004; Malchaire 2006 |
| `physiologicalStrainIndex` | Moran et al. 1998 |
| `sweatRateGonzalez2009` | Gonzalez et al. 2009 |
| `planZhL16Gf` | Bühlmann ZH-L16; Erik Baker GF |
| `pulmonaryOTU`, `arieliPowerEquation` | Bardin & Lambertsen 1970; Arieli 2002 |
| `simulateSafte` | Patent WO2012015383A1 |
| `recommendedWeightLimit` | Waters et al. 1993, NIOSH Pub. 94-110 |
| `havA8FromAhv` | ISO 5349-1:2001 |
| `aqiFromConcentration` | EPA AirNow 2024 |
| `rebaScore`, `rulaScore` | Hignett & McAtamney 2000; McAtamney & Corlett 1993 |
| `cha2ds2Vasc`, `hasBled`, `stopBangScore` | Lip 2010; Pisters 2010; Chung 2008 |
| `dcsProbabilityAltitude` | Conkin (NASA TM-2011-216147); Webb & Pilmanis 1993 |
| `crewCosmicDoseEstimate` | FAA CARI-7; ICRP 132; NCRP 132 |

---

## Use with Claude / LLMs

This repo ships with an **installable Claude skill** so any LLM-backed agent (Claude Code, Claude API, the desktop app) can answer questions like *"plan a 40 m / 30 min air dive using ZH-L16-C with 30/85 GF"* or *"score this STOP-BANG questionnaire"* by calling the actual calculator.

```bash
# One-shot install at the user level (~/.claude/skills/)
bash .claude/skills/aerospace-calculators/install.sh
```

The installer:
1. Copies the skill manifest, catalog, and examples to `~/.claude/skills/aerospace-calculators/`.
2. Records the path of this checkout so the skill can `npx tsx` calculator code from a known location.
3. Verifies the installation with a lightweight smoke test.

Once installed, Claude will recognise the skill on questions matching the description (altitude, decompression, heat / cold strain, fatigue, ergonomics, occupational exposure, aviation-medical scoring) and either:
- generate code that imports the right function and execute it, or
- answer directly using the catalog as ground truth (with citations).

If you prefer a project-local install, leave the skill in `<repo>/.claude/skills/`; Claude Code reads it automatically when you run from inside the repo.

For non-Claude agents, point them at `.claude/skills/aerospace-calculators/CATALOG.md` (function-by-function reference, JSON-friendly) and `EXAMPLES.md` (input → output patterns).

---

## Repository layout

```
HumanPerformanceCalcs/
├── frontend/                 # React 19 + Vite + Tailwind UI (primary surface)
│   ├── src/
│   │   ├── calculators/      # ★ TS calculator library (28 modules)
│   │   ├── components/       # Layout, charts, UI primitives
│   │   ├── pages/            # Per-domain calculator pages
│   │   └── types/
│   ├── package.json
│   └── vite.config.ts
├── api/                      # FastAPI HTTP wrapper (subset)
├── calculators/              # Python implementations (kept for parity / reference)
├── aerospace_medicine/       # Domain-specific Python helpers
├── legacy_apps/              # Pre-Streamlit Python scripts (not active)
├── streamlit_app.py          # Legacy Streamlit dashboard (frozen)
├── .claude/
│   └── skills/
│       └── aerospace-calculators/   # ★ LLM agent skill
└── tests/                    # pytest suite for the Python side
```

★ = recommended entry points.

---

## Development

```bash
# Frontend tests + build (run from frontend/)
npm run lint
npm run build           # tsc -b && vite build
npm run dev             # local dev server with HMR

# Python side (run from repo root)
pip install -r requirements.txt
pytest tests/
uvicorn api.main:app --reload
```

To add a new calculator:
1. Create `frontend/src/calculators/<name>.ts` following the pattern of any existing module (interfaces for `Inputs` / `Result`, pure exported functions, file-level JSDoc with primary citation).
2. Re-export from `frontend/src/calculators/index.ts`.
3. Add a smoke test (one assertion per function with a known-good reference value).
4. Update [`.claude/skills/aerospace-calculators/CATALOG.md`](.claude/skills/aerospace-calculators/CATALOG.md) so the LLM skill picks it up.
5. `npm run build` must pass clean.

The repo deliberately uses **no runtime dependencies** in the calculator layer. Everything is plain TypeScript / standard library math. This keeps the library trivially portable to Bun, Deno, Cloudflare Workers, Node, or the browser.

---

## Disclaimer

For research and educational use only. **Not** intended for clinical decision-making, operational flight safety, or regulatory compliance without independent validation by qualified professionals (Certified Industrial Hygienist, Aerospace Medicine Specialist, Diving Medical Officer, etc.).

---

## License

Academic use. See repository for the canonical license file.

---

## References

All citations are drawn directly from the file-level JSDoc in `frontend/src/calculators/*.ts`. The entries below are the union of every source referenced across the 28 calculator modules.

### International Standards

- International Civil Aviation Organization. *Manual of the ICAO Standard Atmosphere*. Doc 7488-CD. 3rd ed. Montréal: ICAO; 1993.
- International Organization for Standardization. *Standard Atmosphere*. ISO 2533:1975. Geneva: ISO; 1975.
- International Organization for Standardization. *Ergonomics of the thermal environment — Assessment of heat stress using the WBGT (wet bulb globe temperature) index*. ISO 7243:2017. Geneva: ISO; 2017.
- International Organization for Standardization. *Ergonomics of the thermal environment — Analytical determination and interpretation of heat stress using calculation of the predicted heat strain*. ISO 7933:2023. Geneva: ISO; 2023.
- International Organization for Standardization. *Mechanical vibration — Measurement and evaluation of human exposure to hand-transmitted vibration*. ISO 5349-1:2001. Geneva: ISO; 2001.
- International Organization for Standardization. *Mechanical vibration and shock — Evaluation of human exposure to whole-body vibration*. ISO 2631-1:1997. Geneva: ISO; 1997.

### Occupational & Environmental Health Guidelines

- American Conference of Governmental Industrial Hygienists. *TLVs and BEIs: Threshold Limit Values for Chemical Substances and Physical Agents and Biological Exposure Indices*. Cincinnati: ACGIH; 2024.
- National Institute for Occupational Safety and Health. *Criteria for a Recommended Standard: Occupational Exposure to Heat and Hot Environments*. DHHS (NIOSH) Publication No. 2016-106. Cincinnati: NIOSH; 2016.
- Waters TR, Putz-Anderson V, Garg A, Fine LJ. *Revised NIOSH Equation for the Design and Evaluation of Manual Lifting Tasks*. DHHS (NIOSH) Publication No. 94-110. Cincinnati: NIOSH; 1994.
- US Environmental Protection Agency. *Technical Assistance Document for the Reporting of Daily Air Quality — the Air Quality Index (AQI)*. EPA-454/B-24-002. Research Triangle Park: EPA; 2024.

### Aerospace & Aviation Medicine Textbooks

- United States Air Force. *Flight Surgeon's Guide*. 3rd ed. Brooks Air Force Base: USAF School of Aerospace Medicine; 1991.
- Ernsting J, Nicholson AN, Rainford DJ, editors. *Aviation Medicine*. 4th ed. London: CRC Press; 2016.
- West JB. *Respiratory Physiology: The Essentials*. 9th ed. Philadelphia: Lippincott Williams & Wilkins; 2012.

### Atmospheric & Altitude Physiology

1. Stull R. Wet-bulb temperature from relative humidity and air temperature. J Appl Meteorol Climatol. 2011;50(11):2267–9. https://doi.org/10.1175/JAMC-D-11-0143.1

### Heat & Thermal Stress

2. Moran DS, Shitzer A, Pandolf KB. A physiological strain index to evaluate heat stress. Am J Physiol Regul Integr Comp Physiol. 1998;275(1):R129–34. https://doi.org/10.1152/ajpregu.1998.275.1.R129
3. Belding HS, Hatch TF. Index for evaluating heat stress in terms of resulting physiological strains. Heat Pip Air Cond. 1955;27(8):129–36.
4. Bröde P, Fiala D, Blazejczyk K, Holmér I, Jendritzky G, Kampmann B, et al. Deriving the operational procedure for the Universal Thermal Climate Index (UTCI). Int J Biometeorol. 2012;56(3):481–94. https://doi.org/10.1007/s00484-011-0454-1
5. Gonzalez RR, Cheuvront SN, Montain SJ, Goodman DA, Blanchard LA, Berglund LG, et al. Expanded prediction equations of human sweat loss and water needs. J Appl Physiol. 2009;107(2):379–88. https://doi.org/10.1152/japplphysiol.00089.2009
6. Malchaire J. Predicted heat strain model. Ann Occup Hyg. 2006;50(2):123–32. https://doi.org/10.1093/annhyg/mei083

### Decompression & Diving

7. Bühlmann AA. *Decompression — Decompression Sickness*. Berlin: Springer-Verlag; 1984.
8. Baker EC. *Clearing Up the Confusion About "Gradient Factors"*. [Technical report on the internet]. 1998 [cited 2024]. Available from: https://www.shearwater.com/wp-content/uploads/2012/08/Gradient_Factors.pdf
9. Bardin H, Lambertsen CJ. *A Quantitative Method for Calculating Pulmonary Toxicity: Use of the "Unit Pulmonary Toxicity Dose" (UPTD)*. Report of the Institute for Environmental Medicine. Philadelphia: University of Pennsylvania; 1970.
10. Arieli R, Rashkovan G, Moskovitz Y, Ertracht O. PCO₂ and O₂ toxicity seizure latency in rats: the time-dose relationship. J Appl Physiol. 2002;93(3):1098–105. https://doi.org/10.1152/japplphysiol.00244.2002
11. Webb JT, Pilmanis AA. Altitude decompression sickness between 6858 and 9144 m following a 1-h prebreathe protocol. Aviat Space Environ Med. 1993;64(4):283–8.
12. Conkin J. *Preventing Decompression Sickness Over a Range of Ambulation and Microgravity*. NASA Technical Memorandum TM-2011-216147. Houston: NASA Johnson Space Center; 2011.

### Fatigue, Circadian & Sleep

13. Hursh SR, Raslear TG, Schultz T, Elliott RD. *The Fatigue Avoidance Scheduling Tool: Modeling to Minimize the Risk of Fatigue-Related Performance Failures in Transportation Operations*. International Patent WO2012015383A1. 2012.
14. Tanaka H, Monahan KD, Seals DR. Age-predicted maximal heart rate revisited. J Am Coll Cardiol. 2001;37(1):153–6. https://doi.org/10.1016/S0735-1097(00)01054-8
15. Karvonen MJ, Kentala E, Mustala O. The effects of training on heart rate: a longitudinal study. Ann Med Exp Biol Fenn. 1957;35(3):307–15.

### Ergonomics & Industrial Hygiene

16. Waters TR, Putz-Anderson V, Garg A, Fine LJ. Revised NIOSH equation for the design and evaluation of manual lifting tasks. Ergonomics. 1993;36(7):749–76. https://doi.org/10.1080/00140139308967940
17. Hignett S, McAtamney L. Rapid entire body assessment (REBA). Appl Ergon. 2000;31(2):201–5. https://doi.org/10.1016/S0003-6870(99)00039-3
18. McAtamney L, Corlett EN. RULA: a survey method for the investigation of work-related upper limb disorders. Appl Ergon. 1993;24(2):91–9. https://doi.org/10.1016/0003-6870(93)90080-S

### Clinical & Aviation-Medical Scoring

19. Mifflin MD, St Jeor ST, Hill LA, Scott BJ, Daugherty SA, Koh YO. A new predictive equation for resting energy expenditure in healthy individuals. Am J Clin Nutr. 1990;51(2):241–7. https://doi.org/10.1093/ajcn/51.2.241
20. Du Bois D, Du Bois EF. A formula to estimate the approximate surface area if height and weight be known. Arch Intern Med. 1916;17(6):863–71. https://doi.org/10.1001/archinte.1916.00080130002002
21. Mosteller RD. Simplified calculation of body-surface area. N Engl J Med. 1987;317(17):1098. https://doi.org/10.1056/NEJM198710223171717
22. Haycock GB, Schwartz GJ, Wisotsky DH. Geometric method for measuring body surface area: a height-weight formula validated in infants, children, and adults. J Pediatr. 1978;93(1):62–6. https://doi.org/10.1016/S0022-3476(78)80601-5
23. Boyd E. *The Growth of the Surface Area of the Human Body*. Minneapolis: University of Minnesota Press; 1935.
24. Levey AS, Stevens LA, Schmid CH, Zhang YL, Castro AF 3rd, Feldman HI, et al. A new equation to estimate glomerular filtration rate. Ann Intern Med. 2009;150(9):604–12. https://doi.org/10.7326/0003-4819-150-9-200905050-00006
25. Enright PL, Sherrill DL. Reference equations for the six-minute walk in healthy adults. Am J Respir Crit Care Med. 1998;158(5 Pt 1):1384–7. https://doi.org/10.1164/ajrccm.158.5.9710086
26. Wells PS, Anderson DR, Rodger M, Ginsberg JS, Kearon C, Gent M, et al. Derivation of a simple clinical model to categorize patients' probability of pulmonary embolism: increasing the models utility with the SimpliRED D-dimer. Thromb Haemost. 2001;85(3):416–20. https://doi.org/10.1055/s-0037-1615630
27. Wells PS, Owen C, Doucette S, Fergusson D, Tran H. Does this patient have deep vein thrombosis? JAMA. 2003;295(2):199–207. https://doi.org/10.1001/jama.295.2.199
28. Filley GF, MacIntosh DJ, Wright GW. Carbon monoxide uptake and pulmonary diffusing capacity in normal subjects at rest and during exercise. J Clin Invest. 1954;33(4):530–9. https://doi.org/10.1172/JCI102926
29. Lip GYH, Nieuwlaat R, Pisters R, Lane DA, Crijns HJ. Refining clinical risk stratification for predicting stroke and thromboembolism in atrial fibrillation using a novel risk factor-based approach: the Euro Heart Survey on atrial fibrillation. Chest. 2010;137(2):263–72. https://doi.org/10.1378/chest.09-1584
30. Pisters R, Lane DA, Nieuwlaat R, de Vos CB, Crijns HJ, Lip GY. A novel user-friendly score (HAS-BLED) to assess 1-year risk of major bleeding in patients with atrial fibrillation: the Euro Heart Survey. Chest. 2010;138(5):1093–100. https://doi.org/10.1378/chest.10-0134
31. Chung F, Yegneswaran B, Liao P, Chung SA, Vairavanathan S, Islam S, et al. STOP questionnaire: a tool to screen patients for obstructive sleep apnea. Anesthesiology. 2008;108(5):812–21. https://doi.org/10.1097/ALN.0b013e31816d83e4
32. Borg GAV. Psychophysical bases of perceived exertion. Med Sci Sports Exerc. 1982;14(5):377–81. https://doi.org/10.1249/00005768-198205000-00012

### Radiation — Aircrew Cosmic Dose

- Federal Aviation Administration. *CARI-7: Computer Program for Calculating Cosmic Radiation Dose Rate*. Washington DC: FAA Civil Aerospace Medical Institute; 2014.
- International Commission on Radiological Protection. *Occupational Intakes of Radionuclides: Part 1*. ICRP Publication 132. Ann ICRP. 2016;45(Suppl).
- National Council on Radiation Protection and Measurements. *Radiation Protection Guidance for Activities in Low-Earth Orbit*. NCRP Report No. 132. Bethesda: NCRP; 2000.
