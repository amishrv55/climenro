import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
from datetime import datetime

# Set up custom script path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "scripts"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from load_edgar import load_edgar_ipcc2006, load_edgar_co2, load_edgar_co2bio, load_edgar_ch4, load_edgar_n2o

# ------------------------------
# Load CSS
# ------------------------------
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles.css")

# ------------------------------
# Load data
# ------------------------------
@st.cache_data
def get_data():
    return (
        load_edgar_ipcc2006(),
        load_edgar_co2(),
        load_edgar_co2bio(),
        load_edgar_ch4(),
        load_edgar_n2o(),
    )

df_ar5, df_co2, df_co2bio, df_ch4, df_n2o = get_data()

# ------------------------------
# PAGE HEADER
# ------------------------------
st.markdown(f"""
<div class="page-header">
    <h1>Sector-Wise Emissions Insights</h1>
    <p class="subheader">Compare GHGs Across Sectors and Countries</p>
    <p class="last-updated">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------
# TOP FILTER BAR
# ------------------------------
years = sorted(df_ar5["year"].unique(), reverse=True)
countries = sorted(df_ar5["Country_code_A3"].dropna().unique())
sectors = sorted(df_ar5["ipcc_code_2006_for_standard_report_name"].dropna().unique())

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

# ------------------------------
# Tabs
# ------------------------------
tabs = st.tabs([
    "📋 Activity Summary",
    "AR5 GHG", "CO₂", "CO₂ Bio", "CH₄", "N₂O",
    "📘 GHG Activity Guide"
])

datasets = {
    "AR5 GHG": df_ar5,
    "CO₂": df_co2,
    "CO₂ Bio": df_co2bio,
    "CH₄": df_ch4,
    "N₂O": df_n2o,
}

# ------------------------------
# TAB 1: Summary
# ------------------------------
with tabs[0]:
    st.markdown(f"### 📋 Emission Summary – {selected_sector} in {selected_country} ({selected_year})")

    def extract_emission(df):
        return df[(df["Country_code_A3"] == selected_country) &
                  (df["year"] == selected_year) &
                  (df["ipcc_code_2006_for_standard_report_name"] == selected_sector)]["emissions_mtco2e"].sum()

    val_ar5 = extract_emission(df_ar5)
    val_co2 = extract_emission(df_co2)
    val_co2bio = extract_emission(df_co2bio)
    val_ch4 = extract_emission(df_ch4)
    val_n2o = extract_emission(df_n2o)

    st.markdown(f"""
    In **{selected_country}**, sector **{selected_sector}** emitted in **{selected_year}**:
    - **{val_ar5:,.2f} MtCO₂e** (Total GHG, AR5)
    - **{val_co2:,.2f} MtCO₂e** from CO₂
    - **{val_co2bio:,.2f} MtCO₂e** from CO₂ Bio
    - **{val_ch4:,.2f} MtCO₂e** from CH₄
    - **{val_n2o:,.2f} MtCO₂e** from N₂O
    """)

    def get_rank(df):
        df_filtered = df[(df["year"] == selected_year) &
                         (df["ipcc_code_2006_for_standard_report_name"] == selected_sector)]
        df_rank = df_filtered.groupby("Country_code_A3")["emissions_mtco2e"].sum().reset_index()
        df_rank = df_rank.sort_values("emissions_mtco2e", ascending=False).reset_index(drop=True)
        try:
            return df_rank[df_rank["Country_code_A3"] == selected_country].index[0] + 1
        except:
            return "N/A"

    st.markdown("### 🌐 Global Sector Rank:")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("AR5 Rank", get_rank(df_ar5))
    col2.metric("CO₂ Rank", get_rank(df_co2))
    col3.metric("CO₂ Bio Rank", get_rank(df_co2bio))
    col4.metric("CH₄ Rank", get_rank(df_ch4))
    col5.metric("N₂O Rank", get_rank(df_n2o))

# ------------------------------
# Gas-specific Tabs
# ------------------------------
def render_tab(tab, gas_label, df_gas):
    with tab:
        st.markdown(f"### {gas_label} – {selected_sector} in {selected_country} ({selected_year})")

        df_filtered = df_gas[(df_gas["Country_code_A3"] == selected_country) &
                             (df_gas["year"] == selected_year) &
                             (df_gas["ipcc_code_2006_for_standard_report_name"] == selected_sector)]

        value = df_filtered["emissions_mtco2e"].sum()
        st.metric(label=f"{gas_label} Emissions", value=f"{value:,.2f} MtCO₂e")

        # Emission trend over time
        df_trend = df_gas[(df_gas["Country_code_A3"] == selected_country) &
                          (df_gas["ipcc_code_2006_for_standard_report_name"] == selected_sector)]
        df_line = df_trend.groupby("year")["emissions_mtco2e"].sum().reset_index()

        fig = px.line(df_line, x="year", y="emissions_mtco2e",
                      title=f"{gas_label} Trend – {selected_sector}",
                      labels={"emissions_mtco2e": "Emissions (MtCO₂e)"})
        st.plotly_chart(fig, use_container_width=True)

        # Rank
        df_year_sector = df_gas[(df_gas["year"] == selected_year) &
                                (df_gas["ipcc_code_2006_for_standard_report_name"] == selected_sector)]
        df_rank = df_year_sector.groupby("Country_code_A3")["emissions_mtco2e"].sum().reset_index()
        df_rank = df_rank.sort_values("emissions_mtco2e", ascending=False).reset_index(drop=True)
        try:
            rank = df_rank[df_rank["Country_code_A3"] == selected_country].index[0] + 1
            st.success(f"Global Rank: #{rank}")
        except:
            st.warning("No data available to rank.")

# Render gas tabs
for tab, (label, dataset) in zip(tabs[1:6], datasets.items()):
    render_tab(tab, label, dataset)

# ------------------------------
# Activity Guide Tab
# ------------------------------
with tabs[6]:
    st.markdown("### 📘 Greenhouse Gas Activity Guide")
    st.markdown("""
    This guide explains how different sectors contribute to GHG emissions:
    - **Electricity & Heat**: Coal, oil, gas combustion
    - **Transport**: CO₂, N₂O from fuel use
    - **Agriculture**: CH₄ from livestock, N₂O from fertilizer
    - **Industry**: CO₂ from cement, iron, chemicals
    - **Waste**: CH₄ from landfills
    - **LULUCF**: CO₂ sinks and sources

    Based on IPCC 2006 sector classification.
    """)

# ------------------------------
# Footer
# ------------------------------
st.markdown("---")
st.markdown("""
**📂 Data Source:** [EDGAR v6.0 GHG Dataset](https://edgar.jrc.ec.europa.eu/) – IPCC 2006 sector methodology.
""")
