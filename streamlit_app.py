import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import plotly.graph_objects as go  # type: ignore
import plotly.express as px  # type: ignore
from datetime import datetime
import numpy as np
import io

from calculators import (
    standard_atmosphere,
    alveolar_PO2,
    spo2_unacclimatized,
    spo2_acclimatized,
    pao2_at_altitude,
    ams_probability,
    inspired_PO2,
    oxygen_content,
    tissue_ratio,
    interpret_tr,
    estimate_tuc,
    g_loc_time,
    dose_rate,
    wbgt_indoor,
    wbgt_outdoor,
    heat_stress_index,
    noise_dose_osha,
    noise_dose_niosh,
    permissible_duration,
    calculate_twa_exposure,
    calculate_adjusted_tlv_unusual_schedule,
    assess_exposure_risk,
    calculate_mixed_exposure_index,
    generate_exposure_report,
    calculate_biological_exposure_index,
    mitler_performance,
    homeostatic_waking,
    homeostatic_sleep,
    circadian_component,
    jet_lag_days_to_adjust,
    peak_shivering_intensity,
    AEROSPACE_CHEMICALS
)
from calculators import (
    bmr_mifflin_st_jeor,
    compute_all_bsa,
    egfr_ckd_epi_2009,
    pf_ratio,
    oxygen_index,
    six_minute_walk_distance,
)

try:
    from streamlit_echarts import st_echarts  # type: ignore
    ECHARTS_AVAILABLE = True
except Exception:
    ECHARTS_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Aerospace Physiology & Occupational Health Calculators",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling with light/dark support
st.markdown("""
<style>
    :root {
        --color-primary: #2563eb; /* indigo-600 */
        --color-accent: #7c3aed;  /* violet-600 */
        --color-sky: #0ea5e9;     /* sky-500 */
        --color-success: #22c55e; /* green-500 */
        --color-warning: #f59e0b; /* amber-500 */
        --color-danger: #ef4444;  /* red-500 */
        /* Light theme defaults */
        --color-text: #111827;    /* gray-900 */
        --color-muted: #6b7280;   /* gray-500 */
        --surface: #ffffff;
        --surface-2: #f8fafc;     /* slate-50 */
        --border: #e5e7eb;        /* gray-200 */
    }

    /* Override variables automatically when user prefers dark scheme */
    @media (prefers-color-scheme: dark) {
      :root {
        --color-text: #e5e7eb;    /* slate-200 */
        --color-muted: #9ca3af;   /* gray-400 */
        --surface: #0f172a;       /* slate-900 */
        --surface-2: #111827;     /* gray-900 */
        --border: #334155;        /* slate-600 */
      }
    }

    .main-header {
        font-size: 2.6rem;
        font-weight: 800;
        color: var(--color-text);
        text-align: center;
        margin-bottom: 2rem;
        padding: 1.2rem;
        background: linear-gradient(135deg, rgba(14,165,233,0.12), rgba(99,102,241,0.12));
        border-radius: 14px;
        border: 1px solid var(--border);
    }

    .section-header {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--color-text);
        margin: 1.2rem 0 0.8rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border);
    }

    .info-box, .warning-box, .danger-box, .success-box {
        padding: 1rem 1.2rem;
        border-radius: 12px;
        border: 1px solid var(--border);
        background: var(--surface);
        color: var(--color-text);          /* ensure readable text in both themes */
        box-shadow: 0 5px 18px rgba(2,6,23,0.06);
    }

    .info-box { border-left: 5px solid var(--color-sky); }
    .warning-box { border-left: 5px solid var(--color-warning); }
    .danger-box { border-left: 5px solid var(--color-danger); }
    .success-box { border-left: 5px solid var(--color-success); }

    .metric-card {
        background: var(--surface);
        padding: 1.2rem 1.3rem;
        border-radius: 12px;
        border: 1px solid var(--border);
        box-shadow: 0 5px 18px rgba(2,6,23,0.06);
        margin: 0.5rem 0;
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--color-sky), var(--color-accent));
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 1.1rem;
        font-weight: 700;
        letter-spacing: 0.2px;
        transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease;
        box-shadow: 0 8px 20px rgba(99,102,241,0.25);
    }

    .stButton > button:hover { transform: translateY(-1px); filter: brightness(1.02); }

    .stSelectbox label, .stSlider label, .stRadio label, .stNumberInput label {
        font-weight: 600; color: var(--color-text);
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header">🚀 Aerospace Physiology & Occupational Health Calculators</div>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("## 📋 Navigation")
calculator_category = st.sidebar.selectbox(
    "Select Calculator Category",
    [
        "🏠 Home",
        "🌍 Atmospheric & Physiological",
        "🩺 Clinical Calculators",
        "Occupational Health & Safety",
        "🔬 Environmental Monitoring",
        "🧠 Fatigue & Circadian",
        "📈 Visualization Studio",
        "📊 Risk Assessment Tools"
    ]
)

# Disclaimer
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="info-box">
<strong>Important Disclaimer</strong><br>
These calculators are for educational and research purposes only. 
Do not use for operational decision-making without professional validation.
</div>
""", unsafe_allow_html=True)

if calculator_category == "🏠 Home":
    # Home page with overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="section-header">Welcome to Professional Aerospace Calculators</div>', unsafe_allow_html=True)
        
        st.markdown("""
        This comprehensive suite of calculators provides accurate, scientifically-based tools for:
        
        **🌍 Atmospheric & Physiological Calculations:**
        - International Standard Atmosphere (ISA) properties
        - Alveolar oxygen pressure calculations
        - Time of Useful Consciousness (TUC) estimation
        - G-force tolerance assessment
        - Cosmic radiation dose calculations
        
        **Occupational Health & Safety:**
        - ACGIH TLV/BEI exposure assessments
        - Time-weighted average calculations
        - Mixed chemical exposure indices
        - Aerospace-specific chemical hazard evaluation
        - Biological exposure monitoring
        
        **🔬 Environmental Monitoring:**
        - Heat stress indices (WBGT)
        - Noise exposure assessment
        - Air quality monitoring
        
        **📊 Risk Assessment Tools:**
        - Comprehensive exposure reports
        - Risk stratification
        - Regulatory compliance checking
        """)
        
        st.markdown('<div class="info-box"><strong>New Features:</strong><br>• Aerospace industry-specific occupational health calculations<br>• ACGIH TLV and BEI standards integration<br>• Professional reporting capabilities<br>• Enhanced risk assessment tools</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-header">Quick Stats</div>', unsafe_allow_html=True)
        
        st.metric("Available Calculators", "25+", "5 new")
        st.metric("Chemical Database", f"{len(AEROSPACE_CHEMICALS)}", "aerospace-specific")
        st.metric("Standards Compliance", "ACGIH 2024", "latest")
        
        st.markdown("### 🎯 Featured Calculator")
        if st.button("🧪 Aerospace Chemical Exposure Assessment", type="primary"):
            st.sidebar.selectbox("Select Calculator Category", ["Occupational Health & Safety"], key="nav_override")

