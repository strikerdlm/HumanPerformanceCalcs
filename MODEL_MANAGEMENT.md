# Model Management Guide

This document describes the standardized approach for saving, loading, and managing machine learning models across the Human Performance Calculations project.

## Overview

The project uses a centralized `ModelManager` class in `calculators/models.py` to ensure consistent model handling across all scripts. This approach provides:

- **Standardized file formats** (joblib preferred, pickle fallback)
- **Consistent directory structure** for organized model storage
- **Automatic format detection** when loading models
- **Metadata support** for model documentation
- **Error handling** with clear error messages
- **Backward compatibility** with existing scripts

## Quick Start

### Basic Usage

```python
from calculators.models import ModelManager

# Initialize model manager
manager = ModelManager(base_dir="models")

# Save a model
model_path = manager.save_model(
    model=my_trained_model,
    model_name="dcs_risk_v2",
    model_type="regression",
    metadata={
        "training_date": "2023-12-01",
        "accuracy": 0.95,
        "features": ["altitude", "time", "exercise"]
    }
)

# Load a model
model, metadata = manager.load_model("dcs_risk_v2", "regression")
```

### Convenience Functions

For simple use cases, use the convenience functions:

```python
from calculators.models import save_model, load_model

# Save (automatically detects format)
save_model(my_model, "models/my_model.joblib")

# Load (automatically detects format)
model = load_model("models/my_model.joblib")
```

## Directory Structure

The standardized directory structure organizes models by type and name:

```
models/
├── dcs/                    # DCS risk prediction models
│   ├── trained_model/
│   │   ├── trained_model.joblib
│   │   ├── trained_model_metadata.json
│   │   └── model_info.txt
│   └── ensemble_model/
│       ├── ensemble_model.joblib
│       └── model_info.txt
├── tuc/                    # Time of Useful Consciousness models
│   ├── tuc_predictor/
│   └── altitude_model/
├── fatigue/                # Fatigue assessment models
└── mssq/                   # Motion sickness models
```

## Model Types and Locations

### Standard Model Categories

| Model Type | Directory | Description |
|------------|-----------|-------------|
| `dcs` | `models/dcs/` | Decompression Sickness risk prediction |
| `tuc` | `models/tuc/` | Time of Useful Consciousness prediction |
| `fatigue` | `models/fatigue/` | Fatigue and cognitive performance |
| `mssq` | `models/mssq/` | Motion Sickness Susceptibility |
| `heat_stress` | `models/heat_stress/` | Heat strain and PSI models |
| `general` | `models/general/` | Miscellaneous models |

### Expected Files by Model Type

#### DCS Models (`models/dcs/`)
- `trained_model.joblib` - Main prediction model
- `onehot_encoder.joblib` - Categorical feature encoder
- `column_names.joblib` - Expected input columns

#### TUC Models (`models/tuc/`)
- `tuc_model.joblib` - Full feature TUC predictor
- `tuc_altitude_model.joblib` - Altitude-focused model

#### Fatigue Models (`models/fatigue/`)
- `fatigue_model.pkl` - Fatigue assessment model

#### MSSQ Models (`models/mssq/`)
- `mssq_model.pkl` - Motion sickness susceptibility model

## File Formats

### Supported Formats

1. **joblib** (preferred) - `.joblib` extension
   - Fast serialization for NumPy arrays
   - Better compression
   - Scikit-learn compatibility

2. **pickle** (fallback) - `.pkl` extension
   - Standard Python serialization
   - Universal compatibility

### Format Selection

- **Automatic**: Uses joblib if available, falls back to pickle
- **Explicit**: Specify format with `format_type` parameter

```python
# Automatic format selection
manager.save_model(model, "my_model", format_type="auto")

# Force specific format
manager.save_model(model, "my_model", format_type="joblib")
manager.save_model(model, "my_model", format_type="pickle")
```

## Metadata and Documentation

### Model Metadata

Save important information alongside your models:

```python
metadata = {
    "version": "2.1",
    "training_date": "2023-12-01",
    "training_samples": 1000,
    "validation_accuracy": 0.95,
    "features": ["altitude", "prebreathing_time", "exercise_level"],
    "target": "dcs_risk_percentage",
    "notes": "Improved feature engineering and hyperparameter tuning"
}

manager.save_model(model, "dcs_risk_v2", metadata=metadata)
```

### Automatic Documentation

The ModelManager automatically creates documentation files:

- `model_info.txt` - Basic model information
- `{model_name}_metadata.json` - Custom metadata (if provided)

## Migration Guide

### Updating Existing Scripts

#### Before (Old Approach)
```python
from joblib import dump, load

# Inconsistent paths and error handling
dump(model, "C:/hardcoded/path/model.joblib")
model = load("C:/hardcoded/path/model.joblib")  # May fail silently
```

#### After (New Approach)
```python
from calculators.models import ModelManager

manager = ModelManager()

# Standardized with proper error handling
manager.save_model(model, "dcs_risk", "regression")
model, metadata = manager.load_model("dcs_risk", "regression")
```

### Script-Specific Updates

