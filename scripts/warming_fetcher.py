# scripts/warming_fetcher.py

import requests, os, yaml, json
import pandas as pd

def load_config(path="config/cckp_variables.yaml"):
    current_dir = os.path.dirname(os.path.abspath(__file__))  # e.g. scripts/
    config_path = os.path.join(current_dir, "..", "config", "cckp_variables.yaml")
    config_path = os.path.abspath(config_path)
    with open(path, "r") as f:
        return yaml.safe_load(f)

def build_url(var_list, meta):
    vars_joined = ",".join(var_list)
    return f"https://cckpapi.worldbank.org/cckp/v1/{meta['collection']}_{meta['product']}_{vars_joined}_{meta['product']}_{meta['aggregation']}_{meta['period']}_{meta['percentile']}_{meta['scenario']}_ensemble_all_{meta['statistic']}/{{country}}?_format=json"

def fetch_raw_cckp(country):
    config = load_config()
    url = build_url(config["variables"], config["metadata"]).replace("{country}", country)
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"❌ Failed to fetch from CCKP: {response.status_code}")
    return response.json()

def process_cckp_json(raw_json):
    records = []
    for variable, countries in raw_json["data"].items():
        for ccode, series in countries.items():
            for date, value in series.items():
                records.append({
                    "country": ccode,
                    "variable": variable,
                    "date": date,
                    "value": value
                })
    return pd.DataFrame(records)
