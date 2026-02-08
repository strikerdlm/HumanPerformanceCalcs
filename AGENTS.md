# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**Aerospace Medicine & Human Performance Calculator Suite**: A research-grade computational framework with 29+ scientifically validated calculators for aerospace medicine, occupational health, and human performance assessment in extreme environments. Developed by Dr. Diego Malpica at Universidad Nacional de Colombia.

**Core Mission**: Provide deterministic, scientifically validated calculations with explicit assumptions, transparent methods, and literature traceability.

## Essential Commands

### Environment Setup
```bash
# Create and activate conda environment (REQUIRED - user prefers conda)
conda env create -f environment.yml
conda activate textappv2

# If using venv (fallback only)
python -m venv textappv2
source textappv2/bin/activate  # macOS/Linux
textappv2\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Running the Application
```bash
# Primary interface: Streamlit web app
streamlit run streamlit_app.py --server.port 9876 --server.address 127.0.0.1

# Windows (use address 0.0.0.0 for compatibility)
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8507
# Or use: run_streamlit_admin.bat (run as administrator)

# Alternative: Flask interface (no admin privileges required)
python flask_alternative.py

# CLI interface for individual calculators
python run_calculator.py

# Domain-specific calculator (direct execution)
python aerospace_medicine/heat_stress/strain_index.py
```

### Testing
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_buhlmann.py

# Run with coverage
python -m pytest --cov=calculators --cov-report=html
```

### Code Quality
```bash
# Linting (configured in setup.cfg: max-line-length=100, ignore E203,W503)
flake8 calculators/
flake8 aerospace_medicine/

# Type checking (calculators use type hints extensively)
mypy calculators/ --strict
```

### Frontend Development
```bash
cd frontend/

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Lint TypeScript/React
npm run lint
```

## Architecture Overview

### Two-Layer Calculator System
1. **Core Calculation Package** (`calculators/`): Pure computational functions used by Streamlit app
   - Organized by medical domain (atmosphere.py, phs.py, buhlmann.py, etc.)
   - Exports through `calculators/__init__.py`
   - Type-annotated with dataclasses for inputs/outputs
   - Deterministic, unit-tested implementations

2. **Domain-Organized CLI Scripts** (`aerospace_medicine/`): Standalone calculators with CLI interfaces
   - Subdomains: `decompression/`, `heat_stress/`, `cold_stress/`, `altitude/`, `fatigue/`, `motion_sickness/`
   - Each has standardized `main()` function with input validation using `calculators.utils`
   - Can be run directly or through unified entry point (`run_calculator.py`)

### User Interfaces
- **Primary**: `streamlit_app.py` - Full-featured web interface with visualization studio
- **Alternative**: `flask_alternative.py` - Simplified web interface (Windows-compatible without admin rights)
- **CLI**: `run_calculator.py` - Text-based menu system for all calculators
- **Future**: React frontend (`frontend/`) - Modern web UI (React + TypeScript + Vite)

### Data Flow
```
User Input → Validation (utils.py) → Calculator Function → Result Dataclass → UI Display
                                    ↓
                            Tests verify correctness
```

### Key Files and Locations
- `calculators/__init__.py` - Central export point for all calculator functions
- `calculators/utils.py` - Shared input validation utilities (get_float_input, get_int_input, etc.)
- `calculators/models.py` - Model management utilities for ML components
- `calculators/simulation.py` - Forward trajectory simulators (PHS, Mitler circadian)
- `docs/PROJECT_STRUCTURE.md` - Detailed structural documentation
- `docs/ROADMAP.md` - Development roadmap with scientific references
- `Docs/Manual.md` - User manual for features and calculator usage
- `tests/` - Pytest suite covering all calculators

## Development Conventions

### Scientific Integrity (CRITICAL)
- **All formulas must have peer-reviewed references**: Include citations in docstrings
- **Explicit assumptions**: Document limitations, valid ranges, and edge cases
- **Unit consistency**: Always specify units in variable names or comments (e.g., `altitude_m`, `temperature_C`)
- **Deterministic implementations**: No hidden randomness; same inputs → same outputs
- **Transparent methods**: Code should be readable as scientific documentation

