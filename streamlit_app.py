import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import plotly.graph_objects as go  # type: ignore
import plotly.express as px  # type: ignore
from datetime import datetime
import numpy as np

from calculators import (
    standard_atmosphere,
    alveolar_PO2,
    estimate_tuc,
    g_loc_time,
    dose_rate,
    wbgt_indoor,
    wbgt_outdoor,
    noise_dose_osha,
    noise_dose_niosh,
    permissible_duration,
    calculate_twa_exposure,
    calculate_adjusted_tlv_unusual_schedule,
    assess_exposure_risk,
    calculate_mixed_exposure_index,
    generate_exposure_report,
    calculate_biological_exposure_index,
    AEROSPACE_CHEMICALS
)

# Page configuration
st.set_page_config(
    page_title="Aerospace Physiology & Occupational Health Calculators",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #f0f8ff, #e6f3ff);
        border-radius: 10px;
        border-left: 5px solid #1f4e79;
    }
    
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c5aa0;
        margin: 1.5rem 0 1rem 0;
        padding: 0.5rem 0;
        border-bottom: 2px solid #e1ecf4;
    }
    
    .info-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    
    .danger-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e1ecf4;
        margin: 0.5rem 0;
    }
    
    .stButton > button {
        background-color: #1f4e79;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #2c5aa0;
        transform: translateY(-2px);
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
        "⚠️ Occupational Health & Safety",
        "🔬 Environmental Monitoring",
        "📊 Risk Assessment Tools"
    ]
)

# Disclaimer
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="warning-box">
<strong>⚠️ Important Disclaimer</strong><br>
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
        
        **⚠️ Occupational Health & Safety:**
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
            st.sidebar.selectbox("Select Calculator Category", ["⚠️ Occupational Health & Safety"], key="nav_override")

elif calculator_category == "🌍 Atmospheric & Physiological":
    st.markdown('<div class="section-header">Atmospheric & Physiological Calculators</div>', unsafe_allow_html=True)
    
    calc_type = st.selectbox(
        "Choose Calculator",
        [
            "Standard Atmosphere Properties",
            "Alveolar Oxygen Pressure", 
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
                st.markdown('<div class="danger-box"><strong>⚠️ Critical:</strong> Severe hypoxemia risk</div>', unsafe_allow_html=True)
            elif p_ao2 < 80:
                st.markdown('<div class="warning-box"><strong>⚠️ Warning:</strong> Moderate hypoxemia risk</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-box"><strong>✅ Normal:</strong> Adequate oxygenation</div>', unsafe_allow_html=True)
        
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
                st.markdown('<div class="danger-box"><strong>⚠️ CRITICAL:</strong> Instantaneous loss of consciousness expected</div>', unsafe_allow_html=True)
            else:
                minutes = tuc_sec / 60
                st.metric("Estimated TUC", f"{tuc_sec:.0f} seconds", f"~{minutes:.1f} minutes")
                
                if minutes < 1:
                    st.markdown('<div class="danger-box"><strong>⚠️ CRITICAL:</strong> Less than 1 minute</div>', unsafe_allow_html=True)
                elif minutes < 5:
                    st.markdown('<div class="warning-box"><strong>⚠️ WARNING:</strong> Very limited time</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="info-box"><strong>ℹ️ INFO:</strong> Sufficient time for emergency procedures</div>', unsafe_allow_html=True)
        
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
                st.markdown('<div class="success-box"><strong>✅ SAFE:</strong> Below ~5g most healthy subjects tolerate indefinitely</div>', unsafe_allow_html=True)
            else:
                st.metric("Estimated Tolerance Time", f"{tol:.0f} seconds")
                
                if tol < 15:
                    st.markdown('<div class="danger-box"><strong>⚠️ CRITICAL:</strong> Very short tolerance time</div>', unsafe_allow_html=True)
                elif tol < 60:
                    st.markdown('<div class="warning-box"><strong>⚠️ WARNING:</strong> Limited tolerance time</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="info-box"><strong>ℹ️ INFO:</strong> Reasonable tolerance time</div>', unsafe_allow_html=True)
        
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
                st.markdown('<div class="warning-box"><strong>⚠️ WARNING:</strong> Exceeds public dose limit</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-box"><strong>✅ ACCEPTABLE:</strong> Within public dose limits</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-box">Highly simplified linear model for educational purposes only; real-world exposure depends on solar activity, latitude, and flight duration.</div>', unsafe_allow_html=True)

elif calculator_category == "⚠️ Occupational Health & Safety":
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
                risk_color = {
                    "Low": "success-box",
                    "Moderate": "warning-box", 
                    "High": "danger-box",
                    "Very High": "danger-box"
                }
                
                st.markdown(f'<div class="{risk_color[assessment["risk_level"]]}"><strong>Risk Level: {assessment["risk_level"]}</strong></div>', unsafe_allow_html=True)
                
                st.metric("TLV Ratio", f"{assessment['tlv_ratio']:.2f}", "Should be ≤ 1.0")
                st.metric("8-hr TWA Exposure", f"{assessment['twa_exposure']:.4f} {assessment['units']}")
                st.metric("TLV-TWA", f"{assessment['tlv_twa']:.4f} {assessment['units']}")
                
                # Additional warnings
                if assessment['carcinogen']:
                    st.markdown('<div class="danger-box">⚠️ <strong>CARCINOGEN</strong> - Minimize exposure to lowest feasible level</div>', unsafe_allow_html=True)
                
                if assessment['skin_notation']:
                    st.markdown('<div class="warning-box">👤 <strong>SKIN NOTATION</strong> - Prevent skin contact</div>', unsafe_allow_html=True)
                
                if assessment['stel_exceeded']:
                    st.markdown('<div class="danger-box">🚨 <strong>STEL EXCEEDED</strong> - Short-term exposure limit violated</div>', unsafe_allow_html=True)
            
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
                    st.markdown('<div class="success-box">✅ <strong>ACCEPTABLE:</strong> Mixed exposure within limits</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="danger-box">❌ <strong>EXCEEDS LIMITS:</strong> Immediate action required</div>', unsafe_allow_html=True)
                
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
                st.markdown('<div class="warning-box">⚠️ <strong>REDUCED LIMIT:</strong> More restrictive than standard TLV</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box">ℹ️ <strong>INCREASED LIMIT:</strong> Less restrictive than standard TLV</div>', unsafe_allow_html=True)
    
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
                            st.markdown('<div class="success-box">✅ <strong>WITHIN GUIDELINE:</strong> BEI not exceeded</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="warning-box">⚠️ <strong>EXCEEDS GUIDELINE:</strong> Investigation recommended</div>', unsafe_allow_html=True)
                        
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
                st.markdown('<div class="success-box">✅ <strong>LOW RISK:</strong> Most workers can perform work safely</div>', unsafe_allow_html=True)
            elif wbgt < 30:
                st.markdown('<div class="warning-box">⚠️ <strong>MODERATE RISK:</strong> Caution for unacclimatized workers</div>', unsafe_allow_html=True)
            elif wbgt < 32:
                st.markdown('<div class="warning-box">⚠️ <strong>HIGH RISK:</strong> Work/rest cycles recommended</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="danger-box">🚨 <strong>EXTREME RISK:</strong> Limit exposure time significantly</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-box">WBGT values are based on ISO 7243:2017 standards for heat stress assessment.</div>', unsafe_allow_html=True)
    
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
                st.markdown('<div class="success-box">✅ <strong>LOW RISK:</strong> Well below action level</div>', unsafe_allow_html=True)
            elif dose <= 100:
                st.markdown('<div class="warning-box">⚠️ <strong>ACTION LEVEL:</strong> Implement hearing conservation</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="danger-box">🚨 <strong>OVEREXPOSURE:</strong> Exceeds permissible limit</div>', unsafe_allow_html=True)
        
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

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    <p><strong>Aerospace Physiology & Occupational Health Calculators</strong></p>
    <p>Based on ACGIH TLVs and BEIs (2024), NIOSH Criteria, and International Standards</p>
    <p>For educational and research purposes only • Consult qualified professionals for operational use</p>
</div>
""", unsafe_allow_html=True)