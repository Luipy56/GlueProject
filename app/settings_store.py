from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import AppSetting


async def get_all_settings(session: AsyncSession) -> dict[str, str]:
    rows = (await session.exec(select(AppSetting))).all()
    return {r.key: r.value for r in rows}


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
