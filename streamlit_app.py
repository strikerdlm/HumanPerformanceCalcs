import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import plotly.graph_objects as go  # type: ignore
import plotly.express as px  # type: ignore
from plotly.subplots import make_subplots  # type: ignore
from datetime import datetime
import math
import numpy as np
import io
from contextlib import contextmanager

from calculators import (
    standard_atmosphere,
    alveolar_PO2,
    spo2_unacclimatized,
    spo2_acclimatized,
    pao2_at_altitude,
    ams_probability,
    hape_risk_suona2023,
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
    utci,
    utci_category,
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
    cold_water_survival,
    AEROSPACE_CHEMICALS,
    predicted_heat_strain,
    PredictedHeatStrainResult,
    simulate_phs_trajectory,
    simulate_mitler_trajectory,
    plan_zh_l16_gf,
    GasMix,
    AgsmInputs,
    estimate_gz_tolerance_with_agsm,
    SpatialDisorientationInputs,
    spatial_disorientation_risk,
    SafteInputs,
    SafteParameters,
    SleepEpisode,
    simulate_safte,
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


@st.cache_data(show_spinner=False, max_entries=128)
def _compute_isa_profile(max_alt_m: float, n_points: int = 120) -> dict[str, np.ndarray]:
    """Compute ISA profiles for plotting (cached).

    Notes
    - Cached to keep Streamlit UI responsive when sliders change.
    - Returns numpy arrays for direct Plotly usage.
    """

    max_alt = float(max_alt_m)
    if max_alt <= 0.0:
        raise ValueError("max_alt_m must be > 0")
    n = int(n_points)
    if n < 2 or n > 2000:
        raise ValueError("n_points must be between 2 and 2000")

    altitudes = np.linspace(0.0, max_alt, n)
    temps = np.empty_like(altitudes)
    pressures_hpa = np.empty_like(altitudes)
    for i, alt in enumerate(altitudes):
        isa = standard_atmosphere(float(alt))
        temps[i] = float(isa["temperature_C"])
        pressures_hpa[i] = float(isa["pressure_Pa"]) / 100.0

    return {"alt_m": altitudes, "temp_c": temps, "pressure_hpa": pressures_hpa}

# Page configuration
st.set_page_config(
    page_title="Aerospace Physiology & Occupational Health Calculators",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Neutral “crystal / liquid glass” styling (no injected colors; works in light/dark mode)
# Note: Streamlit doesn't provide stable per-component class hooks, so we apply this to:
# - `.info-box` style callouts already used throughout the app
# - `neutral_box()` containers via a marker element + `:has()` selector (supported in modern Chromium/Edge)
st.markdown(
    """
<style>
  /* Hide the marker node (used only to target crystal containers). */
  .crystal-box-marker {
    display: none;
  }

  /* Crystal callouts (used by existing HTML blocks). */
  .info-box, .warning-box, .danger-box, .success-box {
    border-radius: 16px;
    padding: 0.95rem 1.05rem;
    border: 1px solid rgba(0, 0, 0, 0.10);
    background: rgba(255, 255, 255, 0.55);
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.10);
    backdrop-filter: blur(18px) saturate(165%);
    -webkit-backdrop-filter: blur(18px) saturate(165%);
  }

  /* Crystal containers created via neutral_box(). */
  div[data-testid="stContainer"]:has(.crystal-box-marker) {
    border-radius: 16px;
    border: 1px solid rgba(0, 0, 0, 0.10);
    background: rgba(255, 255, 255, 0.55);
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.10);
    backdrop-filter: blur(18px) saturate(165%);
    -webkit-backdrop-filter: blur(18px) saturate(165%);
  }

  /* Dark mode: keep it neutral (no hues), just invert translucency and borders. */
  @media (prefers-color-scheme: dark) {
    .info-box, .warning-box, .danger-box, .success-box {
      border: 1px solid rgba(255, 255, 255, 0.14);
      background: rgba(0, 0, 0, 0.28);
      box-shadow: 0 18px 50px rgba(0, 0, 0, 0.40);
    }

    div[data-testid="stContainer"]:has(.crystal-box-marker) {
      border: 1px solid rgba(255, 255, 255, 0.14);
      background: rgba(0, 0, 0, 0.28);
      box-shadow: 0 18px 50px rgba(0, 0, 0, 0.40);
    }
  }
</style>
""",
    unsafe_allow_html=True,
)

@contextmanager
def crystal_container(*, in_sidebar: bool = False, border: bool = True):
    """Create a neutral 'crystal' container for card/box UI.

    Notes
    - The crystal look is applied via CSS to containers that include the hidden marker.
    - This intentionally avoids any colored styling so it stays compatible with dark mode.
    """
    if not isinstance(in_sidebar, bool):
        raise TypeError("in_sidebar must be a bool")
    if not isinstance(border, bool):
        raise TypeError("border must be a bool")

    target = st.sidebar if in_sidebar else st
    box = target.container(border=border)
    with box:
        st.markdown('<span class="crystal-box-marker"></span>', unsafe_allow_html=True)
        yield

def neutral_box(markdown_text: str, *, in_sidebar: bool = False) -> None:
    """Render a neutral, theme-safe bordered callout (styled via crystal CSS)."""
    if not isinstance(markdown_text, str):
        raise TypeError("markdown_text must be a str")
    text = markdown_text.strip()
    if not text:
        raise ValueError("markdown_text must be non-empty")

    with crystal_container(in_sidebar=in_sidebar, border=True):
        st.markdown(text)

ROADMAP_PHASE_ONE = [
    {
        "name": "ISO 7933 Predicted Heat Strain",
        "status": "Live",
        "description": "Core temperature + hydration guardrails",
    },
    {
        "name": "Simulation Studio",
        "status": "Live",
        "description": "Forward trajectories + next-step forecasts",
    },
    {
        "name": "Universal Thermal Climate Index",
        "status": "Live",
        "description": "Outdoor thermal comfort envelope",
    },
    {
        "name": "Cold Water Immersion Survival",
        "status": "Live",
        "description": "Hayward–Tikuisis survival curves",
    },
    {
        "name": "Bühlmann ZH-L16 Decompression Algorithm",
        "status": "Live",
        "description": "16-compartment decompression + gradient factors",
    },
    {
        "name": "AGSM Effectiveness Model",
        "status": "Live",
        "description": "Quantify anti-G straining and suit benefit",
    },
    {
        "name": "Spatial Disorientation Risk Assessment",
        "status": "Live",
        "description": "Vestibular + flight condition risk scoring",
    },
]

# Minimal per-item details (lifted from docs/ROADMAP.md) for "coming soon" pages.
# Keep this neutral and informational; do not inject color styling here.
ROADMAP_ITEM_DETAILS: dict[str, dict[str, object]] = {
    "Universal Thermal Climate Index": {
        "phase": "Phase 1",
        "references": [
            "Jendritzky, G., de Dear, R., & Havenith, G. (2012). UTCI—why another thermal index? International Journal of Biometeorology, 56(3), 421–428.",
            "Bröde, P., Fiala, D., Błażejczyk, K., et al. (2012). Deriving the operational procedure for the Universal Thermal Climate Index (UTCI). International Journal of Biometeorology, 56(3), 481–494.",
        ],
    },
    "Cold Water Immersion Survival": {
        "phase": "Phase 1",
        "references": [
            "Tikuisis, P. (1997). Prediction of survival time at sea based on observed body cooling rates. Aviation, Space, and Environmental Medicine, 68(5), 441–448.",
            "Hayward, J. S., Eckerson, J. D., & Collis, M. L. (1975). Effect of behavioral variables on cooling rate of man in cold water. Journal of Applied Physiology, 38(6), 1073–1077.",
            "Xu, X., Tikuisis, P., & Giesbrecht, G. (2005). A mathematical model for human brain cooling during cold-water near-drowning. Journal of Applied Physiology, 99(4), 1428–1435.",
        ],
    },
    "Bühlmann ZH-L16 Decompression Algorithm": {
        "phase": "Phase 1",
        "references": [
            "Bühlmann, A. A. (1984). Decompression-Decompression Sickness. Springer-Verlag.",
            "Bühlmann, A. A. (2002). Tauchmedizin: Barotrauma, Gasembolie, Dekompression, Dekompressionskrankheit (5th ed.). Springer.",
            "Gerth, W. A., & Doolette, D. J. (2007). VVal-18 and VVal-18M thalmann algorithm-based air decompression tables and procedures. NEDU TR 07-09.",
        ],
    },
    "AGSM Effectiveness Model": {
        "phase": "Phase 1",
        "references": [
            "Wood, E. H., Lambert, E. H., Baldes, E. J., & Code, C. F. (1946). Effects of acceleration in relation to aviation. Federation Proceedings, 5, 327–344.",
            "Whinnery, J. E. (1991). Methods for describing and quantifying +Gz-induced loss of consciousness. Aviation, Space, and Environmental Medicine, 62(8), 738–742.",
            "Eiken, O., & Mekjavic, I. B. (2016). Ischaemia-reperfusion and G-LOC: a review of the pathophysiology. Aviation, Space, and Environmental Medicine, 87(6), 584–594.",
        ],
    },
    "Spatial Disorientation Risk Assessment": {
        "phase": "Phase 1",
        "references": [
            "Benson, A. J. (1999). Spatial disorientation—common illusions. In Aviation Medicine (3rd ed.). Butterworth-Heinemann.",
            "Previc, F. H., & Ercoline, W. R. (2004). Spatial Disorientation in Aviation. AIAA.",
            "Cheung, B. (2013). Spatial disorientation: more than just illusion. Aviation, Space, and Environmental Medicine, 84(11), 1211–1214.",
        ],
    },
}


def _coming_soon_label(item_name: str) -> str:
    """Build a stable navigation label for roadmap items that are not yet live."""
    if not isinstance(item_name, str):
        raise TypeError("item_name must be a str")
    name = item_name.strip()
    if not name:
        raise ValueError("item_name must be non-empty")
    return f"🚧 {name} (Coming soon)"


COMING_SOON_NAV: dict[str, dict[str, object]] = {}
for _item in ROADMAP_PHASE_ONE:
    if _item.get("status") != "Live":
        _name = str(_item.get("name", "")).strip()
        if _name:
            COMING_SOON_NAV[_coming_soon_label(_name)] = {
                "name": _name,
                "status": str(_item.get("status", "Planned")),
                "description": str(_item.get("description", "")),
            }


def _request_navigation(target: str) -> None:
    """Request navigation to a new sidebar selection on the next rerun.

    Streamlit forbids mutating a session_state key after the widget with that key is
    instantiated in the same run. We therefore write to a separate key and apply it
    before the selectbox is created.
    """
    if not isinstance(target, str):
        raise TypeError("target must be a str")
    nav_target = target.strip()
    if not nav_target:
        raise ValueError("target must be non-empty")
    st.session_state["nav_to"] = nav_target

# Main header
st.title("🚀 Aerospace Physiology & Occupational Health Calculators")

# Sidebar navigation
st.sidebar.markdown("## 📋 Navigation")
if "nav_to" in st.session_state:
    # Apply pending navigation BEFORE the selectbox is instantiated.
    st.session_state["calculator_category"] = st.session_state.pop("nav_to")
calculator_category = st.sidebar.selectbox(
    "Select Calculator Category",
    [
        "🏠 Home",
        "🗺️ Roadmap",
        *list(COMING_SOON_NAV.keys()),
        "🌍 Atmospheric & Physiological",
        "🩺 Clinical Calculators",
        "Occupational Health & Safety",
        "🔬 Environmental Monitoring",
        "🧠 Fatigue & Circadian",
        "🧪 Simulation Studio",
        "📈 Visualization Studio",
        "📊 Risk Assessment Tools"
    ],
    key="calculator_category",
)

# Disclaimer
st.sidebar.markdown("---")
neutral_box(
    "**Important Disclaimer**\n\n"
    "These calculators are for educational and research purposes only.\n"
    "Do not use for operational decision-making without professional validation.",
    in_sidebar=True,
)

if calculator_category == "🏠 Home":
    hero_left, hero_right = st.columns([2.2, 1.2])

    with hero_left:
        st.caption("Aerospace Medicine Ops Suite")
        st.header("Modern calculators for extreme environments")
        st.write(
            "Run atmospheric physiology, occupational exposure, circadian, and risk assessment workflows in one place. "
            "Models are referenced, vetted, and tuned for aerospace realities."
        )
        neutral_box(
            "- New: ISO 7933 Predicted Heat Strain\n"
            "- ACGIH TLV® + BEI 2024\n"
            "- Plotly + ECharts visual lab"
        )
        st.caption('Roadmap momentum → Phase 1 item "Predicted Heat Strain" is now live in-app.')

    with hero_right:
        with crystal_container(border=True):
            st.markdown("**Mission-ready snapshot**")
            st.metric("Calculators", "29+")
            st.metric("Chemical DB", f"{len(AEROSPACE_CHEMICALS)}")
            st.metric("Compliance", "ACGIH 2024")
            st.caption("Noise · heat · chemicals · biological monitoring")

    st.subheader("Mission-ready focus areas")
    mission_cols = st.columns(3)
    mission_descriptions = [
        ("🌍 Physiology & Atmosphere", ["ISA layers & hypoxia cascade", "TUC + decompression guardrails", "Cosmic radiation planning"]),
        ("🛡️ Occupational & Risk", ["ACGIH TLV® / BEI workflows", "Mixed exposure + TLV scheduling", "Automated reporting exports"]),
        ("🧠 Fatigue & Performance", ["Circadian performance envelopes", "Two-process sleep modelling", "Jet lag + Mitler vigilance"]),
    ]
    for col, (title, bullets) in zip(mission_cols, mission_descriptions):
        with col:
            neutral_box("**" + title + "**\n\n" + "\n".join(f"- {b}" for b in bullets))

    st.subheader("Roadmap momentum")
    roadmap_cols = st.columns(4)
    for idx, info in enumerate(ROADMAP_PHASE_ONE[:4]):
        col = roadmap_cols[idx % 4]
        with col:
            neutral_box(f"**{info['name']}**\n\n{info['status']} · {info['description']}")

    st.markdown("#### Quick launch")
    launch_cols = st.columns(4)
    launch_targets = [
        ("🌍 Physiology", "🌍 Atmospheric & Physiological", "Atmosphere, hypoxia, decompression, radiation"),
        ("🩺 Clinical", "🩺 Clinical Calculators", "Bedside indices and clinical physiology tools"),
        ("🛡️ Occupational", "Occupational Health & Safety", "Noise, chemicals, TLVs/BEIs and reporting"),
        ("🧪 Simulation", "🧪 Simulation Studio", "Forward trajectories (PHS, circadian envelopes)"),
    ]
    for i, (label, target, subtitle) in enumerate(launch_targets):
        with launch_cols[i]:
            with crystal_container(border=True):
                st.markdown(f"**{label}**")
                st.caption(subtitle)
                st.button(
                    "Open",
                    key=f"quick_launch_{i}",
                    on_click=_request_navigation,
                    args=(target,),
                )

    neutral_box(
        "Need a specific calculator fast? Use the sidebar navigation or jump into the Visualization Studio for bespoke plots."
    )

elif calculator_category == "🗺️ Roadmap":
    st.subheader("Roadmap")
    st.caption("Derived from `docs/ROADMAP.md` (Phase 1 highlighted).")

    with crystal_container(border=True):
        st.markdown("**Phase 1 — High-Priority Additions (0–6 months)**")
        for item in ROADMAP_PHASE_ONE:
            st.markdown(f"- **{item['name']}** — {item['status']} · {item['description']}")

    st.markdown("#### Phase 1: coming soon")
    soon_cols = st.columns(3)
    soon_items = [v for v in COMING_SOON_NAV.values()]
    for idx, item in enumerate(soon_items):
        col = soon_cols[idx % 3]
        with col:
            with crystal_container(border=True):
                st.markdown(f"**{item['name']}**")
                st.caption(f"{item['status']} · {item['description']}")
                st.button(
                    "Open preview",
                    key=f"roadmap_open_preview_{idx}",
                    on_click=_request_navigation,
                    args=(_coming_soon_label(str(item["name"])),),
                )

    with st.expander("View full roadmap (from docs/ROADMAP.md)", expanded=False):
        try:
            with open("docs/ROADMAP.md", "r", encoding="utf-8") as f:
                roadmap_md = f.read()
        except OSError as e:
            st.error(f"Unable to read docs/ROADMAP.md: {e}")
        else:
            st.markdown(roadmap_md)

elif calculator_category in COMING_SOON_NAV:
    item = COMING_SOON_NAV[calculator_category]
    name = str(item["name"])
    status = str(item["status"])
    description = str(item["description"])
    details = ROADMAP_ITEM_DETAILS.get(name, {})
    phase = str(details.get("phase", "Phase 1"))
    refs = details.get("references", [])
    if not isinstance(refs, list):
        refs = []

    st.subheader(f"{name} — coming soon")
    st.caption(f"{phase} · Status: {status}")

    with crystal_container(border=True):
        st.markdown("**What you’ll get**")
        st.markdown(f"- {description}" if description else "- Roadmap item (details pending)")

    with crystal_container(border=True):
        st.markdown("**Why this is on the roadmap**")
        st.markdown(
            "This section is a placeholder UI preview so users can see what’s planned and why, "
            "without breaking the current calculators."
        )

    if refs:
        with crystal_container(border=True):
            st.markdown("**Key references (from `docs/ROADMAP.md`)**")
            for r in refs:
                if isinstance(r, str) and r.strip():
                    st.markdown(f"- {r.strip()}")

    col_back1, col_back2 = st.columns([1, 1])
    with col_back1:
        st.button(
            "Back to Roadmap",
            key="coming_soon_back_to_roadmap",
            on_click=_request_navigation,
            args=("🗺️ Roadmap",),
        )
    with col_back2:
        st.button(
            "Back to Home",
            key="coming_soon_back_to_home",
            on_click=_request_navigation,
            args=("🏠 Home",),
        )

elif calculator_category == "🌍 Atmospheric & Physiological":
    st.subheader("Atmospheric & Physiological Calculators")
    
    calc_type = st.selectbox(
        "Choose Calculator",
        [
            "Standard Atmosphere Properties",
            "Alveolar Oxygen Pressure", 
            "Altitude & Hypoxia Predictions",
            "Acute Mountain Sickness Risk",
            "HAPE Risk (Suona 2023 Nomogram)",
            "Oxygen Cascade",
            "Decompression Tissue Ratio (TR)",
            "Bühlmann ZH-L16 GF Decompression Planner",
            "AGSM Effectiveness (Anti-G +Gz)",
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
        
        # Create visualization (cached computation)
        profile = _compute_isa_profile(max_alt_m=20_000.0, n_points=140)
        
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=profile["temp_c"],
                y=profile["alt_m"] / 1000.0,
                mode="lines",
                name="Temperature",
            )
        )
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

    elif calc_type == "HAPE Risk (Suona 2023 Nomogram)":
        st.markdown("### 🫁 High-Altitude Pulmonary Edema (HAPE) Risk")
        st.markdown(
            "This calculator implements the published HAPE risk prediction "
            "nomogram (**model 1 with SpO₂**) from Suona et al., *BMJ Open* "
            "2023;13:e074161, using age, mode of transport, symptoms, and "
            "oxygen saturation measured at altitude."
        )
        col1, col2 = st.columns([1, 1])
        with col1:
            age_years = st.number_input("Age (years)", min_value=14, max_value=80, value=30, step=1)
            transport_label = st.selectbox(
                "Mode of travel to high altitude",
                [
                    "Aeroplane",
                    "Train",
                    "Vehicle / Other",
                ],
            )
            fatigue = st.checkbox("Fatigue", value=True)
            cough = st.checkbox("Cough", value=True)
            sputum = st.checkbox("Coughing sputum (white or pink, foamy)", value=False)
            spo2 = st.slider("SpO₂ at altitude (%)", min_value=50, max_value=100, value=78, step=1)

        # Normalise transport mode for the model
        transport_mode: str
        if "train" in transport_label.lower():
            transport_mode = "train"
        elif "plane" in transport_label.lower():
            transport_mode = "plane"
        else:
            transport_mode = "vehicle"

        # Ensure logical consistency between cough and sputum
        if sputum and not cough:
            cough = True

        result = hape_risk_suona2023(
            age_years=float(age_years),
            spo2_percent=float(spo2),
            transport_mode=transport_mode,
            fatigue=bool(fatigue),
            cough=bool(cough),
            sputum=bool(sputum),
        )

        with col2:
            st.markdown("#### Results")
            st.metric("Predicted HAPE Risk", f"{result.probability * 100:.1f} %")
            st.metric("Nomogram Total Points", f"{result.total_points:.1f}")
            if result.probability < 0.1:
                assessment = "Low estimated risk (within this model)"
            elif result.probability < 0.5:
                assessment = "Moderate estimated risk (within this model)"
            else:
                assessment = "High estimated risk (within this model)"
            st.markdown(
                f"<div class=\"info-box\"><strong>Assessment:</strong> {assessment}</div>",
                unsafe_allow_html=True,
            )

            st.markdown(
                "<div class=\"info-box\">"
                "Based on the HAPE risk prediction nomogram (model 1 with SpO₂) from "
                "<a href=\"https://doi.org/10.1136/bmjopen-2023-074161\" target=\"_blank\">"
                "Suona et al., BMJ Open 2023;13:e074161</a>. "
                "Implementation details and validation for this app are documented in "
                "<a href=\"https://github.com/strikerdlm/HumanPerformanceCalcs/blob/main/docs/HAPE.md\" target=\"_blank\">docs/HAPE.md</a>. "
                "Educational and research use only; not for clinical decision-making."
                "</div>",
                unsafe_allow_html=True,
            )

            with st.expander("Scientific rationale, model details & references"):
                st.markdown(
                    """
                    **Scientific rationale**

                    - High-altitude pulmonary edema (HAPE) is a non-cardiogenic pulmonary edema
                      triggered by hypobaric hypoxia, typically within the first 2–5 days after
                      ascent to high altitude.
                    - Clinical risk correlates with the degree of hypoxaemia (low SpO₂), speed
                      of ascent and early respiratory symptoms such as fatigue, cough and
                      frothy sputum.

                    **Model used in this calculator**

                    - Suona et al. developed and internally validated a multivariable logistic
                      regression model for HAPE among travellers to the Qinghai–Tibet plateau,
                      then presented it as a nomogram (Figure 2A).
                    - Predictors: age, mode of transport (aeroplane / train / vehicle),
                      fatigue, cough, expectoration, and SpO₂ at altitude (model 1 with SpO₂).
                    - This app reproduces that nomogram by assigning points to each predictor
                      (digitised from Figure 2A), summing them to a total score, and converting
                      that score to probability using a logistic curve calibrated to the
                      nomogram's \"Total Points → Risk\" scale.
                    - Implementation details, assumptions and unit tests are documented in
                      `docs/HAPE.md` in the HumanPerformanceCalcs repository.

                    **Key references**

                    - Suona Y, et al. *Predictive model for estimating the risk of high-altitude
                      pulmonary edema: a single-centre retrospective outcome-reporting study*.
                      BMJ Open. 2023;13:e074161. doi:10.1136/bmjopen-2023-074161.
                    - App-specific documentation:
                      https://github.com/strikerdlm/HumanPerformanceCalcs/blob/main/docs/HAPE.md
                    """
                )

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

    elif calc_type == "Bühlmann ZH-L16 GF Decompression Planner":
        st.markdown("### 🧮 Bühlmann ZH‑L16 (Gradient Factors) Decompression Planner")

        neutral_box(
            "**Research/education use only.** Deterministic Bühlmann ZH‑L16 GF planner (ZH‑L16C/B), "
            "unit-tested against an external reference stop schedule.\n\n"
            "It does not model bubble dynamics or individual susceptibility."
        )

        with crystal_container(border=True):
            st.markdown("**Profile inputs**")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                depth_m = float(st.slider("Max depth (m)", 0.0, 100.0, 40.0, step=1.0))
                profile_minutes = float(st.slider("“for X minutes” (min)", 1.0, 240.0, 35.0, step=1.0))
            with col_b:
                gf_low = float(st.slider("GF Low", 0.05, 1.00, 0.30, step=0.01))
                gf_high = float(st.slider("GF High", 0.10, 1.00, 0.85, step=0.01))
            with col_c:
                descent_rate = float(st.slider("Descent rate (m/min)", 5.0, 40.0, 20.0, step=1.0))
                ascent_rate = float(st.slider("Ascent rate (m/min)", 3.0, 20.0, 10.0, step=1.0))

        with crystal_container(border=True):
            st.markdown("**Gas + environment**")
            col_g1, col_g2, col_g3 = st.columns(3)
            with col_g1:
                o2_percent = float(st.slider("O₂ (%)", 10.0, 100.0, 21.0, step=1.0))
                he_percent = float(st.slider("He (%)", 0.0, 80.0, 0.0, step=1.0))
            with col_g2:
                model_variant = st.selectbox("Model variant", ["zh-l16c-gf", "zh-l16b-gf"], index=0)
                include_descent = st.checkbox(
                    "Interpret “for X minutes” as runtime at max depth (includes descent)",
                    value=True,
                    help=(
                        "If enabled, time at depth is computed as max(0, X − descent_time). "
                        "This matches the convention used by some planners and the external reference schedule."
                    ),
                )
            with col_g3:
                surface_pressure_mbar = float(st.slider("Surface pressure (mbar)", 800.0, 1050.0, 1013.25, step=1.0))

        n2_percent = 100.0 - o2_percent - he_percent
        if n2_percent <= 0.0:
            neutral_box("Gas mix invalid: O₂% + He% must be < 100%.")
        else:
            if st.button("Compute decompression plan", type="primary"):
                try:
                    plan = plan_zh_l16_gf(
                        max_depth_m=depth_m,
                        bottom_time_min=profile_minutes,
                        gas=GasMix(o2=o2_percent / 100.0, he=he_percent / 100.0),
                        include_descent_in_bottom_time=bool(include_descent),
                        gf_low=gf_low,
                        gf_high=gf_high,
                        model=model_variant,  # type: ignore[arg-type]
                        surface_pressure_bar=surface_pressure_mbar / 1000.0,
                        descent_rate_m_per_min=descent_rate,
                        ascent_rate_m_per_min=ascent_rate,
                        stop_step_m=3.0,
                    )
                except (ValueError, TypeError, RuntimeError) as e:
                    neutral_box(f"**Unable to compute plan**\n\n- {e}")
                else:
                    with crystal_container(border=True):
                        st.markdown("**Decompression stops (3 m increments)**")
                        if not plan.stops:
                            st.markdown("- No decompression stops required for this profile (per model settings).")
                        else:
                            df = pd.DataFrame(
                                [{"Stop depth (m)": float(s.depth_m), "Stop time (min)": int(s.minutes)} for s in plan.stops]
                            )
                            st.dataframe(df, use_container_width=True, hide_index=True)
                            st.metric("Total decompression time", f"{plan.total_decompression_minutes} min")

                    with crystal_container(border=True):
                        st.markdown("**Model notes**")
                        st.markdown(
                            "- Tissue loading uses the Schreiner equation.\n"
                            "- Ascent ceilings use Bühlmann ZH‑L16 A/B coefficients with Erik Baker Gradient Factors.\n"
                            "- Depth↔pressure conversion uses 0.09985 bar/m (OSTC/DecoTengu convention)."
                        )

    elif calc_type == "AGSM Effectiveness (Anti-G +Gz)":
        st.markdown("### 🛡️ AGSM Effectiveness Model (+Gz)")

        neutral_box(
            "**Research/education use only.** This tool estimates how anti‑G equipment and AGSM quality can shift +Gz tolerance.\n\n"
            "Default deltas are anchored to a published comparative study of configurations (no suit, suit, suit+PBG, suit+AGSM, suit+PBG+AGSM)."
        )

        with crystal_container(border=True):
            st.markdown("**Inputs**")
            col1, col2, col3 = st.columns(3)
            with col1:
                baseline = float(st.slider("Baseline relaxed tolerance (Gz)", 1.0, 8.0, 3.4, step=0.1))
                agsm_quality = float(st.slider("AGSM quality (0–100%)", 0.0, 100.0, 100.0, step=1.0))
            with col2:
                anti_g_suit = st.checkbox("Anti‑G suit (AGS) worn", value=True)
                pbg = st.checkbox("Pressure breathing for G (PBG/PBfG)", value=False, disabled=not anti_g_suit)
            with col3:
                max_cap = float(st.slider("Physiologic/equipment cap (Gz)", 6.0, 12.0, 9.0, step=0.1))

        with crystal_container(border=True):
            st.markdown("**Model parameters (advanced; defaults from literature anchor)**")
            c1, c2, c3 = st.columns(3)
            with c1:
                suit_delta = float(st.slider("Suit delta (Gz)", 0.0, 6.0, 3.1, step=0.1))
            with c2:
                pbg_delta = float(st.slider("PBG delta (Gz)", 0.0, 4.0, 1.5, step=0.1))
            with c3:
                agsm_delta = float(st.slider("AGSM delta at 100% (Gz)", 0.0, 6.0, 2.4, step=0.1))

        try:
            res = estimate_gz_tolerance_with_agsm(
                AgsmInputs(
                    baseline_relaxed_gz=baseline,
                    anti_g_suit=bool(anti_g_suit),
                    pressure_breathing_for_g=bool(pbg),
                    agsm_quality=float(agsm_quality / 100.0),
                    suit_delta_gz=suit_delta,
                    pbg_delta_gz=pbg_delta,
                    agsm_delta_gz=agsm_delta,
                    max_system_gz=max_cap,
                )
            )
        except (TypeError, ValueError) as e:
            neutral_box(f"**Unable to compute**\n\n- {e}")
        else:
            with crystal_container(border=True):
                st.markdown("**Outputs**")
                st.metric("Estimated +Gz tolerance", f"{res.capped_estimated_gz:.2f} Gz")
                if res.was_capped:
                    st.caption("Capped at the configured max (represents saturation/limits of the protection ensemble).")

                df = pd.DataFrame(
                    [
                        {"Component": "Baseline (relaxed)", "ΔGz": res.baseline_relaxed_gz},
                        {"Component": "Anti‑G suit", "ΔGz": res.suit_component_gz},
                        {"Component": "Pressure breathing (PBG)", "ΔGz": res.pbg_component_gz},
                        {"Component": "AGSM (quality‑scaled)", "ΔGz": res.agsm_component_gz},
                        {"Component": "Raw sum", "ΔGz": res.raw_estimated_gz},
                    ]
                )
                st.dataframe(df, use_container_width=True, hide_index=True)

            with crystal_container(border=True):
                st.markdown("**Reference anchor**")
                st.markdown(
                    "- Study comparing configurations during rapid-onset +Gz profiles: `PubMed 17484342`.\n"
                    "- Default parameters mirror those reported condition values (and are user-adjustable)."
                )

elif calculator_category == "🩺 Clinical Calculators":
    st.subheader("Clinical Calculators")
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
            fig.add_vline(x=float(scr), line_dash='dash')
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
                "series": [{"type": "bar", "data": [float(ratio)], "itemStyle": {"borderRadius": [6,6,0,0]}}],
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
    st.subheader("Occupational Health & Safety Calculators")
    
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
    st.subheader("Environmental Monitoring Calculators")
    
    calc_type = st.selectbox(
        "Choose Calculator",
        [
            "Universal Thermal Climate Index (UTCI)",
            "Cold Water Immersion Survival Time",
            "Heat Stress Index (WBGT)",
            "Heat Stress Index (HSI)",
            "Predicted Heat Strain (ISO 7933)",
            "Cold Exposure: Peak Shivering",
            "Noise Exposure Assessment"
        ]
    )
    
    if calc_type == "Universal Thermal Climate Index (UTCI)":
        st.markdown("### 🧊 Universal Thermal Climate Index (UTCI)")
        st.caption("Outdoor ‘feels-like’ equivalent temperature (polynomial approximation).")

        col1, col2 = st.columns([1, 1])
        with col1:
            ta_c = st.number_input("Air temperature Ta (°C)", -50.0, 60.0, 20.0, step=0.5)
            tr_c = st.number_input("Mean radiant temperature Tr (°C)", -50.0, 90.0, 20.0, step=0.5)
            wind_10m = st.number_input("Wind speed at 10 m (m/s)", 0.0, 30.0, 2.0, step=0.1)
            rh = st.slider("Relative humidity (%)", 0, 100, 50, step=1)
            strict = st.checkbox(
                "Strict validity bounds",
                value=False,
                help="If enabled, raises an error when inputs are outside common UTCI_approx validity bounds.",
            )

        with col2:
            st.markdown("#### Results")
            try:
                utci_c = utci(
                    air_temperature_c=float(ta_c),
                    mean_radiant_temperature_c=float(tr_c),
                    wind_speed_10m_m_s=float(wind_10m),
                    relative_humidity_percent=float(rh),
                    strict=bool(strict),
                    clamp_wind=True,
                )
            except ValueError as e:
                st.error(f"Input out of bounds: {e}")
            else:
                st.metric("UTCI (equivalent temperature)", f"{utci_c:.2f} °C", utci_category(utci_c))
                neutral_box(
                    "**Interpretation**\n\n"
                    "UTCI is categorized on a 10-level thermal stress scale (heat/cold stress). "
                    "This value is intended for outdoor thermal assessment; it is not a substitute "
                    "for operational risk management without context and validation."
                )

    elif calc_type == "Cold Water Immersion Survival Time":
        st.markdown("### 🌊 Cold Water Immersion Survival Time")
        st.caption("Hypothermia-limited guidance for immersion in cold water (does not model cold shock or swim failure).")

        model_choice = st.radio(
            "Model",
            [
                "Hayward et al. (1975) — temperature-only equation",
                "Golden (1996) cited in TP 13822 — fully clothed + lifejacket (5–15°C)",
            ],
            horizontal=False,
        )
        model = "hayward_1975" if model_choice.startswith("Hayward") else "golden_lifejacket_tp13822"

        col1, col2 = st.columns([1, 1])
        with col1:
            water_temp_c = st.number_input("Water temperature (°C)", -2.0, 30.0, 10.0, step=0.5)
            strict = st.checkbox(
                "Strict validity bounds",
                value=True,
                help="If enabled, raises an error when inputs are outside the supported ranges for the chosen model.",
            )

            neutral_box(
                "**Important**\n\n"
                "- **Cold shock** can be fatal in ~3–5 minutes.\n"
                "- **Swimming failure** can occur in under ~30 minutes.\n"
                "- These estimates are **hypothermia-limited** only; drowning risk can dominate earlier."
            )

        with col2:
            st.markdown("#### Results")
            try:
                est = cold_water_survival(float(water_temp_c), model=model, strict=bool(strict))
            except ValueError as e:
                st.error(f"Input out of bounds: {e}")
            else:
                st.metric("Estimated survival time", f"{est.survival_time_hours:.2f} hours", f"{est.survival_time_minutes:.0f} min")
                with crystal_container(border=True):
                    st.markdown("**Model notes**")
                    for n in est.notes:
                        st.markdown(f"- {n}")

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
    
    elif calc_type == "Predicted Heat Strain (ISO 7933)":
        st.markdown("### ♨️ Predicted Heat Strain (ISO 7933 inspired)")
        input_col1, input_col2 = st.columns(2)
        with input_col1:
            metabolic_rate = st.slider("Metabolic rate (W/m²)", 150.0, 650.0, 380.0, step=10.0)
            clothing = st.slider("Clothing insulation (clo)", 0.3, 1.6, 0.9, step=0.1)
            air_velocity = st.slider("Air speed (m/s)", 0.1, 3.0, 0.6, step=0.1)
        with input_col2:
            air_temp = st.slider("Air temperature (°C)", 20.0, 50.0, 32.0, step=0.5)
            mean_radiant = st.slider("Mean radiant / globe (°C)", 20.0, 60.0, 38.0, step=0.5)
            rh = st.slider("Relative humidity (%)", 10.0, 100.0, 55.0, step=1.0)
            exposure = st.slider("Exposure duration (min)", 15.0, 240.0, 90.0, step=5.0)

        with st.expander("Advanced physiology assumptions", expanded=False):
            mechanical_power = st.slider("External mechanical power (W/m²)", 0.0, 80.0, 0.0, step=5.0)
            body_mass = st.slider("Body mass (kg)", 55.0, 110.0, 75.0, step=1.0)
            body_surface_area = st.slider("Body surface area (m²)", 1.4, 2.4, 1.9, step=0.05)
            baseline_core = st.slider("Baseline core temperature (°C)", 36.5, 37.5, 37.0, step=0.1)
            core_limit = st.slider("Core temperature limit (°C)", 37.5, 39.5, 38.5, step=0.1)
            dehydration_limit = st.slider("Dehydration limit (% body mass)", 2.0, 7.0, 5.0, step=0.5)

        phs_result = predicted_heat_strain(
            metabolic_rate_w_m2=float(metabolic_rate),
            air_temperature_C=float(air_temp),
            mean_radiant_temperature_C=float(mean_radiant),
            relative_humidity_percent=float(rh),
            air_velocity_m_s=float(air_velocity),
            clothing_insulation_clo=float(clothing),
            exposure_minutes=float(exposure),
            mechanical_power_w_m2=float(mechanical_power),
            body_mass_kg=float(body_mass),
            body_surface_area_m2=float(body_surface_area),
            baseline_core_temp_C=float(baseline_core),
            core_temp_limit_C=float(core_limit),
            dehydration_limit_percent=float(dehydration_limit),
        )

        stats_col1, stats_col2, stats_col3 = st.columns(3)
        delta_core = phs_result.predicted_core_temperature_C - baseline_core
        with stats_col1:
            st.metric(
                "Predicted core temperature",
                f"{phs_result.predicted_core_temperature_C:.2f} °C",
                f"{delta_core:+.2f} °C vs baseline",
            )
        with stats_col2:
            st.metric(
                "Sweat rate (req / max)",
                f"{phs_result.required_sweat_rate_L_per_h:.2f} / {phs_result.max_sustainable_sweat_rate_L_per_h:.2f} L/h",
            )
            st.caption(f"Effective evaporation uses {phs_result.actual_sweat_rate_L_per_h:.2f} L/h")
        with stats_col3:
            st.metric(
                "Allowable exposure",
                f"{phs_result.allowable_exposure_minutes:.0f} min",
                phs_result.limiting_factor,
            )

        hydration_message = (
            "Monitor hydration closely; dehydration is the limiting factor."
            if phs_result.limiting_factor == "Dehydration limit"
            else "Core temperature guardrail is currently most restrictive."
        )
        st.markdown(
            f"""
            <div class="info-box">
                <strong>Hydration load:</strong> {phs_result.predicted_water_loss_L:.2f} L ({phs_result.dehydration_percent_body_mass:.1f}% body mass).
                {hydration_message}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Core temperature profile visual
        try:
            max_time = float(exposure)
            timeline = np.linspace(5.0, max_time, max(2, int(max_time // 5)))
            temps = [
                predicted_heat_strain(
                    metabolic_rate_w_m2=float(metabolic_rate),
                    air_temperature_C=float(air_temp),
                    mean_radiant_temperature_C=float(mean_radiant),
                    relative_humidity_percent=float(rh),
                    air_velocity_m_s=float(air_velocity),
                    clothing_insulation_clo=float(clothing),
                    exposure_minutes=float(t),
                    mechanical_power_w_m2=float(mechanical_power),
                    body_mass_kg=float(body_mass),
                    body_surface_area_m2=float(body_surface_area),
                    baseline_core_temp_C=float(baseline_core),
                    core_temp_limit_C=float(core_limit),
                    dehydration_limit_percent=float(dehydration_limit),
                ).predicted_core_temperature_C
                for t in timeline
            ]
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=timeline,
                    y=temps,
                    mode="lines",
                    name="Core temp",
                )
            )
            fig.add_hline(y=core_limit, line_dash="dash", annotation_text="Core limit")
            fig.update_layout(
                title="Predicted core temperature trajectory",
                xaxis_title="Exposure time (minutes)",
                yaxis_title="Core temperature (°C)",
                height=380,
            )
            st.plotly_chart(fig, use_container_width=True)
        except ValueError:
            st.warning("Unable to render profile for the current inputs.")
    
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
        fig.add_trace(go.Scatter(x=levels, y=osha_times, mode='lines+markers', name='OSHA'))
        fig.add_trace(go.Scatter(x=levels, y=niosh_times, mode='lines+markers', name='NIOSH'))
        fig.update_layout(
            title="Permissible Exposure Time vs Noise Level",
            xaxis_title="Noise Level (dBA)",
            yaxis_title="Permissible Time (hours)",
            yaxis_type="log"
        )
        st.plotly_chart(fig, use_container_width=True)

elif calculator_category == "📈 Visualization Studio":
    st.subheader("Visualization Studio")

    # Display controls (neutral + theme-safe: no manual palette or custom colors)
    with st.container():
        col_theme, col_height = st.columns([1, 1])

        theme_base = st.get_option("theme.base") or "light"
        theme_template = "plotly_dark" if theme_base == "dark" else "plotly_white"
        col_theme.caption(f"Plot theme: **{theme_template}** (auto)")

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
    st.subheader("Risk Assessment Tools")
    tool = st.selectbox(
        "Choose Tool",
        [
            "Aerospace Chemical Risk Dashboard",
            "Spatial Disorientation Risk Assessment",
        ],
        index=0,
    )

    if tool == "Spatial Disorientation Risk Assessment":
        st.markdown("### 🧭 Spatial Disorientation (SD) Risk Assessment")

        neutral_box(
            "**Research/education use only.** This tool computes a transparent SD Risk Index (0–100) from "
            "physiology-grounded components (leans threshold, canal entrainment window, Coriolis threshold, "
            "somatogravic tilt from GIA).\n\n"
            "It is not a calibrated mishap probability."
        )

        with crystal_container(border=True):
            st.markdown("**Flight conditions**")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                imc = st.checkbox("IMC", value=True)
            with c2:
                night = st.checkbox("Night", value=False)
            with c3:
                nvg = st.checkbox("NVG", value=False)
            with c4:
                time_no_horizon = float(st.slider("Time since horizon reference (s)", 0.0, 180.0, 45.0, step=5.0))

        with crystal_container(border=True):
            st.markdown("**Maneuver / motion**")
            m1, m2, m3 = st.columns(3)
            with m1:
                yaw_rate = float(st.slider("Yaw/turn rate (deg/s)", 0.0, 60.0, 1.0, step=0.5))
                turn_dur = float(st.slider("Sustained turn duration (s)", 0.0, 120.0, 60.0, step=5.0))
            with m2:
                head_move = st.checkbox("Head movement during turn (Coriolis trigger)", value=False)
                workload = float(st.slider("Workload (0–100%)", 0.0, 100.0, 50.0, step=5.0))
            with m3:
                # Somatogravic: forward linear acceleration produces an apparent pitch tilt (GIA).
                forward_accel_g = float(st.slider("Forward acceleration (g)", -0.30, 1.00, 0.00, step=0.02))

        try:
            res = spatial_disorientation_risk(
                SpatialDisorientationInputs(
                    imc=bool(imc),
                    night=bool(night),
                    nvg=bool(nvg),
                    time_since_horizon_reference_s=time_no_horizon,
                    yaw_rate_deg_s=yaw_rate,
                    sustained_turn_duration_s=turn_dur,
                    head_movement_during_turn=bool(head_move),
                    forward_accel_m_s2=forward_accel_g * 9.80665,
                    workload=float(workload / 100.0),
                )
            )
        except (TypeError, ValueError) as e:
            neutral_box(f"**Unable to compute**\n\n- {e}")
        else:
            with crystal_container(border=True):
                st.markdown("**Outputs**")
                st.metric("SD Risk Index (0–100)", f"{res.risk_index_0_100:.1f}")
                st.metric("Risk level", res.risk_level)
                st.metric("Somatogravic tilt (deg)", f"{res.somatogravic_tilt_deg:.1f}")

                if res.likely_illusions:
                    st.markdown("**Likely illusion types (scenario-based)**")
                    for it in res.likely_illusions:
                        st.markdown(f"- {it}")

            with crystal_container(border=True):
                st.markdown("**Component breakdown (0–1)**")
                df_sd = pd.DataFrame(
                    [
                        {"Component": "Cue deprivation", "Score": res.cue_deprivation_component_0_1},
                        {"Component": "Leans (below ~2°/s)", "Score": res.leans_risk_component_0_1},
                        {"Component": "Canal entrainment (~10–20s)", "Score": res.canal_entraintment_component_0_1},
                        {"Component": "Coriolis (head movement; >~10°/s)", "Score": res.coriolis_component_0_1},
                        {"Component": "Somatogravic (GIA tilt)", "Score": res.somatogravic_component_0_1},
                    ]
                )
                st.dataframe(df_sd, use_container_width=True, hide_index=True)

            with st.expander("References (model anchors)", expanded=False):
                st.markdown(
                    "- [FAA: Spatial Disorientation (Airman Education Programs)](https://www.faa.gov/pilots/training/airman_education/topics_of_interest/spatial_disorientation)\n"
                    "- [StatPearls: Physiology of Spatial Orientation (NCBI Bookshelf)](https://www.ncbi.nlm.nih.gov/books/NBK518976/)\n"
                    "- [Houben et al. (2022): Coriolis illusion threshold (PubMed 34924407)](https://pubmed.ncbi.nlm.nih.gov/34924407/)\n"
                    "- [Somatogravic demonstration: 0.58 g ≈ 30° (PubMed 9491247)](https://pubmed.ncbi.nlm.nih.gov/9491247/)"
                )

    else:
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
    st.subheader("Fatigue & Circadian Calculators")

    calc_type = st.selectbox(
        "Choose Calculator",
        [
            "Circadian Performance (Mitler)",
            "Two-Process Model (S & C)",
            "Jet Lag Recovery",
            "SAFTE Effectiveness (patent-derived)",
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

    elif calc_type == "SAFTE Effectiveness (patent-derived)":
        st.markdown("### 🧠 SAFTE Effectiveness (patent-derived)")
        neutral_box(
            "**Research/education use only.** This implements the core SAFTE equations as documented in `WO2012015383A1` "
            "(patent images Eq. 1–9). It does not include FAST-specific sleep prediction or circadian phase shifting/jet-lag logic.\n\n"
            "If you need operational use, confirm licensing and validate against your organization’s reference tool."
        )

        with crystal_container(border=True):
            st.markdown("**Simulation window**")
            c1, c2, c3 = st.columns(3)
            with c1:
                horizon_days = int(st.slider("Horizon (days)", 1, 14, 3, step=1))
            with c2:
                step_minutes = int(st.select_slider("Step (min)", options=[5, 10, 15, 30, 60], value=10))
            with c3:
                start_hour = float(st.slider("Start clock hour (local)", 0.0, 23.0, 8.0, step=0.5))

        with crystal_container(border=True):
            st.markdown("**Sleep schedule (repeating daily)**")
            s1, s2, s3 = st.columns(3)
            with s1:
                sleep_start = float(st.slider("Main sleep start (hour)", 0.0, 23.5, 23.0, step=0.5))
            with s2:
                sleep_duration_h = float(st.slider("Main sleep duration (h)", 0.0, 12.0, 8.0, step=0.25))
            with s3:
                nap_enabled = st.checkbox("Add daily nap", value=False)

            nap_start = 0.0
            nap_duration_h = 0.0
            if nap_enabled:
                n1, n2 = st.columns(2)
                with n1:
                    nap_start = float(st.slider("Nap start (hour)", 0.0, 23.5, 14.0, step=0.5))
                with n2:
                    nap_duration_h = float(st.slider("Nap duration (h)", 0.0, 4.0, 0.5, step=0.25))

        with crystal_container(border=True):
            st.markdown("**Initial state + constants**")
            i1, i2, i3 = st.columns(3)
            with i1:
                initial_reservoir_pct = float(st.slider("Initial reservoir (%)", 0.0, 100.0, 100.0, step=1.0))
            with i2:
                effectiveness_warn = float(st.slider("Warn threshold (%)", 0.0, 100.0, 77.0, step=1.0))
            with i3:
                _ = st.caption("Defaults use patent constants: Rc=2880, K=0.5 units/min, etc.")

        horizon_minutes = int(horizon_days * 24 * 60)
        start_dt = datetime(2025, 1, 1, int(start_hour) % 24, int(round((start_hour % 1.0) * 60)) % 60, 0)

        def _episodes_for_day(day_index: int) -> list[SleepEpisode]:
            base = day_index * 24.0
            eps: list[SleepEpisode] = []
            if sleep_duration_h > 0.0:
                s = base + sleep_start
                e = s + sleep_duration_h
                # Wrap across midnight if needed.
                if e <= base + 24.0 + 1e-12:
                    eps.append(SleepEpisode(start_min=(s - start_hour) * 60.0, end_min=(e - start_hour) * 60.0))
                else:
                    # split: [start, 24) and [0, end-24)
                    eps.append(SleepEpisode(start_min=(s - start_hour) * 60.0, end_min=((base + 24.0) - start_hour) * 60.0))
                    eps.append(SleepEpisode(start_min=((base + 24.0) - start_hour) * 60.0, end_min=(e - start_hour) * 60.0))

            if nap_enabled and nap_duration_h > 0.0:
                ns = base + nap_start
                ne = ns + nap_duration_h
                if ne <= base + 24.0 + 1e-12:
                    eps.append(SleepEpisode(start_min=(ns - start_hour) * 60.0, end_min=(ne - start_hour) * 60.0))
                else:
                    eps.append(SleepEpisode(start_min=(ns - start_hour) * 60.0, end_min=((base + 24.0) - start_hour) * 60.0))
                    eps.append(SleepEpisode(start_min=((base + 24.0) - start_hour) * 60.0, end_min=(ne - start_hour) * 60.0))
            return eps

        episodes_all: list[SleepEpisode] = []
        for d in range(horizon_days):
            episodes_all.extend(_episodes_for_day(d))

        # Sort + merge overlaps conservatively.
        episodes_all.sort(key=lambda ep: ep.start_min)
        merged: list[SleepEpisode] = []
        for ep in episodes_all:
            if not merged:
                merged.append(ep)
                continue
            prev = merged[-1]
            if ep.start_min <= prev.end_min + 1e-9:
                merged[-1] = SleepEpisode(prev.start_min, max(prev.end_min, ep.end_min))
            else:
                merged.append(ep)

        try:
            params = SafteParameters()
            initial_units = params.reservoir_capacity_rc * (initial_reservoir_pct / 100.0)
            series = simulate_safte(
                SafteInputs(
                    start_datetime_local=start_dt,
                    horizon_minutes=horizon_minutes,
                    step_minutes=step_minutes,
                    sleep_episodes=tuple(merged),
                    initial_reservoir_units=initial_units,
                    params=params,
                )
            )
        except (ValueError, TypeError) as e:
            neutral_box(f"**Unable to run SAFTE simulation**\n\n- {e}")
        else:
            eff = [p.effectiveness_E for p in series.points]
            t_hours = [p.t_min / 60.0 for p in series.points]
            asleep_flags = [p.asleep for p in series.points]
            min_eff = min(eff) if eff else float("nan")

            theme_base_local = st.get_option("theme.base") or "light"
            theme_template_local = "plotly_dark" if theme_base_local == "dark" else "plotly_white"

            with crystal_container(border=True):
                st.markdown("**Summary**")
                st.metric("Minimum effectiveness", f"{min_eff:.1f}%")
                below = sum(1 for x in eff if x < effectiveness_warn)
                st.metric("Points below threshold", f"{below} / {len(eff)}")

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=t_hours, y=eff, mode="lines", name="Effectiveness (%)"))
            fig.add_hline(y=effectiveness_warn, line_dash="dash", opacity=0.5)
            fig.update_layout(
                title="SAFTE Effectiveness Forecast (patent-derived)",
                xaxis_title="Time since start (hours)",
                yaxis_title="Effectiveness (%)",
                height=420,
                template=theme_template_local,
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("References (equation sources)", expanded=False):
                st.markdown(
                    "- [WO2012015383A1 (Patent equations used; Eq. 1–9)](https://patents.google.com/patent/WO2012015383A1/en)\n"
                    "- [Frontiers/PMC operational use context (PMC9623177)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9623177/)\n"
                    "- [SAFTEr open-source R package (patent-equation implementation)](https://github.com/InstituteBehaviorResources/SAFTEr)"
                )

elif calculator_category == "🧪 Simulation Studio":
    st.subheader("Simulation Studio")
    st.markdown(
        '<div class="info-box"><strong>Purpose:</strong> Forward-simulate scientifically grounded calculators that naturally support time-stepping (e.g., ISO 7933 PHS, circadian envelopes). These are deterministic samplers of existing models—not new ML “black boxes”.</div>',
        unsafe_allow_html=True,
    )

    sim_type = st.selectbox(
        "Choose Simulator",
        [
            "Heat Strain Simulator (ISO 7933-inspired PHS)",
            "Circadian Forecast (Mitler performance envelope)",
        ],
    )

    theme_base = st.get_option("theme.base") or "light"
    theme_template = "plotly_dark" if theme_base == "dark" else "plotly_white"

    if sim_type == "Heat Strain Simulator (ISO 7933-inspired PHS)":
        st.markdown("### ♨️ Heat Strain Simulator — forward trajectory + next-step forecast")

        input_col1, input_col2, input_col3 = st.columns([1.0, 1.0, 1.0])
        with input_col1:
            metabolic_rate = st.slider("Metabolic rate (W/m²)", 150.0, 650.0, 380.0, step=10.0)
            clothing = st.slider("Clothing insulation (clo)", 0.3, 1.6, 0.9, step=0.1)
            air_velocity = st.slider("Air speed (m/s)", 0.1, 3.0, 0.6, step=0.1)
        with input_col2:
            air_temp = st.slider("Air temperature (°C)", 20.0, 50.0, 32.0, step=0.5)
            mean_radiant = st.slider("Mean radiant / globe (°C)", 20.0, 60.0, 38.0, step=0.5)
            rh = st.slider("Relative humidity (%)", 10.0, 100.0, 55.0, step=1.0)
        with input_col3:
            horizon = st.slider("Simulation horizon (min)", 15.0, 360.0, 120.0, step=5.0)
            step_minutes = st.select_slider(
                "Time step (min)",
                options=[1.0, 2.0, 5.0, 10.0, 15.0],
                value=5.0,
                help="Smaller steps look smoother but run more model evaluations.",
            )

        with st.expander("Advanced physiology assumptions", expanded=False):
            adv1, adv2, adv3 = st.columns(3)
            with adv1:
                mechanical_power = st.slider("External mechanical power (W/m²)", 0.0, 80.0, 0.0, step=5.0)
                body_mass = st.slider("Body mass (kg)", 55.0, 110.0, 75.0, step=1.0)
            with adv2:
                body_surface_area = st.slider("Body surface area (m²)", 1.4, 2.4, 1.9, step=0.05)
                baseline_core = st.slider("Baseline core temperature (°C)", 36.5, 37.5, 37.0, step=0.1)
            with adv3:
                core_limit = st.slider("Core temperature limit (°C)", 37.5, 39.5, 38.5, step=0.1)
                dehydration_limit = st.slider("Dehydration limit (% body mass)", 2.0, 7.0, 5.0, step=0.5)

        try:
            traj = simulate_phs_trajectory(
                metabolic_rate_w_m2=float(metabolic_rate),
                air_temperature_C=float(air_temp),
                mean_radiant_temperature_C=float(mean_radiant),
                relative_humidity_percent=float(rh),
                air_velocity_m_s=float(air_velocity),
                clothing_insulation_clo=float(clothing),
                exposure_minutes=float(horizon),
                step_minutes=float(step_minutes),
                mechanical_power_w_m2=float(mechanical_power),
                body_mass_kg=float(body_mass),
                body_surface_area_m2=float(body_surface_area),
                baseline_core_temp_C=float(baseline_core),
                core_temp_limit_C=float(core_limit),
                dehydration_limit_percent=float(dehydration_limit),
            )

            # Next-step forecast: one more step beyond the horizon (bounded).
            next_horizon = float(horizon) + float(step_minutes)
            next_point = predicted_heat_strain(
                metabolic_rate_w_m2=float(metabolic_rate),
                air_temperature_C=float(air_temp),
                mean_radiant_temperature_C=float(mean_radiant),
                relative_humidity_percent=float(rh),
                air_velocity_m_s=float(air_velocity),
                clothing_insulation_clo=float(clothing),
                exposure_minutes=float(next_horizon),
                mechanical_power_w_m2=float(mechanical_power),
                body_mass_kg=float(body_mass),
                body_surface_area_m2=float(body_surface_area),
                baseline_core_temp_C=float(baseline_core),
                core_temp_limit_C=float(core_limit),
                dehydration_limit_percent=float(dehydration_limit),
            )

            # Summary metrics
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Core temp @ horizon", f"{traj.core_temperature_C[-1]:.2f} °C")
            col_m2.metric(
                "Dehydration @ horizon", f"{traj.dehydration_percent_body_mass[-1]:.2f} %"
            )
            allow = float(traj.allowable_exposure_minutes)
            if math.isfinite(allow):
                allow_display = f"{allow:.0f} min"
                allow_note = traj.limiting_factor
            else:
                allow_display = "No limit (model)"
                allow_note = "No limit reached (model)"
            col_m3.metric(
                "Allowable exposure",
                allow_display,
                allow_note,
            )
            col_m4.metric(
                f"Next +{step_minutes:.0f} min Δcore",
                f"{(next_point.predicted_core_temperature_C - traj.core_temperature_C[-1]):+.2f} °C",
            )

            # Modern stacked plot with risk shading.
            fig = make_subplots(
                rows=3,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.08,
                subplot_titles=(
                    "Core temperature trajectory",
                    "Dehydration trajectory",
                    "Sweat rate (required vs max vs effective)",
                ),
            )

            x = np.array(traj.times_minutes, dtype=float)
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=np.array(traj.core_temperature_C, dtype=float),
                    mode="lines",
                    name="Core temp",
                ),
                row=1,
                col=1,
            )
            fig.add_hline(
                y=float(core_limit),
                line_dash="dash",
                annotation_text="Core limit",
                row=1,
                col=1,
            )

            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=np.array(traj.dehydration_percent_body_mass, dtype=float),
                    mode="lines",
                    name="Dehydration %",
                ),
                row=2,
                col=1,
            )
            fig.add_hline(
                y=float(dehydration_limit),
                line_dash="dash",
                annotation_text="Dehydration limit",
                row=2,
                col=1,
            )

            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=np.array(traj.required_sweat_rate_L_per_h, dtype=float),
                    mode="lines",
                    name="SWreq",
                ),
                row=3,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=np.array(traj.max_sustainable_sweat_rate_L_per_h, dtype=float),
                    mode="lines",
                    name="SWmax",
                ),
                row=3,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=np.array(traj.actual_sweat_rate_L_per_h, dtype=float),
                    mode="lines",
                    name="SWeff",
                ),
                row=3,
                col=1,
            )

            # Visual guardrail: mark allowable exposure (if within horizon).
            if math.isfinite(allow) and allow < float(horizon):
                fig.add_vline(x=allow, line_dash="dot")

            fig.update_layout(
                template=theme_template,
                height=820,
                margin=dict(l=40, r=20, t=80, b=40),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.0),
                hovermode="x unified",
            )
            fig.update_xaxes(title_text="Time (minutes)", row=3, col=1)
            fig.update_yaxes(title_text="°C", row=1, col=1)
            fig.update_yaxes(title_text="% body mass", row=2, col=1)
            fig.update_yaxes(title_text="L/h", row=3, col=1)

            st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True, "scrollZoom": True})

            st.markdown(
                '<div class="info-box"><strong>Interpretation:</strong> The dotted vertical line indicates the model’s calculated allowable exposure limit under the selected guardrails.</div>',
                unsafe_allow_html=True,
            )
        except ValueError as e:
            st.error(f"Simulation error: {e}")

    else:
        st.markdown("### 🧠 Circadian Forecast — performance envelope")

        col1, col2, col3 = st.columns(3)
        with col1:
            horizon_hours = st.slider(
                "Forecast horizon (hours)", 12.0, 72.0, 48.0, step=6.0
            )
            step_minutes = st.select_slider(
                "Time step (min)",
                options=[5.0, 10.0, 15.0, 30.0, 60.0],
                value=15.0,
            )
        with col2:
            phi = st.slider("Phase (φ, hours)", -12.0, 12.0, 0.0, step=0.5)
            SD = st.slider("Sleep debt parameter (SD)", 0.5, 5.0, 2.0, step=0.1)
        with col3:
            K = st.slider("Scaling (K)", 0.5, 5.0, 2.0, step=0.1)

        try:
            traj = simulate_mitler_trajectory(
                phi_hours=float(phi),
                SD=float(SD),
                K=float(K),
                horizon_hours=float(horizon_hours),
                step_minutes=float(step_minutes),
            )

            x = np.array(traj.times_hours, dtype=float)
            y = np.array(traj.performance, dtype=float)

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="lines",
                    name="Mitler performance",
                )
            )
            fig.update_layout(
                template=theme_template,
                title="Mitler performance forecast",
                xaxis_title="Time (hours)",
                yaxis_title="Performance (unitless)",
                height=520,
                margin=dict(l=40, r=20, t=70, b=40),
                hovermode="x unified",
            )
            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displaylogo": False, "responsive": True, "scrollZoom": True},
            )

            st.markdown(
                '<div class="info-box"><strong>Note:</strong> This is an educational circadian-performance envelope; it does not ingest real sleep logs or operational schedules.</div>',
                unsafe_allow_html=True,
            )
        except ValueError as e:
            st.error(f"Forecast error: {e}")

# Footer
st.markdown("---")
st.caption("**Aerospace Physiology & Occupational Health Calculators**  \nFor educational and research purposes only • Consult qualified professionals for operational use")
