from calculators.duty_time import Faa117CumulativeInputs, faa117_cumulative_limits


def test_cumulative_limits_ok() -> None:
    res = faa117_cumulative_limits(
        Faa117CumulativeInputs(
            flight_time_last_672h=90.0,
            flight_time_last_365d=900.0,
            fdp_last_168h=50.0,
            fdp_last_672h=180.0,
            had_30h_free_past_168h=True,
            planned_flight_time_hours=5.0,
            planned_fdp_hours=8.0,
        )
    )
    assert res.flight_time_672h_ok is True
    assert res.flight_time_365d_ok is True
    assert res.fdp_168h_ok is True
    assert res.fdp_672h_ok is True


def test_cumulative_limits_exceed() -> None:
    res = faa117_cumulative_limits(
        Faa117CumulativeInputs(
            flight_time_last_672h=99.0,
            flight_time_last_365d=999.0,
            fdp_last_168h=59.5,
            fdp_last_672h=189.0,
            had_30h_free_past_168h=False,
            planned_flight_time_hours=2.0,
            planned_fdp_hours=2.0,
        )
    )
    assert res.flight_time_672h_ok is False
    assert res.flight_time_365d_ok is False
    assert res.fdp_168h_ok is False
    assert res.fdp_672h_ok is False


