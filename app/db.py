from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings
from app import models as _models  # noqa: F401  — register SQLModel metadata


def _database_url() -> str:
    if settings.database_url:
        return settings.database_url
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    path = settings.sqlite_path
    return f"sqlite+aiosqlite:///{path}"


engine: AsyncEngine = create_async_engine(
    _database_url(),
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def _migrate_sqlite_add_llm_snippet_column() -> None:
    if "sqlite" not in _database_url().lower():
        return
    async with engine.begin() as conn:
        r = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='scraperun'")
        )
        if r.fetchone() is None:
            return
        r2 = await conn.execute(text("PRAGMA table_info(scraperun)"))
        col_names = {row[1] for row in r2.fetchall()}
        if "llm_response_snippet" not in col_names:
            await conn.execute(text("ALTER TABLE scraperun ADD COLUMN llm_response_snippet TEXT"))


async def _migrate_sqlite_drop_legacy_portal_columns() -> None:
    """Remove per-portal config moved to AppSetting (Config). Requires SQLite 3.35+ DROP COLUMN."""
    if "sqlite" not in _database_url().lower():
        return
    async with engine.begin() as conn:
        r = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='portal'")
        )
        if r.fetchone() is None:
            return
        r2 = await conn.execute(text("PRAGMA table_info(portal)"))
        col_names = {row[1] for row in r2.fetchall()}
        for col in ("listing_strategy", "prompt_template", "fetch_detail_for_phone"):
            if col not in col_names:
                continue
            try:
                await conn.execute(text(f'ALTER TABLE portal DROP COLUMN "{col}"'))
            except Exception:
                # Older SQLite without DROP COLUMN: leave table; ORM ignores unknown columns at read time
                pass


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    await _migrate_sqlite_add_llm_snippet_column()
    await _migrate_sqlite_drop_legacy_portal_columns()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
