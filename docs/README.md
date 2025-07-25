# Human Performance Calculations for Aerospace Medicine

This repository provides Python implementations of advanced physiological calculations for aerospace medicine and human performance assessment. The tools are designed for research and educational purposes, with a focus on scientific accuracy, usability, and safety.

## ⚠️ Important Disclaimer

**These implementations are for research and educational purposes only. They should not be used for operational decision-making or medical diagnosis without proper validation and supervision by qualified professionals.**

## Project Structure

The project is organized into domain-specific packages for better maintainability and navigation:

- **`aerospace_medicine/`** - Main organized calculator package
  - `decompression/` - DCS risk assessment and barotrauma calculations
  - `heat_stress/` - Heat strain, PSI, and sweat rate calculations
  - `cold_stress/` - Wind chill and cold exposure assessments
  - `altitude/` - Altitude effects and TUC calculations
  - `fatigue/` - Cognitive performance and fatigue modeling
  - `motion_sickness/` - Motion sickness susceptibility tools

- **`calculators/`** - Core calculation engines (used by streamlit app)
- **`models/`** - Machine learning models directory
- **`tests/`** - Unit tests
- **`docs/`** - Project documentation
- **`run_calculator.py`** - Unified CLI entry point

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed organization information.

## Key Features & Modules

### 1. Decompression Sickness (DCS) Risk Assessment
- **DCS Risk Calculator**: Machine learning-based DCS risk prediction with robust error handling, input validation, and actionable safety warnings.
- **DCS Ensemble Model**: Enhanced ensemble model for DCS risk with improved feature handling and model portability.
- **Barotrauma Treatment**: Barometric treatment modeling with confidence interval calculations.

### 2. Fatigue and Cognitive Performance
- **Fatigue Model**: Comprehensive fatigue modeling using homeostatic and circadian processes, including sleep quality, chronotype, and workload factors.

### 3. Heat Stress Assessment
- **PHS-HR Model**: Complete implementation of the Predicted Heat Strain using Heart Rate (PHS-HR) model, compliant with ISO 7933, including core temperature, heart rate, and sweat rate predictions.
- **Physiological Strain Index**: Accurate calculation of the Physiological Strain Index (PSI) with age-adjusted heart rate options and detailed risk interpretation.
- **Sweat Rate Calculator**: Sweat rate and dehydration risk calculator aligned with ACSM guidelines, including fluid replacement recommendations and performance warnings.

### 4. Cold Stress and Environmental Conditions
- **Wind Chill Calculator**: Wind Chill Temperature calculator using the latest NOAA formula, with input validation, frostbite risk assessment, and safety warnings.
- **Cold Stress Survival**: Cold stress survival prediction.

### 5. Altitude and Atmospheric Calculations
- **Altitude Calculator**: Altitude calculations from barometric pressure.
- **TUC Models**: Machine learning-based Time of Useful Consciousness (TUC) predictions using physiological and environmental parameters.

### 6. Additional Tools
- **MSSQ Calculator**: Motion Sickness Susceptibility Questionnaire processing.
- **Regional Tools**: Ontario-specific sweat rate calculations.

### 7. Interactive Web App
- **Streamlit App**: User-friendly web interface for key calculators, including standard atmosphere, alveolar oxygen, TUC, G-force tolerance, and cosmic radiation dose.

## Installation Requirements

```bash
pip install pandas numpy matplotlib scikit-learn joblib category-encoders streamlit
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

## Usage

### Unified CLI Interface (Recommended)
Use the new organized entry point for all calculators:

```bash
python run_calculator.py
```

This provides an organized menu system with calculators grouped by medical domain.

### Individual Calculator Modules
Each calculator can also be run independently:

```bash
# New organized structure
python aerospace_medicine/heat_stress/strain_index.py
python aerospace_medicine/decompression/dcs_risk.py
python aerospace_medicine/cold_stress/wind_chill.py

# Legacy scripts (still available)
python PhysiolStrainIndex.py
python DCSCalcV5.py
python WCT.py
```

### Web Interface
For the interactive web app:

```bash
streamlit run streamlit_app.py
```

### Programmatic Usage
```python
# Import organized calculators
from aerospace_medicine.heat_stress import strain_index_calculator
from aerospace_medicine.decompression import dcs_risk_calculator

# Use core calculation functions
from calculators import standard_atmosphere, alveolar_PO2, estimate_tuc
```

## Recent Improvements

- **Updated scientific formulas** (NOAA, ACSM, ISO 7933, Moran et al.)
- **Comprehensive input validation** and error handling for all modules
- **Detailed risk stratification** and actionable recommendations
- **Enhanced documentation** and scientific references
- **Modular, maintainable code structure** with clear docstrings and type hints
- **User-friendly interfaces** with clear prompts and safety warnings
- **Standardized CLI interfaces** across all calculators with consistent error handling
- **Refactored utility modules** for input validation and common functions
- **Comprehensive unit testing** suite for core calculation functions
- **Configurable file paths** eliminating hardcoded dependencies
- **Centralized model management** with standardized saving/loading (see [MODEL_MANAGEMENT.md](MODEL_MANAGEMENT.md))
- **🆕 Organized project structure** with domain-based calculator organization
- **🆕 Unified CLI entry point** (run_calculator.py) for easy access to all tools
- **🆕 Professional package structure** suitable for research and educational use

## Scientific References

The implementations are based on established formulas and models from:
- NOAA Wind Chill Guidelines (2001)
- American College of Sports Medicine (ACSM) hydration guidelines
- Physiological Strain Index (Moran et al., 1998)
- ISO 7933:2004 (Heat stress assessment)
- Various aerospace medicine and human factors research

## Documentation

- [Project Structure Guide](PROJECT_STRUCTURE.md) - Detailed explanation of the organized structure
- [Improvements Summary](IMPROVEMENTS_SUMMARY.md) - Development history and enhancements
- [Model Management Guide](MODEL_MANAGEMENT.md) - Machine learning model handling

## Contributing

When contributing improvements:
1. Ensure scientific accuracy with proper references
2. Include comprehensive error handling and input validation
3. Add proper documentation and docstrings
4. Validate with test cases and physiologically realistic ranges
5. Consider operational safety implications and provide clear disclaimers
6. Follow the organized structure for new calculators

## License

This project is intended for educational and research use only.

## Contact

For questions about implementations or suggestions for improvements, please refer to the project documentation or contact qualified aerospace medicine professionals for validation and operational guidance. 