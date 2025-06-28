import streamlit as st
import pandas as pd
import os
import sys
import plotly.graph_objects as go
import numpy as np
from scipy.stats import ttest_ind

# Set page config first
st.set_page_config(page_title="📉 Policy Effectiveness", layout="wide")

# Setup script path
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "scripts"))
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

# Imports
from load_edgar import load_edgar_ipcc2006

@st.cache_data
def load_data():
    vectors = pd.read_csv("data/policy_vectors.csv").dropna(subset=["jurisdiction"])
    edgar = load_edgar_ipcc2006()
    return vectors, edgar

vectors_df, edgar_df = load_data()

# Tabs
tab0, tab1, tab2, tab3, tab4 = st.tabs([
    "📘 Overview",
    "📈 Emissions Trend",
    "📉 Pre vs Post Analysis",
    "📊 Policy Factor Scores",
    "💰 Emissions per GDP"
])

# -------------------------------
# 📘 Tab 0: Overview
# -------------------------------
with tab0:
    st.markdown("## 📘 Module Overview: Policy Effectiveness")
    st.markdown("""
    This module evaluates how effective national **carbon pricing policies** have been in reducing emissions over time.

    ### 🔍 What It Shows
    - National emissions trend before and after policy adoption
    - Comparison of slopes (emission growth rate)
    - Policy metadata (ETS, Tax, Hybrid) and duration
    - Emissions per GDP efficiency tracking
    - Statistical tests to assess significance of observed changes

    ### 🧪 Methodology
    - Policy metadata sourced from a `policy_vectors.csv` file
    - Emissions data from **EDGAR GHG dataset**
    - Analysis includes:
        - Emission slopes (pre vs post)
        - Emissions per GDP trend
        - T-test for statistical significance
        - Dynamic peak and slope tracking

    ### 🧭 How to Use
    1. Select a country from the dropdown
    2. Analyze emission trends and slope changes after policy adoption
    3. Check if emissions intensity per GDP improved
    4. Review tabular policy feature scores for insight into effectiveness

    ### 🌍 Significance
    - Identifies if emissions declined after carbon pricing policies
    - Highlights lagging or successful policy environments
    - Quantifies impact using objective, statistically sound indicators
    """)

# -------------------------------
# Sidebar Input (shared across tabs)
# -------------------------------
available_countries = sorted(vectors_df["jurisdiction"].dropna().unique())
country = st.sidebar.selectbox("Choose Country", available_countries, index=available_countries.index("Finland") if "Finland" in available_countries else 0)

policy_row = vectors_df[vectors_df["jurisdiction"] == country].iloc[0]

# Extract Metadata
policy_type = "Tax" if policy_row.get("policy_type_tax") == 1 else (
              "ETS" if policy_row.get("policy_type_ets") == 1 else (
              "Hybrid" if policy_row.get("policy_type_hybrid") == 1 else "N/A"))
duration = int(policy_row.get("duration_years", 0))
adoption_year = 2024 - duration if duration else None

# Shared Data
edgar_country = edgar_df[edgar_df["Name"] == country]
edgar_country = edgar_country.groupby("year", as_index=False)["emissions_mtco2e"].sum()

# -------------------------------
# 📈 Tab 1: Emissions Trend
# -------------------------------
with tab1:
    st.subheader(f"📈 Emissions Trend with Policy Marker – {country}")
    st.markdown(f"""
    **Policy Type:** {policy_type}  
    **Adoption Year:** {adoption_year if adoption_year else 'Unknown'}  
    **Duration:** {duration} years
    """)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edgar_country["year"], y=edgar_country["emissions_mtco2e"],
                             mode="lines+markers", name="Emissions", line=dict(color="steelblue")))
    if adoption_year:
        fig.add_vline(x=adoption_year, line_dash="dash", line_color="red")
        fig.add_annotation(x=adoption_year, y=edgar_country["emissions_mtco2e"].max(),
                           text=f"Policy Adopted: {adoption_year}", showarrow=True, arrowhead=1)

    fig.update_layout(xaxis_title="Year", yaxis_title="Emissions (MtCO₂e)")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 📉 Tab 2: Pre vs Post Policy
