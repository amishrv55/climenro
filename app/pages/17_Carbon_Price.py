import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Setup paths ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
DATA_DIR = os.path.join(BASE_DIR, "data")

if SCRIPTS_DIR not in sys.path:
    sys.path.append(SCRIPTS_DIR)

from carbon_price import CarbonPriceAnalyzer

# --- Page Setup ---
st.set_page_config(page_title="💸 Carbon Pricing & Inflation", layout="wide")
st.title("💸 Carbon Pricing & Inflation Analysis")

# --- Load Analyzer ---
@st.cache_resource
def init_analyzer():
    return CarbonPriceAnalyzer(
        carbon_price_path=os.path.join(DATA_DIR, "carbon_price_world_bank.xlsx"),
        inflation_path=os.path.join(DATA_DIR, "world_bank_inflation_consumer_price.csv")
    )

analyzer = init_analyzer()

# --- Get Country & Year Options ---
try:
    available_countries = analyzer.get_available_countries()
    if not available_countries:
        st.error("No countries found in carbon pricing data.")
        st.stop()
    min_year = int(analyzer.carbon_data["year"].min())
    max_year = int(analyzer.carbon_data["year"].max())
except Exception as e:
    st.error(f"Initialization error: {e}")
    st.stop()

# --- Filter Inputs (Top Filter Bar) ---
st.markdown("### 🔍 Select Parameters")
col1, col2, col3 = st.columns([3, 2, 2])
with col1:
    country = st.selectbox("🌍 Country", options=available_countries, index=available_countries.index("India") if "India" in available_countries else 0)
with col2:
    start_year = st.number_input("Start Year", min_value=min_year, max_value=max_year, value=min_year)
with col3:
    end_year = st.number_input("End Year", min_value=min_year, max_value=max_year, value=max_year)

st.markdown("<hr class='thin-line'/>", unsafe_allow_html=True)

# --- Tabs ---
tab0, tab1 = st.tabs(["📘 Overview", "📊 Price & Inflation Trends"])

# ----------------------------
# Tab 0: Overview
# ----------------------------
with tab0:
    st.markdown("## 📘 Module Overview – Carbon Pricing & Inflation")
    st.markdown("""
    This module analyzes trends in **carbon pricing instruments** and links them to **inflation trends** across countries.

    ### 🧾 What It Shows
    - Official carbon pricing schemes: ETS, carbon taxes, hybrids
    - Nominal and inflation-adjusted prices over time
    - Annual inflation rates
    - Country-wise comparison and downloadable dataset

    ### 🧪 Methodology
    - Carbon pricing data from **World Bank Carbon Pricing Dashboard**
    - Inflation data from **World Bank CPI Data**
    - Merged by country and year
    - Prices are shown in **USD per metric ton of CO₂**
    - Prices compared with consumer inflation to assess real trends

    ### 📂 Datasets Used
    - `carbon_price_world_bank.xlsx`
    - `world_bank_inflation_consumer_price.csv`

    ### 🌍 Significance
    - Helps assess **price effectiveness** and **burden on economies**
    - Provides input for climate fiscal policy evaluations
    - Useful for international comparisons of carbon pricing efforts

    ### 🧭 How to Use
    1. Choose a country and a time range
    2. View trends in nominal carbon prices and inflation
    3. Download combined data for further research

    ---
    """)

# ----------------------------
# Tab 1: Price and Inflation Trends
# ----------------------------
with tab1:
    st.header(f"📈 Carbon Pricing & Inflation – {country} ({start_year} to {end_year})")

    try:
        # Filter data
        carbon_df, inflation_df = analyzer.get_country_data(country)
        carbon_df = carbon_df[(carbon_df["year"] >= start_year) & (carbon_df["year"] <= end_year)]
        inflation_df = inflation_df[(inflation_df["year"] >= start_year) & (inflation_df["year"] <= end_year)]

        if carbon_df.empty and inflation_df.empty:
            st.warning("No data available for selected range.")
            st.stop()

        # Charts
        col1, col2 = st.columns(2)
        with col1:
            if not carbon_df.empty:
                st.plotly_chart(analyzer.generate_price_plot(carbon_df), use_container_width=True)
            else:
                st.info("No carbon pricing data available.")
        with col2:
            if not inflation_df.empty:
                st.plotly_chart(analyzer.generate_inflation_plot(inflation_df), use_container_width=True)
            else:
                st.info("No inflation data available.")

        # Merged Table View
        with st.expander("📊 View Combined Data Table"):
            merged = pd.merge(carbon_df, inflation_df, how="left", on=["year", "country"])
            display_cols = ["year", "type", "initiative", "price_usd", "inflation_pct"]
            display_df = merged[display_cols].sort_values("year").rename(columns={
                "year": "Year",
                "type": "Instrument Type",
                "initiative": "Initiative",
                "price_usd": "Price (USD/tCO₂)",
                "inflation_pct": "Inflation (%)"
            })
            st.dataframe(display_df, height=300)

        # Download
        if not carbon_df.empty or not inflation_df.empty:
            csv = merged.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"carbon_pricing_inflation_{country}.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
