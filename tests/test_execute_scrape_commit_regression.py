"""
Regression: after committing listing rows, updating ScrapeRun must not touch
expired ORM state in a way that triggers sqlalchemy.exc.MissingGreenlet on async.
"""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.db import AsyncSessionLocal, init_db
from app.jobs.scrape_job import execute_scrape
from app.models import Listing, RunStatus, ScrapeRun
from app.seed import ensure_seed_data
from sqlmodel import select


@asynccontextmanager
async def _noop_browser():
    yield MagicMock()


@pytest.mark.asyncio
async def test_execute_scrape_success_path_with_merge_and_final_update(monkeypatch: pytest.MonkeyPatch) -> None:
    await init_db()
    async with AsyncSessionLocal() as s:
        await ensure_seed_data(s)

    monkeypatch.setattr(
        "app.jobs.scrape_job.persistent_browser_context",
        _noop_browser,
    )

    async def fake_pass(session, portal, ctx, max_listings: int = 45):  # noqa: ARG001
        return [
            {
                "url": "https://www.idealista.com/inmueble/99999999/",
                "title": "Test listing",
                "price_raw": "100.000 €",
                "m2": "80 m²",
                "seller_type": "private",
                "phone": None,
            }
        ]

    monkeypatch.setattr("app.jobs.scrape_job.run_portal_llm_pass", fake_pass)
    monkeypatch.setattr(
        "app.jobs.scrape_job.enrich_with_detail_phones",
        AsyncMock(side_effect=lambda rows, ctx, fetch_detail=True: rows),
    )

    async with AsyncSessionLocal() as session:
        run = await execute_scrape(session, portal_id=None)

    assert run.status == RunStatus.success.value
    assert run.csv_path
    assert run.new_listings >= 1

    async with AsyncSessionLocal() as session:
        rows = (await session.exec(select(Listing))).all()
        assert any("99999999" in x.canonical_url for x in rows)
        r2 = (await session.exec(select(ScrapeRun).where(ScrapeRun.id == run.id))).first()
        assert r2 is not None
        assert r2.status == RunStatus.success.value
