import pandas as pd
import os

def load_edgar_ipcc2006(filepath="data/EDGAR_AR5_GHG_1970_2023.xlsx", sheet_name="IPCC 2006"):
    return _load_edgar_file(filepath, sheet_name)

def load_edgar_co2(filepath="data/EDGAR_CO2_1970_2023.xlsx", sheet_name="IPCC 2006"):
    return _load_edgar_file(filepath, sheet_name)

def load_edgar_co2bio(filepath="data/EDGAR_CO2bio_1970_2023.xlsx", sheet_name="IPCC 2006"):
    return _load_edgar_file(filepath, sheet_name)

def load_edgar_ch4(filepath="data/EDGAR_CH4_1970_2023.xlsx", sheet_name="IPCC 2006"):
    return _load_edgar_file(filepath, sheet_name)

def load_edgar_n2o(filepath="data/EDGAR_N2O_1970_2023.xlsx", sheet_name="IPCC 2006"):
    return _load_edgar_file(filepath, sheet_name)

def _load_edgar_file(filepath, sheet_name):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    full_path = os.path.join(base_dir, filepath)
    df = pd.read_excel(full_path, sheet_name=sheet_name, header=9)

    # Identify year columns
    year_cols = [col for col in df.columns if str(col).startswith("Y_")]

    # Melt wide to long format
    df_long = df.melt(
        id_vars=["Country_code_A3", "Name", 
                 "ipcc_code_2006_for_standard_report", 
                 "ipcc_code_2006_for_standard_report_name", 
                 "Substance", "fossil_bio"],
        value_vars=year_cols,
        var_name="year",
        value_name="emissions_gg"
    )

    # Clean columns
    df_long['year'] = df_long['year'].str.replace("Y_", "").astype(int)
    df_long['emissions_mtco2e'] = df_long['emissions_gg'] / 1000
    df_long.dropna(subset=["emissions_mtco2e"], inplace=True)

    return df_long

def load_population(filepath="data/total_population_un.csv"):
    df = pd.read_csv(filepath, encoding="utf-8", skiprows = 4)
    df = df.melt(id_vars=["Country Name", "Country Code"], var_name="year", value_name="population")
    df = df.rename(columns={"Country Code": "Country_code_A3", "Country Name": "Country"})
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year", "population"])
    df["year"] = df["year"].astype(int)
    return df


def load_gdp(filepath="data/imf_gdp_current_prices.csv"):
    # Load while skipping row 1 (empty), keep row 0 as header
    df = pd.read_csv(filepath, encoding="ISO-8859-1", skiprows=[1])

    # Rename first column to 'Country'
    df = df.rename(columns={df.columns[0]: "Country"})

    # Keep only numeric year columns
    year_cols = [col for col in df.columns if col.isdigit()]
    df = df[["Country"] + year_cols]

    # Melt into long format
    df = df.melt(id_vars=["Country"], var_name="year", value_name="gdp_billion_usd")

    # Clean values
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["gdp_billion_usd"] = pd.to_numeric(df["gdp_billion_usd"].replace("no data", pd.NA), errors="coerce")
    df = df.dropna(subset=["year", "gdp_billion_usd"])
    df["year"] = df["year"].astype(int)

    return df