elif calculator_category == "🌍 Atmospheric & Physiological":
    st.markdown('<div class="section-header">Atmospheric & Physiological Calculators</div>', unsafe_allow_html=True)
    
    calc_type = st.selectbox(
        "Choose Calculator",
        [
            "Standard Atmosphere Properties",
            "Alveolar Oxygen Pressure", 
            "Altitude & Hypoxia Predictions",
            "Acute Mountain Sickness Risk",
            "Oxygen Cascade",
            "Decompression Tissue Ratio (TR)",
            "Time of Useful Consciousness",
            "G-Force Tolerance",
            "Cosmic Radiation Dose"
        ]
    )
    
    if calc_type == "Standard Atmosphere Properties":
        st.markdown("### 🌍 International Standard Atmosphere (ISA)")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            alt_ft = st.slider("Altitude (ft)", 0, 60_000, 0, step=1_000)
            alt_m = alt_ft * 0.3048
            
        result = standard_atmosphere(alt_m)
        
        with col2:
            st.markdown("#### Results")
            st.metric("Temperature", f"{result['temperature_C']:.2f} °C", f"{result['temperature_C']*9/5 + 32:.1f} °F")
            st.metric("Pressure", f"{result['pressure_Pa']/100:.2f} hPa", f"{result['pressure_Pa']/3386.39:.2f} inHg")
            st.metric("Density", f"{result['density_kg_m3']:.4f} kg/m³")
            st.metric("O₂ Partial Pressure", f"{result['pO2_Pa']/100:.2f} hPa")
        
        # Create visualization
        altitudes = np.linspace(0, 20000, 100)
        temps = [standard_atmosphere(alt)['temperature_C'] for alt in altitudes]
        pressures = [standard_atmosphere(alt)['pressure_Pa']/100 for alt in altitudes]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=temps, y=altitudes/1000, mode='lines', name='Temperature', line=dict(color='red')))
        fig.update_layout(
            title="ISA Temperature Profile",
            xaxis_title="Temperature (°C)",
            yaxis_title="Altitude (km)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('<div class="info-box">Calculations up to 11 km assume a linear temperature lapse rate; 11–20 km is treated as isothermal, and 20–32 km uses a warming layer per ISA.</div>', unsafe_allow_html=True)
    
    elif calc_type == "Alveolar Oxygen Pressure":
        st.markdown("### 🫁 Alveolar Oxygen Pressure (PAO₂)")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            alt_ft = st.slider("Altitude (ft)", 0, 40_000, 0, step=1_000)
            alt_m = alt_ft * 0.3048
            FiO2 = st.number_input("Inspired O₂ fraction (FiO₂)", 0.0, 1.0, 0.21, step=0.01)
            PaCO2 = st.number_input("Arterial CO₂ (PaCO₂) [mmHg]", 20.0, 60.0, 40.0, step=1.0)
            RQ = st.number_input("Respiratory Quotient (R)", 0.5, 1.2, 0.8, step=0.05)
        
        p_ao2 = alveolar_PO2(alt_m, FiO2, PaCO2, RQ)
        
        with col2:
            st.markdown("#### Results")
            st.metric("PAO₂", f"{p_ao2:.1f} mmHg")
            
            # Risk assessment
            if p_ao2 < 60:
                st.markdown('<div class="info-box"><strong>Assessment:</strong> PAO₂ in low range</div>', unsafe_allow_html=True)
            elif p_ao2 < 80:
                st.markdown('<div class="info-box"><strong>Assessment:</strong> PAO₂ in borderline range</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box"><strong>Assessment:</strong> PAO₂ within typical range</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-box"><strong>Formula:</strong> PAO₂ = FiO₂·(Pb − PH₂O) − PaCO₂/R</div>', unsafe_allow_html=True)
    
    elif calc_type == "Time of Useful Consciousness":
        st.markdown("### ⏱️ Time of Useful Consciousness (TUC)")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            alt_ft = st.slider("Altitude (ft)", 10_000, 50_000, 25_000, step=1_000)
        
        tuc_sec = estimate_tuc(alt_ft)
        
        with col2:
            st.markdown("#### Results")
            if tuc_sec == 0:
                st.markdown('<div class="info-box"><strong>Note:</strong> Estimated TUC is 0 seconds at this altitude.</div>', unsafe_allow_html=True)
            else:
                minutes = tuc_sec / 60
                st.metric("Estimated TUC", f"{tuc_sec:.0f} seconds", f"~{minutes:.1f} minutes")
                
                if minutes < 1:
                    st.markdown('<div class="info-box"><strong>Note:</strong> Estimated TUC less than 1 minute</div>', unsafe_allow_html=True)
                elif minutes < 5:
                    st.markdown('<div class="info-box"><strong>Note:</strong> Very limited time available</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="info-box"><strong>Note:</strong> Sufficient time for emergency procedures (estimate)</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-box">Interpolated from published USAF reference values; individual tolerance varies significantly.</div>', unsafe_allow_html=True)
    
    elif calc_type == "G-Force Tolerance":
        st.markdown("### 🎯 G-Force Tolerance")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            Gz = st.slider("Sustained +Gz (g)", 1.0, 9.0, 6.0, step=0.1)
        
        tol = g_loc_time(Gz)
        
        with col2:
            st.markdown("#### Results")
            if tol == float("inf"):
                st.markdown('<div class="info-box"><strong>Note:</strong> Below ~5g, many subjects tolerate indefinitely (literature)</div>', unsafe_allow_html=True)
            else:
                st.metric("Estimated Tolerance Time", f"{tol:.0f} seconds")
                
                if tol < 15:
                    st.markdown('<div class="info-box"><strong>Note:</strong> Very short estimated tolerance time</div>', unsafe_allow_html=True)
                elif tol < 60:
                    st.markdown('<div class="info-box"><strong>Note:</strong> Limited estimated tolerance time</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="info-box"><strong>Note:</strong> Reasonable estimated tolerance time</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-box">Simplified Stoll curve approximation; assumes seated posture and no countermeasures.</div>', unsafe_allow_html=True)
    
    elif calc_type == "Cosmic Radiation Dose":
        st.markdown("### ☢️ Cosmic Radiation Dose at Cruise")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            alt_ft = st.slider("Flight altitude (ft)", 0, 45_000, 35_000, step=1_000)
            polar = st.checkbox("Polar route (>60° latitude)")
        
        dose = dose_rate(alt_ft, polar)
        
        with col2:
            st.markdown("#### Results")
            st.metric("Dose Rate", f"{dose:.2f} µSv/h")
            
            # Annual dose estimation
            annual_hours = st.number_input("Flight hours per year", 0, 1000, 500, step=50)
            annual_dose = dose * annual_hours
            st.metric("Estimated Annual Dose", f"{annual_dose:.1f} µSv/year")
            
            # Risk assessment
            if annual_dose > 1000:  # 1 mSv/year for public
                st.markdown('<div class="info-box"><strong>Assessment:</strong> Above public dose guideline</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box"><strong>Assessment:</strong> Within public dose guideline</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-box">Highly simplified linear model for educational purposes only; real-world exposure depends on solar activity, latitude, and flight duration.</div>', unsafe_allow_html=True)

    elif calc_type == "Altitude & Hypoxia Predictions":
        st.markdown("### 🏔️ Altitude & Hypoxia Predictions")
        col1, col2 = st.columns([1, 1])
        with col1:
            alt_ft = st.slider("Altitude (ft)", 0, 30000, 10000, step=1000)
            alt_m = alt_ft * 0.3048
            accl = st.radio("Acclimatization", ["Unacclimatized", "Acclimatized"], horizontal=True)
            spo2_u = spo2_unacclimatized(alt_m)
            spo2_a = spo2_acclimatized(alt_m)
        with col2:
            st.markdown("#### Oxygen Saturation")
            st.metric("SpO₂ (unacclimatized)", f"{spo2_u:.1f} %")
            st.metric("SpO₂ (acclimatized)", f"{spo2_a:.1f} %")
        # Mini-plot
        alts = np.linspace(0, 6000, 120)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=alts, y=[spo2_unacclimatized(a) for a in alts], name="Unacclimatized"))
        fig.add_trace(go.Scatter(x=alts, y=[spo2_acclimatized(a) for a in alts], name="Acclimatized"))
        fig.update_layout(title="SpO₂ vs Altitude", xaxis_title="Altitude (m)", yaxis_title="SpO₂ (%)", height=360)
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Arterial Oxygen at Altitude (PaO₂) Estimator", expanded=False):
            colp1, colp2, colp3 = st.columns(3)
            with colp1:
                pa02_ground = st.number_input("PaO₂ at ground (mmHg)", 40.0, 120.0, 90.0, step=1.0)
            with colp2:
                fev1_pct = st.number_input("FEV₁ (%)", 20.0, 120.0, 100.0, step=1.0)
            with colp3:
                st.write("")
                st.write("")
                pa02_alt = pao2_at_altitude(pa02_ground, fev1_pct)
                st.metric("Predicted PaO₂ at altitude", f"{pa02_alt:.1f} mmHg")

    elif calc_type == "Acute Mountain Sickness Risk":
        st.markdown("### 🩺 Acute Mountain Sickness (AMS) Risk")
        col1, col2 = st.columns([1, 1])
        with col1:
            aae = st.number_input("Accumulated Altitude Exposure (km·days)", min_value=0.0, value=1.0, step=0.1)
        prob = ams_probability(aae)
        with col2:
            st.markdown("#### Results")
            st.metric("AMS Probability", f"{prob*100:.1f} %")
            if prob < 0.2:
                st.markdown('<div class="info-box"><strong>Risk:</strong> Low</div>', unsafe_allow_html=True)
            elif prob < 0.5:
                st.markdown('<div class="info-box"><strong>Risk:</strong> Moderate</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box"><strong>Risk:</strong> Elevated</div>', unsafe_allow_html=True)
        # Simple curve
        aae_vals = np.linspace(0, 6, 120)
        probs = [ams_probability(x) for x in aae_vals]
        fig = go.Figure(data=[go.Scatter(x=aae_vals, y=[p*100 for p in probs], mode="lines")])
        fig.update_layout(title="AMS Probability vs AAE", xaxis_title="AAE (km·days)", yaxis_title="Probability (%)", height=360)
        st.plotly_chart(fig, use_container_width=True)

    elif calc_type == "Oxygen Cascade":
        st.markdown("### 🧪 Oxygen Cascade")
        col1, col2 = st.columns([1, 1])
        with col1:
            alt_ft = st.slider("Altitude (ft)", 0, 30000, 0, step=1000)
            alt_m = alt_ft * 0.3048
            fio2 = st.number_input("FiO₂", 0.0, 1.0, 0.21, step=0.01)
            paco2 = st.number_input("PaCO₂ (mmHg)", 20.0, 60.0, 40.0, step=1.0)
            rq = st.number_input("Respiratory Quotient (R)", 0.5, 1.2, 0.8, step=0.05)
            hb = st.number_input("Hemoglobin (g/dL)", 5.0, 20.0, 15.0, step=0.1)
            aagrad = st.number_input("A–a gradient (mmHg)", 0.0, 30.0, 5.0, step=1.0)
        with col2:
            pio2 = inspired_PO2(alt_m, fio2)
            pao2 = alveolar_PO2(alt_m, fio2, paco2, rq)
            pao2_art = max(0.0, pao2 - aagrad)
            # Estimate SaO2 via Hill (same as AltitudeCalculator)
            def estimate_sao2(pao2_mmHg: float, P50: float = 26.8, n: float = 2.7) -> float:
                if pao2_mmHg <= 0:
                    return 0.0
                ratio = (pao2_mmHg ** n) / (pao2_mmHg ** n + P50 ** n)
                return max(0.0, min(100.0, 100.0 * ratio))
            sao2_pct = estimate_sao2(pao2_art)
            cao2 = oxygen_content(hb, sao2_pct, pao2_art)
            st.markdown("#### Results")
            st.metric("PiO₂", f"{pio2:.1f} mmHg")
            st.metric("PAO₂", f"{pao2:.1f} mmHg")
            st.metric("PaO₂ (est)", f"{pao2_art:.1f} mmHg")
            st.metric("SaO₂ (est)", f"{sao2_pct:.0f} %")
            st.metric("CaO₂", f"{cao2:.2f} mL/dL")
        # Quick viz CaO2 vs altitude
        alts = np.linspace(0, 10000, 120)
        pao2s = [alveolar_PO2(a, fio2, paco2, rq) - aagrad for a in alts]
        sao2s = [estimate_sao2(p) for p in pao2s]
        cao2s = [oxygen_content(hb, s, max(0.0, p)) for s, p in zip(sao2s, pao2s)]
        fig = go.Figure(data=[go.Scatter(x=alts/0.3048, y=cao2s, mode="lines", name="CaO₂")])
        fig.update_layout(title="CaO₂ vs Altitude", xaxis_title="Altitude (ft)", yaxis_title="CaO₂ (mL/dL)", height=360)
        st.plotly_chart(fig, use_container_width=True)

    elif calc_type == "Decompression Tissue Ratio (TR)":
        st.markdown("### 🫧 Decompression Tissue Ratio (TR)")
        col1, col2 = st.columns([1, 1])
        with col1:
            alt_ft = st.slider("Altitude (ft)", 0, 40000, 0, step=1000)
            alt_m = alt_ft * 0.3048
            p_amb = standard_atmosphere(alt_m)["pressure_Pa"] / 133.322
            # Assume tissues saturated at sea-level N2 by default
            default_ptissue = 0.78 * (101325 / 133.322)
            ptissue = st.number_input("Tissue N₂ partial pressure (mmHg)", 0.0, 800.0, float(default_ptissue), step=1.0)
        with col2:
            tr = tissue_ratio(ptissue, p_amb)
            st.markdown("#### Results")
            st.metric("Ambient Pressure", f"{p_amb:.1f} mmHg")
            st.metric("TR", f"{tr:.2f}")
            st.markdown(f"<div class='info-box'><strong>Assessment:</strong> {interpret_tr(tr)}</div>", unsafe_allow_html=True)
        # Viz: TR vs altitude
        alts_ft = np.linspace(0, 40000, 160)
        p_ambs = [standard_atmosphere(a*0.3048)["pressure_Pa"]/133.322 for a in alts_ft]
        trs = [tissue_ratio(ptissue, p) for p in p_ambs]
        fig = go.Figure(data=[go.Scatter(x=alts_ft, y=trs, mode="lines")])
        fig.update_layout(title="TR vs Altitude (fixed tissue N₂)", xaxis_title="Altitude (ft)", yaxis_title="TR", height=360)
        st.plotly_chart(fig, use_container_width=True)

