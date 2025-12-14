import math

import pytest

from calculators.spatial_disorientation import (
    SpatialDisorientationInputs,
    spatial_disorientation_risk,
)


def test_somatogravic_tilt_matches_physics_example_058g_is_about_30deg() -> None:
    # PubMed 9491247 notes a 0.58 g linear acceleration corresponding to ~30° pitch-up GIA.
    a = 0.58 * 9.80665
    res = spatial_disorientation_risk(
        SpatialDisorientationInputs(
            imc=True,
            night=False,
            nvg=False,
            time_since_horizon_reference_s=60.0,
            yaw_rate_deg_s=0.0,
            sustained_turn_duration_s=0.0,
            head_movement_during_turn=False,
            forward_accel_m_s2=a,
            workload=0.5,
        )
    )
    assert res.somatogravic_tilt_deg == pytest.approx(30.0, abs=0.75)


def test_leans_component_high_for_slow_turn_under_threshold() -> None:
    res = spatial_disorientation_risk(
        SpatialDisorientationInputs(
            imc=True,
            night=False,
            nvg=False,
            time_since_horizon_reference_s=45.0,
            yaw_rate_deg_s=1.0,  # below ~2 deg/s
            sustained_turn_duration_s=60.0,
            head_movement_during_turn=False,
            forward_accel_m_s2=0.0,
            workload=0.2,
        )
    )
    # For yaw_rate=1 deg/s and threshold=2 deg/s, the below-threshold factor is 0.5;
    # with long duration, the component should be "high-ish" (>= ~0.45).
    assert res.leans_risk_component_0_1 >= 0.45


def test_coriolis_component_requires_head_movement_and_high_yaw_rate() -> None:
    res_no_head = spatial_disorientation_risk(
        SpatialDisorientationInputs(
            imc=True,
            night=False,
            nvg=False,
            time_since_horizon_reference_s=45.0,
            yaw_rate_deg_s=20.0,
            sustained_turn_duration_s=60.0,
            head_movement_during_turn=False,
            forward_accel_m_s2=0.0,
            workload=0.2,
        )
    )
    assert res_no_head.coriolis_component_0_1 == 0.0

    res_head = spatial_disorientation_risk(
        SpatialDisorientationInputs(
            imc=True,
            night=False,
            nvg=False,
            time_since_horizon_reference_s=45.0,
            yaw_rate_deg_s=20.0,
            sustained_turn_duration_s=60.0,
            head_movement_during_turn=True,
            forward_accel_m_s2=0.0,
            workload=0.2,
        )
    )
    assert res_head.coriolis_component_0_1 > 0.2


def test_workload_bounds_validation() -> None:
    with pytest.raises(ValueError):
        _ = spatial_disorientation_risk(
            SpatialDisorientationInputs(
                imc=False,
                night=False,
                nvg=False,
                time_since_horizon_reference_s=0.0,
                yaw_rate_deg_s=0.0,
                sustained_turn_duration_s=0.0,
                head_movement_during_turn=False,
                forward_accel_m_s2=0.0,
                workload=1.1,
            )
        )


