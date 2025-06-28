import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import sys

# --- Page Configuration ---
st.set_page_config(page_title="💡 Co-Benefit Analyzer", layout="wide")
st.title("💡 Co-Benefit Analyzer")

# --- Add Scripts Directory ---
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "scripts"))
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

from co_benefit_analyzer import (
    load_life_expectancy_data,
    load_pm25_data,
    load_gdp_data,
    merge_co_benefit_data,
    get_country_trends
)

# --- Load Data ---
@st.cache_data
def load_all_data():
    df_life = load_life_expectancy_data()
    df_pm25 = load_pm25_data()
    df_gdp = load_gdp_data()
    merged = merge_co_benefit_data(df_life, df_pm25, df_gdp)
    return merged

df = load_all_data()

# --- Country Selection ---
available_countries = sorted(df["country"].dropna().unique())

col1 = st.columns([3])[0]
selected_country = col1.selectbox("🌍 Select Country", available_countries, index=available_countries.index("India") if "India" in available_countries else 0)
country_data = get_country_trends(df, selected_country)

# --- Tabs ---
tab0, tab1, tab2, tab3 = st.tabs([
    "📘 Overview",
    "🌿 Health & Pollution",
    "📈 Economic Growth",
    "📊 Raw Data"
])

# ----------------------------
# Tab 0: Overview
# ----------------------------
with tab0:
    st.markdown("## 📘 Module Overview – Co-Benefit Analyzer")
    st.markdown("""
    This module explores the **co-benefits** of climate actions, particularly focusing on their **impacts on public health and economic indicators** such as:

    - **Life Expectancy**
    - **Air Quality (PM2.5)**
    - **GDP Growth**

    ### 🧪 Methodology
    - Datasets for **life expectancy**, **PM2.5 pollution**, and **GDP** are merged by country and year.
    - Time-series visualization is used to detect patterns over time.
    - The module allows users to compare how improvements in air quality may lead to improved life expectancy and how these relate to economic growth.

    ### 📂 Datasets Used
    - `life_expectancy_world_bank.csv`
    - `pm25_world_bank.csv`
    - `owid-energy-data.csv` (for GDP)

    ### 🔍 What It Shows
    - Relationship between PM2.5 and health (life expectancy)
    - GDP trends over time
    - Combined country-level time series for climate-health-economic nexus

    ### 🌍 Significance
    - Helps policymakers and researchers analyze the **co-benefits** of emission-reduction policies.
    - Provides evidence for **climate-health linkages**.
    - Supports **multi-sectoral planning** (health, climate, and economy).

    ### 🧭 How to Use
    1. Select a **country** from the dropdown above.
    2. Navigate tabs to explore:
        - Trends in **health & pollution**
        - **Economic growth** patterns
        - View raw underlying data
    """)

# ----------------------------
# Tab 1: Health & Pollution
# ----------------------------
with tab1:
    st.subheader(f"🌿 Life Expectancy vs PM2.5 – {selected_country}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=country_data["year"], y=country_data["life_expectancy"],
                             mode="lines+markers", name="Life Expectancy (Years)", yaxis="y1", line=dict(color="green")))
    fig.add_trace(go.Scatter(x=country_data["year"], y=country_data["pm25"],
                             mode="lines+markers", name="PM2.5 (μg/m³)", yaxis="y2", line=dict(color="red")))

    fig.update_layout(
        title="Life Expectancy vs PM2.5 Pollution",
        xaxis_title="Year",
        yaxis=dict(title="Life Expectancy", side="left"),
        yaxis2=dict(title="PM2.5 (μg/m³)", overlaying="y", side="right"),
        legend=dict(x=0.02, y=1.15, orientation="h")
    )
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# Tab 2: Economic Growth
# ----------------------------
with tab2:
    st.subheader(f"📈 GDP Trend – {selected_country}")

    fig_gdp = go.Figure()
    fig_gdp.add_trace(go.Scatter(x=country_data["year"], y=country_data["gdp"],
                                 mode="lines+markers", name="GDP (US$)", line=dict(color="blue")))
    fig_gdp.update_layout(
        title="GDP Over Time",
        xaxis_title="Year",
        yaxis_title="GDP (current US$)",
    )
    st.plotly_chart(fig_gdp, use_container_width=True)

# ----------------------------
# Tab 3: Raw Data
# ----------------------------
with tab3:
    st.subheader("📊 Raw Data View")
    st.dataframe(country_data, use_container_width=True)
