import os
import sys
import pandas as pd

# Base directory setup for cross-folder imports and file access
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.append(SCRIPTS_DIR)



# Import necessary local modules
#from policy_effectiveness import summarize_policy_effectiveness
from policy_vectorizer import score_policy_vector
from sector_vulnerability import get_sector_vulnerability_by_country
from co_benefit_analyzer import get_country_trends
from resilience_index import gain_trend_for_country
from co_benefit_analyzer import load_life_expectancy_data

DATA_DIR = os.path.join(BASE_DIR, "data")


def generate_country_story(country_name):
    """
    Generate a comprehensive dictionary capturing a country's climate policy journey and metrics.
    """

    # --- Load Datasets ---
    vectors_path = os.path.join(DATA_DIR, "policy_vectors.csv")
    edgar_path = os.path.join(DATA_DIR, "EDGAR_AR5_GHG_1970_2023.xlsx")
    gain_path = os.path.join(DATA_DIR, "nd_gain", "gain.csv")
    sector_data_path = os.path.join(DATA_DIR, "nd_gain", "vulnerability")
    energy_path = os.path.join(DATA_DIR, "owid-energy-data.csv")
    lifeexp_path = os.path.join(DATA_DIR, "owid_life_expectancy.csv")
    pm25_path = os.path.join(DATA_DIR, "PM2.5_WHO.csv")

    try:
        vectors = pd.read_csv(vectors_path)
        gain = pd.read_csv(gain_path)
        energy = pd.read_csv(energy_path)
        life = pd.read_csv(lifeexp_path)
        pm25 = pd.read_csv(pm25_path)
    except Exception as e:
        return {"error": f"❌ Failed to load required data: {e}"}

    # --- Get Policy Vector ---
    try:
        vector_row = vectors[vectors["jurisdiction"] == country_name].iloc[0]
        policy_vector = score_policy_vector(vector_row)
    except Exception as e:
        policy_vector = {}
        print(f"Warning: Could not find policy vector for {country_name}: {e}")

    # --- Summarize Policy Effectiveness ---
    try:
        policy_effectiveness = summarize_policy_effectiveness(country_name)
    except Exception as e:
        policy_effectiveness = {"note": f"Effectiveness summary not available: {e}"}

    # --- ND-GAIN Index Trend ---
    try:
        df_gain_long = gain.melt(id_vars=["ISO3", "Name"], var_name="year", value_name="gain_index")
        df_gain_long["year"] = df_gain_long["year"].astype(int)
        nd_gain_trend = gain_trend_for_country(df_gain_long, country_name)
    except Exception as e:
        nd_gain_trend = pd.DataFrame()
        print(f"Warning: ND-GAIN data issue for {country_name}: {e}")

    # --- Sector Vulnerability ---
    try:
        from sector_vulnerability import load_sector_vulnerability_data
        sector_df = load_sector_vulnerability_data()
        sector_vulnerability = get_sector_vulnerability_by_country(sector_df, country_name)
    except Exception as e:
        sector_vulnerability = pd.DataFrame()
        print(f"Warning: Sector vulnerability data issue: {e}")

    # --- Co-Benefits (Health, GDP, Pollution) ---
    try:
        from co_benefit_analyzer import prepare_lifeexp_data, prepare_pm25_data, prepare_gdp_data, merge_co_benefit_data
        df_life = load_life_expectancy_data(life)
        df_pm25 = prepare_pm25_data(pm25)
        df_gdp = prepare_gdp_data(energy)
        merged_df = merge_co_benefit_data(df_life, df_pm25, df_gdp)

        from co_benefit_analyzer import get_country_trends
        co_benefits = get_country_trends(merged_df, country_name)
    except Exception as e:
        co_benefits = pd.DataFrame()
        print(f"Warning: Co-benefits data issue: {e}")

    # --- Final Story Structure ---
    story = {
        "country": country_name,
        "policy_vector": policy_vector,
        "policy_effectiveness_summary": policy_effectiveness,
        "resilience_trend": nd_gain_trend,
        "sector_vulnerability": sector_vulnerability,
        "co_benefits": co_benefits
    }

    return story
