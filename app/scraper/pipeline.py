import json
from typing import Any

from playwright.async_api import BrowserContext
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import llm_base_url_from_env
from app.llm.client import chat_completion_json
from app.models import Portal
from app.scraper import idealista
from app.settings_store import get_all_settings


async def run_portal_llm_pass(
    session: AsyncSession,
    portal: Portal,
    context: BrowserContext,
    *,
    max_listings: int = 45,
) -> list[dict[str, Any]]:
    settings_map = await get_all_settings(session)
    base_url = (
        llm_base_url_from_env()
        or settings_map.get("llm_base_url", "").strip()
        or "https://api.openai.com/v1"
    )
    api_key = settings_map.get("llm_api_key", "")
    model = settings_map.get("llm_model", "gpt-4o-mini")
    temperature = float(settings_map.get("llm_temperature", "0.2"))
    system_list = settings_map.get("list_extraction_system_prompt", "")

    candidates = await idealista.extract_listing_candidates(portal.search_url, context)
    candidates = candidates[:max_listings]

    user_payload = {
        "portal": portal.name,
        "instructions": portal.prompt_template,
        "listings": candidates,
    }
    messages = [
        {"role": "system", "content": system_list},
        {
            "role": "user",
            "content": json.dumps(user_payload, ensure_ascii=False),
        },
    ]
    parsed = await chat_completion_json(
        base_url=base_url,
        api_key=api_key,
        model=model,
        temperature=temperature,
        messages=messages,
    )
    listings = parsed.get("listings")
    if not isinstance(listings, list):
        return []
    normalized: list[dict[str, Any]] = []
    for row in listings:
        if not isinstance(row, dict):
            continue
        url = str(row.get("url", "")).strip()
        if not url:
            continue
        normalized.append(
            {
                "url": url,
                "title": row.get("title"),
                "price_raw": row.get("price_raw"),
                "m2": row.get("m2"),
                "seller_type": str(row.get("seller_type", "unknown")).lower(),
                "phone": row.get("phone"),
            }
        )
    return normalized


async def enrich_with_detail_phones(
    rows: list[dict[str, Any]],
    context: BrowserContext,
    *,
    fetch_detail: bool,
) -> list[dict[str, Any]]:
    if not fetch_detail:
        return rows
    out: list[dict[str, Any]] = []
    for row in rows:
        st = row.get("seller_type", "unknown")
        url = row.get("url", "")
        phone = row.get("phone")
        if st == "private" and url and not phone:
            try:
                phone = await idealista.extract_detail_phone(url, context)
            except Exception:
                phone = None
            row = {**row, "phone": phone}
        out.append(row)
    return out
