from typing import Tuple
from .atmosphere import standard_atmosphere


def ambient_pressure_mmHg(altitude_m: float) -> float:
    """Ambient pressure (mmHg) from ISA at altitude."""
    return standard_atmosphere(altitude_m)["pressure_Pa"] / 133.322


def tissue_ratio(Ptissue_N2_mmHg: float, Pambient_mmHg: float) -> float:
    """Compute Tissue Ratio (TR) for decompression assessment: TR = Ptissue_N₂ / Pambient.

    At sea level equilibrium, TR ≈ 0.78. Values substantially above ~1.2 may
    indicate elevated DCS risk depending on tissue kinetics and profile.
    """
    Pamb = max(1e-6, float(Pambient_mmHg))
    return max(0.0, float(Ptissue_N2_mmHg) / Pamb)


def interpret_tr(tr: float) -> str:
    """Basic qualitative interpretation for TR values."""
    if tr < 0.9:
        return "No decompression stress expected"
    if tr < 1.2:
        return "Mild decompression stress"
    if tr < 1.5:
        return "Moderate decompression stress"
    return "High decompression stress"