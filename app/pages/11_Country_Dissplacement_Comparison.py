import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# ✅ Set page config early
st.set_page_config(page_title="🌍 Country Displacement Comparison", layout="wide")

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "scripts"))
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

from owid_functions import load_owid_data
from displacement_analysis import compare_displacement_scores

# Load data
@st.cache_data
def load_data():
    return load_owid_data()

df = load_data()

# Run comparison
displacement_df = compare_displacement_scores(df)
all_scores_df = compare_displacement_scores(df, latest_only=False)

# ---------------------------
# 📂 Tabs
# ---------------------------
tab0, tab1, tab2 = st.tabs([
    "📘 Overview",
    "🌎 Top 20 Countries",
    "🔍 Individual Country View"
])

# ---------------------------
# 📘 Tab 0: Overview
# ---------------------------
with tab0:
    st.markdown("## 📘 Module Overview: Country Displacement Comparison")
    st.markdown("""
    This module compares how effectively countries are **displacing fossil fuels with renewable energy**.

    ### 🔍 What It Shows
    - Countries ranked by **displacement score**
    - Trend and score for selected country
    - Latest year-by-year leaderboard

    ### 🧪 Methodology
    - Dataset: **Our World in Data (OWID)** – Global electricity dataset
    - **Displacement Score = % Growth in Renewable – % Growth in Fossil**
        - ✅ Positive score = Renewables are outpacing fossil fuels (desired)
        - ❌ Negative score = Fossils are still growing faster or not falling

    ### 🧭 How to Use
    - Use **Top 20 tab** to identify leaders in fossil fuel displacement
    - Use **Individual Country tab** to explore any country’s latest performance

    ### 🌍 Significance
    This metric provides a quick signal of **transition quality** — beyond just renewable capacity.
    """)

# ---------------------------
# 🌎 Tab 1: Top 20 Countries
# ---------------------------
with tab1:
    st.markdown("## 🌍 Top 20 Countries by Displacement Score (Latest Year)")

    non_zero_df = displacement_df.dropna(subset=["displacement_score"])
    top20 = non_zero_df.sort_values("displacement_score", ascending=False).head(20)

    fig = px.bar(
        top20,
        x="country",
        y="displacement_score",
        color="displacement_score",
        color_continuous_scale="Greens",
        title="Top 20 Countries by Fossil Displacement Score",
        labels={"displacement_score": "Score (%)", "country": "Country"}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# 🔍 Tab 2: Individual Country
# ---------------------------
with tab2:
    st.markdown("## 🔍 Individual Country Score Explorer")

    available_countries = sorted(all_scores_df["country"].dropna().unique())
    selected_country = st.selectbox("Select Country", available_countries, index=available_countries.index("India") if "India" in available_countries else 0)

    country_data = all_scores_df[all_scores_df["country"] == selected_country].sort_values("year")
    
    if not country_data.empty:
        st.line_chart(country_data.set_index("year")["displacement_score"])
        latest = country_data.tail(1)
        st.metric(
            label=f"Latest Score ({latest['year'].values[0]})",
            value=f"{latest['displacement_score'].values[0]:.2f}%"
        )
        st.caption("A positive score indicates clean energy is replacing fossil fuels.")
    else:
        st.warning("No data available for this country.")

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.caption("Climenro | Fossil Displacement Comparison | Data: Our World in Data (OWID)")
