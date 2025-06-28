import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Add custom script paths
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "scripts"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from load_edgar import load_edgar_ipcc2006, load_edgar_co2, load_edgar_co2bio, load_edgar_ch4, load_edgar_n2o
from edgar_functions import *

# Load custom style
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("styles.css")

# ------------------------------
# LOAD DATA (needed early for country list)
# ------------------------------
@st.cache_data
def get_data():
    return load_edgar_ipcc2006(), load_edgar_co2(), load_edgar_co2bio(), load_edgar_ch4(), load_edgar_n2o()

df, df_co2, df_co2bio, df_ch4, df_n2o = get_data()

# ------------------------------
# PAGE HEADER
# ------------------------------
st.markdown("""
<div class="page-header">
    <h1>Emissions & Sector Insights</h1>
    <p class="subheader">Comprehensive Trends, Sector Analysis, and Fuel Breakdown</p>
    <p class="last-updated">Last updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M') + """</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------
# TOP FILTER BAR (Always visible)
# ------------------------------
years = sorted(df["year"].unique(), reverse=True)
countries = sorted(df["Country_code_A3"].unique())

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    selected_country = st.selectbox("🌍 Select Country", countries, index=countries.index("IND"))
with col2:
    selected_year = st.selectbox("📅 Select Year", years, index=0)
with col3:
    if st.button("🔄 Reset Filters"):
        selected_country = "IND"
        selected_year = years[0]  # Reset to first year in list

st.markdown("<hr class='thin-line'/>", unsafe_allow_html=True)

# ------------------------------
# TABS
# ------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "🌐 Understanding GHGs", 
    "📋 Country Summary", 
    "📈 GHG Emissions", 
    "🟦 CO₂ Emission", 
    "🟩 CO₂ Bio", 
    "🟫 Total CO₂", 
    "🟥 CH₄", 
    "🟨 N₂O",
    "📊 Global Sector Insights", 
    "🌍 Benchmarks"
])

# ------------------------------
# TAB 1: Introduction
# ------------------------------
with tab1:
    st.markdown("## 🌐 Understanding Greenhouse Gases (GHGs)")
    st.markdown("""
    Greenhouse gases (GHGs) trap heat in the Earth's atmosphere, causing the **greenhouse effect**. They vary in source, lifetime, and warming potential.

    ### 🔹 Why GHGs Matter
    Human activities (fossil fuels, agriculture) have increased GHGs, accelerating global warming and climate instability.

    ### 🔸 Major Types of GHGs:

    | Gas  | Description | Sources | Global Warming Potential (100 yr) |
    |------|-------------|---------|----------------------------------|
    | CO₂  | Most abundant GHG | Fossil fuels, deforestation | 1 |
    | CH₄  | Potent, short-lived | Livestock, waste, gas leaks | 28–34 |
    | N₂O  | Long-lived | Fertilizers, industry | 265–298 |
    | HFCs/PFCs/SF₆ | Synthetic | Refrigerants, semiconductors | Hundreds to thousands |

    ### 🧮 Measurement
    GHGs are measured in **MtCO₂e** — metric tons of CO₂ equivalent — which normalizes across gases using their warming potential.

    ### 📊 Source
    [EDGAR GHG v6.0 Dataset](https://edgar.jrc.ec.europa.eu/overview.php?v=GHGts)

    ---
    """, unsafe_allow_html=True)

