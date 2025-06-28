import streamlit as st
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt

# ✅ Set page config first
st.set_page_config(page_title="🔄 Fossil Fuel Displacement", layout="wide")

# Setup import path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "scripts"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Imports
from displacement_analysis import *
from owid_functions import load_owid_data

# Load data
@st.cache_data
def load_data():
    return load_owid_data()

df = load_data()

# -----------------------------
# 🎛️ Top Filter Bar
# -----------------------------
countries = sorted(df["iso_code"].dropna().unique())
selected_country = st.selectbox("🌍 Select Country (ISO Code)", countries, index=countries.index("IND"))

st.markdown("<hr class='thin-line'/>", unsafe_allow_html=True)

# -----------------------------
# 📂 Tabs
# -----------------------------
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📘 Overview",
    "📊 Fossil vs Renewables",
    "📈 Annual Growth Rates",
    "📎 Energy Shares",
    "🟢 Displacement Score",
    "📓 Interpretation"
])

# -----------------------------
# 📘 Tab 0: Overview
# -----------------------------
with tab0:
    st.markdown("## 📘 Module Overview: Fossil Displacement by Renewables")
    st.markdown("""
    This module tracks how **renewable energy is replacing fossil fuels** over time using country-level electricity data.

    ### 🔍 What It Shows
    - Trends in fossil and renewable generation (TWh)
    - Annual growth rates (%)
    - Fossil vs renewable energy share in total electricity
    - Displacement score = difference in growth rates
    - Whether clean energy is really *displacing* fossil fuels

    ### 🧪 Methodology
    - Data Source: **Our World in Data (OWID)** Energy Dataset
    - Calculation:
        - Displacement Score = Renewable growth (%) – Fossil growth (%)
        - Positive score = Renewable replacing fossil
        - Negative = Fossil still growing faster

    ### 🧭 How to Use
    1. Choose a country using the filter above
    2. Explore each tab for growth, shares, displacement scores
    3. Focus on years where renewables begin outpacing fossil fuels

    ### 🌍 Significance
    Displacement score is critical to understand if a country is transitioning *away* from fossil fuels — not just *adding* renewables.
    """)

# -----------------------------
# 📊 Tab 1: Fossil vs Renewable Energy
# -----------------------------
with tab1:
    st.markdown(f"## 📊 Fossil vs Renewable Energy – {selected_country}")
    data1 = fossil_vs_renewable_energy(df, selected_country)
    st.line_chart(data1.set_index("year"))

# -----------------------------
# 📈 Tab 2: Annual Growth Rate
# -----------------------------
with tab2:
    st.markdown(f"## 📈 Annual Growth Rate – {selected_country}")
    data2 = energy_growth_rates(df, selected_country)
    st.line_chart(data2.set_index("year")[["fossil_growth", "renewable_growth"]])

# -----------------------------
# 📎 Tab 3: Energy Share in Total Mix
# -----------------------------
with tab3:
    st.markdown(f"## 📎 Energy Share in Total Mix – {selected_country}")
    data3 = energy_shares(df, selected_country)
    st.line_chart(data3.set_index("year"))

# -----------------------------
# 🟢 Tab 4: Displacement Score
# -----------------------------
with tab4:
    st.markdown(f"## 🟢 Displacement Score – {selected_country}")
    data4 = displacement_score(df, selected_country)
    fig, ax = plt.subplots()
    ax.plot(data4["year"], data4["displacement_score"], color="green")
    ax.axhline(0, linestyle="--", color="gray")
    ax.set_ylabel("Displacement Score (%)")
    ax.set_xlabel("Year")
    ax.set_title(f"{selected_country}: Displacement Effectiveness Over Time")
    st.pyplot(fig)

# -----------------------------
# 📓 Tab 5: Interpretation Guide
# -----------------------------
with tab5:
    st.markdown("## 📓 How to Interpret Displacement Score")
    st.markdown("""
    The **Displacement Score** helps answer:  
    > *Is renewable energy actually replacing fossil fuels — or just being added on top of them?*

    - **✅ Positive Score:**  
      Renewable energy is growing *faster* than fossil fuel energy.  
      Indicates effective displacement.

    - **❌ Negative Score:**  
      Fossil fuel usage is still growing faster or not declining enough.  
      Indicates that renewables may not be reducing carbon emissions yet.

    This metric supports more nuanced policy monitoring than just measuring total renewable energy.

    ---
    """)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Climenro | Fossil Displacement Tracker | Data: OWID Energy Dataset")
