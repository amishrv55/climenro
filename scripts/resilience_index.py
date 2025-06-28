import pandas as pd
import os

# Load ND-GAIN gain.csv from specified path
def load_gain_data(filepath="data/nd_gain/gain.csv"):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    full_path = os.path.join(base_dir, filepath)
    df = pd.read_csv(full_path)
    # Melt the dataframe into long format for year-wise plotting
    df_long = df.melt(id_vars=["ISO3", "Name"], var_name="year", value_name="gain_index")
    df_long["year"] = df_long["year"].astype(int)
    return df_long

# Get latest gain index snapshot for each country
def latest_gain_snapshot(df_long):
    latest_year = df_long["year"].max()
    latest = df_long[df_long["year"] == latest_year]
    return latest.sort_values("gain_index", ascending=False)

# Get trend for a specific country
def gain_trend_for_country(df_long, country_name):
    return df_long[df_long["Name"] == country_name].sort_values("year")

# Compare multiple countries' trends
def gain_trend_multi(df_long, countries):
    return df_long[df_long["Name"].isin(countries)].sort_values(["Name", "year"])

# Top N improvers from start to latest year
def top_improvers(df_long, top_n=10):
    start_year = df_long["year"].min()
    end_year = df_long["year"].max()
    start = df_long[df_long["year"] == start_year][["Name", "gain_index"]].set_index("Name")
    end = df_long[df_long["year"] == end_year][["Name", "gain_index"]].set_index("Name")
    delta = (end["gain_index"] - start["gain_index"]).sort_values(ascending=False).head(top_n)
    return delta.reset_index().rename(columns={"gain_index": "gain_delta"})

# Run tests
gain_df = load_gain_data()
snapshot = latest_gain_snapshot(gain_df)
trend_example = gain_trend_for_country(gain_df, "Finland")
top_delta = top_improvers(gain_df)

gain_df.head(), snapshot.head(), trend_example.head(), top_delta.head()

def compute_country_ranks_over_time(df_gain_long, country_name):
    # Group by year and rank countries based on gain_index
    rank_data = []

    for year in sorted(df_gain_long["year"].unique()):
        df_year = df_gain_long[df_gain_long["year"] == year]
        df_year = df_year.dropna(subset=["gain_index"])
        df_year["rank"] = df_year["gain_index"].rank(ascending=False, method="min")

        country_row = df_year[df_year["Name"] == country_name]
        if not country_row.empty:
            rank_data.append({
                "year": year,
                "rank": int(country_row["rank"].values[0])
            })

    return pd.DataFrame(rank_data)


