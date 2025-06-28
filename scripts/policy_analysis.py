import pandas as pd

def load_policy_data(filepath="data/gen_info.csv"):
    df = pd.read_csv(filepath)
    return df

def get_policy_types(df):
    return df["Type"].dropna().unique()

def count_policies_by_type(df):
    return df["Type"].value_counts().reset_index().rename(columns={"index": "Policy Type", "Type": "Count"})

def countries_per_policy_type(df):
    return df.groupby("Type")["Jurisdiction covered"].nunique().reset_index().rename(columns={
        "Jurisdiction covered": "Number of Countries"
    })

def policy_adoption_timeline(df):
    df["adoption_year"] = df["Status"].str.extract(r"(\d{4})").astype(float)
    return df.dropna(subset=["adoption_year", "Jurisdiction covered", "Type"])[
        ["adoption_year", "Jurisdiction covered", "Type", "Instrument name"]
    ].rename(columns={"Jurisdiction covered": "country"})


def sectoral_coverage_summary(df):
    sector_cols = [
        'Electricity and heat', 'Industry', 'Mining and extractives',
        'Transport', 'Aviation', 'Buildings',
        'Agriculture, forestry and fishing fuel use', 'Agricultural emissions',
        'Waste', 'LULUCF'
    ]

    sector_counts = []
    for col in sector_cols:
        count = df[col].notna().sum()
        sector_counts.append({"Sector": col, "Count": count})

    return pd.DataFrame(sector_counts)



def get_policy_adoption_year(df, country_name):
    row = df[df["Jurisdiction covered"].str.contains(country_name, case=False, na=False)]
    row = row[row["Status"].str.contains(r"\d{4}")]
    if not row.empty:
        year = row.iloc[0]["Status"]
        return int(pd.to_numeric(str(year).strip()[-4:], errors='coerce'))
    return None


import pandas as pd

def count_countries_per_policy(df):
    """
    Returns a DataFrame with the number of unique countries adopting each carbon policy type.
    """
    grouped = df.groupby("Type")["Jurisdiction covered"].nunique().reset_index()
    grouped.columns = ["Type", "country_count"]
    return grouped
