from datetime import datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import BlacklistEntry


async def active_patterns(session: AsyncSession) -> list[str]:
    now = datetime.utcnow()
    rows = (await session.exec(select(BlacklistEntry))).all()
    out: list[str] = []
    for r in rows:
        if r.expires_at and r.expires_at < now:
            continue
        out.append(r.pattern)
    return out


def is_blocked(canonical_url: str, patterns: list[str]) -> bool:
    u = canonical_url
    for p in patterns:
        if not p:
            continue
        if u == p or u.startswith(p):
            return True
    return False
