from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import AppSetting, Portal


DEFAULT_PORTAL = {
    "name": "Idealista Garraf",
    "search_url": "https://www.idealista.com/venta-viviendas/barcelona/garraf/",
    "prompt_template": (
        "You classify real-estate listing snippets from Idealista. "
        "Private seller: individual name, no major agency branding. "
        "Agency: known agency names/logos implied in text. "
        "Return strict JSON only."
    ),
    "fetch_detail_for_phone": True,
    "enabled": True,
}

DEFAULT_SETTINGS: dict[str, str] = {
    "scrape_interval_hours": "8",
    "llm_provider": "openai_compatible",
    "llm_base_url": "https://api.openai.com/v1",
    "llm_api_key": "",
    "llm_model": "gpt-4o-mini",
    "llm_temperature": "0.2",
    "list_extraction_system_prompt": (
        "You are a structured extraction assistant. "
        "Given listing snippets (url + text), output JSON with key "
        "'listings': array of {url,title,price_raw,m2,seller_type} "
        "where seller_type is one of: private, agency, unknown."
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
