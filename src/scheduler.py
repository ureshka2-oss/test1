"""
Task scheduler for periodic data refresh and analysis using APScheduler.
"""

import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from src.data_loader import load_market_data, validate_data, clean_data
from src.analysis import (
    market_size_by_sector,
    growth_leaders,
    sustainability_score,
)
import io
import contextlib

logger = logging.getLogger(__name__)

# In-memory cache for pre-computed analysis results
_cache = {
    "market_data": None,
    "market_size": None,
    "growth_leaders": None,
    "sustainability_scores": None,
    "last_refreshed": None,
    "last_report": None,
    "data_issues": [],
}

scheduler = BackgroundScheduler(
    jobstores={"default": MemoryJobStore()},
    job_defaults={"coalesce": True, "max_instances": 1},
)


def get_cache():
    """Return the current analysis cache."""
    return _cache


def refresh_data():
    """Reload market data from disk and update the cache."""
    logger.info("Running scheduled data refresh...")
    try:
        df = load_market_data()
        issues = validate_data(df)
        if issues:
            logger.warning("Data validation issues: %s", issues)
        _cache["market_data"] = clean_data(df)
        _cache["data_issues"] = issues
        _cache["last_refreshed"] = datetime.now().isoformat()
        logger.info("Data refresh completed at %s", _cache["last_refreshed"])
    except Exception:
        logger.exception("Data refresh failed")


def refresh_analysis():
    """Re-run analysis on cached data and store results."""
    logger.info("Running scheduled analysis refresh...")
    df = _cache.get("market_data")
    if df is None:
        logger.warning("No cached data available, running data refresh first")
        refresh_data()
        df = _cache.get("market_data")
        if df is None:
            return

    try:
        raw_df = load_market_data()
        _cache["market_size"] = market_size_by_sector(raw_df).reset_index().to_dict(orient="records")
        _cache["growth_leaders"] = growth_leaders(raw_df, top_n=5).to_dict(orient="records")
        _cache["sustainability_scores"] = sustainability_score(raw_df).to_dict(orient="records")
        logger.info("Analysis refresh completed")
    except Exception:
        logger.exception("Analysis refresh failed")


def generate_scheduled_report():
    """Generate and cache the executive summary report."""
    logger.info("Running scheduled report generation...")
    try:
        from src.report import generate_report

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            generate_report()
        _cache["last_report"] = {
            "content": buf.getvalue(),
            "generated_at": datetime.now().isoformat(),
        }
        logger.info("Report generation completed")
    except Exception:
        logger.exception("Report generation failed")


def init_scheduler():
    """Initialize and start the scheduler with default jobs."""
    # Refresh data every 30 minutes
    scheduler.add_job(
        refresh_data,
        trigger=IntervalTrigger(minutes=30),
        id="refresh_data",
        name="Refresh market data from disk",
        replace_existing=True,
    )

    # Re-run analysis every hour
    scheduler.add_job(
        refresh_analysis,
        trigger=IntervalTrigger(hours=1),
        id="refresh_analysis",
        name="Refresh pre-computed analysis",
        replace_existing=True,
    )

    # Generate report daily at 6:00 AM
    scheduler.add_job(
        generate_scheduled_report,
        trigger=CronTrigger(hour=6, minute=0),
        id="daily_report",
        name="Generate daily executive report",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))

    # Run initial data load immediately
    refresh_data()
    refresh_analysis()


def shutdown_scheduler():
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")
