## Manual — Aerospace Medicine & Human Performance Calculator Suite

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