### Chart & Visualization Rules
- **No titles on the plot canvas**: Chart titles and subtitles must be rendered as HTML elements above the chart, never inside the ECharts canvas. In the frontend, `ScientificChart` enforces `title: { show: false }` on all merged options.
- **Publication-quality defaults**: Use `PUBLICATION_THEME` and `SCIENTIFIC_COLORS` from `frontend/src/types/index.ts`.
- **Captions below**: Descriptive figure captions go below the chart as `<p className="publication-figure-caption">`.

### Code Patterns

#### Calculator Function Structure
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class CalculatorInputs:
    """Input parameters with units and validation ranges."""
    param_value: float  # Unit: meters, Range: 0-15000
    
@dataclass
class CalculatorResult:
    """Output with all relevant metrics."""
    primary_metric: float
    secondary_metric: Optional[float]
    interpretation: str

def calculator_function(inputs: CalculatorInputs) -> CalculatorResult:
    """
    Brief description of what this calculates.
    
    Reference:
    - Author et al. (YEAR). Title. Journal, vol(issue), pages.
    - DOI or URL if available
    
    Args:
        inputs: Validated input parameters
        
    Returns:
        CalculatorResult with computed metrics
        
    Raises:
        ValueError: If inputs outside valid range
    """
    # Input validation with clear error messages
    if not (0 <= inputs.param_value <= 15000):
        raise ValueError(f"param_value must be 0-15000, got {inputs.param_value}")
    
    # Calculation with intermediate steps documented
    intermediate = inputs.param_value * 0.3048  # Convert feet to meters
    
    # Return structured result
    return CalculatorResult(
        primary_metric=intermediate,
        interpretation="Safe" if intermediate < 100 else "Caution"
    )
```

#### CLI Script Structure (aerospace_medicine/)
```python
#!/usr/bin/env python3
"""
Brief description of calculator.

Reference:
- Citation here

DISCLAIMER: Research/educational use only. Not medical device.
"""
from calculators.utils import get_float_input, get_int_input

def main():
    """Main CLI entry point."""
    print("=== Calculator Name ===")
    print("DISCLAIMER: ...")
    
    # Input collection with validation
    value = get_float_input("Enter value (unit): ", min_value=0, max_value=100)
    
    # Calculation (import from calculators package)
    result = calculator_function(inputs)
    
    # Result display
    print(f"\nResults:")
    print(f"  Metric: {result.primary_metric:.2f} unit")
    
if __name__ == "__main__":
    main()
```

### Testing Requirements
- **Unit tests required** for all calculator functions
- Test edge cases, boundary conditions, and known reference values
- Use pytest fixtures for complex input setups
- Include regression tests for published validation cases
- Test file naming: `test_<module_name>.py`

### Type Hints and Documentation
- Use type hints for all public functions (already standard in calculators/)
- Use dataclasses for structured inputs/outputs
- Docstrings must include: description, references, parameters, returns, raises
- Comment units inline: `# meters`, `# kg/m^3`, `# mmHg`

### File Organization
- New calculators: Add to `calculators/` package with corresponding test
- CLI versions: Add to appropriate `aerospace_medicine/<domain>/` subdirectory
- Export from `calculators/__init__.py` for Streamlit app usage
- Update imports in unified CLI (`run_calculator.py`) if adding new domain

## Platform-Specific Notes

### Windows Development
- **Socket permission issues** are common on Windows 10/11 Enterprise
- Solutions (in order of reliability):
  1. Use `run_streamlit_admin.bat` (run as administrator) - 95% success
  2. Run from elevated PowerShell/Terminal - 95% success
  3. Use Flask alternative (`flask_alternative.py`) - 85% success
  4. Use CLI interface (`run_calculator.py`) - 100% success
- Diagnostic script available: `check_security_settings.ps1`
- Default Streamlit config: `--server.address 0.0.0.0 --server.port 8507`

