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
