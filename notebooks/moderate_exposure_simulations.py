# %% [markdown]
r"""
# Human Performance Calculations – Multiple Exposure Scenarios

This notebook-style script (
[Jupytext](https://jupytext.readthedocs.io/) compatible – each `# %%` denotes a cell) extends
our prior *moderate-exposure* walkthrough.  We now explore **three distinct scenarios**
(*mild*, *moderate* and *high* exposure) for each aerospace-medicine calculator and
summarise the outputs.

> **Disclaimer** — Research & education use only.  Do **not** apply to operational or
> clinical decision-making without professional validation.
"""

# %%
# Standard imports and helper setup
import sys, pathlib, datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

root = pathlib.Path.cwd()
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

plt.style.use("seaborn-v0_8")
# NOTE: Jupyter/IPython magic removed so this file is valid Python when run via
# standard tooling (linters, `python -m compileall`, CI).

subject = {
    "age": 34,
    "weight_kg": 80,
    "height_cm": 178,
    "resting_hr": 70,
}
subject

# %% [markdown]
"""
## 1  Altitude / Barometric Physiology
We vary cabin / ambient pressure across three representative settings:

| Scenario | Pressure (mmHg) | Approx. Altitude (ft) |
|----------|-----------------|-----------------------|
| *Mild*   | 700             | ~3 000                |
| *Mod.*   | 565             | ~8 000                |
| *High*   | 380             | ~18 000               |
"""

# %%
from aerospace_medicine.altitude.altitude_calc import (
    altitude_from_pressure,
    calculate_parameters,
    meters_to_feet,
    interpret_altitude_effects,
)

pressure_scenarios = {
    "Mild": 700,
    "Moderate": 565,
    "High": 380,
}

altitude_rows = []
for label, p_mmHg in pressure_scenarios.items():
    p_hPa = p_mmHg * 1.33322
    alt_m = altitude_from_pressure(p_hPa)
    alt_ft = meters_to_feet(alt_m)
    PAO2, FiO2_eq, PaO2, vol_exp = calculate_parameters(p_hPa)
    altitude_rows.append(
        {
            "Scenario": label,
            "Pressure_mmHg": p_mmHg,
            "Altitude_ft": alt_ft,
            "PAO2": PAO2,
            "PaO2": PaO2,
            "FiO2_eq_%": FiO2_eq * 100,
            "Vol_Exp": vol_exp,
            "Interpretation": interpret_altitude_effects(alt_m, PAO2),
        }
    )

alt_df = pd.DataFrame(altitude_rows)
alt_df

# %%
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(alt_df["Scenario"], alt_df["Altitude_ft"], color="#4c72b0")
ax.set_ylabel("Altitude (ft)")
ax.set_title("Calculated altitude across scenarios")
plt.show()

# %% [markdown]
"""
## 2  Physiological Strain Index (Heat Stress)
We model a 60-min task with increasing thermal/heart-rate load.

| Scenario | ΔCore Temp (°C) | Final HR (bpm) |
|----------|-----------------|---------------|
| *Mild*   | +0.3            | 100           |
| *Mod.*   | +1.0            | 120           |
| *High*   | +1.5            | 140           |
"""

# %%
from PhysiolStrainIndex import physiological_strain_index, interpret_psi

psi_rows = []
for label, (dT, hr_final) in {
    "Mild": (0.3, 100),
    "Moderate": (1.0, 120),
    "High": (1.5, 140),
}.items():
    psi_val = physiological_strain_index(
        initial_core_temp=37.0,
        initial_heart_rate=subject["resting_hr"],
        final_core_temp=37.0 + dT,
        final_heart_rate=hr_final,
        age=subject["age"],
    )
    psi_rows.append(
        {
            "Scenario": label,
            "PSI": psi_val,
            "Interpretation": interpret_psi(psi_val),
        }
    )
psi_df = pd.DataFrame(psi_rows)
psi_df

# %%
fig, ax = plt.subplots(figsize=(6, 3))
ax.bar(psi_df["Scenario"], psi_df["PSI"], color="#ef8a62")
ax.set_ylim(0, 10)
ax.set_ylabel("PSI (0-10)")
ax.set_title("Heat strain across scenarios")
plt.show()

# %% [markdown]
"""
## 3  Sweat-rate & Hydration
60-min cycling sessions under rising heat load and sweat loss.

| Scenario | Weight loss (kg) | Fluid In (L) | Urine (L) |
|----------|-----------------|--------------|-----------|
| *Mild*   | 0.4             | 0.4          | 0.1       |
| *Mod.*   | 0.8             | 0.5          | 0.1       |
| *High*   | 1.3             | 0.7          | 0.1       |
"""

