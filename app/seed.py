from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import AppSetting, Portal


DEFAULT_PORTAL = {
    "name": "Idealista Garraf",
    "search_url": "https://www.idealista.com/venta-viviendas/barcelona/garraf/",
    "enabled": True,
}

DEFAULT_SETTINGS: dict[str, str] = {
    "scrape_interval_hours": "8",
    "llm_provider": "openai_compatible",
    "llm_base_url": "https://api.openai.com/v1",
    "llm_api_key": "",
    "llm_model": "gpt-4o-mini",
    "llm_temperature": "0.2",
    "listing_strategy": "static",
    "list_extraction_system_prompt": (
        "You are a structured extraction assistant. "
        "You must NOT claim you cannot browse the web: snippets and URLs are already in the user JSON; "
        "you only classify and copy fields into JSON. "
        "Classify each listing snippet: private seller means individual name, no major agency branding; "
        "agency means known agency names or logos implied in text. "
        "The user message is JSON with keys portal, search_url, and listings (array of {url, text}). "
        "Output JSON with key 'listings': array of {url,title,price_raw,m2,seller_type} "
        "where seller_type is one of: private, agency, unknown. "
        "Include one row per input listing when the url is present. Return strict JSON only."
    ),
}


async def ensure_seed_data(session: AsyncSession) -> None:
    result = await session.exec(select(Portal))
    if not result.first():
        session.add(Portal(**DEFAULT_PORTAL))
        await session.commit()

    for key, value in DEFAULT_SETTINGS.items():
        existing = await session.get(AppSetting, key)
        if existing is None:
            session.add(AppSetting(key=key, value=value))
    await session.commit()