#### DCSCalcV5.py
```python
# Replace hardcoded model loading
from calculators.models import ModelManager

def load_model_files(model_dir: str = None):
    manager = ModelManager(model_dir or "models")
    
    model, _ = manager.load_model("trained_model", "dcs")
    encoder, _ = manager.load_model("onehot_encoder", "dcs") 
    columns, _ = manager.load_model("column_names", "dcs")
    
    return model, encoder, columns
```

#### TUC4.py / TUC5OnlyAlt.py
```python
# Replace direct joblib usage
from calculators.models import ModelManager

def save_model_and_results(model, metrics, output_dir):
    manager = ModelManager(output_dir)
    
    # Save with metadata
    metadata = {
        "metrics": metrics,
        "model_type": "XGBRegressor",
        "features": ["altitude", "PiO2", "FiO2", "SpO2"]
    }
    
    manager.save_model(model, "tuc_predictor", "regression", metadata=metadata)
```

## Best Practices

### 1. Use Descriptive Model Names
```python
# Good
manager.save_model(model, "dcs_risk_ensemble_v3", "dcs")

# Avoid
manager.save_model(model, "model1", "general")
```

### 2. Include Comprehensive Metadata
```python
metadata = {
    "version": "3.0",
    "creation_date": datetime.now().isoformat(),
    "training_data": "dcs_dataset_2023.xlsx",
    "algorithm": "GradientBoostingRegressor",
    "hyperparameters": {"n_estimators": 100, "learning_rate": 0.1},
    "performance": {"mse": 0.05, "r2": 0.95},
    "features": feature_list,
    "preprocessing": "OneHotEncoder for categorical variables"
}
```

### 3. Organize by Model Purpose
```python
# Group related models by type
manager.save_model(dcs_model, "risk_predictor", "dcs")
manager.save_model(dcs_encoder, "feature_encoder", "dcs")
manager.save_model(tuc_model, "altitude_predictor", "tuc")
```

### 4. Handle Errors Gracefully
```python
try:
    model, metadata = manager.load_model("my_model", "regression")
    print(f"Loaded model with accuracy: {metadata.get('accuracy', 'unknown')}")
except FileNotFoundError:
    print("Model not found. Please train a new model.")
except IOError as e:
    print(f"Error loading model: {e}")
```

### 5. Version Your Models
```python
# Include version in model name
manager.save_model(model, "dcs_risk_v2_1", "dcs")

# Or use metadata
metadata = {"version": "2.1", "previous_version": "2.0"}
manager.save_model(model, "dcs_risk", "dcs", metadata=metadata)
```

## Utility Functions

### List Available Models
```python
# List all models
models = manager.list_models()
print(models)
# Output: {'dcs': ['risk_predictor', 'ensemble_model'], 'tuc': ['altitude_model']}

# List models of specific type
dcs_models = manager.list_models("dcs")
```

### Get Model Information
```python
info = manager.get_model_info("risk_predictor", "dcs")
print(f"Model: {info['name']}")
print(f"Files: {[f['name'] for f in info['files']]}")
if 'metadata' in info:
    print(f"Accuracy: {info['metadata'].get('accuracy')}")
```

### Clean Up Old Models
```python
# Keep only the 3 most recent versions
removed = manager.cleanup_old_models("dcs", keep_latest=3)
print(f"Removed old models: {removed}")
```

### Check Dependencies
```python
from calculators.models import validate_model_dependencies

deps = validate_model_dependencies()
if not deps['joblib']:
    print("Warning: joblib not available, using pickle format")
```

## Environment Variables

Set default paths using environment variables:

```bash
# Set default model directory
export MODEL_BASE_DIR="/path/to/models"

# Script-specific model paths
export DCS_MODEL_DIR="/path/to/dcs/models"
export TUC_MODEL_DIR="/path/to/tuc/models"
```

## Troubleshooting

### Common Issues

#### 1. Model Not Found
```
FileNotFoundError: Model directory not found: models/dcs/my_model
```
**Solution**: Check model name and type, use `list_models()` to see available models.

#### 2. Format Compatibility
```
IOError: Failed to load model: No module named 'sklearn'
```
**Solution**: Ensure required libraries are installed, check model format compatibility.

#### 3. Permission Errors
```
IOError: Failed to save model: Permission denied
```
**Solution**: Check directory permissions, ensure output directory is writable.

### Debug Mode

Enable verbose output for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

manager = ModelManager()
# Now all operations will show detailed logging
```

## Integration with CI/CD

### Model Validation Script
```python
#!/usr/bin/env python
"""Validate all project models are loadable."""

from calculators.models import ModelManager, get_project_model_info

def validate_models():
    manager = ModelManager()
    model_info = get_project_model_info()
    
    for model_type, info in model_info.items():
        try:
            models = manager.list_models(model_type)
            print(f"✓ {model_type}: {len(models.get(model_type, []))} models found")
        except Exception as e:
            print(f"✗ {model_type}: Error - {e}")

if __name__ == "__main__":
    validate_models()
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit
python scripts/validate_models.py || exit 1
```

This standardized approach ensures all models in the project are managed consistently, making the codebase more maintainable and reducing errors related to model handling. 