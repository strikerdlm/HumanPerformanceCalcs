import pytest

from calculators.vision_altitude import estimate_dva_logmar_wang2024, logmar_to_snellen_denominator


def test_logmar_to_snellen_basic() -> None:
    # logMAR 0.0 == 20/20
    assert logmar_to_snellen_denominator(0.0) == 20
    # worse acuity should increase denominator
    assert logmar_to_snellen_denominator(0.3) > 20


def test_ground_velocity_effect_directional() -> None:
    # At ground (from Table 3), logMAR is worse at higher angular velocity (20->80).
    low = estimate_dva_logmar_wang2024(altitude_m=0.0, time_at_altitude_min=0.0, angular_velocity_deg_s=20.0)
    high = estimate_dva_logmar_wang2024(altitude_m=0.0, time_at_altitude_min=0.0, angular_velocity_deg_s=80.0)
    assert high.logmar >= low.logmar


def test_interpolation_is_bounded() -> None:
    # Inputs outside study range clamp without error.
    out = estimate_dva_logmar_wang2024(altitude_m=10000.0, time_at_altitude_min=999.0, angular_velocity_deg_s=5.0)
    assert 0.0 <= out.altitude_m <= 4500.0
    assert 0.0 <= out.time_at_altitude_min <= 30.0
    assert 20.0 <= out.angular_velocity_deg_s <= 80.0


def test_invalid_inputs_raise() -> None:
    with pytest.raises(ValueError):
        _ = estimate_dva_logmar_wang2024(altitude_m=-1.0, time_at_altitude_min=0.0, angular_velocity_deg_s=20.0)
    with pytest.raises(ValueError):
        _ = estimate_dva_logmar_wang2024(altitude_m=0.0, time_at_altitude_min=-1.0, angular_velocity_deg_s=20.0)
    with pytest.raises(ValueError):
        _ = estimate_dva_logmar_wang2024(altitude_m=0.0, time_at_altitude_min=0.0, angular_velocity_deg_s=0.0)


