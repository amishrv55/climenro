import streamlit as st
import pandas as pd
import os
import sys
import plotly.express as px

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "scripts"))
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

from resilience_index import (
    load_gain_data,
    latest_gain_snapshot,
    gain_trend_for_country,
    gain_trend_multi,
    top_improvers,
    compute_country_ranks_over_time,
)

# Page configuration
st.set_page_config(page_title="🛡️ ND-GAIN Climate Resilience Index", layout="wide")
st.title("🛡️ ND-GAIN Climate Resilience Index")

# Load data
@st.cache_data
def load_data():
    return load_gain_data()

df_gain = load_data()
all_countries = sorted(df_gain["Name"].dropna().unique())

# --- Country selector on top ---
col1 = st.columns([3])[0]
selected_country = col1.selectbox("🌍 Select Country", all_countries, index=all_countries.index("India") if "India" in all_countries else 0)

# --- Tabs ---
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📘 Overview",
    "🌐 Global Snapshot",
    "📈 Country Trend",
    "🔍 Compare Countries",
    "📊 Rank Over Time",
    "📈 Top Improvers"
])

# ----------------------------
# Tab 0: Overview
# ----------------------------
with tab0:
    st.markdown("## 📘 Module Overview – ND-GAIN Resilience Index")
    st.markdown("""
    The **ND-GAIN (Notre Dame Global Adaptation Initiative)** index measures a country's **vulnerability** to climate change and its **readiness** to improve resilience.

    ### 🧪 Methodology
    - The **ND-GAIN index** aggregates over 45 indicators covering:
        - **Exposure, sensitivity, and adaptive capacity** in key sectors
        - **Readiness to leverage investments** and implement adaptation strategies
    - Each country gets a score between **0 (worst)** and **100 (best)**.
    - Updated annually since **1995**.

    ### 📂 Datasets Used
    - `nd_gain_country_index.csv` (via Notre Dame Global Adaptation Initiative)

    ### 📊 What It Shows
    - Country rankings by latest resilience scores
    - Resilience **trend over time** for individual countries
    - **Top global improvers** since 1995
    - **Comparative analysis** across selected nations
    - Rank change timeline for each country

    ### 🌍 Significance
    - Assists **policy makers** in benchmarking national readiness for climate impacts
    - Helps identify **resilient vs vulnerable countries**
    - Encourages **targeted climate investment** by development banks, NGOs, and investors

    ### 🧭 How to Use
    1. Select a country from the dropdown above
    2. Use the tabs to explore:
        - Latest scores and ranks
        - Historical performance
        - Comparisons with other countries
        - Countries making the fastest improvements

    ---
    """)

# ----------------------------
# Tab 1: Global Snapshot
# ----------------------------
with tab1:
    st.subheader("🌐 Latest ND-GAIN Resilience Rankings")
    latest = latest_gain_snapshot(df_gain)

    fig_top = px.bar(latest.head(15), x="gain_index", y="Name", orientation="h", title="Top 15 Most Resilient Countries")
    st.plotly_chart(fig_top, use_container_width=True)

    fig_bottom = px.bar(latest.tail(15), x="gain_index", y="Name", orientation="h", title="Bottom 15 Least Resilient Countries")
    st.plotly_chart(fig_bottom, use_container_width=True)

# ----------------------------
# Tab 2: Country Trend
# ----------------------------
with tab2:
    st.subheader(f"📈 ND-GAIN Trend for {selected_country}")
    country_df = gain_trend_for_country(df_gain, selected_country)

    fig = px.line(country_df, x="year", y="gain_index", title=f"ND-GAIN Index for {selected_country}")
    fig.update_traces(mode="lines+markers")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# Tab 3: Compare Countries
# ----------------------------
with tab3:
    st.subheader("🔍 Compare ND-GAIN Trends Across Countries")
    selected = st.multiselect("Select Countries to Compare", all_countries, default=["India", "United States", "Finland", "Germany"])
    if selected:
        multi_df = gain_trend_multi(df_gain, selected)
        fig = px.line(multi_df, x="year", y="gain_index", color="Name", title="ND-GAIN Trends Across Selected Countries")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select at least one country to compare.")

# ----------------------------
# Tab 4: Rank Over Time
# ----------------------------
with tab4:
    st.subheader(f"📊 ND-GAIN Rank of {selected_country} Over Time")
    rank_df = compute_country_ranks_over_time(df_gain, selected_country)

    st.dataframe(rank_df.style.format({"rank": "{:.0f}"}), use_container_width=True)

    fig_rank = px.line(rank_df, x="year", y="rank", title="ND-GAIN Rank Over Time", markers=True)
    fig_rank.update_yaxes(autorange="reversed", title="Rank (Lower is Better)")
    st.plotly_chart(fig_rank, use_container_width=True)

# ----------------------------
# Tab 5: Top Improvers
# ----------------------------
with tab5:
    st.subheader("📈 Countries Improving the Most Since 1995")
    improvers = top_improvers(df_gain, top_n=10)
    fig = px.bar(improvers, x="gain_delta", y="Name", orientation="h", title="Top 10 Most Improved Countries")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📄 View Raw ND-GAIN Data"):
        st.dataframe(df_gain)

# Footer
st.caption("📘 Data Source: Notre Dame Global Adaptation Initiative (ND-GAIN)")
