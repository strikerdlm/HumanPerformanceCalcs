# Human Performance Calculations for Aerospace Medicine

This repository contains Python implementations of various physiological calculations used in aerospace medicine and human performance assessment. These tools are designed for research and educational purposes.

## ⚠️ Important Disclaimer

**These implementations are for research and educational purposes only. They should not be used for operational decision-making or medical diagnosis without proper validation and supervision by qualified professionals.**

## Modules Overview

### 1. Decompression Sickness (DCS) Risk Assessment
- **DCSCalcV5.py**: Machine learning-based DCS risk prediction
- **DCSv10.py**: Updated version with enhanced features
- Calculates risk percentage based on altitude, prebreathing time, time at altitude, and exercise level

### 2. Fatigue and Cognitive Performance
- **FatigueCalcVerAlfa2.py**: Comprehensive fatigue modeling using homeostatic and circadian processes
- Includes sleep quality, chronotype, and workload factors
- Outputs cognitive performance predictions over time

### 3. Heat Stress Assessment
- **PHSHRModel.py**: Predicted Heat Strain using Heart Rate (PHS-HR) model
- **PhysiolStrainIndex.py**: Physiological Strain Index calculation
- **SimpleSweatRate.py**: Basic sweat rate calculation for hydration assessment

### 4. Cold Stress and Environmental Conditions
- **WCT.py**: Wind Chill Temperature calculation using current NOAA formula
- **PSDAColdStress.py**: Cold stress survival prediction
- **BaroTxMCMCVer7.py**: Barometric treatment modeling

### 5. Altitude and Atmospheric Calculations
- **AltitudeCalculator.py**: Altitude calculations from barometric pressure
- **TUC4.py** & **TUC5OnlyAlt.py**: Time of Useful Consciousness predictions

### 6. Additional Tools
- **MSSQCalcCSV.py**: Motion Sickness Susceptibility Questionnaire processing
- **OntarioSweatRate.py**: Ontario-specific sweat rate calculations
- **BaroTxCI95Calc.py**: Confidence interval calculations for barometric treatment

## Installation Requirements

```bash
pip install pandas numpy matplotlib scikit-learn joblib category-encoders
```

## Usage

Each module can be run independently:

```bash
python ModuleName.py
```

Follow the prompts to input required parameters.

## Scientific References

The implementations are based on established formulas and models from:
- NOAA Wind Chill Guidelines (2001)
- American College of Sports Medicine (ACSM) hydration guidelines
- Physiological Strain Index (Moran et al., 1998)
- Various aerospace medicine and human factors research

## Contributing

When contributing improvements:
1. Ensure scientific accuracy with proper references
2. Include comprehensive error handling
3. Add proper documentation
4. Validate with test cases
5. Consider operational safety implications

## License

This project is intended for educational and research use only.
