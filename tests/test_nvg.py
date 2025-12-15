import pytest

from calculators.nvg import (
    ImagingSystem,
    Target,
    assess_target_acquisition,
    cycles_on_target,
    range_for_required_cycles,
)


def test_cycles_decrease_with_range() -> None:
    sys = ImagingSystem(horizontal_pixels=1024, vertical_pixels=768, horizontal_fov_deg=40.0, vertical_fov_deg=30.0)
    tgt = Target(width_m=0.5, height_m=1.8)
    c1 = cycles_on_target(system=sys, target=tgt, range_m=100.0, critical_dimension="height")
    c2 = cycles_on_target(system=sys, target=tgt, range_m=200.0, critical_dimension="height")
    assert c2 < c1


def test_inversion_consistency() -> None:
    sys = ImagingSystem(horizontal_pixels=1024, vertical_pixels=768, horizontal_fov_deg=40.0, vertical_fov_deg=30.0)
    tgt = Target(width_m=0.5, height_m=1.8)
    req = 4.0
    r = range_for_required_cycles(system=sys, target=tgt, required_cycles=req, critical_dimension="height")
    c = cycles_on_target(system=sys, target=tgt, range_m=r, critical_dimension="height")
    assert c == pytest.approx(req, rel=1e-6, abs=1e-6)


def test_assess_johnson_detection_defined_and_monotone() -> None:
    sys = ImagingSystem(horizontal_pixels=1024, vertical_pixels=768, horizontal_fov_deg=40.0, vertical_fov_deg=30.0)
    tgt = Target(width_m=0.5, height_m=1.8)
    near = assess_target_acquisition(
        criteria="johnson",
        discrimination="detection",
        system=sys,
        target=tgt,
        range_m=50.0,
        critical_dimension="height",
    )
    far = assess_target_acquisition(
        criteria="johnson",
        discrimination="detection",
        system=sys,
        target=tgt,
        range_m=500.0,
        critical_dimension="height",
    )
    assert near.cycles_on_target > far.cycles_on_target


def test_invalid_discrimination_for_family_raises() -> None:
    sys = ImagingSystem(horizontal_pixels=1024, vertical_pixels=768, horizontal_fov_deg=40.0, vertical_fov_deg=30.0)
    tgt = Target(width_m=0.5, height_m=1.8)
    with pytest.raises(ValueError):
        _ = assess_target_acquisition(
            criteria="johnson",
            discrimination="classification",
            system=sys,
            target=tgt,
            range_m=100.0,
        )


