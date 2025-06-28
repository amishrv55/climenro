import os
import sys
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ✅ Set page config FIRST
st.set_page_config(page_title="🔁 Renewable Energy vs Emissions", layout="wide")

# Setup path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "scripts"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Load functions
from renewable_vs_emission import *
from load_edgar import load_edgar_ipcc2006

@st.cache_data
def load_energy_data():
    return pd.read_csv("data/owid-energy-data.csv")

# Load data
df_emission = load_edgar_ipcc2006()
df_renew = load_energy_data()

# -----------------------------
# 🔍 Top Filter Bar
# -----------------------------
years = sorted(df_renew['year'].dropna().unique())
countries = sorted(df_renew['iso_code'].dropna().unique())

col1, col2, col3 = st.columns(3)
with col1:
    selected_country = st.selectbox("🌍 Country", countries, index=countries.index("IND"))
with col2:
    start_year = st.selectbox("⏳ Start Year", years, index=years.index(2000))
with col3:
    end_year = st.selectbox("⏩ End Year", years, index=len(years)-1)

st.markdown("<hr class='thin-line'/>", unsafe_allow_html=True)

# -----------------------------
# 📂 Tabs
# -----------------------------
tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📘 Overview",
    "📈 Emissions vs Renewables",
    "📊 Growth Trends",
    "🔗 Correlations",
    "⚡ Emissions per TWh",
    "🌞 Renewable Breakdown",
    "🌍 Global Comparison",
    "🏭 Sectoral View",
    "🛢️ Fossil Electricity Trend"
])

# -----------------------------
# 📘 Tab 0: Overview
# -----------------------------
with tab0:
    st.markdown("## 📘 Module Overview")
    st.markdown("""
    This module analyzes how **renewable energy adoption** relates to **greenhouse gas emissions** using country-level and global data.

    ### 🔍 What It Shows
    - Yearly emissions vs renewable share
    - Year-on-year % change in both
    - Correlation (incl. lagged effect)
    - Emissions per electricity unit
    - Sectoral insights
    - Cross-country comparison

    ### 🧪 Methodology
    - Data Sources:
        - **EDGAR v6.0**: Country-wise emissions data
        - **OWID Energy Dataset**: Renewable shares and generation data
    - Trends are visualized using line charts, twin axes, and correlation metrics
    - Correlation computed using **Pearson coefficient**, lag tested at 2 years

    ### 🧭 How to Use
    1. Choose a country and timeframe above
    2. Navigate through tabs to explore comparative insights
    3. Focus on lag correlation, per-TWh emission efficiency, and cross-country benchmarking

    ### 🌍 Significance
    Helps policy makers and researchers assess whether increasing renewables is resulting in **real-world emission declines**.
    """)

# -----------------------------
# 📈 Tab 1: Emissions vs Renewables
# -----------------------------
with tab1:
    st.markdown("## 📈 Emissions vs Renewable Share Over Time")
    data1 = compare_emission_vs_renewable(df_emission, df_renew, selected_country)
    fig, ax1 = plt.subplots()
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Emissions (MtCO₂e)", color="tab:red")
    ax1.plot(data1['year'], data1['emissions_mtco2e'], color="tab:red", label="Emissions")
    ax1.tick_params(axis='y', labelcolor="tab:red")

    ax2 = ax1.twinx()
    ax2.set_ylabel("Renewable Share (%)", color="tab:green")
    ax2.plot(data1['year'], data1['renewables_share_energy'], color="tab:green", label="Renewables")
    ax2.tick_params(axis='y', labelcolor="tab:green")
    fig.tight_layout()
    st.pyplot(fig)

# -----------------------------
# 📊 Tab 2: Growth Trend Comparison
# -----------------------------
with tab2:
    st.markdown("## 📊 YoY % Change in Emissions vs Renewables")
    data2 = growth_trend_comparison(df_emission, df_renew, selected_country)
    st.line_chart(data2.set_index("year")[['emission_change_pct', 'renewable_change_pct']])

