# scripts/climate_change.py

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def plot_temp_vs_emissions(edgar_df, warming_df, country):
    # Filter and prep
    df_temp = warming_df[warming_df["variable"] == "tas"].copy()
    df_temp["year"] = pd.to_datetime(df_temp["date"]).dt.year

    df_em = edgar_df[edgar_df["Country_code_A3"] == country]
    df_em = df_em[df_em["ipcc_code_2006_for_standard_report_name"] == "Total excluding LULUCF"]
    df_em = df_em.dropna(axis=1)
    df_em = df_em.melt(id_vars=["Country_code_A3"], var_name="year", value_name="emissions")
    df_em["year"] = df_em["year"].str.extract("Y_(\d+)$").astype(int)

    # Merge
    merged = pd.merge(df_temp, df_em, on="year", how="inner")

    # Plot
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()

    ax1.plot(merged["year"], merged["value"], color="orange", label="Temperature (tas)")
    ax2.plot(merged["year"], merged["emissions"], color="green", label="Emissions")

    ax1.set_ylabel("Mean Surface Temp")
    ax2.set_ylabel("Emissions (Gg CO2e)")
    ax1.set_xlabel("Year")
    plt.title(f"{country} - Surface Temp vs Emissions")

    st.pyplot(fig)

# --- scripts/climate_change.py ---
import pandas as pd

# 1. Rolling average for smoother visualization
def compute_rolling_average(df, col, window=5):
    df = df.copy()
    df[col + "_smoothed"] = df[col].rolling(window=window, min_periods=1).mean()
    return df

# 2. Compute lag correlation between emissions and temperature
# Temp today vs. emissions X years ago

def compute_lag_correlation(temp_df, emissions_df, max_lag=10):
    results = []
    for lag in range(0, max_lag + 1):
        merged = pd.merge(temp_df, emissions_df, on="year", how="inner")
        merged["emissions_lagged"] = merged["emissions"].shift(lag)
        merged = merged.dropna()
        corr = merged["temp_ann"].corr(merged["emissions_lagged"])
        results.append({"lag_years": lag, "correlation": corr})
    return pd.DataFrame(results)
