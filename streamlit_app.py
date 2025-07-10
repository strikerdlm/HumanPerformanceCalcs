import streamlit as st  # type: ignore

from calculators import (
    standard_atmosphere,
    alveolar_PO2,
    estimate_tuc,
    g_loc_time,
    dose_rate,
)

st.set_page_config(
    page_title="Aerospace Physiology Calculators",
    page_icon="✈️",
    layout="centered",
)

st.title("✈️ Aerospace Physiology Calculators")

st.sidebar.header("Choose a calculator")
calculator = st.sidebar.selectbox(
    "Calculator", (
        "Standard Atmosphere",
        "Alveolar Oxygen Pressure",
        "Time of Useful Consciousness",
        "G-Force Tolerance",
        "Cosmic Radiation Dose",
    ),
)

# ----------------------------------------------------------------------------
# 1. STANDARD ATMOSPHERE
# ----------------------------------------------------------------------------
if calculator == "Standard Atmosphere":
    st.subheader("International Standard Atmosphere (ISA)")
    alt_ft = st.slider("Altitude (ft)", 0, 60_000, 0, step=1_000)
    alt_m = alt_ft * 0.3048
    result = standard_atmosphere(alt_m)

    st.write(f"**Temperature:** {result['temperature_C']:.2f} °C")
    st.write(f"**Pressure:** {result['pressure_Pa'] / 100:.2f} hPa")
    st.write(f"**Density:** {result['density_kg_m3']:.3f} kg/m³")
    st.write(f"**O₂ Partial Pressure:** {result['pO2_Pa'] / 100:.2f} hPa")

    st.caption("Calculations up to 11 km assume a linear temperature lapse rate; above this an isothermal layer is assumed.")

# ----------------------------------------------------------------------------
# 2. ALVEOLAR GAS EQUATION
# ----------------------------------------------------------------------------
elif calculator == "Alveolar Oxygen Pressure":
    st.subheader("Alveolar Oxygen Pressure (PAO₂)")
    alt_ft = st.slider("Altitude (ft)", 0, 40_000, 0, step=1_000)
    alt_m = alt_ft * 0.3048

    FiO2 = st.number_input("Inspired O₂ fraction (FiO₂)", 0.0, 1.0, 0.21, step=0.01)
    PaCO2 = st.number_input("Arterial CO₂ (PaCO₂) [mmHg]", 20.0, 60.0, 40.0, step=1.0)
    RQ = st.number_input("Respiratory Quotient (R)", 0.5, 1.2, 0.8, step=0.05)

    p_ao2 = alveolar_PO2(alt_m, FiO2, PaCO2, RQ)
    st.write(f"**PAO₂:** {p_ao2:.1f} mmHg")

    st.caption("Alveolar gas equation: PAO₂ = FiO₂·(Pb − PH₂O) − PaCO₂/R.")

# ----------------------------------------------------------------------------
# 3. TUC
# ----------------------------------------------------------------------------
elif calculator == "Time of Useful Consciousness":
    st.subheader("Time of Useful Consciousness (TUC)")
    alt_ft = st.slider("Altitude (ft)", 10_000, 50_000, 25_000, step=1_000)
    tuc_sec = estimate_tuc(alt_ft)

    if tuc_sec == 0:
        st.error("Instantaneous loss of consciousness expected at this altitude without pressure suit.")
    else:
        minutes = tuc_sec / 60
        st.write(f"**Estimated TUC:** {tuc_sec:.0f} s (~{minutes:.1f} min)")

    st.caption("Interpolated from published USAF reference values; individual tolerance varies.")

# ----------------------------------------------------------------------------
# 4. G-FORCE
# ----------------------------------------------------------------------------
elif calculator == "G-Force Tolerance":
    st.subheader("G-Force Tolerance")
    Gz = st.slider("Sustained +Gz (g)", 1.0, 9.0, 6.0, step=0.1)
    tol = g_loc_time(Gz)

    if tol == float("inf"):
        st.success("Below ~5 g most healthy subjects tolerate indefinitely (without anti-G suit).")
    else:
        st.write(f"**Estimated tolerance time:** {tol:.0f} s")

    st.caption("Simplified Stoll curve approximation; assumes seated posture and no countermeasures.")

# ----------------------------------------------------------------------------
# 5. RADIATION DOSE
# ----------------------------------------------------------------------------
else:  # Cosmic Radiation Dose
    st.subheader("Cosmic Radiation Dose at Cruise")
    alt_ft = st.slider("Flight altitude (ft)", 0, 45_000, 35_000, step=1_000)
    polar = st.checkbox("Polar route (>60° latitude)")
    dose = dose_rate(alt_ft, polar)

    st.write(f"**Dose rate:** {dose:.2f} µSv/h")

    st.caption("Highly simplified linear model for educational purposes only; real-world exposure depends on solar activity, latitude, and flight duration.")

st.sidebar.markdown("---")
st.sidebar.write("Developed for educational demonstration of aerospace physiology.")