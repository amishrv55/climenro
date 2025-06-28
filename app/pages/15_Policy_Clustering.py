import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import plotly.express as px

# --- Page Setup ---
st.set_page_config(page_title="Policy Clustering", layout="wide")
st.title("🔍 Policy Vector Clustering Analysis")

# --- Load vectorized policy data ---
@st.cache_data
def load_vector_data():
    return pd.read_csv("data/policy_vectors.csv")

df = load_vector_data()

# --- Required Columns Check ---
meta_cols = ["jurisdiction", "policy_type_tax", "policy_type_ets", "policy_type_hybrid"]
if not all(col in df.columns for col in meta_cols):
    st.error(f"🛑 Required columns not found. Check for: {meta_cols}")
    st.stop()

# --- Infer consolidated policy type ---
def infer_policy_type(row):
    if row["policy_type_tax"] == 1:
        return "Tax"
    elif row["policy_type_ets"] == 1:
        return "ETS"
    elif row["policy_type_hybrid"] == 1:
        return "Hybrid"
    return "Other"

df["Policy Type"] = df.apply(infer_policy_type, axis=1)
X_meta = df[["jurisdiction", "Policy Type"]]
X = df.drop(columns=["jurisdiction", "Policy Type", *meta_cols], errors="ignore")

# --- Standardize ---
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# --- Cluster Control (Top, not Sidebar) ---
st.markdown("### 🔧 Choose Number of Clusters (KMeans)")
num_clusters = st.slider("Number of Clusters", min_value=2, max_value=10, value=4)

# --- Tabs ---
tab0, tab1, tab2, tab3 = st.tabs([
    "📘 Overview",
    "🧬 PCA Clustering",
    "🌀 t-SNE Clustering",
    "📋 Cluster Table"
])

# -----------------------------------------------
# 📘 Tab 0: Overview
# -----------------------------------------------
with tab0:
    st.markdown("## 📘 Module Overview: Policy Clustering")
    st.markdown("""
    This module applies **unsupervised clustering techniques** to group countries based on the **features of their carbon pricing policies**.

    ### 🔍 What It Shows
    - Groups (clusters) of countries with similar policy characteristics
    - Visualizations using **PCA** and **t-SNE** dimensionality reduction
    - Coloring and hover support for policy types and jurisdictions
    - A searchable cluster-wise table

    ### 🧪 Methodology
    - Input: `policy_vectors.csv` with binary/categorical/policy duration flags
    - Features are scaled using `StandardScaler`
    - **KMeans** clustering applied in latent space (controlled via slider above)
    - Dimensionality reduction using:
        - PCA (Principal Component Analysis)
        - t-SNE (nonlinear, perplexity = 5)

    ### 📊 Dataset Fields Used
    - policy_type_tax, policy_type_ets, hybrid, duration, coverage flags, etc.

    ### 🧭 How to Use
    1. Adjust the number of clusters (top of the page)
    2. Explore PCA and t-SNE cluster patterns
    3. Hover over plots to inspect jurisdictions and policy types
    4. Use the final tab to explore a sortable cluster table

    ### 🌍 Significance
    - Helps identify **peer countries** with similar climate instruments
    - Useful for benchmarking, policy design, and international negotiation insights

    ---
    """)

# -----------------------------------------------
# 🧬 Tab 1: PCA Clustering
# -----------------------------------------------
with tab1:
    st.subheader("🧬 PCA – Clustered Policy Vectors")

    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(X_scaled)
    pca_df = pd.DataFrame({
        "PCA1": pca_result[:, 0],
        "PCA2": pca_result[:, 1],
        "Jurisdiction": X_meta["jurisdiction"],
        "Policy Type": X_meta["Policy Type"]
    })

    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    pca_df["Cluster"] = kmeans.fit_predict(X_scaled).astype(str)

    fig_pca = px.scatter(
        pca_df, x="PCA1", y="PCA2", color="Cluster",
        hover_data=["Jurisdiction", "Policy Type"],
        title="PCA: Clustered Policy Vectors"
    )
    st.plotly_chart(fig_pca, use_container_width=True)

# -----------------------------------------------
# 🌀 Tab 2: t-SNE Clustering
# -----------------------------------------------
with tab2:
    st.subheader("🌀 t-SNE – Clustered Policy Vectors")

    tsne = TSNE(n_components=2, perplexity=5, learning_rate=200, n_iter=1000, random_state=42)
    tsne_result = tsne.fit_transform(X_scaled)

    tsne_df = pd.DataFrame({
        "tSNE1": tsne_result[:, 0],
        "tSNE2": tsne_result[:, 1],
        "Jurisdiction": X_meta["jurisdiction"],
        "Policy Type": X_meta["Policy Type"],
        "Cluster": pca_df["Cluster"]
    })

    fig_tsne = px.scatter(
        tsne_df, x="tSNE1", y="tSNE2", color="Cluster",
        hover_data=["Jurisdiction", "Policy Type"],
        title="t-SNE: Clustered Policy Vectors"
    )
    st.plotly_chart(fig_tsne, use_container_width=True)

# -----------------------------------------------
# 📋 Tab 3: Cluster Table
# -----------------------------------------------
with tab3:
    st.subheader("📋 Cluster Membership Table")
    st.dataframe(pca_df.sort_values("Cluster"), use_container_width=True)
