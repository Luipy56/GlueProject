from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlmodel import select

from app.db import AsyncSessionLocal, init_db
from app.models import Portal
from app.scraper.errors import LlmExtractionEmptyError
from app.scraper.pipeline import run_portal_llm_pass
from app.seed import ensure_seed_data


@pytest.mark.asyncio
async def test_run_portal_llm_pass_raises_when_candidates_but_empty_listings(monkeypatch: pytest.MonkeyPatch) -> None:
    await init_db()
    async with AsyncSessionLocal() as s:
        await ensure_seed_data(s)

    monkeypatch.setattr(
        "app.scraper.pipeline.resolve_llm_base_url_with_report",
        AsyncMock(return_value=("http://llm.test/v1", {})),
    )
    monkeypatch.setattr(
        "app.scraper.pipeline.listing_sources.extract_listing_candidates_for_strategy",
        AsyncMock(
            return_value=[
                {"url": "https://www.idealista.com/inmueble/1/", "snippet": "Piso en venta"},
            ]
        ),
    )
    monkeypatch.setattr(
        "app.scraper.pipeline.chat_completion_json",
        AsyncMock(
            return_value=(
                {"listings": []},
                "Como modelo no tengo la capacidad de navegar en sitios web externos.",
            )
        ),
    )

    async with AsyncSessionLocal() as session:
        portal = (await session.exec(select(Portal))).first()
        assert portal is not None
        with pytest.raises(LlmExtractionEmptyError) as ei:
            await run_portal_llm_pass(session, portal, MagicMock())
    msg = str(ei.value).lower()
    assert "extracción" in msg or "vacía" in msg
    assert "navegar" in msg or "scraping" in msg or "json" in msg


@pytest.mark.asyncio
async def test_run_portal_llm_pass_ok_when_no_candidates(monkeypatch: pytest.MonkeyPatch) -> None:
    await init_db()
    async with AsyncSessionLocal() as s:
        await ensure_seed_data(s)

    monkeypatch.setattr(
        "app.scraper.pipeline.resolve_llm_base_url_with_report",
        AsyncMock(return_value=("http://llm.test/v1", {})),
    )
    monkeypatch.setattr(
        "app.scraper.pipeline.listing_sources.extract_listing_candidates_for_strategy",
        AsyncMock(return_value=[]),
    )
    monkeypatch.setattr(
        "app.scraper.pipeline.chat_completion_json",
        AsyncMock(return_value=({"listings": []}, "")),
    )

    async with AsyncSessionLocal() as session:
        portal = (await session.exec(select(Portal))).first()
        assert portal is not None
        out, snippet = await run_portal_llm_pass(session, portal, MagicMock())
    assert out == []
    assert snippet == ""
