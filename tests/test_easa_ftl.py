import pytest

from calculators.easa_ftl import (
    EasaFtlFdpInputs,
    EasaOroFtl210Inputs,
    easa_max_daily_fdp,
    easa_oroflt_210_cumulative_limits,
)


def test_oroflt205_table2_acclimatised_basic() -> None:
    # ORO.FTL.205(b)(1) Table 2: 0600–1329, 1–2 sectors => 13:00
    res = easa_max_daily_fdp(
        EasaFtlFdpInputs(
            reference_time_local_hhmm="07:00",
            flight_sectors=2,
            acclimatisation_state="acclimatised",
            request_extension_without_inflight_rest=False,
        )
    )
    assert abs(res.max_daily_fdp_hours - 13.0) < 1e-9


def test_oroflt205_table2_acclimatised_edge_band() -> None:
    # ORO.FTL.205(b)(1) Table 2: 1330–1359, 1–2 sectors => 12:45
    res = easa_max_daily_fdp(
        EasaFtlFdpInputs(
            reference_time_local_hhmm="13:45",
            flight_sectors=2,
            acclimatisation_state="acclimatised",
        )
    )
    assert abs(res.max_daily_fdp_hours - (12.75)) < 1e-9  # 12:45


def test_oroflt205_unknown_state_table3() -> None:
    # ORO.FTL.205(b)(2) Table 3: unknown state, 1–2 sectors => 11:00
    res = easa_max_daily_fdp(
        EasaFtlFdpInputs(
            reference_time_local_hhmm="07:00",
            flight_sectors=2,
            acclimatisation_state="unknown",
        )
    )
    assert abs(res.max_daily_fdp_hours - 11.0) < 1e-9


def test_csftl1205b_extension_not_allowed() -> None:
    # CS FTL.1.205(b): 0600–0614 => extension not allowed
    res = easa_max_daily_fdp(
        EasaFtlFdpInputs(
            reference_time_local_hhmm="06:10",
            flight_sectors=2,
            acclimatisation_state="acclimatised",
            request_extension_without_inflight_rest=True,
        )
    )
    assert res.extension_allowed is False
    assert res.extension_max_daily_fdp_hours is None


def test_csftl1205b_extension_allowed() -> None:
    # CS FTL.1.205(b): 0700–1329, 1–2 sectors => 14:00
    res = easa_max_daily_fdp(
        EasaFtlFdpInputs(
            reference_time_local_hhmm="07:00",
            flight_sectors=2,
            acclimatisation_state="acclimatised",
            request_extension_without_inflight_rest=True,
        )
    )
    assert res.extension_allowed is True
    assert res.extension_max_daily_fdp_hours is not None
    assert abs(res.extension_max_daily_fdp_hours - 14.0) < 1e-9


def test_oroflt210_cumulative_limits() -> None:
    # ORO.FTL.210 duty + flight time caps.
    res = easa_oroflt_210_cumulative_limits(
        EasaOroFtl210Inputs(
            duty_last_7d_hours=50.0,
            duty_last_14d_hours=90.0,
            duty_last_28d_hours=150.0,
            flight_time_last_28d_hours=80.0,
            flight_time_calendar_year_hours=850.0,
            flight_time_last_12mo_hours=950.0,
            planned_duty_hours=8.0,
            planned_flight_time_hours=5.0,
        )
    )
    assert res.duty_7d_ok is True
    assert res.duty_14d_ok is True
    assert res.duty_28d_ok is True
    assert res.flight_time_28d_ok is True
    assert res.flight_time_calendar_year_ok is True
    assert res.flight_time_12mo_ok is True


def test_oroflt210_negative_rejected() -> None:
    with pytest.raises(ValueError):
        _ = easa_oroflt_210_cumulative_limits(
            EasaOroFtl210Inputs(
                duty_last_7d_hours=-1.0,
                duty_last_14d_hours=0.0,
                duty_last_28d_hours=0.0,
                flight_time_last_28d_hours=0.0,
                flight_time_calendar_year_hours=0.0,
                flight_time_last_12mo_hours=0.0,
                planned_duty_hours=0.0,
                planned_flight_time_hours=0.0,
            )
        )


