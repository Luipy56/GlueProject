import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import AsyncSessionLocal
from app.jobs.scrape_job import SCRAPER_BUSY, execute_scrape
from app.models import ScrapeRun

router = APIRouter(prefix="/api", tags=["api"])


class RunBody(BaseModel):
    portal_id: int | None = None


@router.post("/run", response_model=None)
async def trigger_run(body: RunBody | None = None) -> dict:
    payload = body or RunBody()
    pid = payload.portal_id
    try:
        async with AsyncSessionLocal() as session:
            run: ScrapeRun = await execute_scrape(session, portal_id=pid)
    except RuntimeError as exc:
        if SCRAPER_BUSY in str(exc):
            raise HTTPException(
                status_code=409,
                detail="Another scrape is already in progress.",
            ) from exc
        raise
    except Exception as exc:  # noqa: BLE001
        logging.exception("POST /api/run failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {
        "run_id": run.id,
        "status": run.status,
        "new_listings": run.new_listings,
        "updated_listings": run.updated_listings,
        "error": run.error_message,
        "csv_path": run.csv_path,
    }
