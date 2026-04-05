# SPO2_UI_SECTION.py - Add this before the Footer in streamlit_app.py

# SpO2-Altitude Prediction Models Section
st.markdown("---")
st.header("🩸 SpO₂-Altitude Prediction Models")
st.markdown("Three peer-reviewed models for predicting blood oxygen saturation at altitude")

spo2_tabs = st.tabs(["📊 Niermeyer Linear", "🔄 Alt VAR", "⚗️ Tüshaus Cascade", "📈 Comparison"])

with spo2_tabs[0]:
    st.subheader("Niermeyer et al. Linear Regression Model")
    st.markdown("**Citation:** Niermeyer et al., *European Journal of Applied Physiology*")
    st.code("SpO₂ = 103.3 - (0.0047 × altitude[m]) + Z")
    
    col1, col2 = st.columns(2)
    with col1:
        niermeyer_alt = st.number_input("Altitude (m)", min_value=0, max_value=8848, value=4000, key="niermeyer_alt")
    with col2:
        niermeyer_sex = st.selectbox("Sex", ["male", "female"], key="niermeyer_sex")
    
    if st.button("Calculate SpO₂ (Niermeyer)", key="calc_niermeyer"):
        result = niermeyer_spo2(niermeyer_alt, niermeyer_sex)
        st.metric("Predicted SpO₂", f"{result.predicted_spo2}%")
        st.info(f"**Model:** {result.model_name} | **Confidence:** {result.confidence}")
        st.info(f"**Note:** {result.notes}")
    
    st.subheader("Altitude Sweep")
    alt_range = np.linspace(0, 6000, 100)
    spo2_male = [niermeyer_spo2(int(a), "male").predicted_spo2 for a in alt_range]
    spo2_female = [niermeyer_spo2(int(a), "female").predicted_spo2 for a in alt_range]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=alt_range, y=spo2_male, name="Male (Z=0.7)", mode="lines"))
    fig.add_trace(go.Scatter(x=alt_range, y=spo2_female, name="Female (Z=1.4)", mode="lines"))
    fig.add_hline(y=90, line_dash="dash", line_color="red", annotation_text="90% threshold")
    fig.add_hline(y=85, line_dash="dash", line_color="orange", annotation_text="85% threshold")
    fig.update_layout(title="Niermeyer Model: SpO₂ vs Altitude", xaxis_title="Altitude (m)", yaxis_title="SpO₂ (%)")
    st.plotly_chart(fig, use_container_width=True)

with spo2_tabs[1]:
    st.subheader("Alt et al. Vector Autoregression (VAR) Model")
    st.markdown("**Citation:** Alt et al., *The Sport Journal* (2025)")
    st.markdown("**R² = 0.706** — Captures acclimatization via time-lagged variables")
    st.code("SpO₂(t) = β₀ + β₁·SpO₂(t-12h) + β₂·SpO₂(t-24h) + β₃·HR(t-12h) + β₄·HR(t-24h) + β₅·Altitude + ε")
    
    col1, col2 = st.columns(2)
    with col1:
        var_alt = st.number_input("Current Altitude (m)", 0, 8848, 4000, key="var_alt")
        spo2_12h = st.number_input("SpO₂ 12h ago (%)", 50, 100, 88, key="spo2_12h")
        spo2_24h = st.number_input("SpO₂ 24h ago (%)", 50, 100, 86, key="spo2_24h")
    with col2:
        hr_12h = st.number_input("Heart Rate 12h ago (bpm)", 30, 220, 85, key="hr_12h")
        hr_24h = st.number_input("Heart Rate 24h ago (bpm)", 30, 220, 82, key="hr_24h")
    
    if st.button("Calculate SpO₂ (VAR)", key="calc_var"):
        result = alt_var_spo2(var_alt, spo2_12h, spo2_24h, hr_12h, hr_24h)
        st.metric("Predicted SpO₂", f"{result.predicted_spo2}%")
        st.info(f"**Model:** {result.model_name} | **R² = {result.confidence}")
        st.info(f"**Note:** {result.notes}")

with spo2_tabs[2]:
    st.subheader("Tüshaus et al. Physiological Cascade Model")
    st.markdown("**Citation:** Tüshaus et al., *Physiological Reports*")
    st.code("PAO₂ = FiO₂ × (PB - PH₂O) with ±2% pulse oximeter tolerance")
    
    col1, col2 = st.columns(2)
    with col1:
        tushaus_alt = st.number_input("Altitude (m)", 0, 8848, 4600, key="tushaus_alt")
        fi_o2_tu = st.slider("FiO₂ (%)", 10, 100, 21, key="fi_o2_tu") / 100
    with col2:
        temp_c_tu = st.number_input("Body Temp (°C)", 35.0, 42.0, 37.0, 0.1, key="temp_c_tu")
    
    if st.button("Calculate SpO₂ (Tüshaus)", key="calc_tushaus"):
        result = tushaus_cascade_spo2(tushaus_alt, fi_o2_tu, temp_c_tu)
        st.metric("Predicted SpO₂", f"{result.predicted_spo2}%")
        st.info(f"**{result.notes}**")
    
    st.subheader("Oxygen Cascade")
    pb = 760 * (1 - 2.25577e-5 * tushaus_alt) ** 5.25588
    ph2o = 6.1078 * np.exp((17.2694 * temp_c_tu) / (temp_c_tu + 237.3)) * 0.750062
    pa_o2 = fi_o2_tu * (pb - ph2o)
    
    cascade = pd.DataFrame({
        'Stage': ['Barometric Pressure', 'Water Vapor', 'Alveolar PAO₂'],
        'Pressure (mmHg)': [pb, ph2o, pa_o2]
    })
    st.bar_chart(cascade.set_index('Stage'))

with spo2_tabs[3]:
    st.subheader("Model Comparison")
    
    comp_alt_min = st.number_input("Min Altitude (m)", 0, 6000, 0, key="comp_min")
    comp_alt_max = st.number_input("Max Altitude (m)", 0, 6000, 6000, key="comp_max")
    comp_sex = st.selectbox("Sex for comparison", ["male", "female"], key="comp_sex")
    
    if st.button("Generate Comparison Plot", key="gen_comp"):
        alt_range = np.linspace(comp_alt_min, comp_alt_max, 100)
        
        results_male = [niermeyer_spo2(int(a), comp_sex).predicted_spo2 for a in alt_range]
        results_tushaus = [tushaus_cascade_spo2(int(a)).predicted_spo2 for a in alt_range]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=alt_range, y=results_male, name=f"Niermeyer ({comp_sex})", mode="lines"))
        fig.add_trace(go.Scatter(x=alt_range, y=results_tushaus, name="Tüshaus Cascade", mode="lines", line=dict(dash='dash')))
        fig.add_hline(y=90, line_dash="dot", line_color="red", annotation_text="90% threshold")
        fig.add_hline(y=85, line_dash="dot", line_color="orange", annotation_text="85% threshold")
        fig.update_layout(title="SpO₂ Model Comparison", xaxis_title="Altitude (m)", yaxis_title="SpO₂ (%)", height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Model Differences:**
        - **Niermeyer**: Simple linear, sex-adjusted, NO acclimatization
        - **Tüshaus**: Physiological cascade, PAO₂-based, ±2% tolerance  
        - **Alt VAR**: Requires historical data, captures acclimatization dynamics
        """)