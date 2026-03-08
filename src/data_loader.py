"""
Data loading and validation module for the Global Energy Market Analysis pipeline.
"""

import os
import pandas as pd


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load_market_data(filename="global_energy_market.csv"):
    """Load the global energy market dataset."""
    filepath = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(filepath)
    return df


def validate_data(df):
    """Validate the dataset and return a report of issues."""
    issues = []

    # Check for missing values
    missing = df.isnull().sum()
    for col in missing[missing > 0].index:
        issues.append(f"Column '{col}' has {missing[col]} missing values")

    # Check for negative revenues
    for col in ["revenue_2022_bn", "revenue_2023_bn"]:
        if (df[col] < 0).any():
            issues.append(f"Column '{col}' contains negative values")

    # Check renewable_pct is between 0 and 100
    if (df["renewable_pct"] > 100).any() or (df["renewable_pct"] < 0).any():
        issues.append("renewable_pct contains values outside 0-100 range")

    # Check customer_satisfaction is between 0 and 100
    if (df["customer_satisfaction"] > 100).any() or (df["customer_satisfaction"] < 0).any():
        issues.append("customer_satisfaction contains values outside 0-100 range")

    return issues


def clean_data(df):
    """Clean the dataset by handling missing values and standardizing formats."""
    df = df.copy()

    # Standardize region names
    region_map = {
        "North America": "NA",
        "Europe": "EU",
        "Asia Pacific": "APAC",
        "Middle East": "ME",
        "Africa": "AFR",
        "South America": "SA",
    }
    df["region_code"] = df["region"].map(region_map)

    # Calculate year-over-year revenue growth
    df["revenue_growth_pct"] = (
        (df["revenue_2023_bn"] - df["revenue_2022_bn"]) / df["revenue_2022_bn"] * 100
    )

    # Calculate R&D intensity (R&D spend as % of revenue)
    df["rd_intensity"] = df["r_and_d_spend_mm"] / (df["revenue_2023_bn"] * 1000) * 100

    return df
