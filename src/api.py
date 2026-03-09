"""
FastAPI backend serving energy market analysis results.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from src.data_loader import load_market_data, clean_data
from src.analysis import (
    market_size_by_sector,
    regional_benchmark,
    growth_leaders,
    sustainability_score,
    competitive_positioning,
)
from src.scheduler import (
    init_scheduler,
    shutdown_scheduler,
    scheduler,
    get_cache,
    refresh_data,
    refresh_analysis,
    generate_scheduled_report,
)

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app):
    init_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(
    title="Global Energy Market Analysis API",
    description="Market sizing and benchmarking for the global energy sector",
    version="0.1.0",
    lifespan=lifespan,
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
                / sector_data["revenue_2022_bn"]
                * 100
            ).mean(),
            "avg_carbon_intensity": sector_data["carbon_intensity"].mean(),
            "total_employees": int(sector_data["employees"].sum()),
        }

    return comparison


# --- Scheduler management endpoints ---


@app.get("/api/scheduler/jobs")
def list_scheduled_jobs():
    """List all scheduled jobs and their next run times."""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": str(job.next_run_time) if job.next_run_time else None,
            "trigger": str(job.trigger),
        })
    return {"jobs": jobs}


@app.post("/api/scheduler/jobs/{job_id}/run")
def run_job_now(job_id: str):
    """Trigger a scheduled job to run immediately."""
    job_map = {
        "refresh_data": refresh_data,
        "refresh_analysis": refresh_analysis,
        "daily_report": generate_scheduled_report,
    }
    if job_id not in job_map:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    job_map[job_id]()
    return {"status": "completed", "job_id": job_id}


@app.post("/api/scheduler/jobs/{job_id}/pause")
def pause_job(job_id: str):
    """Pause a scheduled job."""
    try:
        scheduler.pause_job(job_id)
        return {"status": "paused", "job_id": job_id}
    except Exception:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")


@app.post("/api/scheduler/jobs/{job_id}/resume")
def resume_job(job_id: str):
    """Resume a paused scheduled job."""
    try:
        scheduler.resume_job(job_id)
        return {"status": "resumed", "job_id": job_id}
    except Exception:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")


@app.get("/api/scheduler/cache")
def get_cached_data():
    """Get the current state of the analysis cache."""
    cache = get_cache()
    return {
        "last_refreshed": cache["last_refreshed"],
        "data_issues": cache["data_issues"],
        "has_market_size": cache["market_size"] is not None,
        "has_growth_leaders": cache["growth_leaders"] is not None,
        "has_sustainability_scores": cache["sustainability_scores"] is not None,
        "has_report": cache["last_report"] is not None,
    }


@app.get("/api/scheduler/report")
def get_latest_report():
    """Get the latest generated report from the cache."""
    cache = get_cache()
    if cache["last_report"] is None:
        raise HTTPException(status_code=404, detail="No report has been generated yet")
    return cache["last_report"]