### Cross-Platform
- Use absolute paths in code (avoid `cd` in shell commands)
- Test file I/O with both forward slash and backslash
- Conda environments work identically across platforms
- Frontend (React) uses npm consistently across platforms

## Important Constraints and Best Practices

### Python Code Requirements (from user rules)
- **Deterministic implementations**: Bounded loops, finite timeouts, no recursion
- **Explicit validation**: Never use assert for input validation (use explicit ValueError)
- **Type safety**: Full type hints in strict mode (mypy compatible)
- **Immutable boundaries**: Use frozen dataclasses for inputs/outputs
- **Context managers**: Always use `with` for file/resource operations
- **Error handling**: Specific exceptions with context; use `raise ... from e`
- **No eval/exec**: No dynamic code execution on user input
- **Memory bounded**: Explicit limits on data structures (no unbounded growth)

### Documentation Requirements (from user rules)
- **Centralized docs**: Only modify README.md, CHANGELOG.md, or Docs/Manual.md
- **No doc proliferation**: Do not create scattered markdown files without explicit approval
- **Update Manual.md** for new features: Add to Docs/Manual.md with usage examples and references

### Scientific Validation
- Cross-reference with published literature before modifying formulas
- Maintain literature citations in calculator docstrings
- Include model limitations explicitly in UI and documentation
- Test against published reference values when available

## Common Development Tasks

### Adding a New Calculator
1. Create calculation function in `calculators/<module>.py` with:
   - Input/output dataclasses
   - Full type hints
   - Scientific references in docstring
   - Input validation
2. Export from `calculators/__init__.py`
3. Add pytest tests in `tests/test_<module>.py`
4. Integrate into Streamlit UI (`streamlit_app.py`)
5. Optionally create CLI version in `aerospace_medicine/<domain>/`
6. Update `Docs/Manual.md` with usage notes and references
7. Run tests and linting before committing

### Modifying Existing Calculator
1. Review scientific references in docstring
2. Verify changes against published formulas
3. Update tests to cover modified behavior
4. Update documentation if interface changes
5. Check for breaking changes in Streamlit UI integration

### Debugging Streamlit Issues
1. Check conda environment is active (`conda activate textappv2`)
2. Verify port availability (8507, 9876, or alternatives)
3. Review console output for Python exceptions
4. Check `streamlit_app.py` imports from `calculators.__init__`
5. Validate input ranges match calculator function expectations

## Repository Context

### Active Branch
- Current: `main`
- No specific branching strategy documented

### Dependencies
- Python: 3.8+ (3.10+ in environment.yml)
- Key packages: streamlit>=1.28, numpy>=1.24, scipy>=1.10, plotly>=5.15, pytest>=8.0
- Frontend: React 18, TypeScript, Vite, TailwindCSS

### External Resources
- Scientific papers: Referenced in calculator docstrings and docs/ROADMAP.md
- ISO standards: ISO 7933:2023 (PHS), ISO 2631-1 (vibration)
- Regulatory: FAA Part 117, EASA ORO.FTL (duty time limits)

## Known Limitations and Future Work

### Current Gaps (see docs/ROADMAP.md)
- Phase 1 (high priority): Most items completed; further enhancements documented in roadmap
- Phase 2 (medium priority): Advanced fatigue models, enhanced space medicine calculators
- Phase 3 (advanced): Complete space medicine module, motion sickness integration

### Migration Status (see docs/PROJECT_STRUCTURE.md)
- Core `calculators/` package: Complete and stable
- `aerospace_medicine/` domain reorganization: Partially complete (4/15 scripts migrated)
- React frontend: In development, not production-ready

## Contact and References

**Principal Investigator**: Dr. Diego Malpica (dlmalpicah@unal.edu.co)
**Institution**: Universidad Nacional de Colombia
**License**: Academic Use License (see LICENSE file)
**GitHub**: https://github.com/strikerdlm/HumanPerformanceCalcs
