import pytest

from calculators.mssq import MssqShortInputs, compute_mssq_short


def test_mssq_short_zero() -> None:
    res = compute_mssq_short(
        MssqShortInputs(
            section_a_scores_0_3=(0, 0, 0, 0, 0, 0, 0, 0, 0),
            section_b_scores_0_3=(0, 0, 0, 0, 0, 0, 0, 0, 0),
        )
    )
    assert res.section_a_sum_0_27 == 0
    assert res.section_b_sum_0_27 == 0
    assert res.total_sum_0_54 == 0
    assert res.rivera_2022_percentile_band == "<P25"


def test_mssq_short_max() -> None:
    res = compute_mssq_short(
        MssqShortInputs(
            section_a_scores_0_3=(3, 3, 3, 3, 3, 3, 3, 3, 3),
            section_b_scores_0_3=(3, 3, 3, 3, 3, 3, 3, 3, 3),
        )
    )
    assert res.section_a_sum_0_27 == 27
    assert res.section_b_sum_0_27 == 27
    assert res.total_sum_0_54 == 54
    assert res.rivera_2022_percentile_band == ">=P75"


def test_mssq_short_validation_len() -> None:
    with pytest.raises(ValueError):
        _ = compute_mssq_short(
            MssqShortInputs(
                section_a_scores_0_3=(0, 0),  # wrong length
                section_b_scores_0_3=(0, 0, 0, 0, 0, 0, 0, 0, 0),
            )
        )


def test_mssq_short_validation_range() -> None:
    with pytest.raises(ValueError):
        _ = compute_mssq_short(
            MssqShortInputs(
                section_a_scores_0_3=(4, 0, 0, 0, 0, 0, 0, 0, 0),
                section_b_scores_0_3=(0, 0, 0, 0, 0, 0, 0, 0, 0),
            )
        )


def test_mssq_short_band_mid() -> None:
    # Total of 9 matches Rivera P50, so should fall in P50–P75 by our convention (>=P50).
    res = compute_mssq_short(
        MssqShortInputs(
            section_a_scores_0_3=(1, 1, 1, 1, 1, 1, 1, 1, 1),  # 9
            section_b_scores_0_3=(0, 0, 0, 0, 0, 0, 0, 0, 0),
        )
    )
    assert res.total_sum_0_54 == 9
    assert res.rivera_2022_percentile_band == "P50–P75"


