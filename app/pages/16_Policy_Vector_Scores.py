import streamlit as st
import pandas as pd
import os
import sys

# --- Setup path ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "scripts"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# --- Import function ---
from policy_vectorizer import score_policy_vector

# --- Page Config ---
st.set_page_config(page_title="🧠 Policy Vector Scoring", layout="wide")
st.title("🧠 Carbon Policy Vector Scores")

# --- Load Data ---
@st.cache_data
def load_and_score_policy_data():
    df = pd.read_csv("data/gen_info.csv")
    vectors = df.apply(score_policy_vector, axis=1)
    df_vectorized = pd.DataFrame(vectors.tolist())

    # Clean: remove empty/invalid rows
    df_vectorized = df_vectorized.dropna(subset=["jurisdiction"])
    df_vectorized = df_vectorized[df_vectorized["jurisdiction"].str.strip() != ""]
    df_vectorized = df_vectorized[df_vectorized["duration_years"] > 0]
    return df, df_vectorized

raw_df, vector_df = load_and_score_policy_data()

# Optional: Save scored output
vector_df.to_csv("data/policy_vectors.csv", index=False)

# --- Tabs ---
tab0, tab1, tab2 = st.tabs([
    "📘 Overview",
    "📋 Vectorized Policy Table",
    "🔎 Filter by Type"
])

# -------------------------------------
# 📘 Tab 0: Module Overview
# -------------------------------------
with tab0:
    st.markdown("## 📘 About This Module: Policy Vector Scores")
    st.markdown("""
    This module processes and scores carbon pricing policies into **structured numerical vectors** using our in-house policy vectorization engine.

    ### 🔍 What It Shows
    - Converts textual policy descriptions into numerical features
    - Covers attributes such as:
        - Policy type (Tax, ETS, Hybrid)
        - Duration
        - Coverage breadth
        - Sectoral and geographic reach
        - Legal and market strength indicators

    ### 🧪 Methodology
    - Input: `gen_info.csv` (metadata about each policy)
    - Each row is passed through `score_policy_vector()` to compute scores
    - Output: clean dataframe with **feature vectors per jurisdiction**
    - Vector features can then be used in:
        - Machine learning clustering
        - Policy effectiveness scoring
        - Visualization of cross-country patterns

    ### 📊 Fields Generated
    - `jurisdiction`, `duration_years`, `policy_type_tax`, `policy_type_ets`, `coverage_index`, etc.
    - Feature types include binary flags, scalars, durations, normalized coverage

    ### 📈 Significance
    - Enables **quantitative comparison** of diverse policy types
    - Foundation for downstream modules (clustering, benchmarking, effectiveness)
    - Supports data-driven climate policy recommendations

    ---
    """)

# -------------------------------------
# 📋 Tab 1: View Vectorized Table
# -------------------------------------
with tab1:
    st.subheader("📋 Raw Vectorized Policy Data")
    st.dataframe(vector_df.head(50), use_container_width=True)

# -------------------------------------
# 🔎 Tab 2: Filter by Policy Type
# -------------------------------------
with tab2:
    st.subheader("🔎 Filter by Policy Type")
    types = sorted(raw_df["Type"].dropna().unique())
    selected = st.multiselect("Choose Policy Types", types, default=types[:2])
    if selected:
        filtered = vector_df[raw_df["Type"].isin(selected)]
        st.dataframe(filtered, use_container_width=True)
    else:
        st.info("Please select one or more policy types to filter.")
