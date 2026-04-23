import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import APP_VERSION, llm_base_url_from_env
from app.llm.resolver import clear_llm_resolver_cache
from app.db import AsyncSessionLocal
from app.deps import get_session
from app.jobs.scrape_job import SCRAPER_BUSY, execute_scrape
from app.models import BlacklistEntry, Listing, Portal, RunStatus, ScrapeRun
from app.services.blacklist import active_patterns, is_blocked
from app.settings_store import get_all_settings, upsert_settings
from app.worker.scheduler import reschedule_scrape

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
templates.env.globals["app_version"] = APP_VERSION


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    session: AsyncSession = Depends(get_session),
    only_latest_run: int = 0,
) -> HTMLResponse:
    stmt = (
        select(Listing, Portal)
        .join(Portal, Listing.portal_id == Portal.id)
        .order_by(Listing.last_seen.desc())  # type: ignore[union-attr]
    )
    rows = (await session.exec(stmt)).all()
    patterns = await active_patterns(session)
    listings: list[tuple[Listing, Portal]] = []
    for listing, portal in rows:
        if is_blocked(listing.canonical_url, patterns):
            continue
        listings.append((listing, portal))

    latest_run = (
        await session.exec(
            select(ScrapeRun)
            .where(ScrapeRun.status == RunStatus.success.value)
            .order_by(ScrapeRun.id.desc())  # type: ignore[union-attr]
        )
    ).first()

    if only_latest_run and latest_run is not None:
        listings = [t for t in listings if t[0].last_run_id == latest_run.id]
    only_flag = bool(only_latest_run)

    cfg = await get_all_settings(session)
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "listings": listings,
            "latest_run": latest_run,
            "settings": cfg,
            "only_latest_run": only_flag,
        },
    )


