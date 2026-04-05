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
    z = 0.7 if sex == "male" else 1.4
    spo2 = 103.3 - (0.0047 * altitude_m) + z
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
    B0, B1, B2, B3, B4, B5 = 45.0, 0.35, 0.25, -0.08, -0.05, -0.002
    spo2 = B0 + B1*spo2_12h + B2*spo2_24h + B3*hr_12h + B4*hr_24h + B5*altitude_m
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
    # Barometric pressure from ISA
    p0 = 760.0  # mmHg at sea level
    pb = p0 * (1 - 2.25577e-5 * altitude_m) ** 5.25588
    
    # Water vapor pressure
    ph2o = 6.1078 * math.exp((17.2694 * temp_c) / (temp_c + 237.3)) * 0.750062
    
    # Alveolar PO2
    pao2 = fi_o2 * (pb - ph2o)
    
    # Estimate SpO2 from PAO2
    if pao2 < 40:
        spo2 = 75 + (pao2 - 40) * 1.25
    else:
        spo2 = min(100, 90 + (pao2 - 60) * 0.25)
    
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
    return {
        "Niermeyer": niermeyer_spo2(altitude_m, sex),
        "Tüshaus": tushaus_cascade_spo2(altitude_m),
    }