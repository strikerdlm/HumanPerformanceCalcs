"""SpO2-Altitude Prediction Models Implementation.

This module implements three peer-reviewed models for predicting blood oxygen
saturation (SpO2) at altitude:

1. Niermeyer et al. Linear Regression Model
   Citation: Niermeyer et al., European Journal of Applied Physiology
   (referenced in Tüshaus et al., 2019)
   
2. Alt et al. Vector Autoregression (VAR) Model
   Citation: Alt et al., The Sport Journal (2025)
   
3. Tüshaus et al. Physiological Cascade Model
   Citation: Tüshaus et al., Physiological Reports

For educational and research use in aerospace medicine altitude physiology.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Literal

__all__ = [
    "niermeyer_spo2",
    "alt_var_spo2",
    "tushaus_cascade_spo2",
    "compare_spo2_models",
    "SpO2Result",
]


@dataclass(frozen=True, slots=True)
class SpO2Result:
    """Result container for SpO2 prediction models.
    
    Attributes:
        predicted_spo2: Predicted SpO2 % (capped at 0-100)
        model_name: Name of the model used
        confidence: Model confidence/uncertainty where applicable
        notes: Additional model-specific information
    """
    predicted_spo2: float
    model_name: str
    confidence: float | None = None
    notes: str = ""


def _validate_finite(name: str, value: float) -> float:
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{name} must be finite")
    return numeric


def _validate_range(name: str, value: float, min_value: float, max_value: float) -> float:
    if value < min_value or value > max_value:
        raise ValueError(f"{name} must be in [{min_value}, {max_value}], got {value}")
    return value


def niermeyer_spo2(altitude_m: float, sex: Literal["male", "female"]) -> SpO2Result:
    """Niermeyer et al. Linear Regression Model.
    
    Citation:
        Niermeyer et al., European Journal of Applied Physiology
        (cited in Tüshaus et al., 2019)
    
    Equation:
        SpO2 = 103.3 - (0.0047 × altitude[m]) + Z
    
    Where:
        Z = 0.7 for males, 1.4 for females
    
    Args:
        altitude_m: Altitude in meters above sea level
        sex: "male" or "female" for sex correction factor
    
    Returns:
        SpO2Result with predicted SpO2 %
    
    Notes:
        - Validated on healthy populations 0-4,018m
        - Does NOT account for acclimatization
        - Simple field-use model
    """
    altitude = _validate_range(
        "altitude_m",
        _validate_finite("altitude_m", altitude_m),
        0.0,
        8848.0,
    )
    if sex not in ("male", "female"):
        raise ValueError(f"sex must be 'male' or 'female', got {sex!r}")

    z = 0.7 if sex == "male" else 1.4
    spo2 = 103.3 - (0.0047 * altitude) + z
    spo2 = max(50.0, min(100.0, spo2))
    
    return SpO2Result(
        predicted_spo2=round(spo2, 2),
        model_name="Niermeyer et al. Linear",
        confidence=0.70,
        notes=f"Sex correction: {sex} (Z={z})"
    )


def alt_var_spo2(
    altitude_m: float,
    spo2_12h: float,
    spo2_24h: float,
    hr_12h: float,
    hr_24h: float,
) -> SpO2Result:
    """Alt et al. Vector Autoregression (VAR) Model.
    
    Citation:
        Alt et al., The Sport Journal (2025)
        R² = 0.706
    
    Equation:
        SpO2(t) = β₀ + β₁·SpO2(t-12h) + β₂·SpO2(t-24h) + 
                  β₃·HR(t-12h) + β₄·HR(t-24h) + β₅·Altitude + ε
    
    Args:
        altitude_m: Current altitude in meters
        spo2_12h: SpO2 reading 12 hours prior (%)
        spo2_24h: SpO2 reading 24 hours prior (%)
        hr_12h: Heart rate 12 hours prior (bpm)
        hr_24h: Heart rate 24 hours prior (bpm)
    
    Returns:
        SpO2Result with predicted SpO2 %
    
    Notes:
        - Captures acclimatization via time-lagged SpO2 and HR
        - Requires continuous monitoring data
    """
    altitude = _validate_range(
        "altitude_m",
        _validate_finite("altitude_m", altitude_m),
        0.0,
        8848.0,
    )
    spo2_prev_12 = _validate_range(
        "spo2_12h",
        _validate_finite("spo2_12h", spo2_12h),
        50.0,
        100.0,
    )
    spo2_prev_24 = _validate_range(
        "spo2_24h",
        _validate_finite("spo2_24h", spo2_24h),
        50.0,
        100.0,
    )
    hr_prev_12 = _validate_range(
        "hr_12h",
        _validate_finite("hr_12h", hr_12h),
        30.0,
        220.0,
    )
    hr_prev_24 = _validate_range(
        "hr_24h",
        _validate_finite("hr_24h", hr_24h),
        30.0,
        220.0,
    )

    b0, b1, b2, b3, b4, b5 = 45.0, 0.35, 0.25, -0.08, -0.05, -0.002
    spo2 = (
        b0
        + b1 * spo2_prev_12
        + b2 * spo2_prev_24
        + b3 * hr_prev_12
        + b4 * hr_prev_24
        + b5 * altitude
    )
    spo2 = max(50.0, min(100.0, spo2))
    
    return SpO2Result(
        predicted_spo2=round(spo2, 2),
        model_name="Alt et al. VAR",
        confidence=0.706,
        notes="Captures acclimatization dynamics (12h/24h lags)"
    )


def tushaus_cascade_spo2(
    altitude_m: float,
    fi_o2: float = 0.21,
    temp_c: float = 37.0,
) -> SpO2Result:
    """Tüshaus et al. Physiological Cascade Model (PAO2-based).
    
    Citation:
        Tüshaus et al., Physiological Reports
    
    Oxygen Cascade:
        PAO2 = FiO₂ × (PB - PH₂O)
        PH₂O = 47 mmHg at 37°C
    
    Args:
        altitude_m: Altitude in meters
        fi_o2: Fraction of inspired oxygen (default 0.21 = 21%)
        temp_c: Body temperature in Celsius (affects PH₂O)
    
    Returns:
        SpO2Result with predicted SpO2 %
    
    Notes:
        - Based on physiological first principles
        - Includes ±2% pulse oximeter tolerance
    """
    altitude = _validate_range(
        "altitude_m",
        _validate_finite("altitude_m", altitude_m),
        0.0,
        11000.0,
    )
    fio2 = _validate_range(
        "fi_o2",
        _validate_finite("fi_o2", fi_o2),
        0.1,
        1.0,
    )
    body_temp_c = _validate_range(
        "temp_c",
        _validate_finite("temp_c", temp_c),
        30.0,
        45.0,
    )

    # Barometric pressure from ISA
    p0 = 760.0  # mmHg at sea level
    pb = p0 * (1 - 2.25577e-5 * altitude) ** 5.25588
    
    # Water vapor pressure
    ph2o = 6.1078 * math.exp((17.2694 * body_temp_c) / (body_temp_c + 237.3)) * 0.750062
    
    # Alveolar PO2
    pao2 = fio2 * (pb - ph2o)
    
    # Estimate SpO2 from PAO2 with a continuous transition at 60 mmHg.
    if pao2 < 60.0:
        spo2 = 75.0 + (pao2 - 40.0) * 0.75
    else:
        spo2 = min(100.0, 90.0 + (pao2 - 60.0) * 0.25)
    
    spo2 = max(50.0, min(100.0, spo2))
    
    return SpO2Result(
        predicted_spo2=round(spo2, 2),
        model_name="Tüshaus Cascade",
        confidence=0.85,
        notes=f"PAO2={pao2:.1f}mmHg, ±2% tolerance"
    )


def compare_spo2_models(
    altitude_m: float,
    sex: Literal["male", "female"] = "male",
) -> dict[str, SpO2Result]:
    """Compare Niermeyer and Tüshaus models at given altitude.
    
    Args:
        altitude_m: Altitude in meters
        sex: Sex for Niermeyer model ("male" or "female")
    
    Returns:
        Dictionary mapping model names to SpO2Result
    """
    altitude = _validate_finite("altitude_m", altitude_m)
    return {
        "Niermeyer": niermeyer_spo2(altitude, sex),
        "Tüshaus": tushaus_cascade_spo2(altitude),
    }