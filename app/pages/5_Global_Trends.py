import streamlit as st
import os
import sys
import plotly.express as px
import pandas as pd

# --- Directory Setup ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
DATA_DIR = os.path.join(BASE_DIR, "data")

if SCRIPTS_DIR not in sys.path:
    sys.path.append(SCRIPTS_DIR)

# --- Import Data Functions ---
from global_indicators import (
    load_zonal_temperature_data,
    load_global_temperature_data,
    get_global_annual_trend,
    get_zonal_trend_summary,
    get_temperature_rate_of_change,
    get_warming_rate_by_zone,
    load_sea_level_data,
    summarize_sea_level_trend,
    get_sea_level_trend_line,
    load_gas_data
)

# --- Page Configuration ---
st.set_page_config(page_title="🌍 Climenro - Global Climate Indicators", layout="wide")
st.title("🌍 Global Climate Change Indicators")
st.caption("Part of the Climenro Platform for Climate Policy Research & Insights")

# --- Sidebar Info ---
st.sidebar.header("📁 Data Sources")
st.sidebar.markdown("**Temperature:** NASA GISTEMP\n\n**Sea Level:** GRACE/GRACE-FO")

# --- Load Data ---
global_df = load_global_temperature_data()
zonal_df = load_zonal_temperature_data()

# --- Tabs Setup ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "📘 Module Description",
    "🌡️ Global Anomalies",
    "🧭 Zonal Trends",
    "📈 Warming Rate",
    "🧭 Equator vs Poles",
    "🌊 Sea Level Rise",
    "🟢 CO₂ Concentration", 
    "🟣 CH₄ Concentration", 
    "🟠 N₂O Concentration", 
    "🔵 SF₆ Concentration"
])

# --- Tab 1: Module Description ---
with tab1:
    st.subheader("📘 Module Overview")
    st.markdown("""
    This module provides key global indicators of climate change based on standardized datasets
    from NASA and GRACE/GRACE-FO. It includes:

    - **Global Annual Temperature Anomalies** from the GISTEMP dataset (1880–present)
    - **Zonal Surface Temperature Trends** to track warming across latitude bands
    - **Rate of Global and Zonal Warming** with statistical significance
    - **Temperature Trends from Equator to Poles**
    - **Sea Level Rise Trends** using satellite-derived sea level anomalies

    **Significance:** This dashboard helps researchers, policymakers, and educators understand
    the spatial and temporal dynamics of climate change. It offers insights into where warming
    is accelerating, how significant the observed changes are, and how sea level is responding
    to global heating.

    **Usage Tip:** Explore each tab for specific indicators and graphs. Use the sidebar to review
    data sources.
    """)

# --- Tab 2: Global Temperature Anomalies ---

def show_gas_tab(gas_df, gas_name, unit="ppm"):
    st.subheader(f"{gas_name} Concentration Over Time")
    fig1 = px.line(gas_df, x="datetime", y="average", title=f"{gas_name} – Global Monthly Average", labels={"average": f"{gas_name} ({unit})"})
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📊 Monthly Seasonality Pattern")
    fig2 = px.box(gas_df, x="month", y="average", points="all", title=f"{gas_name} – Monthly Seasonality", labels={"month": "Month", "average": f"{gas_name} ({unit})"})
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📈 Mean Monthly Values")
    monthly_avg = gas_df.groupby("month")["average"].mean().reset_index()
    fig3 = px.line(monthly_avg, x="month", y="average", title=f"{gas_name} – Average by Calendar Month", labels={"average": f"{gas_name} ({unit})"})
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.subheader("🌡️ Global Annual Temperature Anomalies")
    global_annual = get_global_annual_trend(global_df)
    fig_global = px.line(
        global_annual, x="Year", y="Annual",
        title="Global Annual Temperature Anomaly (1880–Present)",
        markers=True
    )
    st.plotly_chart(fig_global, use_container_width=True)

# --- Tab 3: Zonal Temperature Trends ---
with tab3:
    st.subheader("🧭 Zonal Temperature Trends")
    zonal_latest = get_zonal_trend_summary(zonal_df)
    st.dataframe(zonal_latest, use_container_width=True)

