from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from app.db import AsyncSessionLocal, init_db
from app.routers import api, web
from app.seed import ensure_seed_data
from app.settings_store import get_setting
from app.worker.scheduler import reschedule_scrape


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with AsyncSessionLocal() as session:
        await ensure_seed_data(session)
    hours = 8.0
    async with AsyncSessionLocal() as session:
        hours = float(await get_setting(session, "scrape_interval_hours", "8"))
    scheduler = AsyncIOScheduler()
    reschedule_scrape(scheduler, hours)
    scheduler.start()
    app.state.scheduler = scheduler
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="Garraf Property Monitor", lifespan=lifespan)
app.include_router(web.router)
app.include_router(api.router)
