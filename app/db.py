from collections.abc import AsyncGenerator

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


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
