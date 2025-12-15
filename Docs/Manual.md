## Manual — Aerospace Medicine & Human Performance Calculator Suite

### UI (Streamlit): roadmap-driven navigation + crystal cards

The Streamlit app includes:

- A **Roadmap** view that summarizes Phase 1 items from `docs/ROADMAP.md`.
- **Coming soon** placeholders for Phase 1 items (so planned tools are discoverable without breaking current workflows).
- A neutral **“crystal / liquid glass”** style applied to **boxes/cards only** (no color palettes injected; compatible with dark mode).

### Atmospheric & Physiological: Bühlmann ZH‑L16 GF Decompression Planner

The **Bühlmann ZH‑L16 GF** decompression planner is available under:

- Sidebar → **🌍 Atmospheric & Physiological** → **Bühlmann ZH‑L16 GF Decompression Planner**

**Inputs (core)**

- Max depth (m)
- “for X minutes” (min)
- GF Low / GF High
- Ascent and descent rates
- Gas mix (O₂% and He%; N₂% is inferred)

**Important time convention**

- The UI includes a toggle to interpret **“for X minutes”** as **runtime at max depth including descent** (i.e., time at depth is \( \max(0, X - t_{descent}) \)).
- Disable the toggle if you want **pure time-at-depth** behavior.

### Atmospheric & Physiological: AGSM Effectiveness (+Gz)

The **AGSM Effectiveness** calculator is available under:

- Sidebar → **🌍 Atmospheric & Physiological** → **AGSM Effectiveness (Anti-G +Gz)**

**What it estimates**

- A transparent **component-style** estimate of how much +Gz tolerance shifts with:
  - anti‑G suit (AGS),
  - pressure breathing for G (PBG/PBfG),
  - AGSM quality (0–100%).

**Scientific anchoring**

- Default deltas are anchored to reported condition values in `PubMed 17484342` (configuration comparisons).
- The UI exposes deltas as **adjustable parameters** so you can tune to your program’s validated data.

### Risk Assessment Tools: Spatial Disorientation (SD) Risk Assessment

The **Spatial Disorientation** tool is available under:

- Sidebar → **📊 Risk Assessment Tools** → **Spatial Disorientation Risk Assessment**

**What it computes**

- **Somatogravic tilt (deg)** from forward linear acceleration using the gravito‑inertial acceleration (GIA) tilt relationship:
  \( \\theta = \\arctan(a_{forward}/g) \\).
- Component scores for common vestibular mechanisms:
  - **Leans** (slow rotation below ~2°/s detection threshold),
  - **Canal entrainment** (~10–20 s constant-rate turns),
  - **Coriolis** (head movement during turn; threshold >~10°/s).
- A bounded **SD Risk Index (0–100)** for *relative* scenario comparison (not a calibrated mishap probability).

**Primary quantitative anchors**

- FAA Spatial Disorientation training materials (leans threshold).
- StatPearls (10–20 s canal entrainment window).
- Houben et al. (2022) for Coriolis threshold (PubMed 34924407).

### Risk Assessment Tools: NVG / EO Target Acquisition (Johnson/ACQUIRE)

The **NVG / EO Target Acquisition** tool estimates **cycles-on-target** for a target at range given an imaging system’s resolution + field-of-view (FOV), and compares it to published **N50** cycle criteria.

- **What it’s good for**: a geometric *feasibility* sanity-check (is the target sampled finely enough for detection/recognition/identification in principle?).
- **What it does not model**: contrast/noise, display luminance, atmospheric attenuation, clutter, gain settings, or human factors/training.
- **Primary reference**: Sjaardema et al. (2015) *History and Evolution of the Johnson Criteria* (SAND2015-6368), which summarizes Johnson and ACQUIRE N50 cycle criteria and their limitations.

### Risk Assessment Tools: Whole-Body Vibration (ISO 2631-1 style A(8) / VDV)

This tool computes ISO 2631‑style exposure metrics from **frequency-weighted** acceleration inputs:

- **Combined \(a_w\)** from tri-axial weighted r.m.s. values (with x/y multiplying factors).
- **A(8)** (8‑hour equivalent acceleration) using \(A(8) = a_w \sqrt{T/8h}\).
- Optional **VDV(8)** scaling if you provide a VDV computed over a reference window.

**Primary references / anchors**

