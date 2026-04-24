"""Dispatch listing HTML extraction by global Config `listing_strategy`."""

import logging
from typing import Final

from playwright.async_api import BrowserContext

_log = logging.getLogger(__name__)

_STRATEGIES: Final[frozenset[str]] = frozenset({"static", "crawl4ai", "agent_experimental"})


def normalize_listing_strategy(raw: str | None) -> str:
    v = (raw or "static").strip().lower()
    return v if v in _STRATEGIES else "static"


async def extract_listing_candidates_for_strategy(
    strategy: str,
    search_url: str,
    context: BrowserContext,
) -> list[dict[str, str]]:
    strat = normalize_listing_strategy(strategy)
    _log.info("listing_strategy=%s search_url=%s", strat, search_url[:120])

    if strat == "crawl4ai":
        from app.scraper import crawl4ai_listings

        return await crawl4ai_listings.extract_listing_candidates(search_url)

    if strat == "agent_experimental":
        from app.scraper import agent_listing

        return await agent_listing.extract_listing_candidates(search_url, context)

    from app.scraper import idealista

    return await idealista.extract_listing_candidates(search_url, context)
