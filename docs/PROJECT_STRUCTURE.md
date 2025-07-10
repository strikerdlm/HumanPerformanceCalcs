# Project Structure Guide

This document explains the reorganized structure of the Human Performance Calculations for Aerospace Medicine project.

## Overview

The project has been reorganized from a flat structure with many root-level scripts into a domain-organized, modular structure that's easier to navigate, maintain, and extend.

## New Directory Structure

```
HumanPerformanceCalcs-main/
├── aerospace_medicine/            # Main organized calculator package
│   ├── __init__.py               # Package exports and documentation
│   ├── decompression/            # DCS & barotrauma calculators
│   │   ├── __init__.py
│   │   ├── dcs_risk.py          # DCSCalcV5.py → reorganized
│   │   ├── dcs_ensemble.py      # DCSv10.py → to be moved
│   │   ├── barotrauma_mcmc.py   # BaroTxMCMCVer7.py → to be moved
│   │   └── barotrauma_ci.py     # BaroTxCI95Calc.py → to be moved
│   ├── heat_stress/              # Heat-related calculators
│   │   ├── __init__.py
│   │   ├── strain_index.py      # PhysiolStrainIndex.py → reorganized
│   │   ├── phs_hr_model.py      # PHSHRModel.py → to be moved
│   │   ├── sweat_rate.py        # SimpleSweatRate.py → to be moved
│   │   └── ontario_sweat.py     # OntarioSweatRate.py → to be moved
│   ├── cold_stress/              # Cold exposure calculators
│   │   ├── __init__.py
│   │   ├── wind_chill.py        # WCT.py → reorganized
│   │   └── cold_survival.py     # PSDAColdStress.py → to be moved
│   ├── altitude/                 # Altitude-related calculators
│   │   ├── __init__.py
│   │   ├── altitude_calc.py     # AltitudeCalculator.py → reorganized
│   │   ├── tuc_v4.py           # TUC4.py → to be moved
│   │   └── tuc_v5.py           # TUC5OnlyAlt.py → to be moved
│   ├── fatigue/                  # Cognitive performance
│   │   ├── __init__.py
│   │   └── fatigue_model.py     # FatigueCalcVerAlfa2.py → to be moved
│   └── motion_sickness/          # Motion & sensory
│       ├── __init__.py
│       └── mssq_calc.py         # MSSQCalcCSV.py → to be moved
├── calculators/                  # Core calculation engines (existing)
│   ├── __init__.py              # Exports for streamlit app
│   ├── utils.py                 # Shared input validation utilities
│   ├── models.py                # Model management utilities
│   ├── atmosphere.py            # Atmospheric calculations
│   ├── tuc.py                   # TUC estimation
│   ├── g_force.py               # G-force calculations
│   └── radiation.py             # Radiation dose calculations
├── models/                       # ML models directory (existing)
├── tests/                        # Unit tests (existing)
├── docs/                         # Documentation
│   ├── PROJECT_STRUCTURE.md     # This file
│   ├── README.md                # Main project documentation
│   ├── IMPROVEMENTS_SUMMARY.md  # Development improvements
│   └── MODEL_MANAGEMENT.md      # Model handling guide
├── streamlit_app.py             # Web interface (unchanged)
├── run_calculator.py            # NEW: Unified CLI entry point
└── requirements.txt             # Dependencies (existing)
```

## Key Improvements

### 1. Domain Organization
Calculators are now organized by medical domain:
- **Decompression**: DCS risk, barotrauma analysis
- **Heat Stress**: PSI, sweat rate, heat strain
- **Cold Stress**: Wind chill, cold survival
- **Altitude**: Barometric effects, TUC models
- **Fatigue**: Cognitive performance modeling
- **Motion Sickness**: MSSQ questionnaire processing

### 2. Standardized CLI Structure
All reorganized calculators follow a consistent pattern:
- Import from `calculators.utils` for input validation
- Standardized `main()` function with proper error handling
- Consistent disclaimer and safety warnings
- Clear result formatting and interpretation

### 3. Unified Entry Point
The new `run_calculator.py` provides:
- Single point of access to all calculators
- Organized menu system by domain
- Consistent user experience
- Error handling for missing modules

### 4. Preserved Existing Structure
- The `calculators/` package remains unchanged (used by streamlit app)
- Model management system is preserved
- Tests directory structure maintained
- All existing functionality retained

## Usage Patterns

### Running Individual Calculators
```bash
# Run specific calculator directly
python aerospace_medicine/heat_stress/strain_index.py

# Or use the unified entry point
python run_calculator.py
```

### Importing in Code
```python
# Import domain packages
from aerospace_medicine import heat_stress, decompression

# Use specific calculators
from aerospace_medicine.heat_stress import strain_index_calculator
from aerospace_medicine.decompression import dcs_risk_calculator
```

### Web Interface
The streamlit app continues to work unchanged:
```bash
streamlit run streamlit_app.py
```

## Migration Status

### ✅ Completed
- [x] Directory structure created
- [x] Package `__init__.py` files with documentation
- [x] DCS Risk Calculator (`dcs_risk.py`)
- [x] Physiological Strain Index (`strain_index.py`)
- [x] Wind Chill Calculator (`wind_chill.py`)
- [x] Altitude Calculator (`altitude_calc.py`)
- [x] Unified CLI entry point (`run_calculator.py`)

### 🔄 In Progress / To Do
- [ ] Complete migration of remaining 11 calculator scripts
- [ ] Update imports in moved scripts
- [ ] Test all calculator integrations
- [ ] Update tests to match new structure
- [ ] Create legacy compatibility layer if needed

## Benefits of New Structure

1. **Better Organization**: Related calculators grouped by medical domain
2. **Easier Navigation**: Clear hierarchy reduces cognitive load
3. **Consistent Interface**: Standardized CLI structure across all tools
4. **Maintainability**: Modular structure easier to extend and modify
5. **Professional Appearance**: Organized structure suitable for research use
6. **Preserved Functionality**: All existing features retained

## Next Steps

1. Complete migration of remaining calculators
2. Update documentation and README
3. Test all integrations
4. Create migration guide for users
5. Consider deprecation warnings for old script usage

This structure provides a solid foundation for continued development while maintaining all existing functionality and improving the overall user and developer experience. 