- Mansfield et al. (2009) provides the metrology equations for r.m.s. and VDV used in ISO‑2631 workflows and discusses frequency range considerations: https://doi.org/10.2486/INDHEALTH.47.402
- Orelaja et al. (2019) quotes commonly used HGCZ bounds in published WBV risk reporting (A(8) 0.47–0.93 m/s²; VDV 8.5–17 m/s^1.75): https://doi.org/10.1155/2019/5723830

### Atmospheric & Physiological: Visual Acuity at Altitude (Dynamic Visual Acuity, DVA)

This tool provides an **empirical dynamic visual acuity (DVA)** estimate (LogMAR) for short-term hypobaric exposure based on a controlled chamber study. It accepts:

- altitude (m)
- time at altitude (0–30 min range from the study protocol)
- target angular velocity (deg/s)

**Reference**

- Wang et al. (2024). *Influence of short-term hypoxia exposure on dynamic visual acuity*. *Frontiers in Neuroscience*, 18:1428987. https://doi.org/10.3389/fnins.2024.1428987

### Fatigue & Circadian: Crew Duty Time Limits (FAA Part 117, unaugmented)

This tool implements the FAA Part 117 **unaugmented** lookup tables:

- **Table A**: maximum flight time based on **report time (acclimated)**.
- **Table B**: maximum FDP based on **scheduled start time (acclimated)** and **number of flight segments**.
- **Not acclimated**: applies the **−30 min FDP reduction** described in § 117.13.

**Primary references (official)**

- eCFR Table A: https://www.ecfr.gov/current/title-14/chapter-I/subchapter-G/part-117/appendix-Table%20A%20to%20Part%20117
- eCFR Table B: https://www.ecfr.gov/current/title-14/chapter-I/subchapter-G/part-117/appendix-Table%20B%20to%20Part%20117
- eCFR § 117.13: https://www.ecfr.gov/current/title-14/chapter-I/subchapter-G/part-117/section-117.13

### Fatigue & Circadian: Crew Duty Time Limits (EASA ORO.FTL, basic)

This tool implements a **scoped, table-driven subset** of EASA Air Ops FTL focused on:

- **ORO.FTL.205(b)**: maximum daily FDP for:
  - **acclimatised** crews (Table 2; start time at reference time + sectors)
  - **unknown** state (Table 3; sectors only)
  - **unknown under FRM** (Table 4; sectors only)
- **CS FTL.1.205(b)**: *planned* FDP extension **without in-flight rest** (maximum daily FDP with extension table; limited time bands and sectors)
- **ORO.FTL.210**: cumulative **duty** and **flight time** caps (7/14/28 days, calendar year, 12 months)

**Important limitations (explicit)**

- This does **not** implement the full ORO.FTL framework (standby, reserve, split duty, operator-specific FTL schemes, full in-flight rest extension schemes, commander’s discretion workflows, or WOCL-dependent special cases beyond what is explicitly tabled in the cited tables).
- Treat as a **planning / education** assistant unless validated against your operator’s approved FTL scheme and rostering system.

**Primary reference (official)**

- EASA. *Easy Access Rules for Air Operations (Regulation (EU) No 965/2012) — Revision 22 (February 2025).* (Official PDF) https://www.easa.europa.eu/en/downloads/20342/en

### Atmospheric & Physiological: Alveolar–arterial Oxygen Gradient (A–a)

This tool computes:

- PAO₂ via the alveolar gas equation (already implemented elsewhere in this suite)
- **A–a gradient** as \(A\!-\!a = P_{AO_2} - P_{aO_2}\)

It also shows an optional **reference upper bound** using either:

- the reported resting-cohort statistics from Filley et al. (1954) (context-specific), or
- a clearly labeled **heuristic age-based shortcut** (provided for convenience; not treated as a primary physiologic law).

**Primary references**

- Filley et al. (1954). *J Clin Invest*. https://doi.org/10.1172/JCI102922
- Harris et al. (1974). *Clinical Science*. https://doi.org/10.1042/cs0460089

### Atmospheric & Physiological: Oxygen Delivery Index (DO₂I)

This tool computes:

- **CaO₂** from hemoglobin-bound oxygen plus dissolved oxygen
- **DO₂** from cardiac output and CaO₂
- **DO₂I** by indexing DO₂ to body surface area (BSA)

Constants (Hüfner capacity and dissolved O₂ solubility) are exposed in the UI because different references use slightly different values.

**Reference**

- Filley et al. (1954). *J Clin Invest* (oxygen content/capacity concepts and measurement context). https://doi.org/10.1172/JCI102922

### Fatigue & Circadian: SAFTE Effectiveness (patent-derived)

The **SAFTE Effectiveness** calculator is available under:

