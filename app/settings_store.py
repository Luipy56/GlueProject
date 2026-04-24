from collections.abc import Mapping

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import AppSetting


async def get_all_settings(session: AsyncSession) -> dict[str, str]:
    rows = (await session.exec(select(AppSetting))).all()
    return {r.key: r.value for r in rows}


def effective_list_extraction_system_prompt(settings_map: Mapping[str, str]) -> str:
    """Single LLM listing prompt: system text plus legacy `listing_extra_instructions` until removed."""
    system = (settings_map.get("list_extraction_system_prompt") or "").strip()
    legacy = (settings_map.get("listing_extra_instructions") or "").strip()
    if not legacy:
        return system
    if not system:
        return legacy
    return f"{system}\n\n{legacy}".strip()


async def get_setting(session: AsyncSession, key: str, default: str = "") -> str:
    row = await session.get(AppSetting, key)
    return row.value if row else default


async def upsert_settings(session: AsyncSession, updates: dict[str, str]) -> None:
    for key, value in updates.items():
        row = await session.get(AppSetting, key)
        if row is None:
            session.add(AppSetting(key=key, value=value))
        else:
            row.value = value
    await session.commit()


async def delete_setting(session: AsyncSession, key: str) -> None:
    row = await session.get(AppSetting, key)
    if row is not None:
        await session.delete(row)
        await session.commit()
