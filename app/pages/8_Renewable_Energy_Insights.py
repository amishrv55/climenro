import os
import sys
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ✅ THIS MUST BE FIRST Streamlit command
st.set_page_config(page_title="⚡ Renewable Energy Insights", layout="wide")

# Now continue as usual
# Setup script path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "scripts"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from owid_functions import *

@st.cache_data
def load_owid():
    return pd.read_csv("data/owid-energy-data.csv")

# ...rest of the script
df = load_owid()

# Custom CSS if available
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("styles.css")

# -------------------------
# Header
# -------------------------
st.markdown("""
<div class="page-header">
    <h1>Renewable Energy Insights</h1>
    <p class="subheader">Explore national and global progress in renewables with OWID energy data</p>
</div>
""", unsafe_allow_html=True)

# -------------------------
# Top Filter Bar
# -------------------------
years = sorted(df["year"].dropna().unique(), reverse=True)
countries = sorted(df["iso_code"].dropna().unique())

col1, col2, col3, col4 = st.columns([2.5, 2.5, 2, 2])
with col1:
    selected_country = st.selectbox("🌍 Country", countries, index=countries.index("IND"))
with col2:
    selected_year = st.selectbox("📅 Year", years, index=0)
with col3:
    comparison_year_start = st.selectbox("🔁 Start Year", years, index=years.index(2000))
with col4:
    comparison_year_end = st.selectbox("⏩ End Year", years, index=0)

st.markdown("<hr class='thin-line'/>", unsafe_allow_html=True)

# -------------------------
# Tabs
# -------------------------
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📘 Overview",
    "📈 Trends Over Time",
    "🔍 Source Breakdown",
    "🌍 Top Countries",
    "🚀 Fastest Growth",
    "🔌 Electricity Mix"
])

# -------------------------
# Tab 0: Overview
# -------------------------
with tab0:
    st.markdown("## 📘 Module Overview")
    st.markdown("""
    This module provides country-level and global insights into **renewable energy trends** using the **Our World in Data (OWID) energy dataset**.

    ### 🔍 What It Shows
    - Share of renewables in electricity generation
    - Type of renewables (solar, wind, hydro, bio, etc.)
    - Country rankings by renewable share and growth
    - Historical trend analysis (2000 onward)

    ### 🧪 Methodology
    - Data Source: **Our World in Data** – OWID Energy Dataset (CSV)
    - Renewable energy share = Renewable electricity (TWh) / Total electricity generation (TWh)
    - Growth calculated as % change in renewable share from Year A to B
    - All values are aggregated annually

    ### 🧭 How to Use
    1. Select a **country** and **year range** from the filter bar above
    2. Explore renewable share trend, source split, and growth performance
    3. Compare country with global leaders or laggards

    ### 📊 Dataset Fields Used
    - `renewables_electricity`, `electricity_generation`, `solar`, `wind`, `hydro`, `bioenergy`, etc.
    - `renewables_share_elec`

    ### 🌍 Significance
    This module allows:
    - Policy makers to benchmark national energy transition
    - Researchers to assess clean energy adoption patterns
    - NGOs to monitor global climate goals

    ---
    """)

# -------------------------
# Tab 1: Trends Over Time
# -------------------------
with tab1:
    st.markdown(f"## 📈 Renewable Share Over Time – {selected_country}")
    trend = renewable_share_over_time(df, selected_country)
    if not trend.empty:
        st.line_chart(trend.set_index("year"))
    else:
        st.warning("No renewable trend data available.")

# -------------------------
# Tab 2: Breakdown by Type
# -------------------------
with tab2:
    st.markdown(f"## 🌞 Breakdown by Renewable Type – {selected_country} ({selected_year})")
    share = renewable_source_breakdown(df, selected_country, selected_year)
    if share:
        fig1, ax1 = plt.subplots()
        ax1.pie(share.values(), labels=share.keys(), autopct="%1.1f%%", startangle=90)
        ax1.set_title("Renewable Energy Source Split")
        st.pyplot(fig1)
    else:
        st.warning("No data available for this country and year.")

# -------------------------
# Tab 3: Top Countries by Share
# -------------------------
with tab3:
    st.markdown(f"## 🌍 Top Countries by Renewable Share – {selected_year}")
    top_countries = top_countries_by_renewable(df, selected_year)
    st.dataframe(top_countries, use_container_width=True)

# -------------------------
# Tab 4: Fastest Growth
# -------------------------
with tab4:
    st.markdown(f"## 🚀 Fastest Growth in Renewable Share ({comparison_year_start} → {comparison_year_end})")
    growth_df = fastest_growth_in_renewables(df, comparison_year_start, comparison_year_end)
    st.dataframe(growth_df, use_container_width=True)

# -------------------------
# Tab 5: Electricity Mix
# -------------------------
with tab5:
    st.markdown(f"## 🔌 Electricity Mix – {selected_country} ({selected_year})")
    mix = electricity_mix(df, selected_country, selected_year)
    if mix:
        fig2, ax2 = plt.subplots()
        ax2.bar(mix.keys(), mix.values(), color=["gray", "green"])
        ax2.set_ylabel("Electricity (TWh)")
        ax2.set_title(f"{selected_country} Electricity Mix in {selected_year}")
        st.pyplot(fig2)
    else:
        st.warning("Electricity mix data unavailable for this selection.")

# -------------------------
# Footer
# -------------------------
st.markdown("---")
st.caption("© 2025 Climenro | Renewable Insights | Data: Our World in Data (OWID)")
