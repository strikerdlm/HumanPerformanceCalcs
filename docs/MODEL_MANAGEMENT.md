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
manager.save_model(model, "my_model", "classification")

# Explicit format
manager.save_model(model, "my_model", "classification", format_type="joblib")
```

## ModelManager Class

### Initialization

```python
from calculators.models import ModelManager

# Default models directory
manager = ModelManager()

# Custom base directory
manager = ModelManager(base_dir="custom_models")
```

### Saving Models

```python
# Basic save
model_path = manager.save_model(
    model=trained_model,
    model_name="my_predictor",
    model_type="classification"
)

# Save with metadata
model_path = manager.save_model(
    model=trained_model,
    model_name="my_predictor", 
    model_type="classification",
    metadata={
        "training_date": "2023-12-01",
        "accuracy": 0.95,
        "features": ["feature1", "feature2"],
        "description": "Improved model with better accuracy"
    },
    overwrite=True
)
```

### Loading Models

```python
# Load model only
model = manager.load_model("my_predictor", "classification")

# Load model with metadata
model, metadata = manager.load_model(
    "my_predictor", 
    "classification", 
    return_metadata=True
)

# Load from specific path
model = manager.load_model_from_path("models/custom/my_model.joblib")
```

### Model Information

```python
# List all models
models = manager.list_models()
print(models)
# {'classification': ['my_predictor', 'other_model'], 'regression': ['dcs_risk']}

# Get model info
info = manager.get_model_info("my_predictor", "classification")
print(info)
# {'size_mb': 1.5, 'created': '2023-12-01', 'format': 'joblib'}
```

## Integration with Calculators

### DCS Risk Calculator Example

```python
from calculators.models import ModelManager
from pathlib import Path

def load_dcs_models():
    """Load DCS prediction models."""
    manager = ModelManager()
    
    try:
        # Load main model
        model = manager.load_model("trained_model", "dcs")
        
        # Load encoder
        encoder = manager.load_model("onehot_encoder", "dcs") 
        
        # Load column names
        columns = manager.load_model("column_names", "dcs")
        
        return model, encoder, columns
        
    except FileNotFoundError:
        # Fallback to legacy file locations
        base_dir = Path(__file__).parent / "models"
        model = load_legacy_model(base_dir / "trained_model.joblib")
        # ... handle legacy loading
```

### Best Practices

1. **Use ModelManager for new code**: Provides consistency and error handling
2. **Include metadata**: Document model version, accuracy, and features
3. **Handle missing models gracefully**: Provide clear error messages
4. **Version your models**: Use descriptive names with version information
5. **Test model loading**: Verify models load correctly in your calculator

## Error Handling

### Common Error Scenarios

```python
try:
    model = manager.load_model("my_model", "classification")
except FileNotFoundError:
    print("Model not found. Please train the model first.")
except ImportError:
    print("Required libraries (joblib/pickle) not available.")
except Exception as e:
    print(f"Error loading model: {e}")
```

### Model Validation

```python
# Check if model exists before loading
if manager.model_exists("my_model", "classification"):
    model = manager.load_model("my_model", "classification")
else:
    print("Model does not exist. Training new model...")
    # train_new_model()
```

## Migration from Legacy Code

### Before (Legacy)
```python
import joblib
import os

# Hardcoded paths
model_path = "trained_model.joblib"
if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    raise FileNotFoundError(f"Model not found: {model_path}")
```

### After (ModelManager)
```python
from calculators.models import ModelManager

manager = ModelManager()
try:
    model = manager.load_model("trained_model", "dcs")
except FileNotFoundError:
    print("Model not found. Please ensure model files are in models/dcs/")
    # Provide helpful guidance to user
```

## Advanced Features

### Batch Operations

```python
# Save multiple related models
models_to_save = [
    (main_model, "main_predictor", {"accuracy": 0.95}),
    (encoder, "feature_encoder", {"type": "onehot"}),
    (scaler, "feature_scaler", {"type": "standard"})
]

for model, name, metadata in models_to_save:
    manager.save_model(model, name, "dcs", metadata=metadata)
```

### Model Versioning

```python
# Save model with version
manager.save_model(
    model, 
    "dcs_predictor_v2", 
    "dcs",
    metadata={"version": "2.0", "improvements": "Added new features"}
)

# Load specific version
model = manager.load_model("dcs_predictor_v2", "dcs")
```

## Troubleshooting

### Model Not Loading

1. **Check file existence**: Verify model files are in expected location
2. **Check format compatibility**: Ensure joblib/pickle versions are compatible
3. **Check dependencies**: Verify required libraries are installed
4. **Check permissions**: Ensure read access to model files

### Performance Issues

1. **File size**: Large models may take time to load
2. **Compression**: Use joblib for better compression of NumPy arrays
3. **Caching**: Consider caching frequently used models in memory

### Version Conflicts

1. **joblib versions**: Different versions may have compatibility issues
2. **Python versions**: Models saved in one Python version may not load in another
3. **Library dependencies**: Ensure consistent versions across environments

## Contact and Support

For questions about model management or issues with specific models, please refer to the main project documentation or contact the development team. 