elif calculator_category == "🩺 Clinical Calculators":
    st.markdown('<div class="section-header">Clinical Calculators</div>', unsafe_allow_html=True)
    use_echarts = st.toggle("Use ECharts for plots", value=ECHARTS_AVAILABLE, help="Enhance plots with ECharts if available")

    tool = st.selectbox(
        "Choose Tool",
        [
            "Basal Metabolic Rate (Mifflin–St Jeor)",
            "Body Surface Area (4 formulas)",
            "eGFR (CKD‑EPI 2009)",
            "PaO₂/FiO₂ Ratio (P/F)",
            "Oxygen Index (OI)",
            "6‑Minute Walk Distance"
        ]
    )

    if tool == "Basal Metabolic Rate (Mifflin–St Jeor)":
        col1, col2 = st.columns([1,1])
        with col1:
            sex = st.radio("Sex", ["Male", "Female"], horizontal=True)
            weight = st.slider("Weight (kg)", 30.0, 200.0, 75.0, step=0.5)
            height = st.slider("Height (cm)", 140.0, 210.0, 175.0, step=0.5)
            age = st.slider("Age (yr)", 15, 90, 35)
        bmr = bmr_mifflin_st_jeor(weight, height, age, sex)
        with col2:
            st.metric("BMR", f"{bmr:.0f} kcal/day")
        vary = st.radio("Vary parameter", ["Weight", "Age", "Height"], horizontal=True)
        if vary == "Weight":
            xs = np.linspace(max(30.0, weight-20), min(200.0, weight+20), 60)
            ys = [bmr_mifflin_st_jeor(x, height, age, sex) for x in xs]
            xlab = "Weight (kg)"
        elif vary == "Age":
            xs = np.linspace(15, 90, 60)
            ys = [bmr_mifflin_st_jeor(weight, height, x, sex) for x in xs]
            xlab = "Age (yr)"
        else:
            xs = np.linspace(140, 210, 60)
            ys = [bmr_mifflin_st_jeor(weight, x, age, sex) for x in xs]
            xlab = "Height (cm)"
        if use_echarts:
            opts = {
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "value", "name": xlab},
                "yAxis": {"type": "value", "name": "BMR (kcal/day)"},
                "series": [{"type": "line", "smooth": True, "data": [[float(x), float(y)] for x,y in zip(xs, ys)], "areaStyle": {}}],
            }
            st_echarts(opts, height=420)
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines', fill='tozeroy', name='BMR'))
            fig.update_layout(title=f"BMR vs {vary}", xaxis_title=xlab, yaxis_title="BMR (kcal/day)")
            st.plotly_chart(fig, use_container_width=True)

    elif tool == "Body Surface Area (4 formulas)":
        col1, col2 = st.columns([1,1])
        with col1:
            weight = st.slider("Weight (kg)", 10.0, 200.0, 70.0, step=0.5)
            height = st.slider("Height (cm)", 50.0, 210.0, 170.0, step=0.5)
        values = compute_all_bsa(height, weight)
        with col2:
            st.metric("Mosteller", f"{values['Mosteller']:.3f} m²")
            st.metric("DuBois", f"{values['DuBois']:.3f} m²")
            st.metric("Haycock", f"{values['Haycock']:.3f} m²")
            st.metric("Boyd", f"{values['Boyd']:.3f} m²")
        if use_echarts:
            opts = {
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": list(values.keys())},
                "yAxis": {"type": "value", "name": "BSA (m²)"},
                "series": [{"type": "bar", "data": [float(v) for v in values.values()], "itemStyle": {"borderRadius": [6,6,0,0]}}],
            }
            st_echarts(opts, height=360)
        else:
            fig = px.bar(x=list(values.keys()), y=list(values.values()), labels={"x": "Formula", "y": "BSA (m²)"})
            st.plotly_chart(fig, use_container_width=True)

    elif tool == "eGFR (CKD‑EPI 2009)":
        col1, col2 = st.columns([1,1])
        with col1:
            sex = st.radio("Sex", ["Male", "Female"], horizontal=True)
            age = st.slider("Age (yr)", 18, 90, 50)
            scr = st.number_input("Serum Creatinine (mg/dL)", 0.1, 20.0, 1.0, step=0.1)
            race_black = st.checkbox("Apply race factor (Black)", value=False)
        res = egfr_ckd_epi_2009(scr, age, sex, is_black=race_black)
        with col2:
            st.metric("eGFR", f"{res.value_ml_min_1_73m2:.0f} mL/min/1.73m²")
        scrs = np.linspace(0.4, 5.0, 100)
        y = [egfr_ckd_epi_2009(v, age, sex, race_black).value_ml_min_1_73m2 for v in scrs]
        if use_echarts:
            opts = {
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "value", "name": "Scr (mg/dL)"},
                "yAxis": {"type": "value", "name": "eGFR (mL/min/1.73m²)"},
                "series": [{"type": "line", "smooth": True, "data": [[float(a), float(b)] for a,b in zip(scrs, y)]}],
                "markLine": {"data": [{"xAxis": float(scr), "label": {"formatter": "Current Scr"}}]},
            }
            st_echarts(opts, height=420)
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=scrs, y=y, mode='lines', name='eGFR'))
            fig.add_vline(x=float(scr), line_dash='dash', line_color='red')
            fig.update_layout(title="eGFR vs Creatinine", xaxis_title="Scr (mg/dL)", yaxis_title="eGFR (mL/min/1.73m²)")
            st.plotly_chart(fig, use_container_width=True)

    elif tool == "PaO₂/FiO₂ Ratio (P/F)":
        col1, col2 = st.columns([1,1])
        with col1:
            pao2 = st.number_input("PaO₂ (mmHg)", 30.0, 600.0, 90.0, step=1.0)
            fio2 = st.slider("FiO₂", 0.21, 1.0, 0.21, step=0.01)
        ratio = pf_ratio(pao2, fio2)
        with col2:
            st.metric("P/F Ratio", f"{ratio:.0f}")
        if use_echarts:
            opts = {
                "tooltip": {"show": True},
                "xAxis": {"type": "category", "data": ["Ratio"]},
                "yAxis": {"type": "value", "name": "mmHg"},
                "series": [{"type": "bar", "data": [float(ratio)], "itemStyle": {"color": "#0ea5e9", "borderRadius": [6,6,0,0]}}],
                "markLine": {"data": [
                    {"yAxis": 300, "lineStyle": {"type": "dashed"}},
                    {"yAxis": 200, "lineStyle": {"type": "dashed"}},
                    {"yAxis": 100, "lineStyle": {"type": "dashed"}},
                ]}
            }
            st_echarts(opts, height=320)
        else:
            fig = px.bar(x=["Ratio"], y=[ratio], labels={"x": "", "y": "mmHg"})
            fig.add_hline(y=300, line_dash="dash")
            fig.add_hline(y=200, line_dash="dash")
            fig.add_hline(y=100, line_dash="dash")
            st.plotly_chart(fig, use_container_width=True)

    elif tool == "Oxygen Index (OI)":
        col1, col2 = st.columns([1,1])
        with col1:
            pao2 = st.number_input("PaO₂ (mmHg)", 30.0, 600.0, 90.0, step=1.0)
            fio2 = st.slider("FiO₂", 0.21, 1.0, 0.5, step=0.01)
            map_cm = st.slider("Mean Airway Pressure (cmH₂O)", 0.0, 40.0, 12.0, step=0.5)
        oi = oxygen_index(pao2, fio2, map_cm)
        with col2:
            st.metric("Oxygen Index", f"{oi:.1f}")
        if use_echarts:
            opts = {
                "series": [{
                    "type": "gauge",
                    "min": 0, "max": 40,
                    "axisLine": {"lineStyle": {"width": 10}},
                    "detail": {"formatter": "{value}"},
                    "data": [{"value": float(oi), "name": "OI"}]
                }]
            }
            st_echarts(opts, height=300)
        else:
            fig = go.Figure(go.Indicator(mode="gauge+number", value=oi, gauge={'axis': {'range': [0, 40]}}))
            st.plotly_chart(fig, use_container_width=True)

    elif tool == "6‑Minute Walk Distance":
        col1, col2 = st.columns([1,1])
        with col1:
            sex = st.radio("Sex", ["Male", "Female"], horizontal=True)
            height = st.slider("Height (cm)", 140.0, 200.0, 170.0, step=0.5)
            weight = st.slider("Weight (kg)", 35.0, 160.0, 70.0, step=0.5)
            age = st.slider("Age (yr)", 20, 90, 50)
        res = six_minute_walk_distance(height, weight, age, sex)
        with col2:
            st.metric("Predicted 6MWD", f"{res.predicted_m:.0f} m")
            st.metric("LLN", f"{res.lower_limit_normal_m:.0f} m")
        ages = np.linspace(20, 90, 70)
        curve = [six_minute_walk_distance(height, weight, a, sex).predicted_m for a in ages]
        if use_echarts:
            opts = {
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "value", "name": "Age (yr)"},
                "yAxis": {"type": "value", "name": "6MWD (m)"},
                "series": [{"type": "line", "smooth": True, "data": [[float(a), float(b)] for a,b in zip(ages, curve)], "areaStyle": {}}],
                "markLine": {"data": [{"xAxis": float(age), "label": {"formatter": "Age"}}]},
            }
            st_echarts(opts, height=420)
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ages, y=curve, mode='lines', fill='tozeroy'))
            fig.update_layout(title="6MWD vs Age", xaxis_title="Age (yr)", yaxis_title="6MWD (m)")
            st.plotly_chart(fig, use_container_width=True)


