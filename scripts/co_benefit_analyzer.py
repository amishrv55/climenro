import pandas as pd
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

def load_life_expectancy_data():
    path = os.path.join(BASE_DIR, "owid_life_expectancy.csv")
    df = pd.read_csv(path)
    df = df.rename(columns={
        "Entity": "country",
        "Year": "year",
        "Period life expectancy at birth - Sex: total - Age: 0": "life_expectancy"
    })
    df = df[["country", "year", "life_expectancy"]]
    df = df.dropna()
    df["year"] = df["year"].astype(int)
    return df


def load_pm25_data():
    path = os.path.join(BASE_DIR, "PM2.5_WHO.csv")
    df = pd.read_csv(path)
    
    df = df.rename(columns={"Country Name": "country"})
    year_cols = [col for col in df.columns if col.isdigit()]
    
    df_long = df.melt(id_vars=["country"], value_vars=year_cols,
                      var_name="year", value_name="pm25")
    df_long["year"] = df_long["year"].astype(int)
    df_long["pm25"] = pd.to_numeric(df_long["pm25"], errors="coerce")
    df_long = df_long.dropna(subset=["pm25"])
    return df_long


def load_gdp_data():
    path = os.path.join(BASE_DIR, "owid-energy-data.csv")
    df = pd.read_csv(path)
    
    df = df.rename(columns={"country": "country", "year": "year"})
    df = df[["country", "year", "gdp"]]
    df = df.dropna(subset=["gdp"])
    df["year"] = df["year"].astype(int)
    return df


def merge_co_benefit_data(df_life, df_pm25, df_gdp):
    df = pd.merge(df_life, df_pm25, on=["country", "year"], how="inner")
    df = pd.merge(df, df_gdp, on=["country", "year"], how="inner")
    df = df.dropna(subset=["life_expectancy", "pm25", "gdp"])
    return df


# ---------- 5. Get Country Trend ----------
def get_country_trends(df, country_name):
    return df[df["country"] == country_name].sort_values("year")
