import streamlit as st
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "scripts"))
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

from load_edgar import load_edgar_ipcc2006
from warming_loader import load_region_temp
from climate_change import compute_rolling_average, compute_lag_correlation

# Page config
st.set_page_config(page_title="Warming vs Emissions", layout="wide")

# Load CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles.css")

# -------------------------------
# Header
# -------------------------------
st.markdown("""
<div class="page-header">
    <h1>Warming vs Emissions</h1>
    <p class="subheader">Correlating India's national emissions with regional warming</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# Top Filter Bar
# -------------------------------
regions = ["Himalayas", "Ganga Plain", "Kolkata", "Mumbai", "Chennai"]

col1, col2 = st.columns([4, 1])
with col1:
    selected_region = st.selectbox("🌍 Select Region", regions, index=0)
with col2:
    if st.button("🔄 Reset Region"):
        selected_region = "Himalayas"

st.markdown("<hr class='thin-line'/>", unsafe_allow_html=True)

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    return load_edgar_ipcc2006()

edgar_df = load_data()

# Load and preprocess temperature data
try:
    temp_df = load_region_temp(selected_region)
    temp_df = compute_rolling_average(temp_df, "temp_ann")
except FileNotFoundError:
    st.error(f"❌ Temperature data for '{selected_region}' not found.")
    st.stop()

# Compute India total emissions
def get_india_total_emissions(df, country_code="IND"):
    df_ind = df[df["Country_code_A3"] == country_code]
    if df_ind.empty:
        return pd.DataFrame(columns=["year", "emissions"])
    df_result = df_ind.groupby("year")["emissions_mtco2e"].sum().reset_index()
    df_result.columns = ["year", "emissions"]
    return df_result

emissions_df = get_india_total_emissions(edgar_df)

# Merge on year
if "temp_ann_smoothed" not in temp_df.columns:
    st.error("❌ Smoothed temperature column not found.")
    st.stop()

merged_df = pd.merge(
    temp_df[["year", "temp_ann_smoothed"]],
    emissions_df,
    on="year",
    how="inner"
).rename(columns={"temp_ann_smoothed": "temp_ann"})

# -------------------------------
# Tabs
# -------------------------------
tab1, tab2 = st.tabs(["📘 Module Overview", f"📈 Warming vs Emissions – {selected_region}"])

# -------------------------------
# Tab 1: Description & Methodology
# -------------------------------
with tab1:
    st.markdown("## 📘 Module Overview")
    st.markdown("""
    This module analyzes the **relationship between regional warming in India** and **national-level greenhouse gas emissions**.  
    It enables users to explore whether observed temperature trends in specific Indian regions correlate with total emissions reported for the country.

    ### 🧪 Methodology
    - **Temperature data** from NASA POWER for 5 regions of India (2001–2022)
    - **Emissions data** from EDGAR v6.0 – Total national GHG emissions (IPCC 2006)
    - Data are aligned **by year** and smoothed using a 5-year **rolling average**
    - Correlation coefficient is calculated between temperature trend and national emissions

    ### 📊 Data Sources
    - 📁 `EDGAR v6.0` – European Commission GHG inventory
    - 📁 `NASA POWER` – Surface air temperature (T2M) by region

    ### 📈 What You Can Do
    - View side-by-side plots of temperature and emissions
    - Analyze trend similarity over time
    - Download merged dataset for further research

    ### 🌍 Significance
    This module helps assess whether **local climate impacts** may be statistically associated with **national-level emissions**, aiding:
    - Policy framing for **regional climate risk**
    - Awareness about **regional vulnerability**
    - Data-backed storytelling in climate research

    ---
    """)

# -------------------------------
# Tab 2: Warming vs Emissions Plot
# -------------------------------
with tab2:
    st.markdown(f"### 📈 Temperature vs Emissions – {selected_region} vs India")

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Temperature (°C)", color="tab:red")
    ax1.plot(merged_df["year"], merged_df["temp_ann"], color="tab:red", label="Smoothed Temp")
    ax1.tick_params(axis='y', labelcolor="tab:red")

    ax2 = ax1.twinx()
    ax2.set_ylabel("Emissions (MtCO₂e)", color="tab:blue")
    ax2.plot(merged_df["year"], merged_df["emissions"], color="tab:blue", label="India Emissions")
    ax2.tick_params(axis='y', labelcolor="tab:blue")

    fig.tight_layout()
    st.pyplot(fig)

    # Correlation
    correlation = merged_df["temp_ann"].corr(merged_df["emissions"])
    st.metric(label="📊 Correlation (Temp vs Emissions)", value=f"{correlation:.2f}")
    st.caption("Note: Correlation uses 5-year rolling average temperature.")

    # Download
    download_df = merged_df.rename(columns={
        "temp_ann": "Temperature (°C)",
        "emissions": "Emissions (MtCO₂e)"
    })
    st.download_button(
        label="📥 Download Merged Data",
        data=download_df.to_csv(index=False),
        file_name=f"{selected_region.lower().replace(' ', '_')}_temp_vs_emissions.csv"
    )

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("""
<div class="footer">
    <div>© 2025 Climenro Climate Intelligence. All rights reserved.</div>
    <div class="footer-links">
        <a href="#">Terms</a> | 
        <a href="#">Privacy</a> | 
        <a href="#">Sources</a> | 
        <a href="#">Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)