elif calculator_category == "Occupational Health & Safety":
    st.markdown('<div class="section-header">Occupational Health & Safety Calculators</div>', unsafe_allow_html=True)
    
    calc_type = st.selectbox(
        "Choose Calculator",
        [
            "Chemical Exposure Assessment",
            "Time-Weighted Average Calculator",
            "Mixed Chemical Exposure",
            "Unusual Work Schedule TLV",
            "Biological Exposure Index",
            "Comprehensive Exposure Report"
        ]
    )
    
    if calc_type == "Chemical Exposure Assessment":
        st.markdown("### 🧪 Aerospace Chemical Exposure Assessment")
        st.markdown("*Based on ACGIH TLV/BEI Standards (2024)*")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            chemical = st.selectbox(
                "Select Chemical",
                list(AEROSPACE_CHEMICALS.keys()),
                format_func=lambda x: AEROSPACE_CHEMICALS[x].name
            )
            
            concentration = st.number_input(
                f"Measured Concentration ({AEROSPACE_CHEMICALS[chemical].units})",
                min_value=0.0,
                value=0.0,
                step=0.001,
                format="%.4f"
            )
            
            duration = st.number_input(
                "Exposure Duration (hours)",
                min_value=0.1,
                max_value=8.0,
                value=8.0,
                step=0.1
            )
        
        if concentration > 0:
            assessment = assess_exposure_risk(chemical, concentration, duration)
            
            with col2:
                st.markdown("#### Assessment Results")
                
                # Risk level with color coding
                st.markdown(f'<div class="info-box"><strong>Risk Level:</strong> {assessment["risk_level"]}</div>', unsafe_allow_html=True)
                
                st.metric("TLV Ratio", f"{assessment['tlv_ratio']:.2f}", "Should be ≤ 1.0")
                st.metric("8-hr TWA Exposure", f"{assessment['twa_exposure']:.4f} {assessment['units']}")
                st.metric("TLV-TWA", f"{assessment['tlv_twa']:.4f} {assessment['units']}")
                
                # Additional information (neutral tone)
                if assessment['carcinogen']:
                    st.markdown('<div class="info-box"><strong>Note:</strong> Carcinogen classification applies</div>', unsafe_allow_html=True)
                if assessment['skin_notation']:
                    st.markdown('<div class="info-box"><strong>Note:</strong> Skin notation present (avoid dermal contact)</div>', unsafe_allow_html=True)
                if assessment['stel_exceeded']:
                    st.markdown('<div class="info-box"><strong>Note:</strong> STEL exceeded</div>', unsafe_allow_html=True)
            
            # Detailed information
            st.markdown("#### Detailed Information")
            col3, col4 = st.columns([1, 1])
            
            with col3:
                st.markdown(f"**Chemical:** {assessment['chemical']}")
                st.markdown(f"**CAS Number:** {assessment['cas_number']}")
                st.markdown(f"**Critical Effects:** {assessment['critical_effects']}")
            
            with col4:
                st.markdown(f"**Recommendation:** {assessment['recommendation']}")
                
                # Permissible exposure time
                max_time = (AEROSPACE_CHEMICALS[chemical].tlv_twa * 8.0) / concentration if concentration > 0 else 8.0
                max_time = min(max_time, 8.0)
                st.markdown(f"**Max Permissible Time:** {max_time:.1f} hours")
    
    elif calc_type == "Time-Weighted Average Calculator":
        st.markdown("### ⏱️ Time-Weighted Average Calculator")
        
        st.markdown("Calculate 8-hour TWA exposure from multiple exposure periods:")
        
        # Dynamic input for multiple exposures
        num_periods = st.number_input("Number of exposure periods", min_value=1, max_value=10, value=3)
        
        concentrations = []
        durations = []
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**Concentrations (ppm or mg/m³)**")
            for i in range(num_periods):
                conc = st.number_input(f"Period {i+1}", min_value=0.0, value=0.0, step=0.001, key=f"conc_{i}")
                concentrations.append(conc)
        
        with col2:
            st.markdown("**Durations (hours)**")
            for i in range(num_periods):
                dur = st.number_input(f"Period {i+1}", min_value=0.0, max_value=8.0, value=0.0, step=0.1, key=f"dur_{i}")
                durations.append(dur)
        
        if sum(durations) > 0 and sum(durations) <= 8.0:
            try:
                twa = calculate_twa_exposure(concentrations, durations)
                
                st.markdown("#### Results")
                st.metric("8-hour TWA Exposure", f"{twa:.4f}")
                st.metric("Total Exposure Time", f"{sum(durations):.1f} hours")
                
                # Create visualization
                periods = [f"Period {i+1}" for i in range(num_periods)]
                fig = go.Figure(data=[
                    go.Bar(x=periods, y=concentrations, name="Concentration"),
                ])
                fig.update_layout(title="Exposure Concentrations by Period", yaxis_title="Concentration")
                st.plotly_chart(fig, use_container_width=True)
                
            except ValueError as e:
                st.error(f"Error: {e}")
        elif sum(durations) > 8.0:
            st.error("Total exposure time cannot exceed 8 hours")
    
    elif calc_type == "Mixed Chemical Exposure":
        st.markdown("### 🧪 Mixed Chemical Exposure Assessment")
        
        st.markdown("Assess exposure to multiple chemicals with similar health effects:")
        
        selected_chemicals = st.multiselect(
            "Select Chemicals",
            list(AEROSPACE_CHEMICALS.keys()),
            format_func=lambda x: AEROSPACE_CHEMICALS[x].name
        )
        
        if selected_chemicals:
            exposures = {}
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**Enter Exposure Concentrations:**")
                for chem in selected_chemicals:
                    chem_data = AEROSPACE_CHEMICALS[chem]
                    exposure = st.number_input(
                        f"{chem_data.name} ({chem_data.units})",
                        min_value=0.0,
                        value=0.0,
                        step=0.001,
                        key=f"mixed_{chem}"
                    )
                    exposures[chem] = exposure
            
            mixed_index = calculate_mixed_exposure_index(exposures, selected_chemicals)
            
            with col2:
                st.markdown("#### Results")
                st.metric("Mixed Exposure Index", f"{mixed_index:.3f}", "Should be ≤ 1.0")
                
                if mixed_index <= 1.0:
                    st.markdown('<div class="info-box"><strong>Assessment:</strong> Mixed exposure within guideline</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="info-box"><strong>Assessment:</strong> Mixed exposure exceeds guideline</div>', unsafe_allow_html=True)
                
                # Individual contributions
                st.markdown("**Individual Contributions:**")
                for chem in selected_chemicals:
                    if exposures[chem] > 0:
                        contribution = exposures[chem] / AEROSPACE_CHEMICALS[chem].tlv_twa
                        st.write(f"• {AEROSPACE_CHEMICALS[chem].name}: {contribution:.3f}")
    
    elif calc_type == "Unusual Work Schedule TLV":
        st.markdown("### 📅 Adjusted TLV for Unusual Work Schedules")
        st.markdown("*Using Brief & Scala Model*")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            chemical = st.selectbox(
                "Select Chemical",
                list(AEROSPACE_CHEMICALS.keys()),
                format_func=lambda x: AEROSPACE_CHEMICALS[x].name,
                key="schedule_chem"
            )
            
            hours_per_day = st.number_input("Hours per day", min_value=1.0, max_value=24.0, value=12.0, step=0.5)
            days_per_week = st.number_input("Days per week", min_value=1.0, max_value=7.0, value=4.0, step=0.5)
            weeks_per_year = st.number_input("Weeks per year", min_value=1, max_value=52, value=50)
        
        standard_tlv = AEROSPACE_CHEMICALS[chemical].tlv_twa
        adjusted_tlv = calculate_adjusted_tlv_unusual_schedule(
            standard_tlv, hours_per_day, days_per_week, weeks_per_year
        )
        
        with col2:
            st.markdown("#### Results")
            st.metric("Standard TLV-TWA", f"{standard_tlv:.4f} {AEROSPACE_CHEMICALS[chemical].units}")
            st.metric("Adjusted TLV-TWA", f"{adjusted_tlv:.4f} {AEROSPACE_CHEMICALS[chemical].units}")
            
            adjustment_factor = adjusted_tlv / standard_tlv
            st.metric("Adjustment Factor", f"{adjustment_factor:.3f}")
            
            if adjustment_factor < 1.0:
                st.markdown('<div class="info-box"><strong>Adjusted TLV:</strong> More restrictive than standard</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box"><strong>Adjusted TLV:</strong> Less restrictive than standard</div>', unsafe_allow_html=True)
    
    elif calc_type == "Biological Exposure Index":
        st.markdown("### 🩸 Biological Exposure Index (BEI) Assessment")
        
        # Filter chemicals that have BEI values
        bei_chemicals = {k: v for k, v in AEROSPACE_CHEMICALS.items() if v.bei_value is not None}
        
        if not bei_chemicals:
            st.warning("No BEI values available for chemicals in current database.")
        else:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                chemical = st.selectbox(
                    "Select Chemical with BEI",
                    list(bei_chemicals.keys()),
                    format_func=lambda x: bei_chemicals[x].name
                )
                
                biomarker_conc = st.number_input(
                    f"Biomarker Concentration ({bei_chemicals[chemical].bei_units})",
                    min_value=0.0,
                    value=0.0,
                    step=0.001
                )
                
                sample_timing = st.selectbox(
                    "Sample Timing",
                    ["end_of_shift", "end_of_workweek", "pre_shift", "during_shift"]
                )
            
            if biomarker_conc > 0:
                bei_assessment = calculate_biological_exposure_index(chemical, biomarker_conc, sample_timing)
                
                with col2:
                    st.markdown("#### BEI Assessment Results")
                    
                    if bei_assessment['bei_available']:
                        st.metric("BEI Ratio", f"{bei_assessment['bei_ratio']:.2f}", "Should be ≤ 1.0")
                        st.metric("BEI Value", f"{bei_assessment['bei_value']} {bei_assessment['bei_units']}")
                        
                        if bei_assessment['bei_ratio'] <= 1.0:
                            st.markdown('<div class="info-box"><strong>Assessment:</strong> BEI not exceeded</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="info-box"><strong>Assessment:</strong> BEI exceeded</div>', unsafe_allow_html=True)
                        
                        st.markdown(f"**Recommended Action:** {bei_assessment['recommended_action']}")
                    else:
                        st.info(bei_assessment['message'])
    
    elif calc_type == "Comprehensive Exposure Report":
        st.markdown("### 📊 Comprehensive Exposure Assessment Report")
        
        facility_name = st.text_input("Facility Name", "Aerospace Manufacturing Facility")
        assessment_date = st.date_input("Assessment Date", datetime.now().date())
        
        st.markdown("#### Enter Chemical Exposures:")
        
        exposures = {}
        selected_chems = st.multiselect(
            "Select Chemicals for Assessment",
            list(AEROSPACE_CHEMICALS.keys()),
            format_func=lambda x: AEROSPACE_CHEMICALS[x].name
        )
        
        if selected_chems:
            for chem in selected_chems:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    conc = st.number_input(
                        f"{AEROSPACE_CHEMICALS[chem].name} Concentration ({AEROSPACE_CHEMICALS[chem].units})",
                        min_value=0.0,
                        value=0.0,
                        step=0.001,
                        key=f"report_{chem}_conc"
                    )
                
                with col2:
                    dur = st.number_input(
                        f"{AEROSPACE_CHEMICALS[chem].name} Duration (hours)",
                        min_value=0.1,
                        max_value=8.0,
                        value=8.0,
                        step=0.1,
                        key=f"report_{chem}_dur"
                    )
                
                exposures[chem] = {"concentration": conc, "duration": dur}
            
            if st.button("Generate Comprehensive Report", type="primary"):
                report = generate_exposure_report(
                    facility_name,
                    assessment_date.strftime("%Y-%m-%d"),
                    exposures
                )
                
                st.markdown("#### Generated Report")
                st.text_area("", report, height=600)
                
                # Download button
                st.download_button(
                    label="Download Report as Text File",
                    data=report,
                    file_name=f"exposure_report_{assessment_date.strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )

elif calculator_category == "🔬 Environmental Monitoring":
    st.markdown('<div class="section-header">Environmental Monitoring Calculators</div>', unsafe_allow_html=True)
    
    calc_type = st.selectbox(
        "Choose Calculator",
        [
            "Heat Stress Index (WBGT)",
            "Heat Stress Index (HSI)",
            "Cold Exposure: Peak Shivering",
            "Noise Exposure Assessment"
        ]
    )
    
    if calc_type == "Heat Stress Index (WBGT)":
        st.markdown("### 🌡️ Wet Bulb Globe Temperature (WBGT)")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            environment = st.radio("Environment Type", ["Indoor", "Outdoor"])
            
            if environment == "Indoor":
                dry_bulb = st.number_input("Dry Bulb Temperature (°C)", -10.0, 60.0, 25.0, step=0.1)
                wet_bulb = st.number_input("Wet Bulb Temperature (°C)", -10.0, 60.0, 20.0, step=0.1)
                globe_temp = st.number_input("Globe Temperature (°C)", -10.0, 80.0, 30.0, step=0.1)
                
                wbgt = wbgt_indoor(wet_bulb, globe_temp, T_db=dry_bulb)
            else:
                dry_bulb = st.number_input("Dry Bulb Temperature (°C)", -10.0, 60.0, 25.0, step=0.1)
                wet_bulb = st.number_input("Wet Bulb Temperature (°C)", -10.0, 60.0, 20.0, step=0.1)
                globe_temp = st.number_input("Globe Temperature (°C)", -10.0, 80.0, 35.0, step=0.1)
                
                wbgt = wbgt_outdoor(wet_bulb, globe_temp, T_db=dry_bulb)
        
        with col2:
            st.markdown("#### Results")
            st.metric("WBGT Index", f"{wbgt:.1f} °C")
            
            # Risk assessment based on ACGIH guidelines
            if wbgt < 28:
                st.markdown('<div class="info-box"><strong>Risk Category:</strong> Low</div>', unsafe_allow_html=True)
            elif wbgt < 30:
                st.markdown('<div class="info-box"><strong>Risk Category:</strong> Moderate</div>', unsafe_allow_html=True)
            elif wbgt < 32:
                st.markdown('<div class="info-box"><strong>Risk Category:</strong> High</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box"><strong>Risk Category:</strong> Extreme</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-box">WBGT values are based on ISO 7243:2017 standards for heat stress assessment.</div>', unsafe_allow_html=True)
    
    elif calc_type == "Heat Stress Index (HSI)":
        st.markdown("### 🔥 Heat Stress Index (HSI)")
        col1, col2 = st.columns([1, 1])
        with col1:
            M = st.number_input("Metabolic rate (W/m²)", 0.0, 800.0, 300.0, step=10.0)
            Tdb = st.number_input("Dry-bulb (°C)", -10.0, 60.0, 30.0, step=0.1)
            RH = st.number_input("Relative Humidity (%)", 0.0, 100.0, 50.0, step=1.0)
            v = st.number_input("Air speed (m/s)", 0.0, 5.0, 0.5, step=0.1)
            Wext = st.number_input("External work (W/m²)", 0.0, 400.0, 0.0, step=10.0)
            Tg = st.number_input("Globe temperature (°C, optional)", -10.0, 80.0, Tdb, step=0.1)
        with col2:
            hsi = heat_stress_index(M, Tdb, RH, v, Wext, Tg)
            st.markdown("#### Results")
            st.metric("HSI", f"{hsi:.1f} %")
            if hsi < 20:
                st.markdown('<div class="info-box"><strong>Assessment:</strong> Acceptable</div>', unsafe_allow_html=True)
            elif hsi < 40:
                st.markdown('<div class="info-box"><strong>Assessment:</strong> Caution</div>', unsafe_allow_html=True)
            elif hsi < 100:
                st.markdown('<div class="info-box"><strong>Assessment:</strong> High strain</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box"><strong>Assessment:</strong> Uncompensable heat stress</div>', unsafe_allow_html=True)
    
    elif calc_type == "Cold Exposure: Peak Shivering":
        st.markdown("### 🥶 Peak Shivering Intensity")
        col1, col2 = st.columns([1, 1])
        with col1:
            vo2max = st.number_input("VO₂max (ml·kg⁻¹·min⁻¹)", 15.0, 90.0, 45.0, step=1.0)
            bmi = st.number_input("BMI (kg/m²)", 15.0, 40.0, 24.0, step=0.1)
            age = st.number_input("Age (years)", 16, 80, 30, step=1)
        shiv = peak_shivering_intensity(vo2max, bmi, age)
        with col2:
            st.markdown("#### Results")
            st.metric("Shivering peak", f"{shiv:.1f} ml·kg⁻¹·min⁻¹")
            st.markdown(f"<div class='info-box'>Represents ~{shiv/3.5:.1f}× resting metabolism</div>", unsafe_allow_html=True)
    
    elif calc_type == "Noise Exposure Assessment":
        st.markdown("### 🔊 Noise Exposure Assessment")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            noise_level = st.number_input("Noise Level (dBA)", 50.0, 130.0, 90.0, step=0.1)
            exposure_time = st.number_input("Exposure Time (hours)", 0.1, 8.0, 8.0, step=0.1)
            
            standard = st.radio("Select Standard", ["OSHA", "NIOSH"])
        
        with col2:
            st.markdown("#### Results")
            
            if standard == "OSHA":
                dose = noise_dose_osha([noise_level], [exposure_time])
                perm_time = permissible_duration(
                    noise_level, criterion_level=90.0, exchange_rate=5.0
                )
            else:
                dose = noise_dose_niosh([noise_level], [exposure_time])
                perm_time = permissible_duration(
                    noise_level, criterion_level=85.0, exchange_rate=3.0
                )
            
            st.metric("Noise Dose", f"{dose:.1f}%", "Should be ≤ 100%")
            st.metric("Permissible Duration", f"{perm_time:.1f} hours")
            
            if dose <= 50:
                st.markdown('<div class="info-box"><strong>Assessment:</strong> Below action level</div>', unsafe_allow_html=True)
            elif dose <= 100:
                st.markdown('<div class="info-box"><strong>Assessment:</strong> Near action level</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box"><strong>Assessment:</strong> Exceeds permissible limit</div>', unsafe_allow_html=True)
        
        # Comparison chart
        levels = np.arange(80, 120, 5)
        osha_times = [
            permissible_duration(level, criterion_level=90.0, exchange_rate=5.0)
            for level in levels
        ]
        niosh_times = [
            permissible_duration(level, criterion_level=85.0, exchange_rate=3.0)
            for level in levels
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=levels, y=osha_times, mode='lines+markers', name='OSHA', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=levels, y=niosh_times, mode='lines+markers', name='NIOSH', line=dict(color='red')))
        fig.update_layout(
            title="Permissible Exposure Time vs Noise Level",
            xaxis_title="Noise Level (dBA)",
            yaxis_title="Permissible Time (hours)",
            yaxis_type="log"
        )
        st.plotly_chart(fig, use_container_width=True)

