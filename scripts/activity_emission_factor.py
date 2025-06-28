import pandas as pd

def load_activity_table(path='data/activity_emission_factor.csv'):
    df = pd.read_csv(path, encoding='utf-8')
    df['Keywords'] = df['Keywords'].fillna('').apply(
        lambda x: [kw.strip().lower() for kw in x.split(',')]
    )
    return df

def load_country_factors(path='data/country_composite_factor.csv'):
    df = pd.read_csv(path, encoding='utf-8')
    df['Country'] = df['Country'].str.strip()
    return df

def get_displacement_ratio(country_name, df_country):
    row = df_country[df_country['Country'].str.lower() == country_name.lower()]
    if not row.empty:
        return float(row.iloc[0]['Displacement Ratio'])
    return None  # Or raise warning


def classify_policy(policy_text, df_activity):
    policy_text = policy_text.lower()
    match_scores = []

    for idx, row in df_activity.iterrows():
        score = sum(1 for kw in row['Keywords'] if kw in policy_text)
        match_scores.append(score)

    best_idx = pd.Series(match_scores).idxmax()

    if match_scores[best_idx] == 0:
        return {"matched": False, "activity_class": None}

    return {
        "matched": True,
        "activity_class": df_activity.loc[best_idx, 'Activity Class'],
        "keywords_matched": [kw for kw in df_activity.loc[best_idx, 'Keywords'] if kw in policy_text],
        "emission_per_unit": df_activity.loc[best_idx, 'CO₂e Impact'],
        "unit": df_activity.loc[best_idx, 'Unit'],
        "instrument_type": df_activity.loc[best_idx, 'Instrument Type'],
        "sector": df_activity.loc[best_idx, 'Sector']
    }


def estimate_emission_impact(policy_result, budget, subsidy_per_unit, displacement_ratio):
    try:
        # Parse emission value from policy_result['emission_per_unit'] like '–1.6 tons'
        emission_value = float(policy_result['emission_per_unit'].replace('–', '-').split()[0])
        estimated_units = budget / subsidy_per_unit
        total_impact = estimated_units * emission_value * displacement_ratio
        return round(total_impact, 2)
    except Exception as e:
        return None

def parse_emission_value(emission_str):
    try:
        return float(emission_str.replace('–', '-').replace(',', '').split()[0])
    except Exception:
        return None

def get_required_input_type(activity_row):
    if isinstance(activity_row, pd.Series):
        return activity_row.get('Required Input Type', 'budget').strip().lower()
    return 'budget'

def estimate_units(policy_row, user_input, country_row=None):
    input_type = get_required_input_type(policy_row)
    
    if input_type == 'budget':
        unit_cost = policy_row.get('Default Unit Cost')
        if pd.isna(unit_cost) or unit_cost == 0:
            return None
        displacement_ratio = 1.0
        if country_row is not None and policy_row.get('Uses Displacement', False):
            displacement_ratio = float(country_row.get('Displacement Ratio', 1.0))
        return (user_input / float(unit_cost)) * displacement_ratio
    
    else:
        # For other direct quantity inputs (length, area, etc.)
        return user_input

def estimate_emission_impact(policy_row, user_input, country_row=None):
    emission_per_unit = parse_emission_value(policy_row.get('CO₂e Impact', ''))
    if emission_per_unit is None:
        return None

    units = estimate_units(policy_row, user_input, country_row)
    if units is None:
        return None

    return round(units * emission_per_unit, 2)

def get_activity_row(policy_result, df_activity):
    return df_activity[df_activity['Activity Class'] == policy_result['activity_class']].iloc[0]

def build_policy_node(policy_text, country, budget, subsidy_per_unit=5000, df_activity=None, df_country=None):
    result = classify_policy(policy_text, df_activity)
    displacement_ratio = get_displacement_ratio(country, df_country)

    if not result["matched"] or not displacement_ratio:
        return None  # Or handle gracefully

    # Estimate total impact
    activity_row = get_activity_row(result, df_activity)
    country_row = df_country[df_country['Country'].str.lower() == country.lower()].iloc[0]
    total_impact = estimate_emission_impact(activity_row, budget, country_row)
    emission_value = parse_emission_value(result['emission_per_unit'])  # reuse for alignment


    # Alignment
    alignment = "Positive" if emission_value < 0 else "Negative" if emission_value > 0 else "Neutral"
    node_color = "green" if alignment == "Positive" else "red" if alignment == "Negative" else "gray"

    # Normalize impact to [0–100] for node size (basic scaling, improve later)
    node_size = min(max(abs(total_impact), 10), 100)

    return {
        "Policy Node": result["activity_class"],
        "Core Intent": result["activity_class"],
        "Sector": result["sector"],
        "Dept": sector_to_dept(result["sector"]),
        "CO₂ Impact (Mt ±)": round(total_impact / 1e6, 4) if total_impact else None,
        "Impact Factor": round(total_impact / 1e6, 4) if total_impact else None,
        "Alignment": alignment,
        "Instrument": result.get("instrument_type", "Subsidy"),  # Default
        "Start–End": "2025–2030",
        "Beneficiary": sector_to_beneficiary(result["sector"]),
        "Influencer": sector_to_influencer(result["sector"]),
        "Efficiency": get_efficiency_score(country, df_country),
        "Node Size": node_size,
        "Node Color": node_color
    }

def sector_to_dept(sector):
    mapping = {
        "Transport": "Ministry of Transport",
        "Electricity": "Ministry of Energy",
        "Cement": "Ministry of Industry",
        "Agriculture": "Ministry of Agriculture",
        "Waste": "Urban Development",
        # Add more...
    }
    return mapping.get(sector, "General")

def sector_to_beneficiary(sector):
    mapping = {
        "Transport": "Urban Citizens",
        "Cement": "Cement Companies",
        "Electricity": "Power Producers",
        # ...
    }
    return mapping.get(sector, "Public")

def sector_to_influencer(sector):
    mapping = {
        "Transport": "UNEP, EV Lobbies",
        "Cement": "IPCC, Carbon Funders",
        "Electricity": "Renewable Advocates",
        # ...
    }
    return mapping.get(sector, "General Influencers")

def get_efficiency_score(country, df_country):
    row = df_country[df_country['Country'].str.lower() == country.lower()]
    if not row.empty:
        return float(row.iloc[0]['Efficiency'])
    return 0.5
