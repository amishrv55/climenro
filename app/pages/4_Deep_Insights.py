import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Fix path for custom imports
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "scripts"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from load_edgar import load_edgar_ipcc2006, load_population, load_gdp
from edgar_functions import (
    sector_contribution,
    fastest_growing_sectors,
    manufacturing_vs_global_avg,
    cumulative_emissions_n_years,
    top_growth_countries,
    compare_country_with_global,
    compare_sector_with_global,
    get_per_capita_emission,
    get_emission_per_gdp
)

# -------------------------------
# Load Custom CSS
# -------------------------------
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles.css")

# -------------------------------
# Header
# -------------------------------
st.markdown(f"""
<div class="page-header">
    <h1>Deep Emissions Insights & Benchmarks</h1>
    <p class="subheader">Growth trends, sector contributions, benchmarking, and efficiency metrics</p>
    <p class="last-updated">Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# Load & Cache Data
# -------------------------------
@st.cache_data
def get_data():
    return load_edgar_ipcc2006(), load_population(), load_gdp()

df, df_pop, df_gdp = get_data()

# -------------------------------
# Top Filter Bar
# -------------------------------
years = sorted(df["year"].unique(), reverse=True)
countries = sorted(df["Country_code_A3"].dropna().unique())
sectors = sorted(df["ipcc_code_2006_for_standard_report_name"].dropna().unique())

col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
with col1:
    selected_country = st.selectbox("🌍 Country", countries, index=countries.index("IND"))
with col2:
    selected_year = st.selectbox("📅 Year", years, index=0)
with col3:
    selected_sector = st.selectbox("🏭 Sector", sectors)
with col4:
    if st.button("🔄 Reset"):
        selected_country = "IND"
        selected_year = years[0]
        selected_sector = sectors[0]

st.markdown("<hr class='thin-line'/>", unsafe_allow_html=True)

# -------------------------------
# Tabs
# -------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Sector Analysis", "📈 Growth Rates", "📏 Country Benchmarks", "🌍 Sector Benchmarks", "👥 Per Capita & GDP"
])

# -------------------------------
# Tab 1: Sector Analysis
# -------------------------------
with tab1:
    st.markdown(f"### 📊 Cumulative Emissions – {selected_country}")

    cum_5 = cumulative_emissions_n_years(df, selected_country, selected_year, 5)
    cum_10 = cumulative_emissions_n_years(df, selected_country, selected_year, 10)
    cum_15 = cumulative_emissions_n_years(df, selected_country, selected_year, 15)

    col1, col2, col3 = st.columns(3)
    col1.metric("5-Year Emissions", f"{cum_5:,.0f} MtCO₂e")
    col2.metric("10-Year Emissions", f"{cum_10:,.0f} MtCO₂e")
    col3.metric("15-Year Emissions", f"{cum_15:,.0f} MtCO₂e")

# -------------------------------
# Tab 2: Growth Rates
# -------------------------------
with tab2:
    st.markdown("### 🚀 Top Emitting Countries by Growth")

    for n in [5, 10, 15]:
        st.markdown(f"#### 🔼 Growth Over Last {n} Years")
        top_growth = top_growth_countries(df, selected_year, n)
        fig = px.bar(top_growth, x="Country_code_A3", y="growth_rate",
                     labels={"growth_rate": "Growth (%)"},
                     title=f"Top 10 Growth Countries – Last {n} Years",
                     color="growth_rate",
                     color_continuous_scale="Reds")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(top_growth, use_container_width=True)

# -------------------------------
# Tab 3: Country Benchmarking
# -------------------------------
with tab3:
    st.markdown(f"### 📏 Country Benchmark – {selected_country} vs Global")

    country_val, global_avg = compare_country_with_global(df, selected_country, selected_year)
    delta = country_val - global_avg
    delta_pct = (delta / global_avg) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Country Emission", f"{country_val:,.1f} MtCO₂e")
    col2.metric("Global Avg", f"{global_avg:,.1f} MtCO₂e")
    col3.metric("Difference", f"{delta:+.1f} MtCO₂e ({delta_pct:+.1f}%)")

# -------------------------------
# Tab 4: Sector Benchmarking
# -------------------------------
with tab4:
    st.markdown(f"### 📏 Sector Benchmark – {selected_sector} in {selected_country} vs Global")

    country_sec, global_sec = compare_sector_with_global(df, selected_country, selected_sector, selected_year)
    delta_sec = country_sec - global_sec
    delta_sec_pct = (delta_sec / global_sec) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Sector Emission", f"{country_sec:,.1f} MtCO₂e")
    col2.metric("Global Sector Avg", f"{global_sec:,.1f} MtCO₂e")
    col3.metric("Difference", f"{delta_sec:+.1f} MtCO₂e ({delta_sec_pct:+.1f}%)")

# -------------------------------
# Tab 5: Per Capita and GDP Efficiency
# -------------------------------
with tab5:
    st.markdown(f"### 👥 Per Capita Emissions – {selected_country}")
    df_capita = get_per_capita_emission(df, df_pop)
    df_country = df_capita[df_capita["Country_code_A3"] == selected_country]
    fig_pc = px.line(df_country, x="year", y="per_capita_emission",
                     labels={"per_capita_emission": "tCO₂e per person"},
                     title="Per Capita Emission Trend")
    st.plotly_chart(fig_pc, use_container_width=True)

    st.markdown("### 💰 Emission Intensity per GDP")
    df_eff = get_emission_per_gdp(df, df_gdp, df_pop)
    df_eff_country = df_eff[df_eff["Country_code_A3"] == selected_country]
    fig_eff = px.line(df_eff_country, x="year", y="emission_per_gdp",
                      labels={"emission_per_gdp": "MtCO₂e per Billion USD"},
                      title="Emission Efficiency per GDP")
    st.plotly_chart(fig_eff, use_container_width=True)

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("""
<div class="footer">
    <div>© 2025 Climenro Climate Intelligence. All rights reserved.</div>
    <div class="footer-links">
        <a href="#">Terms of Service</a> | 
        <a href="#">Privacy Policy</a> | 
        <a href="#">Data Sources</a> | 
        <a href="#">Contact Us</a>
    </div>
</div>
""", unsafe_allow_html=True)