elif calculator_category == "📈 Visualization Studio":
    st.markdown('<div class="section-header">Visualization Studio</div>', unsafe_allow_html=True)

    # Display controls
    with st.container():
        col_theme, col_palette, col_height = st.columns([1, 1, 1])

        # Theme selection with auto detection from Streamlit theme
        theme_base = st.get_option("theme.base") or "light"
        theme_default = "plotly_dark" if theme_base == "dark" else "plotly_white"
        theme_choice = col_theme.selectbox(
            "Plot Theme",
            ["Auto", "Light", "Dark", "Seaborn", "Simple White", "GGPlot2", "Presentation"],
            help="Choose a visual theme. 'Auto' follows the app's light/dark mode."
        )
        theme_template = {
            "Auto": theme_default,
            "Light": "plotly_white",
            "Dark": "plotly_dark",
            "Seaborn": "seaborn",
            "Simple White": "simple_white",
            "GGPlot2": "ggplot2",
            "Presentation": "presentation",
        }[theme_choice]

        # Palette selection
        palette_options = {
            "Auto": None,
            "Plotly": px.colors.qualitative.Plotly,
            "D3": px.colors.qualitative.D3,
            "Bold": px.colors.qualitative.Bold,
            "Pastel": px.colors.qualitative.Pastel,
            "Set2": px.colors.qualitative.Set2,
            "Dark24": px.colors.qualitative.Dark24,
            "Vivid": px.colors.qualitative.Vivid,
        }
        palette_name = col_palette.selectbox("Color Palette", list(palette_options.keys()), index=0)
        colorway_selected = palette_options[palette_name]

        # Resizable height
        plot_height = col_height.slider("Plot Height", min_value=420, max_value=900, value=640, step=20)

        col_style1, col_style2, col_style3 = st.columns([1, 1, 1])
        show_legend = col_style1.toggle("Show Legend", value=True)
        show_grid = col_style2.toggle("Show Grid", value=True)
        hover_unified = col_style3.toggle("Unified Hover", value=True, help="Show a single tooltip for all traces aligned on x-axis")

    # Helper to style figures consistently
    def style_fig(fig, title: str):
        fig.update_layout(
            title=title,
            template=theme_template,
            font=dict(family="Inter, system-ui, sans-serif", size=14),
            height=plot_height,
            colorway=colorway_selected if colorway_selected else None,
            margin=dict(l=50, r=30, t=60, b=50),
            showlegend=show_legend,
        )
        fig.update_xaxes(showgrid=show_grid)
        fig.update_yaxes(showgrid=show_grid)
        if hover_unified:
            fig.update_layout(hovermode="x unified")
        return fig

    vis_type = st.selectbox(
        "Choose Visualization",
        [
            "PAO₂ vs Altitude & FiO₂",
            "SpO₂ vs Altitude (Acclimatized vs Unacclimatized)",
            "AMS Probability vs AAE",
            "CaO₂ vs PaO₂ & Hb",
            "WBGT (Outdoor) vs Dry-Bulb & RH",
            "Noise Permissible Duration vs Level & Exchange Rate",
            "Mixed Chemical Index (2 chemicals)"
        ]
    )

    plot_mode = st.radio("Plot Type", ["2D", "3D"], horizontal=True)

    # Trace style for 2D plots
    trace_style = st.radio("Trace Style (2D)", ["Lines", "Lines + Markers", "Markers", "Area"], horizontal=True)
    smooth_lines = st.toggle("Smooth Lines", value=False)
    mode_map = {
        "Lines": "lines",
        "Lines + Markers": "lines+markers",
        "Markers": "markers",
        "Area": "lines",
    }

    with st.expander("Export Options", expanded=False):
        export_format = st.selectbox("Export format", ["png", "svg", "pdf"], index=0)
        export_scale = st.slider("Export scale (higher = higher DPI)", 1, 4, 2)

    if vis_type == "PAO₂ vs Altitude & FiO₂":
        col1, col2 = st.columns(2)
        with col1:
            alt_range_ft = st.slider("Altitude range (ft)", 0, 40000, (0, 30000), step=1000)
            fio2_min, fio2_max = st.slider("FiO₂ range", 0.10, 1.00, (0.21, 1.00), step=0.01)
            paco2 = st.slider("PaCO₂ (mmHg)", 20.0, 60.0, 40.0, step=1.0)
            rq = st.slider("Respiratory Quotient (R)", 0.6, 1.2, 0.8, step=0.05)
        with col2:
            if plot_mode == "2D":
                fixed_fio2 = st.slider("Fixed FiO₂", fio2_min, fio2_max, 0.21, step=0.01)
                altitudes_ft = np.linspace(alt_range_ft[0], alt_range_ft[1], 120)
                altitudes_m = altitudes_ft * 0.3048
                values = [alveolar_PO2(a, fixed_fio2, paco2, rq) for a in altitudes_m]
                fig = go.Figure()
                mode_map = {
                    "Lines": "lines",
                    "Lines + Markers": "lines+markers",
                    "Markers": "markers",
                    "Area": "lines",
                }
                fig.add_trace(go.Scatter(
                    x=altitudes_ft,
                    y=values,
                    mode=mode_map[trace_style],
                    name=f"FiO₂={fixed_fio2:.2f}",
                    fill="tozeroy" if trace_style == "Area" else None,
                ))
                style_fig(fig, "Alveolar Oxygen Pressure vs Altitude")
                fig.update_xaxes(title_text="Altitude (ft)")
                fig.update_yaxes(title_text="PAO₂ (mmHg)")
                if smooth_lines:
                    fig.update_traces(line_shape="spline")
                st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True, "scrollZoom": True})
            else:
                altitudes_ft = np.linspace(alt_range_ft[0], alt_range_ft[1], 80)
                fio2_vals = np.linspace(fio2_min, fio2_max, 60)
                A, F = np.meshgrid(altitudes_ft, fio2_vals)
                Z = np.zeros_like(A)
                for i in range(F.shape[0]):
                    for j in range(A.shape[1]):
                        Z[i, j] = alveolar_PO2(A[i, j] * 0.3048, F[i, j], paco2, rq)
                fig = go.Figure(data=[go.Surface(x=A, y=F, z=Z, colorscale="Viridis")])
                style_fig(fig, "PAO₂ Surface: Altitude × FiO₂")
                fig.update_scenes(xaxis_title_text="Altitude (ft)", yaxis_title_text="FiO₂", zaxis_title_text="PAO₂ (mmHg)")
                fig.update_layout(scene=dict(
                    xaxis_title="Altitude (ft)", yaxis_title="FiO₂", zaxis_title="PAO₂ (mmHg)"
                ))
                st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True})

        fig_to_save = fig if 'fig' in locals() else None

    elif vis_type == "WBGT (Outdoor) vs Dry-Bulb & RH":
        col1, col2 = st.columns(2)
        with col1:
            tdb_range = st.slider("Dry-bulb (°C)", -10.0, 60.0, (15.0, 40.0), step=0.5)
            rh_min, rh_max = st.slider("Relative Humidity (%)", 0.0, 100.0, (20.0, 90.0), step=1.0)
            tg = st.slider("Globe temperature (°C)", -10.0, 80.0, 35.0, step=0.5)
        with col2:
            if plot_mode == "2D":
                fixed_rh = st.slider("Fixed RH (%)", rh_min, rh_max, 50.0, step=1.0)
                tdb_vals = np.linspace(tdb_range[0], tdb_range[1], 140)
                wbgt_vals = [wbgt_outdoor(T_nwb=None, T_g=tg, T_db=tdb, RH=fixed_rh) for tdb in tdb_vals]
                fig = go.Figure()
                mode_map = {
                    "Lines": "lines",
                    "Lines + Markers": "lines+markers",
                    "Markers": "markers",
                    "Area": "lines",
                }
                fig.add_trace(go.Scatter(
                    x=tdb_vals,
                    y=wbgt_vals,
                    mode=mode_map[trace_style],
                    name=f"RH={fixed_rh:.0f}%",
                    fill="tozeroy" if trace_style == "Area" else None,
                ))
                style_fig(fig, "WBGT (Outdoor) vs Dry-bulb")
                fig.update_xaxes(title_text="Dry-bulb (°C)")
                fig.update_yaxes(title_text="WBGT (°C)")
                if smooth_lines:
                    fig.update_traces(line_shape="spline")
                st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True, "scrollZoom": True})
            else:
                tdb_vals = np.linspace(tdb_range[0], tdb_range[1], 80)
                rh_vals = np.linspace(rh_min, rh_max, 60)
                T, H = np.meshgrid(tdb_vals, rh_vals)
                Z = np.zeros_like(T)
                for i in range(H.shape[0]):
                    for j in range(T.shape[1]):
                        Z[i, j] = wbgt_outdoor(T_nwb=None, T_g=tg, T_db=T[i, j], RH=H[i, j])
                fig = go.Figure(data=[go.Surface(x=T, y=H, z=Z, colorscale="Turbo")])
                style_fig(fig, "WBGT (Outdoor) Surface: T_db × RH")
                fig.update_layout(scene=dict(
                    xaxis_title="Dry-bulb (°C)", yaxis_title="RH (%)", zaxis_title="WBGT (°C)"
                ))
                st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True})

        fig_to_save = fig if 'fig' in locals() else None

    elif vis_type == "Noise Permissible Duration vs Level & Exchange Rate":
        col1, col2 = st.columns(2)
        with col1:
            level_range = st.slider("Noise level (dBA)", 80.0, 120.0, (85.0, 110.0), step=1.0)
            exch_min, exch_max = st.slider("Exchange rate (dB)", 2.0, 6.0, (3.0, 5.0), step=0.5)
            criterion = st.slider("Criterion level (dBA)", 80.0, 95.0, 85.0, step=1.0)
        with col2:
            if plot_mode == "2D":
                fixed_exch = st.slider("Fixed exchange rate (dB)", exch_min, exch_max, 3.0, step=0.5)
                levels = np.linspace(level_range[0], level_range[1], 120)
                times = [permissible_duration(l, criterion_level=criterion, exchange_rate=fixed_exch) for l in levels]
                fig = go.Figure()
                mode_map = {
                    "Lines": "lines",
                    "Lines + Markers": "lines+markers",
                    "Markers": "markers",
                    "Area": "lines",
                }
                fig.add_trace(go.Scatter(
                    x=levels,
                    y=times,
                    mode=mode_map[trace_style],
                    name=f"Exchange={fixed_exch} dB",
                    fill="tozeroy" if trace_style == "Area" else None,
                ))
                style_fig(fig, "Permissible Duration vs Noise Level")
                fig.update_yaxes(type="log")
                fig.update_xaxes(title_text="Noise level (dBA)")
                fig.update_yaxes(title_text="Permissible time (hours)")
                if smooth_lines:
                    fig.update_traces(line_shape="spline")
                st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True, "scrollZoom": True})
            else:
                levels = np.linspace(level_range[0], level_range[1], 80)
                exch = np.linspace(exch_min, exch_max, 60)
                L, E = np.meshgrid(levels, exch)
                Z = np.zeros_like(L)
                for i in range(E.shape[0]):
                    for j in range(L.shape[1]):
                        Z[i, j] = permissible_duration(L[i, j], criterion_level=criterion, exchange_rate=E[i, j])
                fig = go.Figure(data=[go.Surface(x=L, y=E, z=Z, colorscale="Cividis")])
                style_fig(fig, "Permissible Duration Surface: Level × Exchange Rate")
                fig.update_layout(scene=dict(
                    xaxis_title="Noise level (dBA)", yaxis_title="Exchange rate (dB)", zaxis_title="Time (hours)",
                    zaxis_type="log"
                ))
                st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True})

        fig_to_save = fig if 'fig' in locals() else None

    elif vis_type == "Mixed Chemical Index (2 chemicals)":
        st.markdown("Select two chemicals and explore mixed exposure index (sum of fractions)")
        available = list(AEROSPACE_CHEMICALS.keys())
        colc1, colc2 = st.columns(2)
        with colc1:
            chem_a = st.selectbox("Chemical A", available, format_func=lambda x: AEROSPACE_CHEMICALS[x].name)
        with colc2:
            chem_b = st.selectbox("Chemical B", [k for k in available if k != chem_a], format_func=lambda x: AEROSPACE_CHEMICALS[x].name)

        tlv_a = AEROSPACE_CHEMICALS[chem_a].tlv_twa
        tlv_b = AEROSPACE_CHEMICALS[chem_b].tlv_twa
        units_a = AEROSPACE_CHEMICALS[chem_a].units
        units_b = AEROSPACE_CHEMICALS[chem_b].units

        col1, col2 = st.columns(2)
        with col1:
            xa_max = st.number_input(f"Max concentration for {AEROSPACE_CHEMICALS[chem_a].name} ({units_a})", min_value=0.0, value=float(tlv_a * 2), step=0.1)
            xb_max = st.number_input(f"Max concentration for {AEROSPACE_CHEMICALS[chem_b].name} ({units_b})", min_value=0.0, value=float(tlv_b * 2), step=0.1)
        with col2:
            pass

        if plot_mode == "2D":
            x_a = np.linspace(0, xa_max, 140)
            x_b_fixed = st.slider(f"Fixed {AEROSPACE_CHEMICALS[chem_b].name} concentration ({units_b})", 0.0, xb_max, 0.0, step=max(xb_max/100, 0.01))
            index_vals = x_a / tlv_a + x_b_fixed / tlv_b
            fig = go.Figure()
            mode_map = {
                "Lines": "lines",
                "Lines + Markers": "lines+markers",
                "Markers": "markers",
                "Area": "lines",
            }
            fig.add_trace(go.Scatter(x=x_a, y=index_vals, mode=mode_map[trace_style], name="Mixed Index", fill="tozeroy" if trace_style == "Area" else None))
            style_fig(fig, "Mixed Chemical Exposure Index vs Concentration A")
            fig.update_xaxes(title_text=f"{AEROSPACE_CHEMICALS[chem_a].name} concentration ({units_a})")
            fig.update_yaxes(title_text="Mixed Index (sum of fractions)")
            if smooth_lines:
                fig.update_traces(line_shape="spline")
            st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True, "scrollZoom": True})
        else:
            x_a = np.linspace(0, xa_max, 80)
            x_b = np.linspace(0, xb_max, 60)
            A, B = np.meshgrid(x_a, x_b)
            Z = A / tlv_a + B / tlv_b
            fig = go.Figure(data=[go.Surface(x=A, y=B, z=Z, colorscale="Plasma")])
            style_fig(fig, "Mixed Chemical Index Surface")
            fig.update_layout(scene=dict(
                xaxis_title=f"{AEROSPACE_CHEMICALS[chem_a].name} ({units_a})",
                yaxis_title=f"{AEROSPACE_CHEMICALS[chem_b].name} ({units_b})",
                zaxis_title="Mixed Index"
            ))
            st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True})

        fig_to_save = fig if 'fig' in locals() else None

    elif vis_type == "SpO₂ vs Altitude (Acclimatized vs Unacclimatized)":
        col1, col2 = st.columns(2)
        with col1:
            alt_range_m = st.slider("Altitude range (m)", 0, 6000, (0, 5000), step=100)
        with col2:
            pass
        alts = np.linspace(alt_range_m[0], alt_range_m[1], 160)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=alts, y=[spo2_unacclimatized(a) for a in alts], name="Unacclimatized"))
        fig.add_trace(go.Scatter(x=alts, y=[spo2_acclimatized(a) for a in alts], name="Acclimatized"))
        style_fig(fig, "SpO₂ vs Altitude")
        fig.update_xaxes(title_text="Altitude (m)")
        fig.update_yaxes(title_text="SpO₂ (%)")
        if smooth_lines:
            fig.update_traces(line_shape="spline")
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True, "scrollZoom": True})
        fig_to_save = fig

    elif vis_type == "AMS Probability vs AAE":
        aae_vals = np.linspace(0, 6, 140)
        probs = [ams_probability(x)*100 for x in aae_vals]
        fig = go.Figure(data=[go.Scatter(x=aae_vals, y=probs, mode=mode_map.get(trace_style, "lines"))])
        style_fig(fig, "AMS Probability vs AAE")
        fig.update_xaxes(title_text="AAE (km·days)")
        fig.update_yaxes(title_text="Probability (%)")
        if smooth_lines:
            fig.update_traces(line_shape="spline")
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True, "scrollZoom": True})
        fig_to_save = fig

    elif vis_type == "CaO₂ vs PaO₂ & Hb":
        col1, col2 = st.columns(2)
        with col1:
            pao2_min, pao2_max = st.slider("PaO₂ range (mmHg)", 30.0, 120.0, (60.0, 100.0), step=1.0)
            hb = st.slider("Hemoglobin (g/dL)", 8.0, 18.0, 15.0, step=0.1)
        pa_vals = np.linspace(pao2_min, pao2_max, 140)
        # Hill estimate for SaO2
        def est_sao2(p: float) -> float:
            if p <= 0:
                return 0.0
            P50, n = 26.8, 2.7
            ratio = (p ** n) / (p ** n + P50 ** n)
            return 100.0 * ratio
        cao2_vals = [oxygen_content(hb, est_sao2(p), p) for p in pa_vals]
        fig = go.Figure(data=[go.Scatter(x=pa_vals, y=cao2_vals, mode=mode_map.get(trace_style, "lines"))])
        style_fig(fig, "CaO₂ vs PaO₂ (Hb fixed)")
        fig.update_xaxes(title_text="PaO₂ (mmHg)")
        fig.update_yaxes(title_text="CaO₂ (mL/dL)")
        if smooth_lines:
            fig.update_traces(line_shape="spline")
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True, "scrollZoom": True})
        fig_to_save = fig

    # Export controls
    if 'fig_to_save' in locals() and fig_to_save is not None:
        col_export1, col_export2 = st.columns([1, 1])
        
        with col_export1:
            # Try static image export
            try:
                img_bytes = fig_to_save.to_image(format=export_format, scale=export_scale)
                st.download_button(
                    label=f"Download Static Image ({export_format.upper()})",
                    data=img_bytes,
                    file_name=f"visualization.{export_format}",
                    mime="image/png" if export_format == "png" else ("image/svg+xml" if export_format == "svg" else "application/pdf")
                )
            except Exception as e:
                error_msg = str(e)
                if "Chrome" in error_msg or "kaleido" in error_msg.lower():
                    st.error("**Static Export Unavailable**")
                    st.info("Install Chrome or use HTML export →")
                else:
                    st.warning("Static export failed - use HTML export →")
        
        with col_export2:
            # Fallback: HTML export (always works)
            html_str = fig_to_save.to_html(include_plotlyjs=True)
            st.download_button(
                label="Download Interactive HTML",
                data=html_str,
                file_name="visualization.html",
                mime="text/html"
            )