# ------------------------------
# TAB 2: Country Summary
# ------------------------------
with tab2:
    df_sel = lambda d: d[(d["Country_code_A3"] == selected_country) & (d["year"] == selected_year)]
    total_ghg = df_sel(df)["emissions_mtco2e"].sum()
    total_co2 = df_sel(df_co2)["emissions_mtco2e"].sum()
    total_co2bio = df_sel(df_co2bio)["emissions_mtco2e"].sum()
    total_ch4 = df_sel(df_ch4)["emissions_mtco2e"].sum()
    total_n2o = df_sel(df_n2o)["emissions_mtco2e"].sum()

    # Global totals
    global_ghg = df[df["year"] == selected_year]["emissions_mtco2e"].sum()
    global_co2 = df_co2[df_co2["year"] == selected_year]["emissions_mtco2e"].sum()
    global_co2bio = df_co2bio[df_co2bio["year"] == selected_year]["emissions_mtco2e"].sum()
    global_ch4 = df_ch4[df_ch4["year"] == selected_year]["emissions_mtco2e"].sum()
    global_n2o = df_n2o[df_n2o["year"] == selected_year]["emissions_mtco2e"].sum()

    rank = emission_rank(df, selected_country, selected_year)

    st.markdown(f"### 📋 Emission Summary – {selected_country} ({selected_year})")
    st.markdown(f"""
    - Total GHG emissions: **{total_ghg:,.2f} MtCO₂e**  
    - Fossil CO₂ emissions: **{total_co2:,.2f} MtCO₂e**  
    - Bio CO₂ emissions: **{total_co2bio:,.2f} MtCO₂e**  
    - CH₄ emissions: **{total_ch4:,.2f} MtCO₂e**  
    - N₂O emissions: **{total_n2o:,.2f} MtCO₂e**  
    - Global Rank (GHG): **#{rank}**
    """)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("% Global GHG", f"{100*total_ghg/global_ghg:.2f}%")
    col2.metric("% Global CO₂", f"{100*total_co2/global_co2:.2f}%")
    col3.metric("% CO₂ Bio", f"{100*total_co2bio/global_co2bio:.2f}%")
    col4.metric("% CH₄", f"{100*total_ch4/global_ch4:.2f}%")
    col5.metric("% N₂O", f"{100*total_n2o/global_n2o:.2f}%")

    df_act = df_sel(df).groupby("ipcc_code_2006_for_standard_report_name")["emissions_mtco2e"].sum().reset_index()
    df_top = df_act.sort_values("emissions_mtco2e", ascending=False).head(10)

    st.markdown("### 🔝 Top 10 Emitting Activities")
    fig = px.bar(df_top, x="emissions_mtco2e", y="ipcc_code_2006_for_standard_report_name",
                 orientation='h', color="emissions_mtco2e", color_continuous_scale="Teal")
    fig.update_layout(xaxis_title="Emissions (MtCO₂e)", yaxis_title="Activity")
    st.plotly_chart(fig, use_container_width=True, key=f"top_activities_{selected_country}_{selected_year}")
    st.dataframe(df_top.style.format({"emissions_mtco2e": "{:,.2f}"}), use_container_width=True)

# ------------------------------
# Gas Trend Tabs
# ------------------------------
def gas_emission_tab(df_gas, label, tab):
    with tab:
        df_filtered = df_gas[df_gas["Country_code_A3"] == selected_country]
        df_trend = df_filtered.groupby("year")["emissions_mtco2e"].sum().reset_index()

        st.markdown(f"### 📈 {label} Emissions Over Time – {selected_country}")
        fig = px.line(df_trend, x="year", y="emissions_mtco2e", title="", markers=True)
        fig.update_layout(xaxis_title="Year", yaxis_title="Emissions (MtCO₂e)", font=dict(color="#222"))
        st.plotly_chart(fig, use_container_width=True, key=f"trend_{label}_{selected_country}")

        st.markdown(f"### 🏭 Top 5 Emitting Sectors – {selected_year}")
        df_year = df_filtered[df_filtered["year"] == selected_year]
        df_sector = df_year.groupby("ipcc_code_2006_for_standard_report_name")["emissions_mtco2e"].sum().reset_index()
        df_top5 = df_sector.sort_values(by="emissions_mtco2e", ascending=False).head(5)

        fig2 = px.bar(df_top5, x="emissions_mtco2e", y="ipcc_code_2006_for_standard_report_name", orientation="h",
                     color="emissions_mtco2e", color_continuous_scale="Viridis")
        st.plotly_chart(fig2, use_container_width=True, key=f"sectors_{label}_{selected_country}_{selected_year}")

gas_emission_tab(df, "GHG", tab3)
gas_emission_tab(df_co2, "CO₂", tab4)
gas_emission_tab(df_co2bio, "CO₂ Bio", tab5)
gas_emission_tab(pd.concat([df_co2, df_co2bio]), "Total CO₂", tab6)
gas_emission_tab(df_ch4, "CH₄", tab7)
gas_emission_tab(df_n2o, "N₂O", tab8)

# ------------------------------
# FOOTER
# ------------------------------
st.markdown("---")
st.markdown("""
**📂 Data Source:** [EDGAR v6.0 GHG Dataset](https://edgar.jrc.ec.europa.eu/)  
European Commission's Joint Research Centre using IPCC 2006 sectoral methodology.
""")