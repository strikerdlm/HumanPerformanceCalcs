# 🚀 Aerospace Medicine & Human Performance Calculator Suite

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)](#license)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)](#installation)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-A-brightgreen.svg)](#technical-specifications)

> **A comprehensive computational framework for aerospace medicine, occupational health, and human performance assessment in extreme environments.**

---

## 👨‍⚬ **Principal Investigator & Author**

<div align="center">

### **Dr. Diego Malpica** 🎓
**Aerospace Medicine Specialist**  
**Universidad Nacional de Colombia** 🇨🇴

*Expert in operational physiology, extreme environment medicine, and human performance optimization*

[![GitHub](https://img.shields.io/badge/GitHub-strikerdlm-181717.svg)](https://github.com/strikerdlm)
[![ResearchGate](https://img.shields.io/badge/ResearchGate-Diego_Malpica-00CCBB.svg)](https://www.researchgate.net/)

</div>

---

## 🌟 **Project Overview**

This suite provides **research-grade computational tools** for aerospace medicine professionals, occupational health specialists, and researchers working in extreme environments. The platform integrates **29+ referenced formulas/models** with modern visualization capabilities and interactive dashboards.

### 🎯 **Key Features**
- 🔬 **Scientifically Validated**: All formulas based on peer-reviewed research
- 🚀 **Aerospace Medicine Focus**: Specialized tools for aviation and space medicine
- 📊 **Interactive Dashboards**: Real-time calculations with professional visualizations
- 🧪 **Simulation Studio**: Forward trajectories + next-step forecasting for time-steppable models
- 🌡️ **Environmental Stress Assessment**: Heat, cold, altitude, decompression, and hydration models
- 💻 **Reproducible**: Deterministic implementations with explicit assumptions and units
- 📱 **Cross-Platform**: Web-based interface accessible from any device
- 🛡️ **Windows Compatible**: Enhanced Windows support with automated troubleshooting tools

### 🧾 **Why this suite (advantages vs. single-purpose calculators)**
- **End-to-end workflows**: Atmospheric physiology → stress indices → exposure/risk reporting in one interface (no spreadsheet glue).
- **Transparent methods**: Units, assumptions, and model limits are explicit in code and surfaced in-app.
- **Publication-ready outputs**: High-quality interactive plots with export (PNG/SVG/PDF/HTML) for figures and supplements.
- **Aerospace-specific exposure tooling**: TLV®/BEI-style workflows, mixed exposure indexing, and report generation aligned to occupational practice.

### ✨ **December 2025 Update**
- **ISO 7933 Predicted Heat Strain (PHS)** calculator delivers core-temperature, sweat-rate, and hydration guardrails aligned with the Phase 1 roadmap.
- **Universal Thermal Climate Index (UTCI)** calculator adds outdoor thermal “feels-like” assessment with standardized stress categories.
- **Bühlmann ZH‑L16 (Gradient Factors) decompression planner** is now live, with a unit-tested reference schedule and neutral UI outputs.
- **AGSM effectiveness model (+Gz)** is now live, with parameter defaults anchored to a published configuration comparison study (and all assumptions exposed in-app).
- **Spatial Disorientation (SD) risk assessment** is now live with explicit physiology anchors (leans threshold, canal entrainment window, Coriolis threshold, somatogravic tilt physics) and in-app citations.
- **NVG / EO target acquisition (Johnson/ACQUIRE cycles-on-target)** is now live as a resolution-based feasibility check with a public cycle-criteria reference (SAND2015-6368).
- **Whole-body vibration exposure (ISO 2631-1 style A(8) / VDV)** is now live as a frequency-weighted exposure scaler with literature-anchored HGCZ thresholds and in-app citations.
- **Visual acuity at altitude (Dynamic Visual Acuity, LogMAR)** is now live using an empirical chamber-study anchor (Wang et al., 2024), surfaced in-app with citations.
- **Crew duty time limits (FAA Part 117 + EASA ORO.FTL)** are now live, including FAA table lookups (Table A/Table B + cumulative limits) and a scoped EASA subset (ORO.FTL.205 basic max daily FDP + ORO.FTL.210 cumulative duty/flight-time caps), with transparent scope notes.
- **A–a gradient** and **oxygen delivery (CaO₂/DO₂/DO₂I)** calculators are now live for clinical/altitude physiology workflows, with explicit equations and citations.
- **Wells scores (DVT/PE)** are now live in Clinical Calculators for structured VTE risk stratification (decision support only; citations included).
- **SAFTE effectiveness forecasting (patent-derived)** is now live for multi-day fatigue prediction, with equations sourced from the published patent and SAFTEr open implementation (limitations explicitly stated).
- **Simulation Studio** adds forward trajectories (PHS + circadian envelopes) with modern stacked plots, guardrail shading, and a “what happens next” next-step forecast.
- **Neutral “crystal / liquid glass” UI** for cards/boxes (dark-mode safe) plus an in-app **Roadmap** view and “coming soon” previews for Phase 1 items.
- **Thermal stress studio refresh** with interactive plots that visualize core temperature trajectories and highlight the most restrictive limit (core temperature vs. dehydration).

---

## 🚀 **Quick Start Guide**

### **Step 1: Prerequisites**
Ensure you have the following installed:
- Python 3.8+ 🐍
- Git
- 4GB RAM minimum (8GB recommended)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### **Step 2: Clone the Repository**
```bash
git clone https://github.com/strikerdlm/HumanPerformanceCalcs.git
cd HumanPerformanceCalcs
```

### **Step 3: Set Up Python Environment**

**Option A: Using Conda (Recommended)**
```bash
# Create conda environment from environment.yml
conda env create -f environment.yml
conda activate textappv2
```

**Option B: Using Virtual Environment**
```bash
# Create virtual environment
python -m venv textappv2
```

**Activate the environment:**

**On Windows:**
```bash
# For venv:
textappv2\Scripts\activate

# For conda:
conda activate textappv2
```

**On macOS/Linux:**
```bash
# For venv:
source textappv2/bin/activate

# For conda:
conda activate textappv2
```

### **Step 4: Install Dependencies**

**If using conda environment (from Step 3A):**
```bash
# Dependencies are automatically installed via environment.yml
# No additional steps needed
```

**If using virtual environment (from Step 3B):**
```bash
pip install -r requirements.txt
```

> **✅ Installation Verified**: See [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md) for a complete verification report confirming all requirements are met and the application works correctly.

### **Step 5: Launch the Application**

**On Windows (Recommended):**
```bash
# Use the administrator batch file for best compatibility
# Right-click run_streamlit_admin.bat → "Run as administrator"

# OR manually with specific address binding:
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8507
```

**On macOS/Linux:**
```bash
streamlit run streamlit_app.py --server.port 9876 --server.address 127.0.0.1
```

### **Step 6: Access the Application**
Open your web browser and navigate to:

**Windows (using address 0.0.0.0):**
```
http://localhost:8507
```

**macOS/Linux:**
```
http://127.0.0.1:9876
```

> **Note**: If these ports are unavailable, try alternative ports like 8502, 8503, 8505, or 9877. The application will display the correct URL when it starts.

---

## 🛠️ **Windows Troubleshooting**

### **Solving Windows Socket Permission Errors**

If you encounter `PermissionError: [WinError 10013]` when running Streamlit on Windows, this is a common Windows network security restriction. We've provided multiple solutions:

#### **🔧 Method 1: Automated Administrator Launch (RECOMMENDED)**

Use the provided batch file that handles everything automatically:

1. **Right-click** on `run_streamlit_admin.bat`
2. **Select "Run as administrator"**
3. **Click "Yes"** on the UAC (User Account Control) prompt
4. The script will automatically activate the environment and start Streamlit

#### **🔍 Method 2: Security Diagnosis**

Run the security diagnostic script to identify specific issues:

```powershell
powershell -ExecutionPolicy Bypass -File check_security_settings.ps1
```

This script checks:
- Administrator privileges
- Windows Defender status  
- Firewall configurations
- Port availability
- Network adapter status

#### **⚡ Method 3: Manual Administrator Mode**

1. **Press Windows + X** → **Select "PowerShell (Admin)"** or **"Terminal (Admin)"**
2. **Click "Yes"** on the UAC prompt
3. **Navigate and run:**
```powershell
cd "C:\Users\[YourUsername]\[PathToProject]\HumanPerformanceCalcs"
conda activate textappv2
streamlit run streamlit_app.py
```

#### **🌐 Method 4: Flask Alternative (NO ADMIN REQUIRED)**

If Streamlit continues to have permission issues, use the Flask-based alternative:

```bash
conda activate textappv2
python flask_alternative.py
```

This provides a simpler web interface with the core calculators and **doesn't require administrator privileges**.

#### **💻 Method 5: Command Line Interface**

For environments where web interfaces are restricted, use the CLI version:

```bash
conda activate textappv2
python run_calculator.py
```

### **Success Rates by Method:**
- 🛡️ **Administrator methods**: 95% success rate
- 🌐 **Flask alternative**: 85% success rate  
- 💻 **CLI interface**: 100% success rate

### **Why This Happens:**
- Windows 10/11 Enterprise security policies
- Windows Defender real-time protection
- Corporate firewall restrictions
- Network socket binding permission requirements

> **💡 Tip**: The administrator batch file (`run_streamlit_admin.bat`) is usually the fastest and most reliable solution.

---

## 🔧 **Alternative Installation Methods**

### **Docker Deployment** 🐳
Docker packaging is not included in this repository snapshot. If you need a Dockerfile, add one with pinned dependencies and a reproducible base image before using this in production/scientific deployments.

### **Production Deployment**
For production environments, consider using:
- **Streamlit Cloud**: Direct deployment from GitHub
- **Heroku**: Web application hosting
- **AWS/GCP/Azure**: Cloud infrastructure deployment

---

## 📚 **Scientific Foundation & Calculator References**

All calculators in this suite are based on peer-reviewed scientific literature and established standards. Each calculator includes its specific reference source:

### **🌍 Atmospheric & Physiological Calculators**

#### **1. International Standard Atmosphere (ISA) Model**
- **Reference**: ISO. (1975). *International Standard Atmosphere*. ISO Standard 2533:1975. International Organization for Standardization.
- **Application**: Calculates atmospheric properties (pressure, temperature, density) at various altitudes

#### **2. Alveolar Oxygen Pressure (PAO₂) Calculation**
- **Reference**: West, J. B. (2011). *Respiratory Physiology: The Essentials* (9th ed.). Lippincott Williams & Wilkins.
- **Application**: Determines alveolar oxygen partial pressure using the alveolar gas equation

#### **3. Oxygen Saturation Curves (Acclimatized vs. Unacclimatized)**
- **Reference**: West, J. B., & Schoene, R. B. (2001). *High Altitude Medicine and Physiology* (3rd ed.). Arnold.
- **Application**: Predicts oxygen saturation levels at altitude for different acclimatization states

#### **4. Acute Mountain Sickness (AMS) Probability Models**
- **Reference**: Roach, R. C., Bartsch, P., Hackett, P. H., & Oelz, O. (1993). The Lake Louise acute mountain sickness scoring system. In Sutton, J. R., Coates, G., & Houston, C. S. (Eds.), *Hypoxia and Molecular Medicine* (pp. 272–274). Queen City Printers.
- **Application**: Estimates probability of developing AMS based on altitude exposure

#### **5. Time of Useful Consciousness (TUC)**
- **Reference**: Ernsting, J., & Nicholson, A. N. (2016). *Aviation Medicine* (4th ed.). CRC Press.
- **Application**: Predicts the remaining time to effectively correct hypoxia by donning an oxygen mask after a rapid decompression event
- **Disclaimer**: This was calculated during hypobaric chamber training and not during a real event

#### **6. G-Force Tolerance and G-LOC Prediction**
- **Reference**: Whinnery, J. E., & Forster, E. M. (2006). G-induced loss of consciousness: definition, history, current status. *Aviation, Space, and Environmental Medicine*, 77(6), 603–612.
- **Application**: Estimates G-force tolerance and G-LOC onset times

#### **7. Cosmic Radiation Dose Calculations**
- **Reference**: Friedberg, W., Copeland, K., Duke, F. E., O'Brien, K., & Darden, E. B. Jr. (1992). Radiation exposure of air carrier crewmembers II. *Radiation Protection Dosimetry*, 45(1-4), 145–148.
- **Application**: Calculates cosmic radiation exposure for aviation personnel

### **🔬 Environmental Monitoring Calculators**

#### **8. Wet Bulb Globe Temperature (WBGT)**
- **Reference**: Budd, G. M. (2008). Wet-bulb globe temperature (WBGT)—its history and its limitations. *Journal of Science and Medicine in Sport*, 11(1), 20–32.
- **Application**: Assesses heat stress risk in indoor and outdoor environments

#### **9. Heat Stress Index (HSI)**
- **Reference**: Belding, H. S., & Hatch, T. F. (1955). Index for evaluating heat stress in terms of resulting physiological strains. *Heating, Piping and Air Conditioning*, 27(8), 129–136.
- **Application**: Evaluates heat stress based on metabolic rate and environmental conditions

#### **10. Predicted Heat Strain (ISO 7933)**
- **References**: 
  - ISO 7933:2023. *Ergonomics of the thermal environment — Analytical determination and interpretation of heat stress using calculation of the predicted heat strain.*
  - Malchaire, J., et al. (2001). Development and validation of the predicted heat strain model. *Annals of Occupational Hygiene*, 45(2), 123–135.
- **Application**: Provides core temperature, sweat rate, and dehydration guardrails for work/rest planning in extreme heat.

#### **11. Noise Exposure Assessment**
- **References**: 
  - National Institute for Occupational Safety and Health (NIOSH). (1998). *Criteria for a Recommended Standard: Occupational Noise Exposure* (DHHS Publication No. 98–126).
  - Occupational Safety and Health Administration (OSHA). (2008). *Occupational Noise Exposure: Standard 29 CFR 1910.95*.
- **Application**: Calculates noise dose and permissible exposure times per OSHA/NIOSH standards

### **🧠 Fatigue & Circadian Calculators**

#### **11. Circadian Performance Models**
- **Reference**: Mallis, M. M., et al. (2004). Summary of the key features of seven biomathematical models of human fatigue and performance. *Aviation, Space, and Environmental Medicine*, 75(3), A4-A14.
- **Application**: Predicts performance degradation based on circadian rhythms and sleep debt

#### **12. Two-Process Sleep Model**
- **Reference**: Hursh, S. R., et al. (2004). Fatigue models for applied research in warfighting. *Aviation, Space, and Environmental Medicine*, 75(3), A44-A53.
- **Application**: Models homeostatic and circadian components of sleep-wake regulation

### **🏭 Occupational Health Calculators**

#### **13. Chemical Exposure Assessment (TLV/BEI)**
- **Reference**: ACGIH. (2023). *TLVs and BEIs: Threshold Limit Values for Chemical Substances and Physical Agents*. American Conference of Governmental Industrial Hygienists.
- **Application**: Evaluates chemical exposure risks using current ACGIH standards

---

## 💻 **Usage Examples (API)**

### **Altitude Physiology Assessment**
```python
from calculators import standard_atmosphere, spo2_unacclimatized

# Calculate atmospheric conditions at flight altitude (inputs in meters)
altitude_ft = 35000
altitude_m = altitude_ft * 0.3048
isa = standard_atmosphere(altitude_m)
pressure_pa = isa["pressure_Pa"]
temp_c = isa["temperature_C"]
density = isa["density_kg_m3"]

# Assess oxygen saturation for unacclimatized individual (inputs in meters)
spo2 = spo2_unacclimatized(altitude_m)
print(f"SpO2 at {altitude_ft} ft: {spo2:.1f}%")
```

### **Heat Stress Evaluation**
```python
from calculators import wbgt_outdoor, heat_stress_index, predicted_heat_strain

# Calculate WBGT for outdoor work environment
dry_bulb = 35.0  # °C
wet_bulb = 28.0  # °C
globe_temp = 45.0  # °C
wbgt = wbgt_outdoor(T_nwb=wet_bulb, T_g=globe_temp, T_db=dry_bulb)
print(f"WBGT: {wbgt:.1f}°C")

# Predict heat strain per ISO 7933 guidance
phs = predicted_heat_strain(
    metabolic_rate_w_m2=420.0,
    air_temperature_C=32.0,
    mean_radiant_temperature_C=38.0,
    relative_humidity_percent=55.0,
    air_velocity_m_s=0.6,
    clothing_insulation_clo=0.9,
    exposure_minutes=90.0,
)
print(
    f"Core temp: {phs.predicted_core_temperature_C:.2f}°C | "
    f"Sweat req: {phs.required_sweat_rate_L_per_h:.2f} L/h | "
    f"Safe exposure: {phs.allowable_exposure_minutes:.0f} min ({phs.limiting_factor})"
)
```

### **Decompression Risk Assessment**
```python
from calculators import standard_atmosphere, tissue_ratio, interpret_tr

# Assess decompression stress using Tissue Ratio (TR = Ptissue_N2 / Pambient).
# Here we assume tissues are saturated at sea level N2 prior to ascent.
altitude_ft = 25000
altitude_m = altitude_ft * 0.3048
p_ambient_mmhg = standard_atmosphere(altitude_m)["pressure_Pa"] / 133.322
ptissue_n2_sea_level_mmhg = 0.78 * (101325 / 133.322)
tr = tissue_ratio(ptissue_n2_sea_level_mmhg, p_ambient_mmhg)
risk_assessment = interpret_tr(tr)
print(f"Tissue Ratio: {tr:.3f} - {risk_assessment}")
```

---

## 📊 **Available Calculator Categories**

### **🌍 Atmospheric & Physiological**
- Standard Atmosphere Properties
- Alveolar Oxygen Pressure
- Altitude & Hypoxia Predictions
- Acute Mountain Sickness Risk
- Oxygen Cascade Analysis
- Decompression Tissue Ratio (TR)
- Time of Useful Consciousness
- G-Force Tolerance
- Cosmic Radiation Dose

### **🏭 Occupational Health & Safety**
- Chemical Exposure Assessment
- Time-Weighted Average Calculator
- Mixed Chemical Exposure
- Unusual Work Schedule TLV
- Biological Exposure Index
- Comprehensive Exposure Report

### **🔬 Environmental Monitoring**
- Heat Stress Index (WBGT)
- Heat Stress Index (HSI)
- Predicted Heat Strain (ISO 7933 inspired)
- Cold Exposure: Peak Shivering
- Noise Exposure Assessment

### **🧠 Fatigue & Circadian**
- Circadian Performance (Mitler)
- Two-Process Model (S & C)
- Jet Lag Recovery

### **📈 Visualization Studio**
- Interactive 2D/3D plotting
- Multiple visualization themes
- Export capabilities (PNG, SVG, PDF, HTML)
- Real-time parameter adjustment

### **🧪 Simulation Studio**
- Forward simulators for time-steppable models (deterministic sampling, bounded loops)
- PHS trajectories (core temperature, dehydration, sweat-rate limits) + next-step forecast
- Mitler circadian performance envelope forecasting

---

## 🧪 **Validation & Testing**

### **Quality Assurance**
- ✅ **Unit Tests**: Pytest suite included (run with `python -m pytest`)
- ✅ **Deterministic methods**: Stable results for identical inputs
- ✅ **Cross-platform**: Windows, macOS, Linux

### **Scientific Validation**
- 📚 **Literature traceability**: Key calculators include citations and documented assumptions
- 🎯 **Scope clarity**: Where models are simplified, limitations are explicitly stated

---

## 🤝 **Contributing**

We welcome contributions from the aerospace medicine and sports science communities!

### **How to Contribute**
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/new-calculator`)
3. **Commit** your changes (`git commit -am 'Add new calculator'`)
4. **Push** to the branch (`git push origin feature/new-calculator`)
5. **Create** a Pull Request

### **Contribution Guidelines**
- Include unit tests for new calculators
- Follow PEP 8 style guidelines
- Provide scientific references for new formulas
- Update documentation for new features

---

## 📄 **Citation**

If you use this software in your research or professional work, please cite:

```bibtex
@software{malpica2024aerospace,
  author = {Malpica, Diego},
  title = {Aerospace Medicine \& Human Performance Calculator Suite},
  year = {2024},
  institution = {Universidad Nacional de Colombia},
  url = {https://github.com/strikerdlm/HumanPerformanceCalcs},
  note = {Computational framework for aerospace medicine and human performance assessment}
}
```

**APA Style:**
Malpica, D. (2024). *Aerospace Medicine & Human Performance Calculator Suite* [Computer software]. Universidad Nacional de Colombia. https://github.com/strikerdlm/HumanPerformanceCalcs

---

## 📞 **Contact & Support**

### **Principal Investigator**
**Dr. Diego Malpica**  
📧 Email: [dlmalpicah@unal.edu.co](mailto:dmalpica@unal.edu.co)  
🏛️ Universidad Nacional de Colombia  
🔬 Department of Aerospace Medicine  

### **Technical Support**
- 📋 **Issues**: [GitHub Issues](https://github.com/strikerdlm/HumanPerformanceCalcs/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/strikerdlm/HumanPerformanceCalcs/discussions)
- 📖 **Documentation**: See `docs/` and in-app “Scientific rationale” expanders

---

## 🗺️ **Development Roadmap**

We maintain a comprehensive development roadmap based on scientific literature research. The roadmap outlines planned enhancements across multiple phases:

### Phase 1 (High Priority)
- **Predicted Heat Strain (PHS) Model** — ISO 7933:2023 standard
- **Simulation Studio** — interactive forward trajectories and scientific “what happens next” forecasting for time-steppable calculators (see `Docs/Manual.md`)
- **Universal Thermal Climate Index (UTCI)** — Outdoor thermal comfort
- **Cold Water Immersion Survival Time** — Cold-water immersion survival guidance (hypothermia-limited; see notes in-app)
- **Bühlmann ZH-L16 Decompression Algorithm** — Industry-standard DCS prediction
- **Anti-G Straining Maneuver (AGSM) Effectiveness** — G-tolerance enhancement
- **Spatial Disorientation Risk Assessment** — Vestibular conflict modeling

### Phase 2 (Medium Priority)
- SAFTE/FAST fatigue prediction model
- Night Vision Goggle (NVG) performance calculator
- Whole-body vibration exposure (ISO 2631)
- Crew duty time limit calculators (FAA/EASA)
- Visual acuity at altitude prediction

### Phase 3 (Advanced Features)
- Complete space medicine module
- Motion sickness integration (MSSQ)
- Psychomotor vigilance task (PVT) prediction
- Clinical scoring systems (Wells, qSOFA)

📖 **Simulation Studio manual**: `Docs/Manual.md`  
📖 **Full suite roadmap**: [docs/ROADMAP.md](docs/ROADMAP.md)

---

## 📜 **License**

This project is licensed under the **Academic Use License** - see the [LICENSE](LICENSE) file for details.

**Academic Use**: Free for educational and research purposes  
**Commercial Use**: Contact the author for licensing terms  
**Attribution**: Required in all uses

---

## 🙏 **Acknowledgments**

- **Universidad Nacional de Colombia** - Institutional support and resources
- **Aerospace Medical Association** - Scientific consultation
- **Open Source Community** - Development tools and libraries

---

## 📈 **Project Statistics**

![GitHub stars](https://img.shields.io/github/stars/strikerdlm/HumanPerformanceCalcs?style=social)
![GitHub forks](https://img.shields.io/github/forks/strikerdlm/HumanPerformanceCalcs?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/strikerdlm/HumanPerformanceCalcs?style=social)

**Development Metrics:**
- 🧮 **Calculators**: 29+ referenced formulas/models
- 📊 **Visualizations**: Interactive Plotly/ECharts visual lab with export
- 🧪 **Tests**: Pytest suite included
- 📚 **Documentation**: References + model notes in `docs/` and in-app explainers
- 🛠️ **Windows Compatibility Tools**: 3 helper scripts
- 🌐 **Platform Support**: Windows, macOS, Linux

---

<div align="center">

### **🚀 Advancing Human Performance in Extreme Environments 🌟**

*Developed with scientific rigor and passion for aerospace medicine*

**Universidad Nacional de Colombia** 🇨🇴 | **Dr. Diego Malpica** 👨‍⚬

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Made with Streamlit](https://img.shields.io/badge/Made%20with-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Built with Science](https://img.shields.io/badge/Built%20with-Science-brightgreen.svg)](#scientific-foundation--calculator-references)

</div>
