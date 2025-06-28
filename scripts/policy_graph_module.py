# policy_graph_module.py

import os
import json
import uuid
import pandas as pd
from datetime import datetime

# === 1. Loaders ===
def load_activity_table(path):
    df = pd.read_csv(path)
    df['Keywords'] = df['Keywords'].fillna('').apply(lambda x: [kw.strip().lower() for kw in x.split(',')])
    return df

def load_country_factors(path):
    df = pd.read_csv(path)
    df['Country'] = df['Country'].str.strip()
    return df

# === 2. Core Classification ===
def classify_policy(policy_text, df_activity):
    policy_text = policy_text.lower()
    match_scores = [sum(1 for kw in row['Keywords'] if kw in policy_text) for _, row in df_activity.iterrows()]
    best_idx = pd.Series(match_scores).idxmax()
    if match_scores[best_idx] == 0:
        return None
    return df_activity.iloc[best_idx]

# === 3. Estimators ===
def parse_emission_value(val):
    try:
        val = val.replace('–', '-').replace('+', '').replace('tons', '').replace('Mt', 'e6').replace('kt', 'e3')
        return float(eval(val.strip().split()[0]))
    except:
        return None

def estimate_units(row, input_value, country_row):
    if row['Required Input Type'] == 'budget':
        unit_cost = row.get('Default Unit Cost')
        if pd.isna(unit_cost) or unit_cost == 0:
            return None
        multiplier = float(country_row['Displacement Ratio']) if row.get('Uses Displacement') else 1.0
        return (input_value / unit_cost) * multiplier
    return input_value

def estimate_emission(row, units):
    impact_per_unit = parse_emission_value(row['CO₂e Impact'])
    return round(units * impact_per_unit, 2) if impact_per_unit is not None else None

# === 4. Policy Node Builder ===
def build_policy_node(policy_text, country, user_input, graph_intent, df_activity, df_country):
    activity_row = classify_policy(policy_text, df_activity)
    if activity_row is None:
        return None

    country_row = df_country[df_country['Country'].str.lower() == country.lower()].iloc[0]
    units = estimate_units(activity_row, user_input, country_row)
    impact = estimate_emission(activity_row, units)

    alignment = "Positive" if impact < 0 else "Negative" if impact > 0 else "Neutral"
    node_color = "green" if alignment == "Positive" else "red" if alignment == "Negative" else "gray"
    node_size = min(max(abs(impact), 10), 100)

    return {
        "Policy ID": str(uuid.uuid4())[:8],
        "Title": policy_text[:80],
        "Date": datetime.now().strftime('%Y-%m-%d'),
        "Country": country,
        "Graph Intent": graph_intent,
        "Activity Class": activity_row['Activity Class'],
        "Sector": activity_row['Sector'],
        "Instrument": activity_row['Instrument Type'],
        "CO₂e Impact": impact,
        "Unit": activity_row['Unit'],
        "Alignment": alignment,
        "Node Color": node_color,
        "Node Size": node_size,
        "Parent": graph_intent
    }

# === 5. Save/Load Graph State ===
def save_policy_node(node, path='data/policy_nodes.json'):
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
    else:
        data = []
    data.append(node)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def load_policy_nodes(path='data/policy_nodes.json'):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return []

