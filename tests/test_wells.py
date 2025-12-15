import pytest

from calculators.wells import (
    WellsDvtInputs,
    compute_wells_dvt,
    WellsPeInputs,
    compute_wells_pe,
)


def test_wells_dvt_low_boundary() -> None:
    # total = 0 => low, unlikely
    res = compute_wells_dvt(WellsDvtInputs())
    assert res.total_points == 0.0
    assert res.three_tier == "low"
    assert res.two_tier == "unlikely"


def test_wells_dvt_moderate_and_likely_thresholds() -> None:
    # total = 1 => moderate, unlikely (<=1)
    res1 = compute_wells_dvt(WellsDvtInputs(active_cancer=True))
    assert res1.total_points == 1.0
    assert res1.three_tier == "moderate"
    assert res1.two_tier == "unlikely"

    # total = 2 => moderate, likely (>1)
    res2 = compute_wells_dvt(WellsDvtInputs(active_cancer=True, entire_leg_swollen=True))
    assert res2.total_points == 2.0
    assert res2.three_tier == "moderate"
    assert res2.two_tier == "likely"


def test_wells_dvt_high_threshold() -> None:
    # total >=3 => high
    res = compute_wells_dvt(
        WellsDvtInputs(
            active_cancer=True,
            entire_leg_swollen=True,
            pitting_edema_confined_to_symptomatic_leg=True,
        )
    )
    assert res.total_points == 3.0
    assert res.three_tier == "high"
    assert res.two_tier == "likely"


def test_wells_dvt_alt_dx_subtracts() -> None:
    # two positives minus alternative dx => 0
    res = compute_wells_dvt(
        WellsDvtInputs(active_cancer=True, entire_leg_swollen=True, alternative_diagnosis_as_likely_as_dvt=True)
    )
    assert res.total_points == 0.0
    assert res.three_tier == "low"


def test_wells_dvt_calf_diff_drives_boolean() -> None:
    res = compute_wells_dvt(WellsDvtInputs(calf_diff_cm=3.1))
    assert res.calf_swelling_gt_3cm is True
    assert res.total_points == 1.0


def test_wells_dvt_conflicting_calf_inputs_rejected() -> None:
    with pytest.raises(ValueError):
        _ = compute_wells_dvt(WellsDvtInputs(calf_diff_cm=4.0, calf_swelling_gt_3cm_compared_to_asymptomatic_leg=False))


def test_wells_pe_basic() -> None:
    # zero => low, unlikely
    res = compute_wells_pe(WellsPeInputs())
    assert res.total_points == 0.0
    assert res.three_tier == "low"
    assert res.two_tier == "unlikely"


def test_wells_pe_hr_threshold() -> None:
    res = compute_wells_pe(WellsPeInputs(heart_rate_bpm=101.0))
    assert res.heart_rate_gt_100 is True
    assert res.total_points == 1.5
    assert res.three_tier == "low"  # still <2


def test_wells_pe_moderate_and_likely_cutoff() -> None:
    # 4.0 => moderate, unlikely (<=4)
    res4 = compute_wells_pe(WellsPeInputs(clinical_signs_dvt=True, heart_rate_bpm=101.0))  # 3 + 1.5 = 4.5 (oops)
    assert res4.total_points == 4.5
    assert res4.three_tier == "moderate"
    assert res4.two_tier == "likely"


def test_wells_pe_high_threshold() -> None:
    # >6 => high
    res = compute_wells_pe(WellsPeInputs(clinical_signs_dvt=True, pe_most_likely_diagnosis=True, heart_rate_bpm=101.0))
    assert res.total_points == 7.5
    assert res.three_tier == "high"
    assert res.two_tier == "likely"


def test_wells_pe_conflicting_hr_inputs_rejected() -> None:
    with pytest.raises(ValueError):
        _ = compute_wells_pe(WellsPeInputs(heart_rate_bpm=80.0, heart_rate_bpm_gt_100=True))