# --- Tab 4: Global and Zonal Warming Rate ---
with tab4:
    st.subheader("📈 Global Warming Rate Per Decade")
    rate, p_value = get_temperature_rate_of_change(zonal_df)
    st.markdown(f"**Estimated Rate:** `{rate:.4f} °C/decade`")
    st.markdown(f"**p-value:** `{p_value:.4f}`")

    if p_value < 0.01:
        st.success("✅ Statistically significant warming trend.")
    else:
        st.warning("⚠️ Trend not statistically significant.")

    st.subheader("📊 Warming Rate by Latitude Zones")
    zonal_cols = ["Glob", "NHem", "SHem", "24N-90N", "24S-24N", "90S-24S", "64N-90N", "44N-64N", "24N-44N", "EQU-24N", "24S-EQU", "44S-24S", "64S-44S", "90S-64S"]
    zone_rates_df = get_warming_rate_by_zone(zonal_df, zonal_cols)

    fig_zone = px.bar(
        zone_rates_df, x="zone_name", y="rate_per_decade",
        color="rate_per_decade", color_continuous_scale="Viridis",
        title="Warming Rate per Decade by Zone (°C)",
        labels={"rate_per_decade": "°C/decade", "zone_name": "Latitude Zone"}
    )
    st.plotly_chart(fig_zone, use_container_width=True)

# --- Tab 5: Equator vs Poles ---
with tab5:
    st.subheader("🧭 Equator vs Poles - Temperature Anomalies")
    trend_zones = {
        "Equator (24S–24N)": "24S-24N",
        "Mid-North (24N–44N)": "24N-44N",
        "Mid-South (44S–24S)": "44S-24S",
        "North Pole (64N–90N)": "64N-90N",
        "South Pole (90S–64S)": "90S-64S"
    }

    fig_eq_poles = px.line(
        zonal_df, x="Year",
        y=[zonal_df[zone] for zone in trend_zones.values()],
        labels={"value": "Temp Anomaly (°C)", "variable": "Region"},
        title="Temperature Anomalies: Equator vs Poles"
    )

    for idx, (label, zone_key) in enumerate(trend_zones.items()):
        fig_eq_poles.data[idx].name = label
        fig_eq_poles.data[idx].hovertemplate = f"{label}<br>Year: %{{x}}<br>Temp: %{{y:.2f}}°C"

    st.plotly_chart(fig_eq_poles, use_container_width=True)

# --- Tab 6: Sea Level Rise ---
with tab6:
    st.subheader("🌊 Global Sea Level Rise (GRACE/GRACE-FO)")
    try:
        sea_df = load_sea_level_data()
        sea_summary = summarize_sea_level_trend(sea_df)
        st.markdown(f"**Rate:** `{sea_summary['rate_mm_per_year']:.2f} mm/year`  ")
        st.markdown(f"**Total Rise:** `{sea_summary['total_rise_mm']:.2f} mm`  ")
        st.markdown(f"**Period:** `{sea_summary['start_year']}–{sea_summary['end_year']}`")

        sea_plot = get_sea_level_trend_line(sea_df)
        fig_sea = px.line(sea_plot, x="time", y="sea_level_anomaly",
                          title="Global Sea Level Anomaly Over Time")
        st.plotly_chart(fig_sea, use_container_width=True)
    except Exception as e:
        st.error("❌ Sea level data could not be loaded.")
        st.exception(e)

# Load gas datasets
co2_df = load_gas_data("co2_mm_gl.csv")
ch4_df = load_gas_data("ch4_mm_gl.csv")
n2o_df = load_gas_data("n2o_mm_gl.csv")
sf6_df = load_gas_data("sf6_mm_gl.csv")

# Display in tabs
with tab7:
    show_gas_tab(co2_df, "CO₂", unit="ppm")

with tab8:
    show_gas_tab(ch4_df, "CH₄", unit="ppb")

with tab9:
    show_gas_tab(n2o_df, "N₂O", unit="ppb")

with tab10:
    show_gas_tab(sf6_df, "SF₆", unit="ppt")


# --- Footer ---
st.markdown("---")
st.caption("Climenro | Climate Change Research Platform\n\nData Source: NASA GISTEMP & GRACE/GRACE-FO")