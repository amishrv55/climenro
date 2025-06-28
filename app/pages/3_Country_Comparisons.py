import sys
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Path fix to access scripts/
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "scripts"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from load_edgar import load_edgar_ipcc2006
from edgar_functions import (
    top_emitters_by_gas,
    compare_emission_trends,
    compare_sector_by_country,
    sector_profiles,
    stacked_sector_breakdown,
)

# -------------------------------
# Load Custom CSS
# -------------------------------
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles.css")

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def get_data():
    return load_edgar_ipcc2006()

df = get_data()

# -------------------------------
# Page Header
# -------------------------------
st.markdown("""
<div class="page-header">
    <h1>Country Comparisons & Sectoral Emissions</h1>
    <p class="subheader">Analyze trends, sector emissions, and national profiles across countries</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# Filter Bar
# -------------------------------
years = sorted(df["year"].unique(), reverse=True)
countries = sorted(df["Country_code_A3"].unique())
sectors = sorted(df["ipcc_code_2006_for_standard_report_name"].dropna().unique())

col1, col2 = st.columns([2, 1])
with col1:
    selected_year = st.selectbox("📅 Year", years, index=0)
with col2:
    if st.button("🔄 Reset Filters"):
        selected_year = years[0]

st.markdown("<hr class='thin-line'/>", unsafe_allow_html=True)

# -------------------------------
# Tabs
# -------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Emission Trends",
    "🏭 Sector-Wise Comparison",
    "📊 Sectoral Profiles",
    "📊 Stacked Sector Breakdown"
])

# -------------------------------
# Tab 1: Emission Trends
# -------------------------------
with tab1:
    st.markdown("### 📈 Emission Trends Over Time")
    selected_countries = st.multiselect("Select 2–4 Countries", countries, default=["IND", "USA", "CHN"])
    if len(selected_countries) >= 2:
        trend_df = compare_emission_trends(df, selected_countries)
        st.line_chart(trend_df)
    else:
        st.warning("Please select at least 2 countries.")

# -------------------------------
# Tab 2: Sector-Wise Comparison
# -------------------------------
with tab2:
    st.markdown("### 🏭 Sector Emissions Comparison by Country")
    selected_sector = st.selectbox("Select Sector", sectors, key="sector_compare")
    top_sector_df = compare_sector_by_country(df, selected_sector, selected_year).head(10)

    st.dataframe(top_sector_df, use_container_width=True)

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.bar(top_sector_df["Country_code_A3"], top_sector_df["emissions_mtco2e"], color="#FFA726")
    ax2.set_ylabel("Emissions (MtCO₂e)")
    ax2.set_title(f"{selected_sector} Emissions – {selected_year}")
    ax2.tick_params(axis='x', rotation=45)
    st.pyplot(fig2)

# -------------------------------
# Tab 3: Sectoral Profiles
# -------------------------------
with tab3:
    st.markdown("### 📊 Sectoral Emission Profiles by Country")
    selected_radar_countries = st.multiselect("Select 2–5 Countries", countries, default=["IND", "USA"], key="radar_compare")

    if 1 < len(selected_radar_countries) <= 5:
        radar_df = sector_profiles(df, selected_radar_countries, selected_year)
        st.dataframe(radar_df, use_container_width=True)

        fig3, ax3 = plt.subplots(figsize=(12, 6))
        radar_df.plot(kind="bar", ax=ax3, width=0.8)
        ax3.set_ylabel("Emissions (MtCO₂e)")
        ax3.set_title("Sectoral Emission Profiles")
        ax3.legend(loc='upper right')
        st.pyplot(fig3)
    else:
        st.warning("Please select between 2 and 5 countries.")

# -------------------------------
# Tab 4: Stacked Sector Emissions
# -------------------------------
with tab4:
    st.markdown("### 📊 Stacked Bar: Sector-Wise Emissions by Country")
    selected_stacked_countries = st.multiselect("Select Countries", countries, default=["IND", "USA", "CHN"], key="stacked_compare")

    if selected_stacked_countries:
        stacked_df = stacked_sector_breakdown(df, selected_stacked_countries, selected_year)
        st.dataframe(stacked_df, use_container_width=True)

        # Sort columns by emission magnitude
        ordered_cols = stacked_df.sum().sort_values(ascending=False).index.tolist()
        stacked_df = stacked_df[ordered_cols]

        fig4, ax4 = plt.subplots(figsize=(12, 6))
        stacked_df.plot(kind="bar", stacked=True, ax=ax4, colormap="tab20")
        ax4.set_ylabel("Emissions (MtCO₂e)")
        ax4.set_title("Stacked Sector Emissions – Major Contributors on Top")
        ax4.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="small")
        ax4.tick_params(axis='x', rotation=0)
        st.pyplot(fig4)
    else:
        st.warning("Please select at least one country.")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("""
**📂 Data Source:** [EDGAR v6.0 GHG Dataset](https://edgar.jrc.ec.europa.eu/)  
Country-wise GHG emissions data following IPCC 2006 sector classification.
""")
