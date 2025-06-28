import pandas as pd
import os

def load_region_temp(region_name, base_path="data/nasa_power"):
    file_map = {
        "Himalayas": "India_Himalayas.csv",
        "Ganga Plain": "India_Ganga_Plain.csv",
        "Kolkata": "India_Kolkata.csv",
        "Mumbai": "India_Mumbai.csv",
        "Chennai": "India_Chennai.csv",
    }
    file_path = os.path.join(base_path, file_map[region_name])
    df = pd.read_csv(file_path, skiprows=11, header = 0)
    df = df[df["PARAMETER"] == "T2M"]
    df = df.drop(columns=["PARAMETER"])
    df = df.rename(columns={"ANN": "temp_ann"})
    df["year"] = df["YEAR"]
    df["temp_ann"] = pd.to_numeric(df["temp_ann"], errors="coerce")
    return df[["year", "temp_ann"]].dropna()
