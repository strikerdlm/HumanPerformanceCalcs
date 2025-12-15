import pytest

from calculators.aa_gradient import AaGradientInputs, compute_aa_gradient


def test_aa_gradient_basic_sign() -> None:
    # Sea level, room air, typical values: PAO2 ~ 100, PaO2 ~ 90 => A-a ~ 10
    res = compute_aa_gradient(
        AaGradientInputs(
            altitude_m=0.0,
            pao2_mmHg=90.0,
            paco2_mmHg=40.0,
            fio2=0.21,
            rq=0.8,
            normal_model="filley1954_rest_air_1600ft",
        )
    )
    assert res.pao2_calc_mmHg > 0
    assert res.aa_gradient_mmHg == pytest.approx(res.pao2_calc_mmHg - 90.0, rel=1e-12, abs=1e-12)


def test_aa_gradient_heuristic_requires_age() -> None:
    with pytest.raises(ValueError):
        _ = compute_aa_gradient(
            AaGradientInputs(
                altitude_m=0.0,
                pao2_mmHg=90.0,
                normal_model="heuristic_age_over4_plus4",
            )
        )