elif calculator_category == "📊 Risk Assessment Tools":
    st.markdown('<div class="section-header">Risk Assessment Tools</div>', unsafe_allow_html=True)
    
    st.markdown("### 📋 Quick Risk Assessment Dashboard")
    
    # Chemical database overview
    st.markdown("#### Aerospace Chemical Database Overview")
    
    # Create DataFrame for display
    chem_data = []
    for key, chem in AEROSPACE_CHEMICALS.items():
        chem_data.append({
            "Chemical": chem.name,
            "CAS Number": chem.cas_number,
            "TLV-TWA": f"{chem.tlv_twa} {chem.units}",
            "Carcinogen": "Yes" if chem.carcinogen else "No",
            "Skin Notation": "Yes" if chem.skin_notation else "No",
            "BEI Available": "Yes" if chem.bei_value else "No"
        })
    
    df = pd.DataFrame(chem_data)
    st.dataframe(df, use_container_width=True)
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Chemicals", len(AEROSPACE_CHEMICALS))
    
    with col2:
        carcinogens = sum(1 for chem in AEROSPACE_CHEMICALS.values() if chem.carcinogen)
        st.metric("Carcinogens", carcinogens)
    
    with col3:
        skin_notation = sum(1 for chem in AEROSPACE_CHEMICALS.values() if chem.skin_notation)
        st.metric("Skin Notation", skin_notation)
    
    with col4:
        bei_available = sum(1 for chem in AEROSPACE_CHEMICALS.values() if chem.bei_value)
        st.metric("BEI Available", bei_available)
    
    # Risk matrix visualization
    st.markdown("#### Chemical Risk Matrix")
    
    # Create risk categories based on TLV values (lower TLV = higher risk)
    risk_data = []
    for key, chem in AEROSPACE_CHEMICALS.items():
        if chem.units == "ppm":
            if chem.tlv_twa <= 0.1:
                risk_level = "Very High"
            elif chem.tlv_twa <= 1.0:
                risk_level = "High"
            elif chem.tlv_twa <= 10.0:
                risk_level = "Medium"
            else:
                risk_level = "Low"
        else:  # mg/m³
            if chem.tlv_twa <= 1.0:
                risk_level = "Very High"
            elif chem.tlv_twa <= 10.0:
                risk_level = "High"
            elif chem.tlv_twa <= 100.0:
                risk_level = "Medium"
            else:
                risk_level = "Low"
        
        risk_data.append({
            "Chemical": chem.name,
            "Risk Level": risk_level,
            "Carcinogen": chem.carcinogen
        })
    
    risk_df = pd.DataFrame(risk_data)
    
    # Create sunburst chart
    fig = px.sunburst(
        risk_df,
        path=['Risk Level', 'Chemical'],
        title="Chemical Risk Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

elif calculator_category == "🧠 Fatigue & Circadian":
    st.markdown('<div class="section-header">Fatigue & Circadian Calculators</div>', unsafe_allow_html=True)

    calc_type = st.selectbox(
        "Choose Calculator",
        [
            "Circadian Performance (Mitler)",
            "Two-Process Model (S & C)",
            "Jet Lag Recovery",
        ]
    )

    if calc_type == "Circadian Performance (Mitler)":
        st.markdown("### 🧠 Circadian Performance (Mitler)")
        col1, col2 = st.columns([1, 1])
        with col1:
            t = st.slider("Time (hours)", 0.0, 24.0, 12.0, step=0.5)
            phi = st.slider("Phase (φ, hours)", -12.0, 12.0, 0.0, step=0.5)
            SD = st.slider("Sleep debt parameter (SD)", 0.5, 5.0, 2.0, step=0.1)
            K = st.slider("Scaling (K)", 0.5, 5.0, 2.0, step=0.1)
        perf = mitler_performance(t, phi, SD, K)
        with col2:
            st.markdown("#### Result")
            st.metric("Performance (unitless)", f"{perf:.3f}")
        # Viz over 24h
        ts = np.linspace(0, 24, 180)
        ps = [mitler_performance(x, phi, SD, K) for x in ts]
        fig = go.Figure(data=[go.Scatter(x=ts, y=ps, mode="lines")])
        fig.update_layout(title="Mitler Performance over 24h", xaxis_title="Time (h)", yaxis_title="Performance", height=360)
        st.plotly_chart(fig, use_container_width=True)

    elif calc_type == "Two-Process Model (S & C)":
        st.markdown("### ⏳ Two-Process Model Components")
        col1, col2 = st.columns([1, 1])
        with col1:
            Sa = st.slider("Sa (upper bound)", 0.0, 1.0, 1.0, step=0.01)
            L = st.slider("L (lower bound)", 0.0, 1.0, 0.2, step=0.01)
            U = st.slider("U (upper equilibrium)", 0.0, 1.0, 1.0, step=0.01)
            Sr = st.slider("Sr (recovery baseline)", 0.0, 1.0, 0.3, step=0.01)
            tS = st.slider("Time t (hours)", 0.0, 16.0, 8.0, step=0.5)
            M = st.slider("Circadian amplitude (M)", 0.0, 1.5, 1.0, step=0.05)
            p = st.slider("Phase p (hours)", 0.0, 24.0, 18.0, step=0.5)
        S_wake = homeostatic_waking(Sa, L, tS)
        S_sleep = homeostatic_sleep(U, Sr, tS)
        C_val = circadian_component(M, tS, p)
        with col2:
            st.markdown("#### Results")
            st.metric("S (waking)", f"{S_wake:.3f}")
            st.metric("S' (sleep)", f"{S_sleep:.3f}")
            st.metric("C (circadian)", f"{C_val:.3f}")

    elif calc_type == "Jet Lag Recovery":
        st.markdown("### ✈️ Jet Lag Recovery Time")
        col1, col2 = st.columns([1, 1])
        with col1:
            tz = st.slider("Time zones crossed", 0, 12, 6, step=1)
            direction = st.radio("Direction", ["Eastward", "Westward"], horizontal=True)
        days = jet_lag_days_to_adjust(tz, direction)
        with col2:
            st.markdown("#### Result")
            st.metric("Estimated days to adjust", f"{days:.1f} days")

# Footer
st.markdown("---")
st.markdown("""
<div style=\"text-align: center; color: #666; font-size: 0.9em;\">
    <p><strong>Aerospace Physiology & Occupational Health Calculators</strong></p>
    <p>For educational and research purposes only • Consult qualified professionals for operational use</p>
</div>
""", unsafe_allow_html=True)