# -------------------------------
with tab2:
    st.subheader("📉 Trend Comparison: Before vs After Policy")

    if adoption_year and adoption_year >= edgar_country["year"].min() + 3 and adoption_year <= edgar_country["year"].max() - 3:
        pre = edgar_country[edgar_country["year"] < adoption_year]
        post = edgar_country[edgar_country["year"] >= adoption_year]
        pre_avg, post_avg = pre["emissions_mtco2e"].mean(), post["emissions_mtco2e"].mean()
        delta = post_avg - pre_avg
        st.metric("Average Emissions Change", f"{delta:.2f} MtCO₂e", delta=f"{(delta / pre_avg) * 100:.1f}%")

        # Slope Comparison
        def compute_slope(df):
            x, y = df["year"].values, df["emissions_mtco2e"].values
            return np.polyfit(x, y, 1)[0] if len(x) > 1 else np.nan

        pre_slope = compute_slope(pre)
        post_slope = compute_slope(post)
        peak_year = edgar_country.loc[edgar_country["emissions_mtco2e"].idxmax(), "year"]
        time_to_peak = peak_year - adoption_year if adoption_year else None

        st.markdown(f"**📈 Pre-policy Slope:** {pre_slope:.2f} MtCO₂e/year")
        st.markdown(f"**📉 Post-policy Slope:** {post_slope:.2f} MtCO₂e/year")
        st.markdown(f"**📌 Years to Peak:** {time_to_peak}")

        if post_slope < 0:
            st.success("✅ Emissions reduced after policy.")
        else:
            st.warning("⚠️ Emissions did not decline post-policy.")

        # Statistical Test
        if len(pre) >= 3 and len(post) >= 3:
            t_stat, p_val = ttest_ind(pre["emissions_mtco2e"], post["emissions_mtco2e"], equal_var=False)
            st.markdown("### 📊 T-Test on Emission Averages")
            st.markdown(f"**p-value:** `{p_val:.4f}`")
            if p_val < 0.01:
                st.success("✅ Strong evidence of change (p < 0.01)")
            elif p_val < 0.05:
                st.info("ℹ️ Moderate evidence (p < 0.05)")
            else:
                st.warning("❌ No strong statistical difference.")
    else:
        st.warning("Not enough years for pre/post comparison.")

# -------------------------------
# 📊 Tab 3: Policy Factor Breakdown
# -------------------------------
with tab3:
    st.subheader("📊 Policy Factor Vector Breakdown")
    score_display = policy_row.drop("jurisdiction").reset_index()
    score_display.columns = ["Feature", "Value"]
    score_display = score_display.astype(str)
    st.dataframe(score_display, use_container_width=True)

# -------------------------------
# 💰 Tab 4: Emissions per GDP
# -------------------------------
with tab4:
    st.subheader("💰 Emissions per GDP")

    @st.cache_data
    def load_owid_gdp():
        df = pd.read_csv("data/owid-energy-data.csv")
        return df[["iso_code", "year", "gdp"]]

    gdp_df = load_owid_gdp()
    iso_code = edgar_df[edgar_df["Name"] == country]["Country_code_A3"].iloc[0]
    gdp_country = gdp_df[gdp_df["iso_code"] == iso_code]
    merged = pd.merge(edgar_country, gdp_country, on="year", how="inner")
    merged["emissions_per_gdp"] = merged["emissions_mtco2e"] / merged["gdp"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merged["year"], y=merged["emissions_per_gdp"],
                             mode="lines+markers", name="Emissions/GDP"))
    if adoption_year:
        fig.add_vline(x=adoption_year, line_dash="dash", line_color="red")
    fig.update_layout(title="Emissions per GDP Trend", xaxis_title="Year", yaxis_title="Emissions / GDP")
    st.plotly_chart(fig, use_container_width=True)

    pre = merged[merged["year"] < adoption_year]["emissions_per_gdp"].dropna()
    post = merged[merged["year"] >= adoption_year]["emissions_per_gdp"].dropna()
    if len(pre) >= 3 and len(post) >= 3:
        tstat_gdp, p_gdp = ttest_ind(pre, post, equal_var=False)
        st.markdown(f"**T-test p-value (Emissions per GDP):** `{p_gdp:.4f}`")
        if p_gdp < 0.05:
            st.success("✅ Statistically significant change in emissions intensity.")
        else:
            st.info("ℹ️ No statistically significant difference.")
    else:
        st.warning("⚠️ Insufficient data for GDP efficiency comparison.")
