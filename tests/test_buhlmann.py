import pytest

from calculators.buhlmann import GasMix, plan_zh_l16_gf


def test_zh_l16c_gf_air_40m_35min_matches_decotengu_example() -> None:
    # Cross-check against decotengu dt-lint output for:
    #   python dt-lint -m zh-l16c-gf 40 35
    # (Descent 20 m/min, ascent 10 m/min, GF 30/85, surface 1013.25 mbar, air).
    plan = plan_zh_l16_gf(
        max_depth_m=40.0,
        bottom_time_min=35.0,
        gas=GasMix(o2=0.21, he=0.0),
        gf_low=0.30,
        gf_high=0.85,
        model="zh-l16c-gf",
        surface_pressure_bar=1.01325,
        descent_rate_m_per_min=20.0,
        ascent_rate_m_per_min=10.0,
        stop_step_m=3.0,
    )

    expected = [
        (21.0, 1),
        (18.0, 1),
        (15.0, 2),
        (12.0, 5),
        (9.0, 7),
        (6.0, 15),
        (3.0, 28),
    ]
    got = [(round(s.depth_m, 0), s.minutes) for s in plan.stops]
    assert got == expected
    assert plan.total_decompression_minutes == 59


def test_invalid_gradient_factors() -> None:
    with pytest.raises(ValueError):
        _ = plan_zh_l16_gf(
            max_depth_m=30.0,
            bottom_time_min=20.0,
            gas=GasMix(o2=0.21),
            gf_low=0.9,
            gf_high=0.5,
        )


