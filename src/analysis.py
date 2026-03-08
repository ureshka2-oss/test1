"""
Core analysis module for market sizing and benchmarking.
"""

import pandas as pd
import numpy as np


def market_size_by_sector(df):
    """Calculate total market size by sector."""
    result = df.groupby("sector").agg(
        total_revenue_2023=("revenue_2023_bn", "sum"),
        total_market_cap=("market_cap_bn", "sum"),
        num_companies=("company", "count"),
        avg_employees=("employees", "mean"),
    ).round(1)

    result["avg_revenue_per_company"] = (
        result["total_revenue_2023"] / result["num_companies"]
    ).round(1)

    return result.sort_values("total_revenue_2023", ascending=False)


def regional_benchmark(df):
    """Benchmark companies across regions."""
    result = df.groupby("region").agg(
        total_revenue=("revenue_2023_bn", "sum"),
        avg_carbon_intensity=("carbon_intensity", "mean"),
        avg_renewable_pct=("renewable_pct", "mean"),
        avg_satisfaction=("customer_satisfaction", "mean"),
        total_rd_spend=("r_and_d_spend_mm", "sum"),
    ).round(1)

    return result.sort_values("total_revenue", ascending=False)


def growth_leaders(df, top_n=5):
    """Identify fastest-growing companies by revenue growth."""
    df = df.copy()
    df["revenue_growth_pct"] = (
        (df["revenue_2023_bn"] - df["revenue_2022_bn"]) / df["revenue_2022_bn"] * 100
    ).round(1)

    return df.nlargest(top_n, "revenue_growth_pct")[
        ["company", "sector", "region", "revenue_2022_bn", "revenue_2023_bn", "revenue_growth_pct"]
    ]


def sustainability_score(df):
    """
    Calculate a composite sustainability score for each company.
    Score = weighted combination of renewable_pct, inverse carbon_intensity, and R&D intensity.
    """
    df = df.copy()

    # Normalize metrics to 0-100 scale
    df["norm_renewable"] = df["renewable_pct"]
    df["norm_carbon"] = 100 - (df["carbon_intensity"] / df["carbon_intensity"].max() * 100)
    df["rd_intensity"] = df["r_and_d_spend_mm"] / (df["revenue_2023_bn"] * 1000) * 100
    df["norm_rd"] = df["rd_intensity"] / df["rd_intensity"].max() * 100

    # BUG: Weights don't sum to 1.0 (should be 0.4 + 0.35 + 0.25 = 1.0)
    df["sustainability_score"] = (
        df["norm_renewable"] * 0.4
        + df["norm_carbon"] * 0.35
        + df["norm_rd"] * 0.15
    ).round(1)

    return df[["company", "sector", "region", "sustainability_score", "renewable_pct", "carbon_intensity"]].sort_values(
        "sustainability_score", ascending=False
    )


def competitive_positioning(df, sector):
    """Analyze competitive positioning within a sector."""
    sector_df = df[df["sector"] == sector].copy()

    if sector_df.empty:
        return None

    sector_df["market_share_pct"] = (
        sector_df["revenue_2023_bn"] / sector_df["revenue_2023_bn"].sum() * 100
    ).round(1)

    sector_df["efficiency_ratio"] = (
        sector_df["revenue_2023_bn"] * 1e9 / sector_df["employees"]
    ).round(0)

    return sector_df[
        ["company", "region", "revenue_2023_bn", "market_share_pct", "market_cap_bn", "efficiency_ratio", "customer_satisfaction"]
    ].sort_values("market_share_pct", ascending=False)


# TODO: Add year-over-year trend analysis
# TODO: Add market concentration (HHI) calculation
# TODO: Add correlation analysis between R&D spend and growth
