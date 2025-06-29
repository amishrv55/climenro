import streamlit as st
from PIL import Image

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Climenro – Climate Policy Intelligence",
    layout="wide",
    page_icon="🌍"
)

# --- LOAD CUSTOM CSS ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles.css")

# --- HEADER ---
col1, col2 = st.columns([1, 5])
with col1:
    st.image("app/static/logo_climenro.jpg", width=160)
with col2:
    st.markdown("<h1 class='header-main'>Climenro</h1>", unsafe_allow_html=True)
    st.markdown("<h4 class='header-sub'>Climate Policy Intelligence Platform</h4>", unsafe_allow_html=True)

# --- HORIZONTAL FILTER BAR ---
st.markdown("<hr class='thin-line'/>", unsafe_allow_html=True)
filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])
with filter_col1:
    selected_country = st.selectbox("🌍 Country", ["IND", "USA", "CHN", "BRA", "ZAF", "DEU"])
with filter_col2:
    selected_year = st.selectbox("📅 Year", [2025, 2024, 2023, 2022, 2021])
with filter_col3:
    if st.button("🔄 Reset"):
        selected_country = "IND"
        selected_year = 2023

st.markdown("<hr class='thin-line'/>", unsafe_allow_html=True)

# --- HERO SECTION ---
st.markdown("""
<div class="hero">
    <h3>Making climate policy transparent, fast, and evidence-based</h3>
    <p>Climenro is an AI-powered policy simulation and analysis platform built on real-world climate and economic data from NASA, IEA, EDGAR, OWID, and World Bank.</p>
    <p>We serve cities, nations, NGOs, and consultancies with tools that simplify climate action planning, policy design, and emissions forecasting.</p>
</div>
""", unsafe_allow_html=True)

# --- QUICKSTART GUIDE ---
with st.expander("ℹ️ How to Use Climenro"):
    st.markdown("""
    1. **Select a Module** from the sidebar (e.g., country insights, emissions trends, or policy simulators).
    2. **Choose a Country** and timeframe using the top filter.
    3. **Interact** with visualizations, scenario tools, or policy analyzers.
    4. **Download reports** using the Report Generator module.
    """)

# --- PLATFORM STATS ---
st.markdown("### 🔢 Platform Stats")
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
with metric_col1:
    st.markdown("""<div class="metric-card"><div class="metric-title">🌡️ Global Warming</div><div class="metric-value">+0.21°C/decade</div><div class="metric-caption">NASA GISTEMP</div></div>""", unsafe_allow_html=True)
with metric_col2:
    st.markdown("""<div class="metric-card"><div class="metric-title">🌍 Countries Analyzed</div><div class="metric-value">190+</div><div class="metric-caption">EDGAR + World Bank</div></div>""", unsafe_allow_html=True)
with metric_col3:
    st.markdown("""<div class="metric-card"><div class="metric-title">📘 Policies Vectorized</div><div class="metric-value">600+</div><div class="metric-caption">Carbon pricing, ETS, etc.</div></div>""", unsafe_allow_html=True)
with metric_col4:
    st.markdown("""<div class="metric-card"><div class="metric-title">📊 Datasets Used</div><div class="metric-value">20+</div><div class="metric-caption">Multi-source integrated</div></div>""", unsafe_allow_html=True)

# --- MODULE TABS ---
st.markdown("### 🧭 Explore Modules")
tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 Country & Global Insights", 
    "📈 Emission & Energy Trends", 
    "🏛️ Policy Intelligence", 
    "📊 MACC, Co-benefits & Reporting"
])

with tab1:
    st.markdown("""
    <div class="feature-card">
        <h4>Country & Global Analysis</h4>
        <p>Explore top emitters, sectoral breakdowns, displacement scores, warming linkage, and GDP correlations for 190+ countries.</p>
        <p><b>Modules:</b> 1 to 10</p>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="feature-card">
        <h4>Energy & Emissions Trends</h4>
        <p>Visualize historical data, renewable growth, fossil displacement, and identify lag or lead patterns.</p>
        <p><b>Modules:</b> 5 to 9</p>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("""
    <div class="feature-card">
        <h4>Policy Tools & Simulations</h4>
        <p>Analyze policy effectiveness, simulate future outcomes, calculate economic costs, and create policy vectors with clustering.</p>
        <p><b>Modules:</b> 11 to 21</p>
    </div>
    """, unsafe_allow_html=True)

with tab4:
    st.markdown("""
    <div class="feature-card">
        <h4>Advanced Analysis</h4>
        <p>Build MACC curves, analyze co-benefits (GDP, health, PM2.5), generate country reports and narratives for stakeholders.</p>
        <p><b>Modules:</b> 17 to 25</p>
    </div>
    """, unsafe_allow_html=True)

# --- CLIENTS & PARTNERS ---
st.markdown("### 🤝 Used & Supported by")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.image("https://via.placeholder.com/120x60?text=UN", width=100)
with col2:
    st.image("https://via.placeholder.com/120x60?text=World+Bank", width=100)
with col3:
    st.image("https://via.placeholder.com/120x60?text=GIZ", width=100)
with col4:
    st.image("https://via.placeholder.com/120x60?text=NASA", width=100)
with col5:
    st.image("https://via.placeholder.com/120x60?text=EU+DG+Clima", width=100)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div class="footer">
    <div>© 2025 Climenro – Climate Intelligence Platform. All rights reserved.</div>
    <div class="footer-links">
        <a href="#">Privacy Policy</a> |
        <a href="#">Terms of Service</a> |
        <a href="#">Source Datasets</a> |
        <a href="#">Contact Team</a>
    </div>
</div>
""", unsafe_allow_html=True)
