from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

import logging

from app.db import AsyncSessionLocal
from app.jobs.scrape_job import SCRAPER_BUSY, execute_scrape

logger = logging.getLogger(__name__)


async def scrape_tick() -> None:
    try:
        async with AsyncSessionLocal() as session:
            await execute_scrape(session)
    except RuntimeError as exc:
        if SCRAPER_BUSY in str(exc):
            logger.info("Scheduled scrape skipped: another run is in progress")
            return
        raise


def reschedule_scrape(scheduler: AsyncIOScheduler, hours: float) -> None:
    if scheduler.get_job("scrape"):
        scheduler.remove_job("scrape")
    scheduler.add_job(
        scrape_tick,
        IntervalTrigger(hours=max(0.25, hours)),
        id="scrape",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )
