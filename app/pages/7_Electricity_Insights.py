import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add scripts/ to path
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "scripts"))
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

# Import custom power plant functions
from Electricity_Insights import (
    load_power_plant_data,
    get_country_plant_data,
    get_total_capacity,
    get_fuel_mix_distribution,
    get_fuel_capacity_distribution,
    get_location_map_df,
    capacity_over_time,
    average_capacity_by_fuel,
    generation_efficiency,
    fuel_mix_over_time,
)

# Page config and header
st.set_page_config(page_title="🔌 Electricity Infrastructure Insights", layout="wide")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles.css")

# -------------------------------
# Page Header
# -------------------------------
st.markdown("""
<div class="page-header">
    <h1>Electricity Infrastructure – Country Insights</h1>
    <p class="subheader">Track generation mix, capacity growth, and grid infrastructure per country</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# Load Data and Country Filter
# -------------------------------
df = load_power_plant_data()
available_countries = sorted(df["country"].unique())

col1, col2 = st.columns([5, 1])
with col1:
    selected_country = st.selectbox("🌍 Select Country", available_countries, index=available_countries.index("IND"))
with col2:
    if st.button("🔄 Reset"):
        selected_country = "IND"

st.markdown("<hr class='thin-line'/>", unsafe_allow_html=True)

# Country-specific subset
df_country = get_country_plant_data(df, selected_country)
total_capacity = get_total_capacity(df_country)

# -------------------------------
# Tabs
# -------------------------------
tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📘 Overview",
    "📊 Summary",
    "🧯 Fuel Mix",
    "🗺️ Map View",
    "📈 Capacity Over Time",
    "📊 Avg Capacity by Fuel",
    "⚙️ Generation Efficiency",
    "📊 Fuel Mix Over Time",
    "📄 About"
])

# -------------------------------
# Tab 0: Overview
# -------------------------------
with tab0:
    st.markdown("## 📘 Module Overview")
    st.markdown("""
    This module provides **deep insights into the electricity generation infrastructure** of a country using plant-level data.

    ### 🔍 What Does It Show?
    - Total installed capacity across all power plants
    - Breakdown of power plants by fuel type (e.g., coal, gas, solar)
    - Evolution of capacity and fuel mix over time
    - Power plant map with location and size
    - Estimated vs actual generation efficiency

    ### 🧪 Methodology
    - Data is sourced from the **Global Power Plant Database (GPPD)** maintained by the **World Resources Institute**
    - Aggregation is done at national level using plant-level attributes (fuel type, capacity, commissioning year, generation)
    - Charts are generated using **Plotly** and data is refreshed with every session

    ### 📊 Dataset Fields Used
    - `name`, `primary_fuel`, `capacity_mw`, `commissioning_year`
    - `generation_gwh`, `estimated_generation_gwh`, `latitude`, `longitude`

    ### 🌍 Significance
    This tool helps users:
    - Understand national electricity reliance on fossil or renewable sources
    - Spot under-utilized or aging generation capacity
    - Identify regions for renewable expansion or grid upgrades

    ### ✅ How to Use
    1. Select a **country** at the top
    2. Navigate through tabs to explore capacity, mix, trends, maps, and performance
    3. Use visualizations to inform policy, investment, or research

    ---
    """)

# -------------------------------
# Tab 1: Summary
# -------------------------------
with tab1:
    st.header(f"🔍 Power Infrastructure Summary – {selected_country}")
    st.metric("Total Installed Capacity", f"{total_capacity:,.2f} MW")
    st.dataframe(
        df_country[["name", "capacity_mw", "primary_fuel", "commissioning_year"]]
        .sort_values(by="capacity_mw", ascending=False),
        use_container_width=True
    )

# -------------------------------
# Tab 2: Fuel Mix
# -------------------------------
with tab2:
    st.subheader("💡 Fuel Mix by Capacity and Count")
    fuel_mix_pct = get_fuel_mix_distribution(df_country)
    fuel_mix_cap = get_fuel_capacity_distribution(df_country)

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.pie(
            fuel_mix_pct,
            names="Fuel_Type",
            values="proportion",
            title="Fuel Mix – Plant Count (%)"
        )
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.bar(
            fuel_mix_cap,
            x="primary_fuel",
            y="capacity_mw",
            title="Fuel Mix – Installed Capacity (MW)",
            labels={"capacity_mw": "MW", "primary_fuel": "Fuel"}
        )
        st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# Tab 3: Map
# -------------------------------
with tab3:
    st.subheader("📍 Power Plant Map")
    map_df = get_location_map_df(df_country)
    fig_map = px.scatter_mapbox(
        map_df,
        lat="latitude",
        lon="longitude",
        color="primary_fuel",
        size="capacity_mw",
        hover_name="name",
        zoom=3,
        mapbox_style="open-street-map",
        title="Power Plants Location"
    )
    st.plotly_chart(fig_map, use_container_width=True)

# -------------------------------
# Tab 4: Capacity Over Time
# -------------------------------
with tab4:
    st.subheader("📈 Installed Capacity Over Time")
    cap_time_df = capacity_over_time(df_country)
    fig = px.line(
        cap_time_df,
        x="commissioning_year",
        y="capacity_mw",
        title="Installed Capacity Over Time",
        markers=True,
        labels={"commissioning_year": "Year", "capacity_mw": "MW"}
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Tab 5: Average Capacity by Fuel
# -------------------------------
with tab5:
    st.subheader("📊 Average Plant Capacity by Fuel")
    avg_cap_df = average_capacity_by_fuel(df_country)
    fig = px.bar(
        avg_cap_df,
        x="primary_fuel",
        y="avg_capacity_mw",
        title="Average Capacity by Fuel Type",
        labels={"avg_capacity_mw": "MW", "primary_fuel": "Fuel"}
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Tab 6: Generation Efficiency
# -------------------------------
with tab6:
    st.subheader("⚙️ Generation Efficiency – Actual vs Estimated")
    year = st.selectbox("Select Year", [2013, 2014, 2015, 2016, 2017], index=4)
    try:
        gen_eff_df = generation_efficiency(df_country, year=year)
        st.dataframe(gen_eff_df, use_container_width=True)
        fig = px.scatter(
            gen_eff_df,
            x=f"estimated_generation_gwh_{year}",
            y=f"generation_gwh_{year}",
            color="primary_fuel",
            size="utilization_ratio",
            hover_name="name",
            title=f"Generation Efficiency – {year}"
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning("Not enough data to display efficiency.")

# -------------------------------
# Tab 7: Fuel Mix Over Time
# -------------------------------
with tab7:
    st.subheader("📊 Fuel Mix Evolution Over Time")
    mix_time_df = fuel_mix_over_time(df_country)
    fig = px.area(
        mix_time_df,
        x="commissioning_year",
        y="capacity_mw",
        color="primary_fuel",
        title="Fuel Mix Evolution by Year"
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Tab 8: About
# -------------------------------
with tab8:
    st.markdown("""
    ### 📄 About This Module
    This module is part of the **Climenro Climate Intelligence Platform** and shows generation mix, plant efficiency, and capacity trends using data from the **Global Power Plant Database** (WRI).

    - Uses IPCC-relevant indicators for electricity infrastructure
    - Enables energy planners and researchers to assess readiness and transition potential
    - Fully interactive with visuals and national filtering
    """)

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("© 2025 Climenro | Electricity Insights | Data: GPPD, World Resources Institute")
