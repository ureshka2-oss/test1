"""
FastAPI backend serving energy market analysis results.
"""

from fastapi import FastAPI, HTTPException, Query
from src.data_loader import load_market_data, clean_data
from src.analysis import (
    market_size_by_sector,
    regional_benchmark,
    growth_leaders,
    sustainability_score,
    competitive_positioning,
)

app = FastAPI(
    title="Global Energy Market Analysis API",
    description="Market sizing and benchmarking for the global energy sector",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "Global Energy Market Analysis API", "version": "0.1.0"}


@app.get("/api/market-size")
def get_market_size():
    """Get total market size breakdown by sector."""
    df = load_market_data()
    result = market_size_by_sector(df)
    return result.reset_index().to_dict(orient="records")


@app.get("/api/regional-benchmark")
def get_regional_benchmark():
    """Get regional benchmarking analysis."""
    df = load_market_data()
    result = regional_benchmark(df)
    return result.reset_index().to_dict(orient="records")


@app.get("/api/growth-leaders")
def get_growth_leaders(top_n: int = Query(default=5, ge=1, le=20)):
    """Get top N fastest-growing companies."""
    df = load_market_data()
    result = growth_leaders(df, top_n=top_n)
    return result.to_dict(orient="records")


@app.get("/api/sustainability")
def get_sustainability_scores():
    """Get sustainability scores for all companies."""
    df = load_market_data()
    result = sustainability_score(df)
    return result.to_dict(orient="records")


@app.get("/api/competitive/{sector}")
def get_competitive_positioning(sector: str):
    """Get competitive positioning within a sector."""
    df = load_market_data()

    valid_sectors = df["sector"].unique().tolist()
    if sector not in valid_sectors:
        raise HTTPException(
            status_code=404,
            detail=f"Sector '{sector}' not found. Valid sectors: {valid_sectors}",
        )

    result = competitive_positioning(df, sector)
    return result.to_dict(orient="records")


@app.get("/api/company/{company_name}")
def get_company_details(company_name: str):
    """Get detailed analysis for a specific company."""
    df = load_market_data()
    df_clean = clean_data(df)

    company = df_clean[df_clean["company"] == company_name]
    if company.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Company '{company_name}' not found",
        )

    return company.to_dict(orient="records")[0]


@app.get("/api/compare")
def compare_sectors(sector_a: str, sector_b: str):
    """Compare two sectors head to head."""
    df = load_market_data()

    comparison = {}
    for sector in [sector_a, sector_b]:
        sector_data = df[df["sector"] == sector]
        if sector_data.empty:
            raise HTTPException(status_code=404, detail=f"Sector '{sector}' not found")

        comparison[sector] = {
            "total_revenue": sector_data["revenue_2023_bn"].sum(),
            "avg_growth": (
                (sector_data["revenue_2023_bn"] - sector_data["revenue_2022_bn"])
                / sector_data["revenue_2022_bn"].replace(0, float("nan"))
                * 100
            ).mean(),
            "avg_carbon_intensity": sector_data["carbon_intensity"].mean(),
            "total_employees": int(sector_data["employees"].sum()),
        }

    return comparison
