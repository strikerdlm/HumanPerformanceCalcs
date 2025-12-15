import pytest

from calculators.oxygen_delivery import OxygenDeliveryInputs, compute_oxygen_delivery, dubois_bsa_m2


def test_cao2_components_add() -> None:
    out = compute_oxygen_delivery(
        OxygenDeliveryInputs(
            hb_g_dl=15.0,
            sao2_frac=0.98,
            pao2_mmhg=100.0,
            cardiac_output_l_min=5.0,
            hufner_ml_per_g=1.34,
            alpha_ml_per_dl_per_mmhg=0.003,
        )
    )
    assert out.cao2_ml_o2_dl == pytest.approx(out.o2_bound_ml_o2_dl + out.o2_dissolved_ml_o2_dl, rel=1e-12, abs=1e-12)
    assert out.do2_ml_o2_min > 0


def test_bsa_and_do2i() -> None:
    bsa = dubois_bsa_m2(height_cm=180.0, weight_kg=80.0)
    out = compute_oxygen_delivery(
        OxygenDeliveryInputs(
            hb_g_dl=15.0,
            sao2_frac=0.98,
            pao2_mmhg=100.0,
            cardiac_output_l_min=5.0,
            bsa_m2=bsa,
        )
    )
    assert out.bsa_m2 == pytest.approx(bsa, rel=1e-12, abs=1e-12)
    assert out.do2i_ml_o2_min_m2 is not None
    assert out.do2i_ml_o2_min_m2 == pytest.approx(out.do2_ml_o2_min / bsa, rel=1e-12, abs=1e-12)


