import pytest

from calculators.duty_time import Faa117Inputs, faa117_limits, parse_hhmm


def test_parse_hhmm() -> None:
    assert parse_hhmm("00:00") == 0
    assert parse_hhmm("23:59") == 23 * 60 + 59
    with pytest.raises(ValueError):
        _ = parse_hhmm("24:00")


def test_table_a_max_flight_time() -> None:
    # 0500-1959 => 9h
    lim = faa117_limits(Faa117Inputs(report_time_local_hhmm="07:00", flight_segments=2))
    assert lim.max_flight_time_hours == 9.0
    # 0000-0459 => 8h
    lim2 = faa117_limits(Faa117Inputs(report_time_local_hhmm="04:30", flight_segments=2))
    assert lim2.max_flight_time_hours == 8.0


def test_table_b_fdp_lookup_and_not_acclimated_reduction() -> None:
    # 0700-1159, segments=1 => 14
    lim = faa117_limits(Faa117Inputs(report_time_local_hhmm="07:00", flight_segments=1))
    assert lim.max_fdp_hours == 14.0
    # not acclimated => minus 0.5
    lim2 = faa117_limits(Faa117Inputs(report_time_local_hhmm="07:00", flight_segments=1, not_acclimated=True))
    assert lim2.max_fdp_hours == 13.5


def test_margins() -> None:
    lim = faa117_limits(
        Faa117Inputs(
            report_time_local_hhmm="07:00",
            flight_segments=1,
            scheduled_fdp_hours=12.0,
            scheduled_flight_time_hours=8.0,
        )
    )
    assert lim.flight_time_ok is True
    assert lim.fdp_ok is True
    assert lim.flight_time_margin_hours is not None and lim.flight_time_margin_hours > 0
    assert lim.fdp_margin_hours is not None and lim.fdp_margin_hours > 0


