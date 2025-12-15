"""NVG / electro-optical target acquisition (Johnson / ACQUIRE cycle criteria).

This module implements a transparent, physics-first target acquisition estimate for
imaging systems (including NVG-like displays) using **cycles-on-target** criteria.

Scientific basis (open sources)
------------------------------
We use the historically common *Johnson criteria* (N50 cycles-on-target) and the later
ACQUIRE criteria as summarized in:

- Sjaardema, T. A., Smith, C. S., & Birch, G. C. (2015).
  *History and Evolution of the Johnson Criteria* (SAND2015-6368).
  https://www.osti.gov/servlets/purl/1222446

The report provides the N50 cycle counts for discrimination levels (e.g., detection,
recognition, identification) and discusses later model evolutions such as ACQUIRE.

Important scope notes
---------------------
- This is a **resolution-based** estimate. It does **not** model illumination,
  scintillation/noise, contrast transfer function, atmospheric attenuation, user
  training, or target/background clutter (all of which strongly affect performance).
- Therefore, outputs should be treated as *geometric feasibility* indicators, not
  operational guarantees.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final, Literal

__all__ = [
    "CriteriaFamily",
    "DiscriminationLevel",
    "ImagingSystem",
    "Target",
    "NvgAcquisitionResult",
    "cycles_on_target",
    "range_for_required_cycles",
    "assess_target_acquisition",
]


CriteriaFamily = Literal["johnson", "acquire"]
DiscriminationLevel = Literal["detection", "orientation", "classification", "recognition", "identification"]


@dataclass(frozen=True, slots=True)
class ImagingSystem:
    """Imaging system angular sampling model.

    Inputs represent the displayed/usable resolution and field-of-view, not sensor die specs.
    """

    horizontal_pixels: int
    vertical_pixels: int
    horizontal_fov_deg: float
    vertical_fov_deg: float


@dataclass(frozen=True, slots=True)
class Target:
    width_m: float
    height_m: float


@dataclass(frozen=True, slots=True)
class NvgAcquisitionResult:
    criteria: CriteriaFamily
    discrimination: DiscriminationLevel
    range_m: float
    target_dimension_m: float
    ifov_deg_per_pixel: float
    target_angular_deg: float
    pixels_on_target: float
    cycles_on_target: float
    required_cycles_n50: float
    meets_n50: bool
    ratio_to_n50: float


# N50 cycle criteria as summarized by Sjaardema et al. (2015), Table 1 and Table 4.
# Johnson: Detection 1.0; Orientation 1.4; Recognition 4.0; Identification 6.4.
_JOHNSON_N50: Final[dict[DiscriminationLevel, float]] = {
    "detection": 1.0,
    "orientation": 1.4,
    "recognition": 4.0,
    "identification": 6.4,
    # not defined in Johnson table; keep placeholder and guard in validation
    "classification": float("nan"),
}

# ACQUIRE: Detection 0.75; Classification 1.5; Recognition 3.0; Identification 6.0.
_ACQUIRE_N50: Final[dict[DiscriminationLevel, float]] = {
    "detection": 0.75,
    "classification": 1.5,
    "recognition": 3.0,
    "identification": 6.0,
    # not defined in ACQUIRE table
    "orientation": float("nan"),
}


def _is_finite(x: float) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def _validate_system(sys: ImagingSystem) -> ImagingSystem:
    if not isinstance(sys, ImagingSystem):
        raise TypeError("system must be an ImagingSystem")
    if sys.horizontal_pixels <= 0 or sys.vertical_pixels <= 0:
        raise ValueError("pixel counts must be positive")
    hf = float(sys.horizontal_fov_deg)
    vf = float(sys.vertical_fov_deg)
    if not (_is_finite(hf) and _is_finite(vf)):
        raise TypeError("FOV values must be finite numbers")
    if hf <= 0.0 or vf <= 0.0 or hf > 360.0 or vf > 180.0:
        raise ValueError("FOV values must be within physical bounds")
    return sys


def _validate_target(t: Target) -> Target:
    if not isinstance(t, Target):
        raise TypeError("target must be a Target")
    w = float(t.width_m)
    h = float(t.height_m)
    if not (_is_finite(w) and _is_finite(h)):
        raise TypeError("Target dimensions must be finite numbers")
    if w <= 0.0 or h <= 0.0:
        raise ValueError("Target dimensions must be > 0")
    return t


def _validate_range(range_m: float) -> float:
    r = float(range_m)
    if not _is_finite(r):
        raise TypeError("range_m must be finite")
    if r <= 0.0:
        raise ValueError("range_m must be > 0")
    return r


def _angular_size_deg(size_m: float, range_m: float) -> float:
    # Exact geometry for an object of size at range: theta = 2*atan(size/(2*range))
    return float(math.degrees(2.0 * math.atan2(float(size_m), 2.0 * float(range_m))))


def cycles_on_target(
    *,
    system: ImagingSystem,
    target: Target,
    range_m: float,
    critical_dimension: Literal["width", "height"] = "height",
) -> float:
    """Compute cycles-on-target along a chosen target dimension.

    We approximate cycles by Nyquist: cycles ≈ pixels/2 along the critical dimension.
    """
    sys = _validate_system(system)
    tgt = _validate_target(target)
    r = _validate_range(range_m)

    if critical_dimension not in ("width", "height"):
        raise ValueError("critical_dimension must be 'width' or 'height'")

    if critical_dimension == "width":
        dim_m = float(tgt.width_m)
        fov_deg = float(sys.horizontal_fov_deg)
        px = float(sys.horizontal_pixels)
    else:
        dim_m = float(tgt.height_m)
        fov_deg = float(sys.vertical_fov_deg)
        px = float(sys.vertical_pixels)

    ifov = fov_deg / px
    theta = _angular_size_deg(dim_m, r)
    pix_on_target = theta / ifov
    return float(max(0.0, pix_on_target / 2.0))


def range_for_required_cycles(
    *,
    system: ImagingSystem,
    target: Target,
    required_cycles: float,
    critical_dimension: Literal["width", "height"] = "height",
) -> float:
    """Invert the sampling geometry to solve range for a required cycles-on-target."""
    sys = _validate_system(system)
    tgt = _validate_target(target)
    req = float(required_cycles)
    if not _is_finite(req):
        raise TypeError("required_cycles must be finite")
    if req <= 0.0:
        raise ValueError("required_cycles must be > 0")

    if critical_dimension == "width":
        dim_m = float(tgt.width_m)
        fov_deg = float(sys.horizontal_fov_deg)
        px = float(sys.horizontal_pixels)
    elif critical_dimension == "height":
        dim_m = float(tgt.height_m)
        fov_deg = float(sys.vertical_fov_deg)
        px = float(sys.vertical_pixels)
    else:
        raise ValueError("critical_dimension must be 'width' or 'height'")

    ifov = fov_deg / float(px)
    pixels_needed = 2.0 * req
    theta_deg = pixels_needed * ifov
    theta_rad = math.radians(theta_deg)
    # theta = 2*atan(size/(2*range)) => range = size/(2*tan(theta/2))
    denom = 2.0 * math.tan(theta_rad / 2.0)
    if denom <= 0.0:
        raise ValueError("Invalid geometry for required cycles (theta too small)")
    return float(dim_m / denom)


def assess_target_acquisition(
    *,
    criteria: CriteriaFamily,
    discrimination: DiscriminationLevel,
    system: ImagingSystem,
    target: Target,
    range_m: float,
    critical_dimension: Literal["width", "height"] = "height",
) -> NvgAcquisitionResult:
    """Assess whether cycles-on-target meets N50 criterion (Johnson/ACQUIRE)."""
    if criteria not in ("johnson", "acquire"):
        raise ValueError("criteria must be 'johnson' or 'acquire'")

    table = _JOHNSON_N50 if criteria == "johnson" else _ACQUIRE_N50
    n50 = float(table.get(discrimination, float("nan")))
    if not _is_finite(n50):
        raise ValueError(f"Discrimination level '{discrimination}' is not defined for {criteria} criteria")

    sys = _validate_system(system)
    tgt = _validate_target(target)
    r = _validate_range(range_m)

    if critical_dimension == "width":
        dim_m = float(tgt.width_m)
        ifov = float(sys.horizontal_fov_deg) / float(sys.horizontal_pixels)
        theta = _angular_size_deg(dim_m, r)
        pix = theta / ifov
    elif critical_dimension == "height":
        dim_m = float(tgt.height_m)
        ifov = float(sys.vertical_fov_deg) / float(sys.vertical_pixels)
        theta = _angular_size_deg(dim_m, r)
        pix = theta / ifov
    else:
        raise ValueError("critical_dimension must be 'width' or 'height'")

    cyc = max(0.0, pix / 2.0)
    ratio = float(cyc / n50) if n50 > 0.0 else float("inf")
    return NvgAcquisitionResult(
        criteria=criteria,
        discrimination=discrimination,
        range_m=r,
        target_dimension_m=float(dim_m),
        ifov_deg_per_pixel=float(ifov),
        target_angular_deg=float(theta),
        pixels_on_target=float(pix),
        cycles_on_target=float(cyc),
        required_cycles_n50=float(n50),
        meets_n50=bool(cyc >= n50),
        ratio_to_n50=float(ratio),
    )


