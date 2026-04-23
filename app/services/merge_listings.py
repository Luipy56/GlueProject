from datetime import datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Listing
from app.services.blacklist import is_blocked
from app.util_urls import canonicalize_url


async def merge_listing_row(
    session: AsyncSession,
    *,
    portal_id: int,
    run_id: int,
    url: str,
    title: str | None,
    price_raw: str | None,
    m2: str | None,
    phone: str | None,
    seller_type: str,
    blacklist_patterns: list[str],
) -> tuple[str, Listing | None]:
    """
    Returns (kind, listing):
    - ('blacklist', None)
    - ('new', Listing)
    - ('updated', Listing)
    Does not commit the session.
    """
    canonical = canonicalize_url(url)
    if is_blocked(canonical, blacklist_patterns):
        return "blacklist", None

    existing = (
        await session.exec(select(Listing).where(Listing.canonical_url == canonical))
    ).first()

    now = datetime.utcnow()
    if existing:
        if title:
            existing.title = title
        if price_raw:
            existing.price_raw = price_raw
        if m2:
            existing.m2 = m2
        if phone:
            existing.phone = phone
        if seller_type:
            existing.seller_type = seller_type
        existing.last_seen = now
        existing.last_run_id = run_id
        session.add(existing)
        await session.flush()
        return "updated", existing

    listing = Listing(
        portal_id=portal_id,
        canonical_url=canonical,
        title=title,
        price_raw=price_raw,
        m2=m2,
        phone=phone,
        seller_type=seller_type,
        first_seen=now,
        last_seen=now,
        last_run_id=run_id,
    )
    session.add(listing)
    await session.flush()
    return "new", listing