@router.get("/config", response_class=HTMLResponse)
async def config_get(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> HTMLResponse:
    cfg = await get_all_settings(session)
    env_llm = llm_base_url_from_env()
    effective_llm = env_llm or (cfg.get("llm_base_url", "").strip() or "https://api.openai.com/v1")
    return templates.TemplateResponse(
        request,
        "config.html",
        {
            "settings": cfg,
            "llm_env_override": env_llm,
            "llm_base_url_effective": effective_llm,
        },
    )


@router.post("/config")
async def config_post(
    request: Request,
    session: AsyncSession = Depends(get_session),
    scrape_interval_hours: str = Form(...),
    llm_provider: str = Form(...),
    llm_base_url: str = Form(...),
    llm_api_key: str = Form(""),
    llm_model: str = Form(...),
    llm_temperature: str = Form(...),
    list_extraction_system_prompt: str = Form(...),
) -> RedirectResponse:
    await upsert_settings(
        session,
        {
            "scrape_interval_hours": scrape_interval_hours,
            "llm_provider": llm_provider,
            "llm_base_url": llm_base_url.strip(),
            "llm_api_key": llm_api_key.strip(),
            "llm_model": llm_model.strip(),
            "llm_temperature": llm_temperature.strip(),
            "list_extraction_system_prompt": list_extraction_system_prompt,
        },
    )
    clear_llm_resolver_cache()
    sched = getattr(request.app.state, "scheduler", None)
    if sched is not None:
        try:
            reschedule_scrape(sched, float(scrape_interval_hours))
        except Exception:
            pass
    return RedirectResponse("/config", status_code=303)


@router.get("/portals", response_class=HTMLResponse)
async def portals_get(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> HTMLResponse:
    portals = (await session.exec(select(Portal).order_by(Portal.id))).all()  # type: ignore[arg-type]
    return templates.TemplateResponse(request, "portals.html", {"portals": portals})


@router.post("/portals/add")
async def portals_add(
    session: AsyncSession = Depends(get_session),
    name: str = Form(...),
    search_url: str = Form(...),
    prompt_template: str = Form(...),
    fetch_detail_for_phone: str = Form("off"),
) -> RedirectResponse:
    p = Portal(
        name=name.strip(),
        search_url=search_url.strip(),
        prompt_template=prompt_template,
        fetch_detail_for_phone=(fetch_detail_for_phone == "on"),
        enabled=True,
    )
    session.add(p)
    await session.commit()
    return RedirectResponse("/portals", status_code=303)


@router.post("/portals/edit")
async def portals_edit(
    session: AsyncSession = Depends(get_session),
    portal_id: int = Form(...),
    name: str = Form(...),
    search_url: str = Form(...),
    prompt_template: str = Form(...),
    fetch_detail_for_phone: str = Form("off"),
    enabled: str = Form("off"),
) -> RedirectResponse:
    p = await session.get(Portal, portal_id)
    if p:
        p.name = name.strip()
        p.search_url = search_url.strip()
        p.prompt_template = prompt_template
        p.fetch_detail_for_phone = fetch_detail_for_phone == "on"
        p.enabled = enabled == "on"
        session.add(p)
        await session.commit()
    return RedirectResponse("/portals", status_code=303)


@router.post("/portals/delete")
async def portals_delete(
    portal_id: int = Form(...),
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    p = await session.get(Portal, portal_id)
    if p:
        for row in (await session.exec(select(Listing).where(Listing.portal_id == portal_id))).all():
            await session.delete(row)
        await session.delete(p)
        await session.commit()
    return RedirectResponse("/portals", status_code=303)


@router.get("/runs", response_class=HTMLResponse)
async def runs_get(
    request: Request,
    session: AsyncSession = Depends(get_session),
    error: str = "",
    failed_run: int = 0,
    done_run: int = 0,
) -> HTMLResponse:
    runs = (await session.exec(select(ScrapeRun).order_by(ScrapeRun.id.desc()))).all()  # type: ignore[union-attr]
    banner_error = error.strip()
    failed_run_id: int | None = failed_run or None
    if failed_run_id:
        row = await session.get(ScrapeRun, failed_run_id)
        if row is None:
            banner_error = f"No se encontró la ejecución #{failed_run_id}."
        elif row.error_message:
            banner_error = row.error_message.strip()
        elif row.status == RunStatus.failed.value:
            banner_error = (
                "La ejecución terminó en estado «failed» pero no hay mensaje de error guardado."
            )
    success_message = ""
    done_run_id: int | None = done_run or None
    if done_run_id:
        row_done = await session.get(ScrapeRun, done_run_id)
        if row_done and row_done.status == RunStatus.success.value:
            success_message = (
                f"Ejecución #{done_run_id} correcta: {row_done.new_listings} anuncios nuevos, "
                f"{row_done.updated_listings} actualizados."
            )
    return templates.TemplateResponse(
        request,
        "runs.html",
        {
            "runs": runs,
            "run_error": banner_error,
            "success_message": success_message,
            "failed_run_id": failed_run_id,
            "done_run_id": done_run_id,
        },
    )


@router.get("/runs/{run_id}/download")
async def runs_download(
    run_id: int,
    session: AsyncSession = Depends(get_session),
) -> FileResponse:
    run = await session.get(ScrapeRun, run_id)
    if not run or not run.csv_path:
        raise HTTPException(status_code=404, detail="Run or CSV not found")
    path = Path(run.csv_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="CSV missing on disk")
    return FileResponse(path, filename=path.name, media_type="text/csv")


@router.get("/blacklist", response_class=HTMLResponse)
async def blacklist_get(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> HTMLResponse:
    rows = (await session.exec(select(BlacklistEntry).order_by(BlacklistEntry.id.desc()))).all()  # type: ignore[union-attr]
    return templates.TemplateResponse(request, "blacklist.html", {"entries": rows})


@router.post("/blacklist/add")
async def blacklist_add(
    pattern: str = Form(...),
    note: str = Form(""),
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    session.add(
        BlacklistEntry(
            pattern=pattern.strip(),
            note=note.strip() or None,
            created_at=datetime.utcnow(),
        )
    )
    await session.commit()
    return RedirectResponse("/blacklist", status_code=303)


@router.post("/blacklist/delete")
async def blacklist_delete(
    entry_id: int = Form(...),
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    row = await session.get(BlacklistEntry, entry_id)
    if row:
        await session.delete(row)
        await session.commit()
    return RedirectResponse("/blacklist", status_code=303)


@router.post("/blacklist/from_listing")
async def blacklist_from_listing(
    canonical_url: str = Form(...),
    note: str = Form(""),
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    session.add(
        BlacklistEntry(
            pattern=canonical_url.strip(),
            note=note.strip() or None,
            created_at=datetime.utcnow(),
        )
    )
    await session.commit()
    return RedirectResponse("/", status_code=303)


@router.post("/run-now")
async def run_now(
    portal_id: str = Form(""),
) -> RedirectResponse:
    """Use a dedicated DB session so long scrapes do not share the request session (avoids async/greenlet issues)."""
    pid: int | None = int(portal_id) if portal_id.strip().isdigit() else None
    try:
        async with AsyncSessionLocal() as session:
            run = await execute_scrape(session, portal_id=pid)
    except RuntimeError as exc:
        if SCRAPER_BUSY in str(exc):
            msg = quote(
                "Ya hay una ejecución en curso. Espera a que termine o revisa la tabla de ejecuciones.",
                safe="",
            )
            return RedirectResponse(f"/runs?error={msg}", status_code=303)
        logging.exception("POST /run-now failed")
        msg = quote(str(exc)[:1500], safe="")
        return RedirectResponse(f"/runs?error={msg}", status_code=303)
    except Exception as exc:  # noqa: BLE001
        logging.exception("POST /run-now failed")
        msg = quote(str(exc)[:1500], safe="")
        return RedirectResponse(f"/runs?error={msg}", status_code=303)
    if run.status == RunStatus.failed.value:
        return RedirectResponse(f"/runs?failed_run={run.id}", status_code=303)
    return RedirectResponse(f"/runs?done_run={run.id}", status_code=303)