# -----------------------------
# 🔗 Tab 3: Correlation Analysis
# -----------------------------
with tab3:
    st.markdown("## 🔗 Correlation Between Renewables and Emissions")
    corr = correlation_emission_renewable(df_emission, df_renew, selected_country)
    if corr is not None:
        st.metric(label="📉 Pearson Correlation", value=f"{corr:.2f}")
        st.caption("Closer to -1 = strong inverse relationship")
    else:
        st.warning("Not enough data for correlation.")

    st.markdown("### ⏳ Lag Correlation (2-Year Delay)")
    lag_corr = lag_correlation(df_emission, df_renew, selected_country, lag=2)
    if lag_corr is not None:
        st.metric(label="⏱️ Lagged Correlation", value=f"{lag_corr:.2f}")
        st.caption("Checks if emission decline follows renewable growth after 2 years")
    else:
        st.warning("Insufficient data for lag correlation.")

# -----------------------------
# ⚡ Tab 4: Emissions per TWh
# -----------------------------
with tab4:
    st.markdown("## ⚡ Emissions per TWh of Electricity")
    data4 = emission_per_twh(df_emission, df_renew, selected_country)
    st.line_chart(data4.set_index("year"))

# -----------------------------
# 🌞 Tab 5: Breakdown by Renewable Type
# -----------------------------
with tab5:
    st.markdown("## 🌞 Renewable Sources vs Emissions")
    data5 = renewable_type_vs_emission(df_emission, df_renew, selected_country)
    fig2, ax3 = plt.subplots()
    ax3.plot(data5['year'], data5['emissions_mtco2e'], label="Emissions", color='black')
    ax3.plot(data5['year'], data5['solar_share_elec'], label="Solar", color='orange')
    ax3.plot(data5['year'], data5['wind_share_elec'], label="Wind", color='blue')
    ax3.plot(data5['year'], data5['hydro_share_elec'], label="Hydro", color='green')
    ax3.set_ylabel("Value")
    ax3.set_xlabel("Year")
    ax3.legend()
    st.pyplot(fig2)

# -----------------------------
# 🌍 Tab 6: Global Comparison
# -----------------------------
with tab6:
    st.markdown("## 🌍 Emission Reduction vs Renewable Growth (All Countries)")
    data6 = emission_reduction_vs_renewable_growth(df_emission, df_renew, start_year, end_year)
    data6 = data6.dropna(subset=["emission_change_pct", "renewable_change_pct"])
    data6 = data6.astype({"emission_change_pct": float, "renewable_change_pct": float})
    
    st.scatter_chart(
        data6[["renewable_change_pct", "emission_change_pct"]].rename(columns={
            "renewable_change_pct": "Renewable Growth (%)",
            "emission_change_pct": "Emission Change (%)"
        })
    )
    st.caption("Top-left quadrant = Best performers")

# -----------------------------
# 🏭 Tab 7: Sectoral View
# -----------------------------
with tab7:
    st.markdown("## 🏭 Sectoral Emissions vs Renewable Growth")
    sector_keyword = st.selectbox("Select Sector", ["Manufacturing", "Transport", "Residential", "Electricity", "Agriculture"])
    sector_data = sector_emission_vs_renewable(df_emission, df_renew, selected_country, sector_keyword)

    if not sector_data.empty:
        fig_sector, ax = plt.subplots()
        ax.plot(sector_data['year'], sector_data['emissions_mtco2e'], label="Sector Emissions", color='red')
        ax.plot(sector_data['year'], sector_data['renewables_share_energy'], label="Renewable Share", color='green')
        ax.set_ylabel("Value")
        ax.set_xlabel("Year")
        ax.legend()
        st.pyplot(fig_sector)
    else:
        st.warning("No data available for selected sector and country.")

# -----------------------------
# 🛢️ Tab 8: Fossil Electricity
# -----------------------------
with tab8:
    st.markdown("## 🛢️ Fossil Electricity Trend")
    fossil_data = fossil_electricity_trend(df_renew, selected_country)
    st.line_chart(fossil_data.set_index("year"))

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Climenro | Renewable vs Emission Linkages | Data: EDGAR, OWID")
