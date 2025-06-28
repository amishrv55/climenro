import streamlit as st
import pandas as pd
import os
import sys
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="📜 Carbon Policy Insights", layout="wide")

# --- SCRIPT PATH SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "scripts"))
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

# --- IMPORTS ---
from policy_analysis import (
    load_policy_data,
    get_policy_types,
    countries_per_policy_type,
    count_countries_per_policy,
    policy_adoption_timeline,
    sectoral_coverage_summary,
    get_policy_adoption_year
)
from load_edgar import load_edgar_ipcc2006

# --- LOAD DATA ---
@st.cache_data
def load_data():
    return load_policy_data("data/gen_info.csv")

df = load_data()
edgar_df = load_edgar_ipcc2006()

# --- TABS ---
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📘 Overview",
    "📊 Policy Types",
    "📆 Timeline",
    "🏭 Sectoral Coverage",
    "📈 Country Policy Impact",
    "📜 Dataset Summary"
])

# -------------------------------
# 📘 Tab 0: Module Overview
# -------------------------------
with tab0:
    st.markdown("## 📘 Module Overview: Carbon Policy Insights")
    st.markdown("""
    This module analyzes **carbon pricing instruments** and their **adoption trends**, providing deep insights into how climate policies are distributed across countries and sectors.

    ### 🔍 What It Shows
    - Types of carbon policy instruments globally (ETS, taxes, trading, etc.)
    - Number of countries using each instrument
    - Year of adoption by each country
    - Sectoral distribution of policies
    - Emissions trend before and after adoption

    ### 🧪 Methodology
    - Data Source: Public datasets on carbon policy metadata (`gen_info.csv`)
    - Matched with national emissions from EDGAR GHG dataset
    - Policy adoption shown via scatter plots & emissions timelines

    ### 🧭 How to Use
    1. Navigate tabs for type, timeline, and sector views
    2. Use **Country Policy Impact** tab to check emissions trend vs. policy year
    3. Hover or filter for individual instruments and countries

    ### 🌍 Significance
    This helps:
    - Governments understand global adoption patterns
    - Researchers correlate policy introduction with emission trends
    - Climate advocates identify under-regulated sectors

    ---
    """)

# -------------------------------
# 📊 Tab 1: Policy Type Distribution
# -------------------------------
with tab1:
    st.subheader("🌐 What Types of Carbon Policies Exist?")
    policy_types = get_policy_types(df)
    st.dataframe(policy_types, use_container_width=True)

    st.subheader("📊 Countries by Policy Type")
    policy_count = count_countries_per_policy(df)
    fig = px.bar(policy_count, x="Type", y="country_count", title="Countries Using Each Policy Type", color="Type")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 📆 Tab 2: Timeline of Adoption
# -------------------------------
with tab2:
    st.subheader("📆 Timeline of Carbon Policy Adoption")
    timeline = policy_adoption_timeline(df)
    fig = px.scatter(
        timeline,
        x="adoption_year",
        y="country",
        color="Type",
        title="Year of Policy Adoption by Country",
        hover_data=["Instrument name"]
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 🏭 Tab 3: Sectoral Coverage
# -------------------------------
with tab3:
    st.subheader("🏭 Sectoral Coverage of Climate Policies")
    sector_df = sectoral_coverage_summary(df)
    fig = px.bar(sector_df, x="Sector", y="Count", title="Policy Coverage Across Sectors", color="Sector")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 📈 Tab 4: Country Impact
# -------------------------------
with tab4:
    st.subheader("📈 Emissions Trend with Policy Adoption Marker")

    countries = sorted(df["Jurisdiction covered"].dropna().unique())
    selected_country = st.selectbox("Select Country", countries, index=countries.index("India") if "India" in countries else 0)

    # Match country code with EDGAR dataset
    iso_code = selected_country[:3].upper()
    country_emissions = edgar_df[edgar_df["Country_code_A3"] == iso_code]
    if country_emissions.empty:
        st.warning("No emission data available for this country.")
    else:
        # Aggregate and plot
        country_emissions = country_emissions.groupby("year", as_index=False)["emissions_mtco2e"].sum()
        adoption_year = get_policy_adoption_year(df, selected_country)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=country_emissions["year"], 
            y=country_emissions["emissions_mtco2e"],
            mode="lines+markers", 
            name="Emissions (MtCO₂e)", 
            line=dict(color="steelblue")
        ))

        if adoption_year:
            fig.add_vline(x=adoption_year, line_dash="dash", line_color="red")
            fig.add_annotation(
                x=adoption_year,
                y=country_emissions["emissions_mtco2e"].max(),
                text=f"Policy Adopted: {adoption_year}",
                showarrow=True, arrowhead=1
            )

        fig.update_layout(
            title=f"{selected_country}: Emissions vs Policy Adoption",
            xaxis_title="Year",
            yaxis_title="Emissions (MtCO₂e)"
        )
        st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 📜 Tab 5: Raw Dataset
# -------------------------------
with tab5:
    st.subheader("📜 Raw Policy Dataset Preview")
    st.dataframe(df.head(50), use_container_width=True)

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("📜 Climenro | Carbon Policy Insights | Data: gen_info.csv + EDGAR GHG")
