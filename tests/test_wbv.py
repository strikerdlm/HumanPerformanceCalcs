import pytest

from calculators.wbv import (
    WbvAxisWeightedRms,
    WbvExposureInputs,
    a8_from_aw,
    classify_hgcz_a8,
    combine_axes_iso2631,
    compute_wbv_exposure,
)


def test_combine_axes_zero_ok() -> None:
    aw = combine_axes_iso2631(WbvAxisWeightedRms(awx_m_s2=0.0, awy_m_s2=0.0, awz_m_s2=0.0))
    assert aw == 0.0


def test_a8_scaling_matches_definition() -> None:
    # If exposure duration is 8h, A(8) should equal aw.
    aw = 0.8
    a8 = a8_from_aw(aw_m_s2=aw, exposure_duration_s=8.0 * 3600.0)
    assert a8 == pytest.approx(aw, rel=0.0, abs=1e-12)


def test_a8_zone_classification() -> None:
    assert classify_hgcz_a8(0.1) == "below_lower"
    assert classify_hgcz_a8(0.47) == "within_hgcz"
    assert classify_hgcz_a8(0.9) == "within_hgcz"
    assert classify_hgcz_a8(0.94) == "above_upper"


def test_compute_wbv_exposure_smoke() -> None:
    inp = WbvExposureInputs(
        axis_aw=WbvAxisWeightedRms(awx_m_s2=0.2, awy_m_s2=0.2, awz_m_s2=0.3),
        exposure_duration_s=2.0 * 3600.0,
    )
    out = compute_wbv_exposure(inp)
    assert out.aw_combined_m_s2 > 0.0
    assert out.a8_m_s2 > 0.0
    assert out.vdv8_m_s1_75 is None


