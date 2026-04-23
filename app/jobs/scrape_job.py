import asyncio
import logging
from datetime import datetime

import httpx
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings
from app.models import Portal, RunStatus, ScrapeRun
from app.scraper.pipeline import enrich_with_detail_phones, run_portal_llm_pass
from app.scraper.playwright_session import persistent_browser_context
from app.services.blacklist import active_patterns
from app.services.export_csv import write_listings_csv
from app.services.merge_listings import merge_listing_row

SCRAPER_BUSY = "SCRAPER_BUSY"
_busy_lock = asyncio.Lock()
_scrape_in_progress = False


async def execute_scrape(session: AsyncSession, portal_id: int | None = None) -> ScrapeRun:
    global _scrape_in_progress
    async with _busy_lock:
        if _scrape_in_progress:
            raise RuntimeError(SCRAPER_BUSY)
        _scrape_in_progress = True
    try:
        return await _execute_scrape_impl(session, portal_id)
    finally:
        async with _busy_lock:
            _scrape_in_progress = False


async def _execute_scrape_impl(session: AsyncSession, portal_id: int | None = None) -> ScrapeRun:
    q = select(Portal).where(Portal.enabled.is_(True))
    if portal_id is not None:
        q = q.where(Portal.id == portal_id)
    portals = (await session.exec(q)).all()
    if not portals:
        run = ScrapeRun(
            portal_id=portal_id,
            status=RunStatus.failed.value,
            finished_at=datetime.utcnow(),
            error_message="No enabled portals match criteria.",
        )
        session.add(run)
        await session.commit()
        await session.refresh(run)
        return run

    run = ScrapeRun(portal_id=portal_id, status=RunStatus.running.value)
    session.add(run)
    await session.commit()
    await session.refresh(run)
    run_pk: int = run.id

    csv_rows: list[dict] = []
    new_count = 0
    updated_count = 0

    try:
        patterns = await active_patterns(session)
        async with persistent_browser_context() as ctx:
            for portal in portals:
                rows = await run_portal_llm_pass(session, portal, ctx)
                rows = await enrich_with_detail_phones(
                    rows,
                    ctx,
                    fetch_detail=portal.fetch_detail_for_phone,
                )
                for row in rows:
                    kind, listing = await merge_listing_row(
                        session,
                        portal_id=portal.id,
                        run_id=run_pk,
                        url=str(row.get("url", "")),
                        title=row.get("title"),
                        price_raw=row.get("price_raw"),
                        m2=row.get("m2"),
                        phone=row.get("phone"),
                        seller_type=str(row.get("seller_type", "unknown")),
                        blacklist_patterns=patterns,
                    )
                    if kind == "blacklist" or listing is None:
                        continue
                    if kind == "new":
                        new_count += 1
                    else:
                        updated_count += 1
                    csv_rows.append(
                        {
                            "canonical_url": listing.canonical_url,
                            "title": listing.title or "",
                            "price_raw": listing.price_raw or "",
                            "m2": listing.m2 or "",
                            "phone": listing.phone or "",
                            "seller_type": listing.seller_type,
                            "portal": portal.name,
                            "first_seen": listing.first_seen.isoformat(),
                            "last_seen": listing.last_seen.isoformat(),
                            "run_id": run_pk,
                        }
                    )

        await session.commit()

        csv_path = settings.runs_csv_dir / f"run_{run_pk}.csv"
        write_listings_csv(csv_path, csv_rows)

        run_final = await session.get(ScrapeRun, run_pk)
        if run_final is None:
            raise RuntimeError(f"ScrapeRun id={run_pk} missing after commit")
        run_final.status = RunStatus.success.value
        run_final.finished_at = datetime.utcnow()
        run_final.csv_path = str(csv_path)
        run_final.new_listings = new_count
        run_final.updated_listings = updated_count
        session.add(run_final)
        await session.commit()
        await session.refresh(run_final)
        return run_final
    except Exception as exc:  # noqa: BLE001
        logging.exception("execute_scrape failed run_id=%s", run_pk)
        await session.rollback()
        run_db = await session.get(ScrapeRun, run_pk)
        if run_db is not None:
            run_db.status = RunStatus.failed.value
            run_db.finished_at = datetime.utcnow()
            err_text = str(exc)
            if isinstance(exc, httpx.ConnectError):
                err_text += (
                    "\n\n[Hint] The app already tried several URLs automatically. If it still fails: "
                    "`GET /api/llm-check`, expose Ollama on `0.0.0.0:11434`, or "
                    "`docker compose -f docker-compose.host.yml up` (see README)."
                )
            run_db.error_message = err_text
            session.add(run_db)
            await session.commit()
            await session.refresh(run_db)
            return run_db
        raise
