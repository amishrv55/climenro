import pandas as pd

def forecast_policy_impact(policy_input):
    """
    Forecast CO2 emissions based on simplified policy assumptions.
    """
    country = policy_input["country"]
    initial_emissions = policy_input["initial_emissions"]  # MtCO₂e
    policy_type = policy_input["policy_type"]
    price_signal = policy_input["price_signal"]
    coverage = policy_input["coverage"]
    duration_years = policy_input["duration_years"]

    # Sectoral binary toggles
    sectors = [
        policy_input["covers_transport"],
        policy_input["covers_industry"],
        policy_input["covers_buildings"],
        policy_input["covers_agriculture"],
        policy_input["covers_lulucf"],
    ]

    num_sectors = sum(sectors)

    # Define base effectiveness factor
    base_factor = 0.01  # 1% reduction per year baseline
    price_factor = min(price_signal / 100, 1.5)  # max multiplier
    coverage_factor = coverage / 100
    sector_factor = num_sectors / 5

    # Policy multiplier based on type
    type_multiplier = {
        "Tax": 1.0,
        "ETS": 0.9,
        "Hybrid": 1.2,
    }.get(policy_type, 1.0)

    # Final annual reduction rate
    annual_reduction = (
        base_factor * price_factor * coverage_factor * sector_factor * type_multiplier
    )

    # Forecast emissions
    years = list(range(2025, 2025 + duration_years + 1))
    emissions = [initial_emissions]
    for _ in range(duration_years):
        last = emissions[-1]
        reduced = last * (1 - annual_reduction)
        emissions.append(max(reduced, 0))  # Avoid negative emissions
        total_reductions = initial_emissions - emissions[-1]
        reduction_percent = (total_reductions / initial_emissions) * 100 if initial_emissions else 0
        average_reduction = (total_reductions / duration_years)

    forecast_df = pd.DataFrame({"Year": years, "Projected Emissions (MtCO₂e)": emissions})

    metrics = {
        "annual_reduction": annual_reduction,
        "total_reduction": initial_emissions - emissions[-1],
        "final_emissions": emissions[-1],
        "percent_reduction": reduction_percent,
        "average_reduction": average_reduction,
    }

    metrics["initial_emissions"] = initial_emissions

    return forecast_df, metrics
