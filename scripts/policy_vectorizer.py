import pandas as pd
import numpy as np
from datetime import datetime

def score_policy_vector(row):
    today = datetime.today().year

    # Extract implementation year
    year_match = pd.to_numeric(str(row.get("Status", ""))[-4:], errors="coerce")
    duration_years = today - year_match if pd.notna(year_match) else 0

    # Is the policy still in place?
    is_active = 1 if "implemented" in str(row.get("Status", "")).lower() else 0

    # Carbon price (handle euros and text)
    raw_price = str(row.get("Price on 1 April", "0")).replace("€", "").replace("US$", "")
    price = pd.to_numeric(raw_price.split()[0], errors="coerce")
    price = price if pd.notna(price) else 0

    # Sectors covered
    sectors = [
        "Transport", "Industry", "Buildings", "Agricultural emissions", "LULUCF"
    ]
    sector_flags = [1 if pd.notna(row.get(sec)) and str(row[sec]).strip() != "" else 0 for sec in sectors]
    num_sectors_covered = sum(sector_flags)

    # Overlap indicators (placeholders - update logic later)
    subsidy_overlap = 1 if "subsidy" in str(row.get("Relation to other instruments", "")).lower() else 0
    tax_relief_overlap = 1 if "relief" in str(row.get("Relation to other instruments", "")).lower() else 0

    # Policy type
    policy_type = str(row.get("Type", "")).lower()
    policy_type_tax = 1 if "tax" in policy_type else 0
    policy_type_ets = 1 if "ets" in policy_type or "trading" in policy_type else 0
    policy_type_hybrid = 1 if "hybrid" in policy_type else 0

    return {
        "jurisdiction": row.get("Jurisdiction covered", ""),
        "duration_years": duration_years,
        "is_active": is_active,
        "price_signal": price,
        "num_sectors_covered": num_sectors_covered,
        "covers_transport": sector_flags[0],
        "covers_industry": sector_flags[1],
        "covers_buildings": sector_flags[2],
        "covers_agriculture": sector_flags[3],
        "covers_lulucf": sector_flags[4],
        "subsidy_overlap": subsidy_overlap,
        "tax_relief_overlap": tax_relief_overlap,
        "policy_type_tax": policy_type_tax,
        "policy_type_ets": policy_type_ets,
        "policy_type_hybrid": policy_type_hybrid,
    }
