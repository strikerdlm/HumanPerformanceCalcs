# 🚀 Aerospace Physiology & Occupational Health Calculators

A comprehensive web application for aerospace medicine calculations and occupational health assessments, specifically designed for the aerospace industry. Built with Streamlit and featuring modern, professional UI design.

## ✨ Features

### 🌍 Atmospheric & Physiological Calculations
- **Standard Atmosphere (ISA)**: Temperature, pressure, density calculations up to 32 km
- **Alveolar Oxygen Pressure**: PO₂ calculations using the alveolar gas equation
- **Time of Useful Consciousness (TUC)**: Hypoxia tolerance estimates at altitude
- **G-Force Tolerance**: G-LOC time predictions for acceleration exposure

### 🛡️ Environmental Health Assessments
- **Cosmic Radiation**: Dose rate calculations for flight crews
- **Heat Stress**: WBGT calculations for indoor/outdoor environments
- **Noise Exposure**: OSHA/NIOSH permissible exposure limits and dose calculations

### 🧪 Occupational Health (ACGIH TLV/BEI Standards)
- **Chemical Exposure Assessment**: Risk evaluation for 15+ aerospace chemicals
- **Time-Weighted Average (TWA)**: Multi-period exposure calculations
- **Mixed Chemical Exposure**: Combined exposure index for multiple substances
- **Biological Exposure Indices (BEI)**: Biomarker assessment for select chemicals
- **Exposure Reporting**: Professional assessment reports

### 🎯 Aerospace Industry Focus
Specialized calculations for common aerospace chemicals including:
- Jet Fuel (JP-8, Jet A-1)
- Rocket Propellants (Hydrazine, MMH, UDMH)
- Solvents (MEK, Toluene, Xylene)
- Metals (Beryllium, Chromium VI, Lead)
- And more...

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Windows: Use PowerShell; macOS/Linux: bash/zsh

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aerospace-medicine-calculators
   ```

2. **Create and activate a virtual environment (recommended)**
   ```bash
   # Windows (PowerShell)
   py -m venv .venv
   .venv\\Scripts\\Activate.ps1
   
   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:8501`

### Alternative: Run with Python directly
```bash
python run_calculator.py
```

## 🧪 Testing

Run unit tests (if pytest is installed):
```bash
pytest -q
```

## 📊 Application Structure

```
aerospace-medicine-calculators/
├── streamlit_app.py              # Main Streamlit application
├── run_calculator.py             # Alternative CLI runner
├── test_calculators.py           # Comprehensive test suite
├── requirements.txt              # Python dependencies
├── calculators/                  # Calculator modules
│   ├── __init__.py              # Package initialization
│   ├── atmosphere.py            # Atmospheric calculations
│   ├── tuc.py                   # Time of Useful Consciousness
│   ├── g_force.py               # G-force tolerance
│   ├── radiation.py             # Cosmic radiation
│   ├── wbgt.py                  # Heat stress (WBGT)
│   ├── noise_exposure.py        # Noise exposure limits
│   ├── occupational_health.py   # ACGIH TLV/BEI calculations
│   └── models.py                # Data models and constants
└── aerospace_medicine/           # Legacy module (maintained for compatibility)
```

## 🎨 User Interface

The application features a modern, professional interface with:

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Intuitive Navigation**: Sidebar-based calculator selection
- **Professional Styling**: Color-coded risk levels and clean metrics
- **Interactive Visualizations**: Charts and graphs using Plotly
- **Export Capabilities**: Professional PDF reports for assessments

### Key UI Components
- **Dashboard Overview**: Quick access to all calculator categories
- **Real-time Calculations**: Instant results as you input parameters
- **Risk Assessment**: Color-coded alerts (green/yellow/red) for safety levels
- **Data Visualization**: Interactive charts for exposure trends and risk matrices
- **Professional Reports**: Formatted output suitable for regulatory compliance

## 📚 Scientific Basis

All calculations are based on peer-reviewed scientific literature and industry standards:

### Standards & Guidelines
- **ACGIH**: Threshold Limit Values (TLVs) and Biological Exposure Indices (BEIs) 2024
- **NIOSH**: Criteria Documents and Recommended Exposure Limits
- **OSHA**: Occupational Safety and Health Standards
- **ISO 7243**: Heat stress assessment (WBGT)
- **ICAO Doc 7488**: International Standard Atmosphere
- **USAF Standards**: G-force tolerance and TUC models

### Key References
- West, J.B. (2012). *Respiratory Physiology: The Essentials*. 9th Edition
- ACGIH (2024). *TLVs and BEIs: Threshold Limit Values for Chemical Substances*
- NIOSH (2016). *Criteria for a Recommended Standard: Occupational Exposure to Jet Fuel*
- ICRP Publication 132 (2016). *Radiation Dose to Aircrew*

## ⚠️ Important Disclaimers

**For Educational and Research Use Only**

This application is designed for:
- ✅ Educational purposes and training
- ✅ Research and preliminary assessments
- ✅ Understanding occupational health principles
- ✅ Screening-level calculations

**Not intended for:**
- ❌ Regulatory compliance decisions
- ❌ Legal or official assessments
- ❌ Replacement of professional consultation
- ❌ Operational flight medicine decisions

**Always consult qualified aerospace medicine professionals and industrial hygienists for operational use.**

## 🔧 Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **NumPy**: Numerical computations
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **SciPy**: Scientific utilities

### Performance
- Optimized for real-time calculations
- Responsive design for various screen sizes
- Efficient data processing with NumPy
- Professional-grade visualizations

### Browser Compatibility
- Chrome (recommended)
- Firefox
- Safari
- Edge

## 🤝 Contributing

Contributions are welcome! Please ensure:

1. All calculations include proper scientific references
2. Code follows existing style conventions
3. New features include appropriate tests
4. Documentation is updated accordingly

### Development Setup
```bash
# Create and activate venv (recommended)
py -m venv .venv && .venv\\Scripts\\Activate.ps1  # Windows
# python3 -m venv .venv && source .venv/bin/activate  # macOS/Linux

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run tests
pytest -q

# Start development server (auto-reload on save)
streamlit run streamlit_app.py --server.runOnSave true
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Diego Malpica**
- Aerospace Medicine Researcher
- Industrial Hygiene Specialist

## 🆘 Support

For questions, issues, or feature requests:
1. Check the existing documentation
2. Run the test suite to verify installation
3. Review the scientific references for calculation details
4. Consult aerospace medicine professionals for operational guidance

---

**Remember**: This tool is for educational purposes. Always consult qualified professionals for operational aerospace medicine and occupational health decisions.
