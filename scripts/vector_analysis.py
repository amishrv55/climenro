import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

def normalize_vectors(df):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)
    return pd.DataFrame(X_scaled, columns=df.columns)

def compute_pca(df, n_components=2):
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(df)
    return pd.DataFrame(X_pca, columns=[f"PC{i+1}" for i in range(n_components)]), pca.explained_variance_ratio_

def compute_tsne(df, n_components=2, perplexity=30, random_state=42):
    tsne = TSNE(n_components=n_components, perplexity=perplexity, random_state=random_state)
    X_tsne = tsne.fit_transform(df)
    return pd.DataFrame(X_tsne, columns=[f"TSNE{i+1}" for i in range(n_components)])
