import pytest

from calculators.agsm import AgsmInputs, estimate_gz_tolerance_with_agsm


def test_reference_conditions_match_published_condition_values() -> None:
    # Anchored to the condition values reported in PubMed 17484342:
    # I: relaxed, no garment ~3.4 Gz
    # II: relaxed + anti-G suit >=6.5 Gz
    # III: anti-G suit + pressure breathing >=8.0 Gz
    # IV: anti-G suit + AGSM >=8.9 Gz
    # V: anti-G suit + pressure breathing + AGSM >=9.0 Gz (cap)
    #
    # Our model is deterministic and uses these as defaults, so it should reproduce them
    # exactly when baseline is set to 3.4.

    base = AgsmInputs(baseline_relaxed_gz=3.4, anti_g_suit=False, pressure_breathing_for_g=False, agsm_quality=0.0)
    r1 = estimate_gz_tolerance_with_agsm(base)
    assert r1.capped_estimated_gz == pytest.approx(3.4)

    r2 = estimate_gz_tolerance_with_agsm(
        AgsmInputs(baseline_relaxed_gz=3.4, anti_g_suit=True, pressure_breathing_for_g=False, agsm_quality=0.0)
    )
    assert r2.capped_estimated_gz == pytest.approx(6.5)

    r3 = estimate_gz_tolerance_with_agsm(
        AgsmInputs(baseline_relaxed_gz=3.4, anti_g_suit=True, pressure_breathing_for_g=True, agsm_quality=0.0)
    )
    assert r3.capped_estimated_gz == pytest.approx(8.0)

    r4 = estimate_gz_tolerance_with_agsm(
        AgsmInputs(baseline_relaxed_gz=3.4, anti_g_suit=True, pressure_breathing_for_g=False, agsm_quality=1.0)
    )
    assert r4.capped_estimated_gz == pytest.approx(8.9)

    r5 = estimate_gz_tolerance_with_agsm(
        AgsmInputs(baseline_relaxed_gz=3.4, anti_g_suit=True, pressure_breathing_for_g=True, agsm_quality=1.0)
    )
    assert r5.capped_estimated_gz == pytest.approx(9.0)
    assert r5.was_capped is True


def test_invalid_quality_raises() -> None:
    with pytest.raises(ValueError):
        _ = estimate_gz_tolerance_with_agsm(AgsmInputs(agsm_quality=-0.1))
    with pytest.raises(ValueError):
        _ = estimate_gz_tolerance_with_agsm(AgsmInputs(agsm_quality=1.1))