- Sidebar → **🧠 Fatigue & Circadian** → **SAFTE Effectiveness (patent-derived)**

**What it computes**

- A multi-day time series of **Effectiveness** \(E_t\) using the patent-equation SAFTE core:
  - Sleep reservoir dynamics (linear depletion while awake; fill while asleep after a short delay)
  - Circadian modulation (two-harmonic cosine form)
  - Sleep inertia (first ~120 minutes after waking)

**Key equation sources**

- `WO2012015383A1` for the explicit equation set (Eq. 1–9): `https://patents.google.com/patent/WO2012015383A1/en`
- SAFTEr (IBR) open-source R implementation built from the patent equations: `https://github.com/InstituteBehaviorResources/SAFTEr`

**Important limitations (explicit)**

- This implementation **does not** include FAST’s proprietary sleep prediction pipeline or circadian phase shifting / jet-lag algorithmic adjustments beyond the explicit circadian equation.

### Environmental Monitoring: Universal Thermal Climate Index (UTCI)

The **UTCI** calculator is available under:

- Sidebar → **🔬 Environmental Monitoring** → **Universal Thermal Climate Index (UTCI)**

**Inputs**

- **Ta**: air temperature (°C)
- **Tr**: mean radiant temperature (°C)
- **v**: wind speed at 10 m (m/s)
- **RH**: relative humidity (%)

**Outputs**

- **UTCI (°C)**: equivalent temperature (“feels-like”)
- **Thermal stress category** (10-level UTCI scale)

**Notes**

- The calculator uses the standard **UTCI polynomial approximation** (UTCI_approx, Oct 2009).
- Optional “strict validity bounds” enforces the common published ranges for the polynomial approximation.

### Environmental Monitoring: Cold Water Immersion Survival Time

The **Cold Water Immersion Survival Time** calculator is available under:

- Sidebar → **🔬 Environmental Monitoring** → **Cold Water Immersion Survival Time**

**What it estimates**

- A **hypothermia-limited** survival time estimate based on published temperature–time guidance.

**What it does NOT estimate**

- Cold shock risk (first minutes), swim failure, wave/spray airway compromise, or drowning risk.

**Models available**

- **Hayward et al. (1975)**: temperature-only survival-time equation (cold-water range).
- **Golden (1996) as cited in Transport Canada TP 13822 (2003)**: fully clothed + lifejacket guidance points (5–15°C) with linear interpolation.

### Simulation Studio (interactive forecasting)

The **Simulation Studio** is a UI for models that naturally support **time-stepping**. It generates trajectories by repeatedly sampling the underlying calculator at bounded intervals (deterministic; no hidden state).

#### Scientifically valid simulators (currently implemented)

- **Heat Strain Simulator (ISO 7933-inspired PHS)**
  - **Outputs**: core temperature trajectory, dehydration trajectory, sweat-rate curves (required/max/effective), allowable exposure and limiting factor.
  - **"What happens next"**: a *next-step* forecast is shown as the change in predicted core temperature over the next selected step.
  - **Source model**: `calculators/phs.py` (`predicted_heat_strain`).

- **Circadian Forecast (Mitler performance envelope)**
  - **Outputs**: performance trajectory over a selectable horizon.
  - **Source model**: `calculators/circadian.py` (`mitler_performance`).

#### Important scope notes

- The simulators do **not** invent physiology beyond the source model. They only sample the existing calculator across time.
- Calculators that are *point estimators* (single-shot formulas) are not automatically simulated unless there is a defensible time-dynamics formulation.

### Where to find it in the app

- Sidebar → **🧪 Simulation Studio**
  - **Heat Strain Simulator (ISO 7933-inspired PHS)**
  - **Circadian Forecast (Mitler performance envelope)**

### Roadmap for Simulation Studio coverage

This roadmap is specific to the **interactive simulator + plot** feature (not the full calculator suite).

- **Now (Live)**
  - PHS trajectory simulator with guardrail shading and next-step forecast
  - Mitler performance trajectory simulator

- **Next (scientifically defensible candidates)**
  - **SAFTE/FAST** multi-day fatigue forecasting (requires implementing the published model)
  - **Cold-water immersion survival** curves as time-to-event trajectories once implemented

- **Not yet included (needs validated dynamics / data)**
  - HAPE/AMS point-risk models as a “time simulator” (requires measured inputs over time or a validated altitude→SpO₂ trajectory model)
  - Chemical/noise exposures as dynamic multi-period profiles (needs a standardized exposure timeline schema)
