"""Experimental listing path: LLM-driven browser agent (not shipped by default).

Install optional deps (e.g. browser-use) and wire them here for a Perplexity-style loop.
See README section on agent mode.
"""

import logging

from playwright.async_api import BrowserContext

_log = logging.getLogger(__name__)


async def extract_listing_candidates(page_url: str, context: BrowserContext) -> list[dict[str, str]]:
    _log.warning("agent_experimental listing_strategy requested for %s", page_url)
    raise RuntimeError(
        "listing_strategy=agent_experimental: el modo agente no está implementado en esta imagen. "
        "La app usa Playwright + LLM; un agente tipo browser-use requiere dependencias extra y límites "
        "de pasos (véase README y requirements-agent.txt)."
    )
