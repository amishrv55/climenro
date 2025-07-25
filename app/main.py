import streamlit as st
from PIL import Image

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Climenro – Climate Policy Intelligence",
    layout="wide",
    page_icon="🌍",
    initial_sidebar_state="expanded"
)

# --- LOAD CUSTOM CSS ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles.css")

# --- HEADER ---
header_container = st.container()
with header_container:
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("app/static/logo_climenro.jpg", width=260)
    with col2:
        st.markdown("<h1 class='header-main'>Climenro</h1>", unsafe_allow_html=True)
        st.markdown("<div class='header-sub'>Climate Policy Intelligence Platform</div>", unsafe_allow_html=True)

# --- NOTICE BAR ---
with st.container():
    st.markdown("""
    <div class="notice-bar">
        <div class="notice-icon">🚧</div>
        <div class="notice-content">
            <strong>Pre-Beta Release:</strong> Help us improve by sharing your feedback. 
            Use the sidebar 👈 to navigate between modules.
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- HERO SECTION ---
hero = st.container()
with hero:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-content">
            <h2>Making climate policy transparent, fast, and evidence-based</h2>
            <p class="hero-description">Climenro is an AI-powered policy simulation platform built on real-world climate and economic data from NASA, IEA, EDGAR, OWID, and World Bank.</p>
            <div class="hero-features">
                <div class="feature-pill">🌍 Cities & Nations</div>
                <div class="feature-pill">📊 Policy Design Tools</div>
                <div class="feature-pill">📈 Emissions Forecasting</div>
            </div>
        </div>
        <div class="hero-graphic">
            <div class="globe-animation"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- PLATFORM STATS ---
metrics = st.container()
with metrics:
    st.markdown("### Platform Intelligence")
    metric_cols = st.columns(4)
    stats = [
        {"title": "Global Warming", "value": "+0.21°C/decade", "caption": "NASA GISTEMP"},
        {"title": "Countries Analyzed", "value": "190+", "caption": "EDGAR + World Bank"},
        {"title": "Policies Vectorized", "value": "600+", "caption": "Carbon pricing, ETS"},
        {"title": "Datasets Integrated", "value": "20+", "caption": "Multi-source analysis"}
    ]
    
    for i, stat in enumerate(stats):
        with metric_cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{stat['title']}</div>
                <div class="metric-value">{stat['value']}</div>
                <div class="metric-caption">{stat['caption']}</div>
            </div>
            """, unsafe_allow_html=True)

# --- MODULE TABS ---
tabs_container = st.container()
with tabs_container:
    st.markdown("### Explore Capabilities")
    tab1, tab2, tab3, tab4 = st.tabs([
        "Country Insights", 
        "Emission Trends", 
        "Policy Intelligence", 
        "Reporting"
    ])

    with tab1:
        st.markdown("""
        <div class="feature-card">
            <div class="card-icon">🌍</div>
            <h4>Country & Global Analysis</h4>
            <p>Explore top emitters, sectoral breakdowns, displacement scores, warming linkage, and GDP correlations.</p>
            <div class="card-footer">
                <span class="module-count">Modules 1-10</span>
                <button class="card-button">Explore</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("""
        <div class="feature-card">
            <div class="card-icon">📈</div>
            <h4>Energy & Emissions Trends</h4>
            <p>Visualize historical data, renewable growth, fossil displacement, and identify lag or lead patterns.</p>
            <div class="card-footer">
                <span class="module-count">Modules 5-9</span>
                <button class="card-button">Explore</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown("""
        <div class="feature-card">
            <div class="card-icon">🏛️</div>
            <h4>Policy Tools & Simulations</h4>
            <p>Analyze policy effectiveness, simulate future outcomes, calculate economic costs, and create policy vectors.</p>
            <div class="card-footer">
                <span class="module-count">Modules 11-21</span>
                <button class="card-button">Explore</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        st.markdown("""
        <div class="feature-card">
            <div class="card-icon">📊</div>
            <h4>Advanced Analysis</h4>
            <p>Build MACC curves, analyze co-benefits (GDP, health, PM2.5), generate country reports and narratives.</p>
            <div class="card-footer">
                <span class="module-count">Modules 17-25</span>
                <button class="card-button">Explore</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- QUICKSTART ---
quickstart = st.container()
with quickstart:
    st.markdown("### Getting Started")
    with st.expander("How to use Climenro", expanded=True):
        cols = st.columns(3)
        steps = [
            {"icon": "📍", "title": "Select Module", "text": "Choose from the sidebar menu"},
            {"icon": "🌐", "title": "Choose Location", "text": "Select country or region"},
            {"icon": "📊", "title": "Analyze & Export", "text": "Interact with tools and export insights"}
        ]
        
        for i, step in enumerate(steps):
            with cols[i]:
                st.markdown(f"""
                <div class="quickstart-step">
                    <div class="step-icon">{step['icon']}</div>
                    <h4>{step['title']}</h4>
                    <p>{step['text']}</p>
                </div>
                """, unsafe_allow_html=True)

# --- CLIENTS & PARTNERS ---
partners = st.container()
with partners:
    st.markdown("### Trusted By Global Organizations")
    cols = st.columns(5)
    partners = ["UN", "World Bank", "GIZ", "NASA", "EU DG Clima"]
    for i, partner in enumerate(partners):
        with cols[i]:
            st.markdown(f"""
            <div class="partner-logo">
                <div class="logo-placeholder">{partner}</div>
            </div>
            """, unsafe_allow_html=True)

# --- FOOTER ---
footer = st.container()
with footer:
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <div class="footer-content">
            <div>© 2025 Climenro – Climate Intelligence Platform</div>
            <div class="footer-links">
                <a href="#">Privacy</a> • 
                <a href="#">Terms</a> • 
                <a href="#">Data Sources</a> • 
                <a href="#">Contact</a>
            </div>
        </div>
        <div class="footer-cta">
            Ready to transform climate policy? <button class="footer-button">Request Demo</button>
        </div>
    </div>
    """, unsafe_allow_html=True)