# %%
from SimpleSweatRate import (
    calculate_sweat_rate,
    get_dehydration_percentage,
    interpret_sweat_rate,
    interpret_dehydration,
    calculate_replacement_fluid_needed,
)

sweat_rows = []
for label, (mass_loss, fluid_in) in {
    "Mild": (0.4, 0.4),
    "Moderate": (0.8, 0.5),
    "High": (1.3, 0.7),
}.items():
    pre_w = subject["weight_kg"]
    post_w = pre_w - mass_loss
    duration = 1.0  # hr
    sweat_rate = calculate_sweat_rate(pre_w, post_w, fluid_in, 0.1, duration)
    dehydration_pct = get_dehydration_percentage(pre_w, post_w)
    rec_rate, rec_total = calculate_replacement_fluid_needed(sweat_rate, duration)
    sweat_rows.append(
        {
            "Scenario": label,
            "SweatRate_Lh": sweat_rate,
            "Dehyd_%": dehydration_pct,
            "Rec_Intake_Lh": rec_rate,
            "Interpretation": interpret_sweat_rate(sweat_rate),
        }
    )

sweat_df = pd.DataFrame(sweat_rows)
sweat_df

# %%
fig, ax = plt.subplots(figsize=(7, 3))
ax.bar(sweat_df["Scenario"], sweat_df["SweatRate_Lh"], color="#55a868")
ax.set_ylabel("Sweat rate (L/h)")
ax.set_title("Sweat rate across scenarios")
plt.show()

# %% [markdown]
"""
## 4  Wind-chill (Cold Stress)
We examine three winter aviation ground operations:

| Scenario | Air Temp (°C) | Wind (m/s) |
|----------|--------------|-----------|
| *Mild*   | 8            | 1.5       |
| *Mod.*   | 5            | 5         |
| *High*   | 0            | 10        |
"""

# %%
from WCT import wind_chill_temperature, interpret_wind_chill

wind_rows = []
for label, (temp_c, wind_ms) in {
    "Mild": (8, 1.5),
    "Moderate": (5, 5),
    "High": (0, 10),
}.items():
    wc = wind_chill_temperature(temp_c, max(1.34, wind_ms), output_unit="celsius")
    wind_rows.append(
        {
            "Scenario": label,
            "Ambient_°C": temp_c,
            "Wind_m_s": wind_ms,
            "WindChill_°C": wc,
            "Interpretation": interpret_wind_chill(wc),
        }
    )
wind_df = pd.DataFrame(wind_rows)
wind_df

# %%
fig, ax = plt.subplots(figsize=(6, 3))
ax.bar(wind_df["Scenario"], wind_df["WindChill_°C"], color="#c44e52")
ax.set_ylabel("Wind-chill °C")
ax.set_title("Wind-chill equivalent temperature")
plt.show()

# %% [markdown]
"""
## 5  Fatigue / Cognitive Performance
Simplified 24 h simulation with varying sleep quantity.
"""

# %%
try:
    # Legacy notebook dependency; keep optional so this script remains importable.
    from FatigueCalcVerAlfa2 import simulate_cognitive_performance  # type: ignore
except Exception:  # pragma: no cover - optional notebook dependency
    simulate_cognitive_performance = None

fatigue_rows = []
for label, sleep_hours in {
    "Mild": 8,
    "Moderate": 6,
    "High": 4,
}.items():
    if simulate_cognitive_performance is None:
        continue
    sleep_history = [
        (23, 23 + sleep_hours % 24, 0.8, sleep_hours, 2, sleep_hours - 2, 0),
        (23, 23 + sleep_hours % 24, 0.8, sleep_hours, 2, sleep_hours - 2, 0),
    ]
    work_history = [(9, 17), (9, 17)]
    load_rating_history = [0.5, 0.5]

    t_pts, _, cog_perf = simulate_cognitive_performance(
        24, sleep_history, work_history, load_rating_history, 0
    )
    fatigue_rows.append({"Scenario": label, "MinPerf": np.min(cog_perf), "MeanPerf": np.mean(cog_perf)})

fatigue_df = pd.DataFrame(fatigue_rows)
fatigue_df

# %%
fig, ax = plt.subplots(figsize=(6, 3))
ax.bar(fatigue_df["Scenario"], fatigue_df["MinPerf"], color="#4c72b0")
ax.set_ylabel("Minimum predicted performance score")
ax.set_title("Fatigue impact across scenarios (24 h)")
plt.show()

# %% [markdown]
"""
---

### Summary
This extended analysis compares *mild*, *moderate* and *high* exposure scenarios
across five aerospace-medicine calculators, providing a holistic view of
physiological risk envelopes for a typical male subject.

You can further adapt the `pressure_scenarios`, `psi_rows`, and other dictionaries
above to explore custom conditions.
"""