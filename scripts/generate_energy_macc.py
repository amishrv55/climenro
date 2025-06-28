import pandas as pd
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
LCOE_PATH = os.path.join(BASE_DIR, "lcoe.csv")
GEN_PATH = os.path.join(BASE_DIR, "eia_electricity_generation.csv")

# Technology mapping for LCOE data
LCOE_TECH_MAPPING = {
    "Onshore wind levelized cost of energy": "Wind",
    "Solar photovoltaic levelized cost of energy": "Solar",
    "Hydropower levelized cost of energy": "Hydro"
}

# Technology mapping for Generation data (from your sample)
GEN_TECH_MAPPING = {
    "Nuclear (billion kWh)": "Nuclear",
    "Fossil fuels (billion kWh)": "Fossil Fuels",
    "Coal (billion kWh)": "Coal",
    "Generation (billion kWh)": "Total Generation"
}

EMISSION_FACTORS = {
    "Coal": 0.82,
    "Fossil Fuels": 0.49,
    "Nuclear": 0.012,
    "Hydro": 0.024,
    "Solar": 0.045,
    "Wind": 0.011
}

def load_lcoe_data(proxy_country="Argentina"):
    """Load LCOE data using a proxy country when World data isn't available"""
    try:
        df = pd.read_csv(LCOE_PATH)
        
        # Get data for proxy country
        country_df = df[df["Entity"] == proxy_country].copy()
        
        if country_df.empty:
            available_countries = df["Entity"].unique()
            raise ValueError(
                f"No data for {proxy_country}. Available countries: {available_countries}"
            )
        
        # Melt and process data
        country_df = country_df.melt(
            id_vars=["Entity", "Code", "Year"],
            var_name="Technology",
            value_name="LCOE"
        )
        
        tech_mapping = {
            "Onshore wind levelized cost of energy": "Wind",
            "Solar photovoltaic levelized cost of energy": "Solar",
            "Hydropower levelized cost of energy": "Hydro"
        }
        
        country_df["Technology"] = country_df["Technology"].map(tech_mapping)
        country_df = country_df.dropna(subset=["Technology", "LCOE"])
        country_df["LCOE"] = country_df["LCOE"] * 1000  # USD/MWh
        
        return country_df[["Technology", "Year", "LCOE"]]
    
    except Exception as e:
        raise ValueError(f"LCOE data loading failed: {str(e)}")

def load_generation_data():
    try:
        # Read with skiprows=1 and manual header handling
        df = pd.read_csv(GEN_PATH, skiprows=1, header=None)
        
        # The technology names are in column 1 (second column)
        df = df.rename(columns={1: "Technology"})
        
        # Clean technology names
        df["Technology"] = df["Technology"].map(GEN_TECH_MAPPING)
        df = df.dropna(subset=["Technology"])
        
        # Melt year columns (columns 2 onwards)
        year_cols = [col for col in df.columns if isinstance(col, int) and col >= 2]
        df = df.melt(
            id_vars=["Technology"],
            value_vars=year_cols,
            var_name="Year",
            value_name="Generation"
        )
        
        # Convert year from column index to actual year
        # This assumes columns are in order from 1980 to 2023
        df["Year"] = 1980 + df["Year"] - 2
        df["Generation"] = pd.to_numeric(df["Generation"], errors="coerce")
        
        return df.dropna(subset=["Generation"])
    
    except Exception as e:
        raise ValueError(f"Generation data loading failed: {str(e)}")

def generate_energy_macc(proxy_country="Argentina"):
    """Generate MACC using specified proxy country for LCOE data"""
    try:
        # Load data - now using proxy_country parameter
        lcoe = load_lcoe_data(proxy_country)
        gen = load_generation_data()
        
        # Debug output
        print("Available LCOE Technologies:", lcoe["Technology"].unique())
        print("Available Generation Technologies:", gen["Technology"].unique())
        
        # Find common technologies
        common_techs = list(set(lcoe["Technology"]) & set(gen["Technology"]))
        
        if not common_techs:
            raise ValueError(
                f"No matching technologies between LCOE ({lcoe['Technology'].unique()}) "
                f"and generation ({gen['Technology'].unique()}) data"
            )
        
        # Merge data
        df = pd.merge(
            lcoe[lcoe["Technology"].isin(common_techs)],
            gen[gen["Technology"].isin(common_techs)],
            on=["Technology", "Year"],
            how="inner"
        )
        
        # Calculate MACC metrics
        df["Emission_Factor"] = df["Technology"].map(EMISSION_FACTORS)
        df["Emissions_MtCO2"] = df["Generation"] * df["Emission_Factor"]
        df["Total_Cost_MUSD"] = df["LCOE"] * df["Generation"] / 1e6
        df["Abatement_Cost"] = df["Total_Cost_MUSD"] * 1e6 / (df["Emissions_MtCO2"] * 1e6)
        
        return df[[
            "Technology", "Year", "LCOE", "Generation",
            "Emissions_MtCO2", "Total_Cost_MUSD", "Abatement_Cost"
        ]].rename(columns={"Generation": "Generation_TWh"})
        
    except Exception as e:
        raise ValueError(f"MACC generation failed: {str(e)}")

if __name__ == "__main__":
    test = generate_energy_macc("World")
    print(test.head())