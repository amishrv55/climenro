import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re

class CarbonPriceAnalyzer:
    def __init__(self, carbon_price_path, inflation_path):
        self.carbon_data = self._load_carbon_data(carbon_price_path)
        self.inflation_data = self._load_inflation_data(inflation_path)
        
    def _load_carbon_data(self, filepath):
        """Load and clean World Bank carbon pricing data."""
        # Load both relevant sheets
        df_price = pd.read_excel(filepath, sheet_name="Compliance_Price", skiprows = 1)
        df_info = pd.read_excel(filepath, sheet_name="Compliance_Gen Info", skiprows = 1)

        # Create a mapping from Unique ID to Jurisdiction (country)
        jurisdiction_map = dict(zip(
            df_info["Unique ID"].astype(str), 
            df_info["Jurisdiction covered"]
        ))

        # Rename and clean key columns
        df_price = df_price.rename(columns={
            "Unique ID": "instrument_id",
            "Name of the initiative": "initiative",
            "Instrument Type": "type",
            "Region": "region",
            "Income group": "income_group",
            "Metric": "metric"
        })

        # Extract year columns and reshape to long format
        year_cols = [col for col in df_price.columns if re.match(r"^\d{4}$", str(col))]
        df_long = df_price.melt(
            id_vars=["instrument_id", "initiative", "type", "region", "income_group", "metric"],
            value_vars=year_cols,
            var_name="year",
            value_name="price_usd"
        )

        # Clean data
        df_long["year"] = df_long["year"].astype(int)
        df_long = df_long.dropna(subset=["price_usd"])

        # Map country from jurisdiction info
        df_long["country"] = df_long["instrument_id"].map(jurisdiction_map)

        # Handle missing country values (fallback to extracting from initiative name)
        missing_mask = df_long["country"].isna()
        df_long.loc[missing_mask, "country"] = df_long.loc[missing_mask, "initiative"].str.extract(r'^(.*?)(?:\s+carbon tax|\s+ETS|$)', expand=False)
        df_long["country"] = df_long["country"].str.strip()

        return df_long

    def _load_inflation_data(self, filepath):
        """Load and clean World Bank inflation data."""
        df = pd.read_csv(filepath, skiprows = 3)

        # Clean and rename
        df = df.rename(columns={
            "Country Name": "country",
            "Country Code": "country_code"
        })

        # Remove metadata column if exists
        if "Unnamed: 69" in df.columns:
            df.drop(columns=["Unnamed: 69"], inplace=True)
        
        year_cols = [col for col in df.columns if re.match(r"^\d{4}$", str(col))]
        df_long = df.melt(
            id_vars=["country", "country_code"],
            value_vars=year_cols,
            var_name="year",
            value_name="inflation_pct"
        )

        df_long["year"] = df_long["year"].astype(int)
        df_long = df_long.dropna(subset=["inflation_pct"])
        df_long["country"] = df_long["country"].str.strip()

        return df_long

    def get_available_countries(self):
        """Return list of countries for which carbon pricing data is available."""
        return sorted(self.carbon_data["country"].dropna().unique())

    def get_country_data(self, country):
        """Get both carbon price and inflation data for a specific country."""
        carbon_df = self.carbon_data[self.carbon_data["country"] == country]
        inflation_df = self.inflation_data[self.inflation_data["country"] == country]
        return carbon_df, inflation_df

    def generate_price_plot(self, carbon_df):
        fig = go.Figure()
        for initiative in carbon_df["initiative"].unique():
            subset = carbon_df[carbon_df["initiative"] == initiative]
            fig.add_trace(go.Scatter(
                x=subset["year"],
                y=subset["price_usd"],
                mode="lines+markers",
                name=initiative
            ))
        fig.update_layout(
            title="Carbon Price Timeline",
            xaxis_title="Year",
            yaxis_title="Price (USD/tCO2e)"
        )
        return fig

    def generate_inflation_plot(self, inflation_df):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=inflation_df["year"],
            y=inflation_df["inflation_pct"],
            mode="lines+markers",
            name="Inflation (%)"
        ))
        fig.update_layout(
            title="Inflation Timeline",
            xaxis_title="Year",
            yaxis_title="Inflation (%)"
        )
        return fig
