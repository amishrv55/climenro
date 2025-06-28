import pandas as pd

# 1. Year-over-year comparison of emissions vs renewable share
def compare_emission_vs_renewable(df_emission, df_renew, country_code):
    emissions = df_emission[df_emission["Country_code_A3"] == country_code][["year", "emissions_mtco2e"]]
    renewables = df_renew[df_renew["iso_code"] == country_code][["year", "renewables_share_energy"]]

    merged = pd.merge(emissions, renewables, on="year", how="inner")
    return merged.sort_values("year")

# 2. Emission growth vs renewable growth year-on-year (percentage change)
def growth_trend_comparison(df_emission, df_renew, country_code):
    merged = compare_emission_vs_renewable(df_emission, df_renew, country_code)
    merged["emission_change_pct"] = merged["emissions_mtco2e"].pct_change() * 100
    merged["renewable_change_pct"] = merged["renewables_share_energy"].pct_change() * 100
    return merged.dropna()

# 3. Correlation between emission and renewables (Pearson)
def correlation_emission_renewable(df_emission, df_renew, country_code):
    merged = compare_emission_vs_renewable(df_emission, df_renew, country_code)
    if len(merged) < 5:
        return None  # not enough data points
    return merged["emissions_mtco2e"].corr(merged["renewables_share_energy"])

# 3b. Lag correlation: Renewables this year vs emissions two years later
def lag_correlation(df_emission, df_renew, country_code, lag=2):
    emissions = df_emission[df_emission["Country_code_A3"] == country_code][["year", "emissions_mtco2e"]]
    renewables = df_renew[df_renew["iso_code"] == country_code][["year", "renewables_share_energy"]]

    renewables["year"] = renewables["year"] + lag  # shift renewables forward
    merged = pd.merge(emissions, renewables, on="year", how="inner")

    if len(merged) < 5:
        return None
    return merged["emissions_mtco2e"].corr(merged["renewables_share_energy"])

# 4. Country ranking: Emission reduction with renewable growth
def emission_reduction_vs_renewable_growth(df_emission, df_renew, year_start, year_end):
    # Aggregate start and end values per country
    em_start = df_emission[df_emission["year"] == year_start].groupby("Country_code_A3")["emissions_mtco2e"].sum()
    em_end = df_emission[df_emission["year"] == year_end].groupby("Country_code_A3")["emissions_mtco2e"].sum()
    renew_start = df_renew[df_renew["year"] == year_start].groupby("iso_code")["renewables_share_energy"].mean()
    renew_end = df_renew[df_renew["year"] == year_end].groupby("iso_code")["renewables_share_energy"].mean()

    df_compare = pd.DataFrame({
        "emission_change_pct": ((em_end - em_start) / em_start * 100),
        "renewable_change_pct": ((renew_end - renew_start) / renew_start * 100)
    }).dropna()

    return df_compare.reset_index().rename(columns={"index": "iso_code"})

# 5. Emission per TWh electricity
def emission_per_twh(df_emission, df_renew, country_code):
    merged = pd.merge(
        df_emission[df_emission["Country_code_A3"] == country_code][["year", "emissions_mtco2e"]],
        df_renew[df_renew["iso_code"] == country_code][["year", "electricity_generation"]],
        on="year",
        how="inner"
    ).dropna()
    merged["emission_per_twh"] = merged["emissions_mtco2e"] / merged["electricity_generation"]
    return merged[["year", "emission_per_twh"]]

# 6. Renewable source breakdown vs emission trend (solar/wind)
def renewable_type_vs_emission(df_emission, df_renew, country_code):
    emissions = df_emission[df_emission["Country_code_A3"] == country_code][["year", "emissions_mtco2e"]]
    renewables = df_renew[df_renew["iso_code"] == country_code][[
        "year", "solar_share_elec", "wind_share_elec", "hydro_share_elec"
    ]]
    return pd.merge(emissions, renewables, on="year", how="inner").dropna()

# 7. Fossil electricity decline trend
def fossil_electricity_trend(df_renew, country_code):
    subset = df_renew[df_renew["iso_code"] == country_code][["year", "fossil_electricity"]].dropna()
    return subset.sort_values("year")

# 8. Sector-wise emissions trend comparison (with renewable growth)
def sector_emission_vs_renewable(df_emission, df_renew, country_code, sector_keyword):
    sector_df = df_emission[(df_emission["Country_code_A3"] == country_code) &
                            (df_emission["ipcc_code_2006_for_standard_report_name"].str.contains(sector_keyword, case=False))][["year", "emissions_mtco2e"]]

    renew = df_renew[df_renew["iso_code"] == country_code][["year", "renewables_share_energy"]]

    merged = pd.merge(sector_df, renew, on="year", how="inner")
    return merged.sort_values("year")
